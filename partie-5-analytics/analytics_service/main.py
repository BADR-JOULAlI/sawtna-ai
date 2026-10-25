from contextlib import asynccontextmanager
import os
from pathlib import Path
import httpx
from fastapi import Depends, FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sawtna.config import ROOT
from sawtna.contracts import AnalyticsEvent
from sawtna.security import require_service, require_admin
from sawtna.store import Store


def create_app(store=None):
    store = store or Store("analytics")

    @asynccontextmanager
    async def lifespan(app):
        store.init()
        yield

    app = FastAPI(title="Sawtna Analytics", version="1.0.0", lifespan=lifespan)

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "analytics"}

    @app.post("/v1/events", status_code=202, dependencies=[Depends(require_service)])
    def event(body: AnalyticsEvent):
        store.record_event(body)
        return {"status": "accepted"}

    @app.get("/v1/summary", dependencies=[Depends(require_service)])
    def summary():
        return store.summary()

    async def backend_get(path):
        async with httpx.AsyncClient(base_url=os.getenv("SAWTNA_BACKEND_URL", "http://127.0.0.1:8010"), timeout=5) as client:
            try:
                response = await client.get(path)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as exc:
                raise HTTPException(503, "Backend indisponible.") from exc

    @app.get("/api/documents")
    async def documents():
        return await backend_get("/api/documents")

    @app.get("/api/admin/summary", dependencies=[Depends(require_admin)])
    async def dashboard_summary():
        return {**store.summary(), "corpus": await backend_get("/api/documents"), "services": await backend_get("/health")}

    dist = Path(os.getenv("SAWTNA_WEB_DIST", str(ROOT / "partie-4-frontend/dist")))
    if (dist / "assets").exists():
        app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

    @app.get("/", include_in_schema=False)
    async def root():
        return RedirectResponse("/dashboard#dashboard")

    @app.get("/dashboard", include_in_schema=False)
    async def dashboard():
        if not (dist / "index.html").exists():
            raise HTTPException(503, "Compilez le frontend avec npm run build.")
        return FileResponse(dist / "index.html")

    return app


app = create_app()
