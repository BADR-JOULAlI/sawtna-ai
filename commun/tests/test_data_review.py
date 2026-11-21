import hashlib
import json
from pathlib import Path

import httpx
import pytest

from data_engineering.pipeline import collect, fetch, verified_raw
from data_engineering.quality import needs_ocr
from data_engineering.review import audit_corpus, approve_decisions, verify_review_export


@pytest.fixture
def corpus(tmp_path):
    raw = tmp_path / "raw/official/source.html"
    raw.parent.mkdir(parents=True)
    raw.write_bytes(b"<html><body>Official source</body></html>")
    digest = hashlib.sha256(raw.read_bytes()).hexdigest()
    passages = [{"id": "first", "document_id": "official", "title": "Document officiel",
                 "source_url": "https://maroc.ma/source", "language": "fr",
                 "text": "Extrait documentaire suffisamment long pour tester une revue manuelle des sources officielles.",
                 "sha256": digest},
                {"id": "second", "document_id": "official", "title": "Document officiel",
                 "source_url": "https://maroc.ma/source", "language": "fr",
                 "text": "Autre passage indépendant qui doit rester en attente de décision humaine explicite.",
                 "sha256": digest}]
    source = tmp_path / "pending.jsonl"
    source.write_text("".join(json.dumps(p) + "\n" for p in passages), encoding="utf-8")
    record = {"id": "official", "url": "https://maroc.ma/source", "final_url": "https://maroc.ma/source",
              "format": "html", "sha256": digest, "path": "raw/official/source.html",
              "download_status": "downloaded", "passages": 2, "pages": 1, "collected_at": "2026-10-21T12:00:00Z"}
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps([record]), encoding="utf-8")
    return tmp_path, source, manifest, raw


def test_garbled_long_text_needs_ocr():
    assert needs_ocr("5R\\DXPH\x03GX\x030DURF " * 30)
    assert not needs_ocr("Les documents officiels doivent être relus avant leur ingestion dans le corpus documentaire.")


def test_fetch_retries_transient_but_not_404(monkeypatch):
    monkeypatch.setattr("data_engineering.pipeline.time.sleep", lambda _: None)
    requests = []
    def handler(request):
        requests.append(request)
        return httpx.Response(503 if len(requests) == 1 else 200, content=b"<html>Document</html>")
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        assert fetch({"url": "https://maroc.ma/source"}, client)[1] == "html"
    assert len(requests) == 2
    requests.clear()
    def not_found(request):
        requests.append(request)
        return httpx.Response(404)
    with httpx.Client(transport=httpx.MockTransport(not_found)) as client:
        with pytest.raises(httpx.HTTPStatusError):
            fetch({"url": "https://maroc.ma/source"}, client)
    assert len(requests) == 1


def test_retry_limit(monkeypatch):
    monkeypatch.setattr("data_engineering.pipeline.time.sleep", lambda _: None)
    calls = []
    def handler(request):
        calls.append(request)
        raise httpx.ConnectError("offline", request=request)
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(httpx.ConnectError):
            fetch({"url": "https://maroc.ma/source"}, client)
    assert len(calls) == 3


def test_audit_snapshots_and_pending_decisions(corpus):
    root, source, manifest, _ = corpus
    report = audit_corpus(source, manifest, root, root / "review")
    assert report["summary"]["errors"] == 0
    assert report["summary"]["passages"] == 2
    assert (root / "review/pending.snapshot.jsonl").read_bytes() == source.read_bytes()
    decisions = [json.loads(s) for s in (root / "review/decisions.jsonl").read_text().splitlines()]
    assert all(d["decision"] == "pending" for d in decisions)
    with pytest.raises(ValueError, match="préserver"):
        audit_corpus(source, manifest, root, root / "review")


def test_audit_detects_changed_raw(corpus):
    root, source, manifest, raw = corpus
    raw.write_bytes(b"changed content")
    assert audit_corpus(source, manifest, root, root / "review")["summary"]["errors"] > 0


def test_raw_path_cannot_escape_root(corpus):
    root, _, _, _ = corpus
    with pytest.raises(ValueError, match="hors"):
        verified_raw(root, {"path": "../external.pdf", "sha256": "a" * 64})


def test_audit_duplicate_ids_and_text(corpus):
    root, source, manifest, _ = corpus
    first = source.read_text().splitlines()[0]
    source.write_text(first + "\n" + first + "\n")
    report = audit_corpus(source, manifest, root, root / "review")
    assert any("dupliqué" in err for err in report["errors"])
    assert report["summary"]["duplicate_groups"] == 1


def prepare(corpus):
    root, source, manifest, _ = corpus
    audit_corpus(source, manifest, root, root / "review")
    decisions = root / "review/decisions.jsonl"
    rows = [json.loads(s) for s in decisions.read_text(encoding="utf-8").splitlines()]
    rows[0]["decision"] = "approve"
    rows[0]["comment"] = "Fixture relue pour le test uniquement."
    decisions.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    return decisions, rows


def test_export_only_selected_with_trace(corpus):
    root, source, manifest, _ = corpus
    decisions, _ = prepare(corpus)
    out = root / "reviewed.jsonl"
    assert approve_decisions(source, decisions, out, "Test reviewer", manifest, root) == 1
    assert json.loads(out.read_text())["id"] == "first"
    assert json.loads(out.read_text())["status"] == "reviewed"
    assert [p.id for p in verify_review_export(out)] == ["first"]
    journal = json.loads(Path(str(out) + ".review.json").read_text())
    assert journal["reviewer"] == "Test reviewer"
    assert journal["output_sha256"] == hashlib.sha256(out.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="existe déjà"):
        approve_decisions(source, decisions, out, "Test reviewer", manifest, root)


@pytest.mark.parametrize("change", ["stale", "unknown", "duplicate", "edited_text", "pending", "empty_comment"])
def test_export_rejects_invalid_or_empty_decisions(corpus, change):
    root, source, manifest, _ = corpus
    decisions, rows = prepare(corpus)
    if change == "stale": rows[0]["text_sha256"] = "0" * 64
    elif change == "unknown": rows[0]["id"] = "unknown"
    elif change == "duplicate": rows.append(rows[0])
    elif change == "edited_text": rows[0]["text"] = "New content that was never audited."
    elif change == "pending": rows[0]["decision"] = "pending"
    elif change == "empty_comment": rows[0]["comment"] = "  "
    decisions.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    with pytest.raises(ValueError):
        approve_decisions(source, decisions, root / "reviewed.jsonl", "Reviewer", manifest, root)
    assert not (root / "reviewed.jsonl").exists()


def test_export_blocks_tampered_source(corpus):
    root, source, manifest, raw = corpus
    decisions, _ = prepare(corpus)
    raw.write_bytes(b"tampered")
    with pytest.raises(ValueError, match="Audit bloquant"):
        approve_decisions(source, decisions, root / "reviewed.jsonl", "Reviewer", manifest, root)


def test_offline_reextraction_never_downloads(corpus, monkeypatch):
    root, _, manifest, _ = corpus
    catalog = root / "sources.json"
    catalog.write_text(json.dumps([{"id": "official", "url": "https://maroc.ma/source",
                                    "title": "Document officiel", "language": "fr", "format": "html"}]))
    monkeypatch.setattr("data_engineering.pipeline.fetch", lambda *_: pytest.fail("Unexpected network call"))
    records = collect(catalog, root=root, reuse_manifest=manifest)
    assert records[0]["download_status"] == "reused"
    assert records[0]["collected_at"] == "2026-10-21T12:00:00Z"
    assert records[0]["processed_at"] != records[0]["collected_at"]
    assert (root / "manifests/latest.json").exists()


def test_failed_document_never_leaves_partial_passages(corpus, monkeypatch):
    root, _, manifest, _ = corpus
    catalog = root / "sources.json"
    catalog.write_text(json.dumps([{"id": "official", "url": "https://maroc.ma/source",
                                    "title": "Document officiel", "language": "fr", "format": "html"}]))
    def broken_chunks(*_, **__):
        yield "A sufficiently long and valid passage to append before failure."
        raise ValueError("Extraction failed")
    monkeypatch.setattr("data_engineering.pipeline.split_passages", broken_chunks)
    records = collect(catalog, root=root, reuse_manifest=manifest)
    assert records[0]["download_status"] == "failed"
    assert (root / "processed/pending.jsonl").read_text() == ""


def test_ingestion_refuses_legacy_reviewed_file_without_human_journal(tmp_path):
    path = tmp_path / "reviewed.jsonl"
    row = {"id": "one", "document_id": "doc", "title": "Document officiel",
           "source_url": "https://maroc.ma/doc", "language": "fr",
           "text": "Extrait officiel suffisamment long pour respecter le schéma de passage.",
           "sha256": "a" * 64, "status": "reviewed"}
    path.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Journal de revue humaine absent"):
        verify_review_export(path)


def test_ingestion_accepts_only_matching_reviewed_export(tmp_path):
    path = tmp_path / "reviewed.jsonl"
    row = {"id": "one", "document_id": "doc", "title": "Document officiel",
           "source_url": "https://maroc.ma/doc", "language": "fr",
           "text": "Extrait officiel suffisamment long pour respecter le schéma de passage.",
           "sha256": "a" * 64, "status": "reviewed"}
    payload = json.dumps(row, ensure_ascii=False) + "\n"
    path.write_bytes(payload.encode("utf-8"))
    journal = {"reviewer": "Relecteur de test", "reviewed_at": "2026-11-21T10:00:00+00:00",
               "input_sha256": "b" * 64, "manifest_sha256": "c" * 64, "decisions_sha256": "d" * 64,
               "approved_passages": 1,
               "output_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
               "decisions": [{"id": "one", "document_id": "doc", "page": None,
                              "sha256": "a" * 64,
                              "text_sha256": hashlib.sha256(row["text"].encode("utf-8")).hexdigest(),
                              "decision": "approve", "comment": "Source comparée et passage vérifié."}]}
    path.with_name(path.name + ".review.json").write_text(json.dumps(journal), encoding="utf-8")
    assert [p.id for p in verify_review_export(path)] == ["one"]
