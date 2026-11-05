import json
from pathlib import Path

import pytest

from data_engineering.runner import run


def test_runner_prepares_mvp_ingestion_file_without_review_folder(tmp_path, monkeypatch):
    catalog = tmp_path / "sources.json"
    catalog.write_text(json.dumps([{"id": "one", "title": "Source test", "url": "https://maroc.ma/one",
                                    "language": "fr", "format": "html"}]), encoding="utf-8")
    def fake_fetch(source, client):
        return "<html><main><p>Les électeurs peuvent consulter les informations officielles avant le scrutin.</p></main></html>".encode(), "html", source["url"]
    monkeypatch.setattr("data_engineering.pipeline.fetch", fake_fetch)
    result = run(catalog, tmp_path / "data", ocr=False)
    assert result["status"] == "ready_for_mvp_ingestion"
    assert result["mode"] == "initial"
    assert result["next_action"] == "ingest_reviewed_jsonl"
    output = Path(result["output"])
    assert output.is_file()
    passage = json.loads(output.read_text(encoding="utf-8"))
    assert passage["status"] == "reviewed"
    assert not (tmp_path / "data/reviews").exists()


def test_runner_incremental_mode_downloads_only_missing_sources(tmp_path, monkeypatch):
    catalog = tmp_path / "sources.json"
    catalog.write_text(json.dumps([{"id": "one", "title": "Source test", "url": "https://maroc.ma/one",
                                    "language": "fr", "format": "html"}]), encoding="utf-8")
    calls = []
    def fake_fetch(source, client):
        calls.append(source["id"])
        return "<html><main><p>Un texte officiel suffisamment long pour préparer le corpus électoral local.</p></main></html>".encode(), "html", source["url"]
    monkeypatch.setattr("data_engineering.pipeline.fetch", fake_fetch)
    first = run(catalog, tmp_path / "data")
    second = run(catalog, tmp_path / "data")
    assert calls == ["one"]
    assert first["mode"] == "initial"
    assert second["mode"] == "incremental"


def test_runner_offline_requires_existing_manifest(tmp_path):
    catalog = tmp_path / "sources.json"
    catalog.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="Manifeste absent"):
        run(catalog, tmp_path / "data", offline=True)
