import uuid
import numpy as np
import pytest
from fastapi.testclient import TestClient
from sawtna.nlp import app, baseline, tokens
from sawtna.analytics import create_app
from sawtna.store import Store


def test_nlp_vectors_normalized_multilingual_and_model_disclosed(monkeypatch):
    monkeypatch.setenv("SAWTNA_SERVICE_KEY","secret")
    monkeypatch.setenv("SAWTNA_EMBEDDER","concept-hash-v1")
    client = TestClient(app)
    assert client.post("/v1/embeddings", json={"texts":["bonjour"]}).status_code == 401
    result = client.post("/v1/embeddings", headers={"X-Service-Key":"secret"}, json={"texts":["élections communales","الانتخابات الجماعية"]}).json()
    assert result["model"] == "concept-hash-v1"
    assert result["dimensions"] == 384
    assert np.linalg.norm(result["vectors"][0]) == pytest.approx(1)
    assert np.dot(*result["vectors"]) > .9
    assert baseline("élections communales") == baseline("élections communales")


def test_common_darija_prefixes_are_recognized():
    assert "concept1" in tokens("ljama3iya")
    assert "concept2" in tokens("tachri3iya")


def test_analytics_idempotency_privacy_and_summary(tmp_path, monkeypatch):
    monkeypatch.setenv("SAWTNA_SERVICE_KEY","secret")
    app = create_app(Store("analytics", str(tmp_path / "events.sqlite")))
    event = {"event_id":str(uuid.uuid4()),"event":"question_answered","language":"ar","latency_ms":42}
    with TestClient(app) as client:
        assert client.get("/v1/summary").status_code == 401
        headers = {"X-Service-Key":"secret"}
        for _ in range(2):
            assert client.post("/v1/events", headers=headers, json=event).status_code == 202
        assert client.post("/v1/events", headers=headers, json={**event,"question":"private"}).status_code == 422
        summary = client.get("/v1/summary", headers=headers).json()
        assert summary["questions"] == 1
        assert summary["answer_rate"] == 100
        assert summary["average_latency_ms"] == 42
        assert len(summary["daily"]) == 7
