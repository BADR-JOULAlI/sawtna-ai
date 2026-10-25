import httpx
import pytest
from fastapi.testclient import TestClient
from sawtna.analytics import create_app as create_analytics
from sawtna.backend import create_app
from sawtna.nlp import app as nlp
from sawtna.store import Store


@pytest.fixture
def stack(tmp_path, monkeypatch):
    monkeypatch.setenv("SAWTNA_EMBEDDER", "concept-hash-v1")
    monkeypatch.setenv("SAWTNA_SERVICE_KEY", "test-service-key")
    monkeypatch.setenv("SAWTNA_ADMIN_KEY", "test-admin-key")
    monkeypatch.setenv("SAWTNA_RATE_LIMIT", "100")
    analytics_store = Store("analytics", str(tmp_path / "analytics.sqlite"))
    analytics_app = create_analytics(analytics_store)
    backend_store = Store("backend", str(tmp_path / "backend.sqlite"))
    with TestClient(analytics_app):
        backend_app = create_app(backend_store,
            nlp_transport=httpx.ASGITransport(app=nlp),
            analytics_transport=httpx.ASGITransport(app=analytics_app))
        with TestClient(backend_app) as client:
            yield client, backend_store, analytics_store
