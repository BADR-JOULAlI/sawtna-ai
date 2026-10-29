import hashlib
import json

import pytest

from data_engineering.pipeline import collect
from data_engineering.review import audit_corpus
from data_engineering.triage import classify


@pytest.fixture
def expansion(tmp_path):
    old = {"id": "existing", "url": "https://maroc.ma/existing", "title": "Texte existant",
           "language": "fr", "format": "html"}
    new = {"id": "new-ar", "url": "https://maroc.ma/new", "title": "نص جديد",
           "language": "ar", "format": "html", "legal_family": "test-family", "document_role": "amendment"}
    raw = tmp_path / "raw/existing/source.html"
    raw.parent.mkdir(parents=True)
    raw.write_bytes(b"<html><p>Les elections et les candidatures doivent faire l'objet d'une relecture.</p></html>")
    manifest = tmp_path / "old-manifest.json"
    manifest.write_text(json.dumps([{**old, "sha256": hashlib.sha256(raw.read_bytes()).hexdigest(),
                                    "path": "raw/existing/source.html", "final_url": old["url"],
                                    "collected_at": "2026-10-21T10:00:00Z"}]), encoding="utf-8")
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps([old, new]), encoding="utf-8")
    return tmp_path, catalog, manifest, raw


def test_extend_catalog_fetches_only_new_sources_and_preserves_origin(expansion, monkeypatch):
    root, catalog, manifest, _ = expansion
    calls = []
    def fetch_new(source, client):
        calls.append(source["id"])
        return ('<html><meta charset="utf-8"><p>التسجيل في اللوائح الانتخابية والترشيح والتصويت مواضيع تحتاج إلى مراجعة النص الأصلي.</p></html>'.encode(),
                "html", source["url"])
    monkeypatch.setattr("data_engineering.pipeline.fetch", fetch_new)
    records = collect(catalog, root=root, reuse_manifest=manifest, download_missing=True)
    assert calls == ["new-ar"]
    assert [r["download_status"] for r in records] == ["reused", "downloaded"]
    assert records[0]["collected_at"] == "2026-10-21T10:00:00Z"
    assert records[1]["collected_at"] == records[1]["processed_at"]
    assert records[1]["legal_family"] == "test-family"
    assert manifest.read_bytes() != (root / "manifests/latest.json").read_bytes()
    report = audit_corpus(root / "processed/pending.jsonl", root / "manifests/latest.json", root, root / "review")
    assert report["summary"]["errors"] == 0
    assert report["summary"]["languages"] == {"fr": 1, "ar": 1}
    assert report["legal_families"]["test-family"][0]["role"] == "amendment"
    decisions = [json.loads(line) for line in (root / "review/decisions.jsonl").read_text(encoding="utf-8").splitlines()]
    triage = [json.loads(line) for line in (root / "review/triage.jsonl").read_text(encoding="utf-8").splitlines()]
    assert {r["id"] for r in decisions} == {r["id"] for r in triage}
    assert all(r["decision"] == "pending" for r in decisions)
    assert all("decision" not in r for r in triage)
    assert {r["category"] for r in triage} == {"electoral_terms"}
    assert (root / "review/priorites.md").is_file()


def test_offline_mode_still_refuses_missing_source(expansion, monkeypatch):
    root, catalog, manifest, _ = expansion
    monkeypatch.setattr("data_engineering.pipeline.fetch", lambda *_: pytest.fail("Offline mode downloaded"))
    records = collect(catalog, root=root, reuse_manifest=manifest)
    assert records[0]["download_status"] == "reused"
    assert records[1]["download_status"] == "failed"
    assert "hors ligne" in records[1]["error"]


@pytest.mark.parametrize("damage", ["hash", "url"])
def test_expansion_never_silently_replaces_broken_cached_document(expansion, monkeypatch, damage):
    root, catalog, manifest, raw = expansion
    entries = json.loads(catalog.read_text(encoding="utf-8"))[:1]
    if damage == "hash":
        raw.write_bytes(b"tampered")
    else:
        entries[0]["url"] = "https://maroc.ma/changed"
    catalog.write_text(json.dumps(entries), encoding="utf-8")
    monkeypatch.setattr("data_engineering.pipeline.fetch", lambda *_: pytest.fail("Unexpected replacement"))
    records = collect(catalog, root=root, reuse_manifest=manifest, download_missing=True)
    assert records[0]["download_status"] == "failed"
    assert (root / "processed/pending.jsonl").read_text() == ""


def test_download_missing_requires_manifest(expansion):
    root, catalog, _, _ = expansion
    with pytest.raises(ValueError, match="reuse-manifest"):
        collect(catalog, root=root, download_missing=True)


@pytest.mark.parametrize(("text", "category", "rule"), [
    ("Conditions d’ÉLIGIBILITÉ et inscription sur les listes électorales.", "electoral_terms", "listes_electorales"),
    ("التَّسْجِيلُ في اللَّوائِحِ الانْتِخابِيَّةِ والتَّصْوِيتُ", "electoral_terms", "listes_electorales"),
    ("والانـتخابات والترشيح للتصويت", "electoral_terms", "elections_vote"),
    ("Les compétences de la Cour constitutionnelle.", "institutional_context", "institutions"),
    ("اختصاصات مجلس النواب والمحكمة الدستورية", "institutional_context", "institutions"),
    ("Arrêté concernant un établissement et son budget.", "unclassified", None),
])
def test_bilingual_triage_explains_matches(text, category, rule):
    result = classify(text)
    assert result["category"] == category
    assert (rule in result["evidence"]) if rule else not result["evidence"]


def test_triage_keeps_unclassified_and_duplicates_without_altering_passages():
    from data_engineering.triage import build_triage
    from sawtna.contracts import Passage
    passages = [Passage(id="one", document_id="doc", title="Document", source_url="https://maroc.ma/doc",
                        text="Un passage sans mot-clé qui ne doit pas disparaître de la revue.", sha256="a" * 64),
                Passage(id="two", document_id="doc", title="Document", source_url="https://maroc.ma/doc",
                        text="Les élections et les électeurs sont mentionnés dans cette fixture de test.", sha256="a" * 64)]
    before = [p.model_dump() for p in passages]
    result = build_triage(passages, [{"id": "doc"}], {"one": ["duplicate_text"]})
    assert [p.model_dump() for p in passages] == before
    assert result["passages"][0]["id"] == "one"
    assert len(result["passages"]) == 2
    assert result["summary"] == {"unclassified": 1, "electoral_terms": 1}
