import json
import pytest
from sawtna.config import ROOT


def test_integrated_services_and_storage(stack):
    client, _, _ = stack
    health = client.get("/health").json()
    assert health["status"] == "ok"
    assert all(health["dependencies"].values())
    assert client.get("/").status_code == 200
    corpus = client.get("/api/documents").json()
    assert corpus["passages"] >= 6
    assert corpus["documents"][0]["status"] == "reviewed"


@pytest.mark.parametrize("question,language,expected", [
    ("Comment sont élus les membres de la Chambre des représentants ?", "fr", "constitution:62"),
    ("كيف يتم انتخاب أعضاء مجلس النواب؟", "ar", "constitution:62"),
    ("Kifach kaytntakhbo nowab?", "darija", "constitution:62"),
    ("Comment sont élus les conseils des communes ?", "fr", "constitution:135"),
    ("Le Parlement comprend combien de Chambres ?", "fr", "constitution:60"),
])
def test_real_cross_service_retrieval(stack, question, language, expected):
    client, _, analytics = stack
    response = client.post("/api/ask", json={"question": question, "language": language})
    assert response.status_code == 200
    data = response.json()
    assert data["answerable"]
    assert expected in [s["id"] for s in data["sources"]]
    assert all(s["source_url"].startswith("https://maroc.ma/") for s in data["sources"])
    assert analytics.summary()["questions"] == 1


def test_unknown_question_does_not_fabricate(stack):
    client, _, _ = stack
    data = client.post("/api/ask", json={"question": "Quel est le prix du carburant demain ?", "language": "fr"}).json()
    assert data["sources"] == []
    assert not data["answerable"]


def test_citations_are_verbatim_indexed_text(stack):
    client, _, _ = stack
    data = client.post("/api/ask", json={"question": "Quels sont les conseils des communes ?"}).json()
    originals = {p["id"]: p["text"] for p in json.loads((ROOT / "commun/data/seed/foundation.json").read_text(encoding="utf-8"))}
    for source in data["sources"]:
        assert source["text"] == originals[source["id"]]


@pytest.mark.parametrize("payload", [
    {"question": "  "},
    {"question": "x" * 1501},
    {"question": "bonjour", "language": "en"},
    {"question": "bonjour", "email": "should-not-be-accepted@example.org"},
])
def test_input_contract_is_strict(stack, payload):
    assert stack[0].post("/api/ask", json=payload).status_code == 422


def test_quiz_scored_on_server_and_cited(stack):
    client, _, analytics = stack
    quiz = client.get("/api/quiz").json()
    assert len(quiz["questions"]) == 4
    assert all("answer" not in q for q in quiz["questions"])
    result = client.post("/api/quiz/submit", json={"answers": {"vote":0, "chambers":1, "mandate":2, "territories":0}, "language":"fr"}).json()
    assert result["score"] == 100
    assert all(c["source"] and c["source_url"] for c in result["corrections"])
    assert analytics.summary()["quizzes_completed"] == 1


def test_quiz_rejects_incomplete_or_invented_answers(stack):
    client = stack[0]
    assert client.post("/api/quiz/submit", json={"answers":{}}).status_code == 422
    assert client.post("/api/quiz/submit", json={"answers":{"vote":5}}).status_code == 422


def test_admin_requires_secret(stack):
    client = stack[0]
    assert client.get("/api/admin/summary").status_code == 401
    assert client.get("/api/admin/summary", headers={"X-Admin-Key":"wrong"}).status_code == 401
    assert client.get("/api/admin/summary", headers={"X-Admin-Key":"test-admin-key"}).status_code == 200


def test_ingestion_review_gate_and_idempotency(stack):
    client, store, _ = stack
    original = json.loads((ROOT / "commun/data/seed/foundation.json").read_text(encoding="utf-8"))[0]
    import hashlib
    passage = {**original, "sha256":hashlib.sha256(original["text"].encode()).hexdigest()}
    assert client.post("/v1/ingest", json={"passages":[passage]}).status_code == 401
    headers = {"X-Service-Key":"test-service-key"}
    assert client.post("/v1/ingest", headers=headers, json={"passages":[{**passage,"status":"pending_review"}]}).status_code == 422
    before = store.documents()[0]["passages"]
    for _ in range(2):
        assert client.post("/v1/ingest", headers=headers, json={"passages":[passage]}).status_code == 200
    assert store.documents()[0]["passages"] == before


def test_no_question_text_or_identity_stored_in_analytics(stack):
    client, store, analytics = stack
    question = "Quels sont les droits de vote de Fatima ?"
    client.post("/api/ask", json={"question":question})
    with analytics.connection() as conn:
        rows = [dict(r) for r in conn.execute("SELECT * FROM events").fetchall()]
    assert question not in json.dumps(rows)
    assert all(set(r) == {"id","day","event","language","latency_ms","score"} for r in rows)
    assert store.pending_events() == []


def test_nlp_failure_is_explicit_and_does_not_return_invented_sources(stack, monkeypatch):
    from nlp_service import main as nlp
    def fail(*_args, **_kwargs):
        from fastapi import HTTPException
        raise HTTPException(503, "NLP indisponible")
    monkeypatch.setattr(nlp, "embed", fail)
    response = stack[0].post("/api/ask", json={"question":"Quel est le rôle du Parlement ?"})
    assert response.status_code == 503


ADMIN = {"X-Admin-Key": "test-admin-key"}


def test_retire_passage_removes_it_from_search_and_audits(stack):
    client, _, _ = stack
    question = {"question": "Comment sont élus les conseils des communes ?", "language": "fr"}
    assert "constitution:135" in [s["id"] for s in client.post("/api/ask", json=question).json()["sources"]]
    before = client.get("/api/documents").json()["passages"]

    response = client.post("/api/admin/passages/constitution:135/retire", headers=ADMIN,
                           json={"reason": "Remplacé par un lot relu et corrigé"})
    assert response.status_code == 200
    body = response.json()
    assert body["retired"] == "constitution:135" and body["remaining_passages"] == before - 1

    assert "constitution:135" not in [s["id"] for s in client.post("/api/ask", json=question).json()["sources"]]
    assert client.get("/api/documents").json()["passages"] == before - 1
    audit = client.get("/api/admin/passages/retired", headers=ADMIN).json()
    assert audit["total"] == 1 and audit["retired"][0]["reason"] == "Remplacé par un lot relu et corrigé"
    # Retiring twice is reported, never silently accepted.
    again = client.post("/api/admin/passages/constitution:135/retire", headers=ADMIN, json={"reason": "Deuxième essai"})
    assert again.status_code == 404


def test_retire_passage_requires_admin_key_and_reason(stack):
    client, _, _ = stack
    url = "/api/admin/passages/constitution:62/retire"
    assert client.post(url, json={"reason": "Sans clé admin"}).status_code == 401
    assert client.post(url, headers={"X-Admin-Key": "wrong"}, json={"reason": "Mauvaise clé"}).status_code == 401
    assert client.post(url, headers={"X-Service-Key": "test-service-key"}, json={"reason": "Clé de service"}).status_code == 401
    assert client.post(url, headers=ADMIN, json={}).status_code == 422
    assert client.post(url, headers=ADMIN, json={"reason": "abc"}).status_code == 422
    assert client.get("/api/admin/passages/retired").status_code == 401
    assert client.get("/api/documents").json()["passages"] >= 6


def test_retire_never_empties_the_corpus(stack):
    client, _, _ = stack
    ids = [p["id"] for p in json.loads((ROOT / "commun/data/seed/foundation.json").read_text(encoding="utf-8"))]
    for pid in ids[:-1]:
        assert client.post(f"/api/admin/passages/{pid}/retire", headers=ADMIN, json={"reason": "Test de retrait"}).status_code == 200
    last = client.post(f"/api/admin/passages/{ids[-1]}/retire", headers=ADMIN, json={"reason": "Test de retrait"})
    assert last.status_code == 409
    assert client.get("/api/documents").json()["passages"] == 1


def test_retired_passage_cannot_be_reingested(stack):
    client, store, _ = stack
    seed = {p["id"]: p for p in json.loads((ROOT / "commun/data/seed/foundation.json").read_text(encoding="utf-8"))}
    original = {**seed["constitution:30"], "sha256": "0" * 64}
    fresh = {**seed["constitution:62"], "id": "nouveau-passage-relu", "sha256": "1" * 64}
    assert client.post("/api/admin/passages/constitution:30/retire", headers=ADMIN, json={"reason": "Remplacé par un lot corrigé"}).status_code == 200
    before = client.get("/api/documents").json()["passages"]
    # Replaying an old lot with the retired passage is refused as a whole, nothing is indexed.
    response = client.post("/v1/ingest", headers={"X-Service-Key": "test-service-key"}, json={"passages": [fresh, original]})
    assert response.status_code == 409
    assert response.json()["detail"]["retired_ids"] == ["constitution:30"]
    assert client.get("/api/documents").json()["passages"] == before
    # Without the retired passage the same lot goes through.
    assert client.post("/v1/ingest", headers={"X-Service-Key": "test-service-key"}, json={"passages": [fresh]}).status_code == 200
    assert client.get("/api/documents").json()["passages"] == before + 1
