import asyncio
import hashlib
import json
import os
import time
import uuid
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from typing import Literal
import httpx
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import Field
from sawtna.config import ROOT, service_key
from sawtna.contracts import AskRequest, EmbedResponse, Passage, StrictModel
from .quiz import grade, public_quiz, QUESTIONS
from sawtna.security import require_admin, require_service
from sawtna.store import Store


class QuizSubmission(StrictModel):
    language: Literal["fr", "ar", "darija"] = "fr"
    answers: dict[str, int] = Field(max_length=10)


class IngestRequest(StrictModel):
    passages: list[Passage] = Field(min_length=1, max_length=64)


def create_app(store=None, nlp_transport=None, analytics_transport=None):
    store = store or Store("backend")
    nlp_url = os.getenv("SAWTNA_NLP_URL", "http://127.0.0.1:8011")
    analytics_url = os.getenv("SAWTNA_ANALYTICS_URL", "http://127.0.0.1:8012")
    headers = {"X-Service-Key": service_key()}
    clients = {}

    async def encode(texts, kind):
        try:
            response = await clients["nlp"].post("/v1/embeddings", json={"texts": texts, "kind": kind})
            response.raise_for_status()
            result = EmbedResponse.model_validate(response.json())
            if len(result.vectors) != len(texts) or result.dimensions != 384:
                raise ValueError("Réponse embeddings incompatible")
            return result
        except (httpx.HTTPError, ValueError) as exc:
            raise HTTPException(503, "Le service NLP est indisponible. Réessayez dans un instant.") from exc

    async def flush_events():
        for event in store.pending_events():
            try:
                response = await clients["analytics"].post("/v1/events", json=event)
                response.raise_for_status()
                store.mark_delivered(event["event_id"])
            except httpx.HTTPError:
                break

    async def retry_events():
        while True:
            await asyncio.sleep(3)
            await flush_events()

    @asynccontextmanager
    async def lifespan(app):
        store.init()
        clients["nlp"] = httpx.AsyncClient(base_url=nlp_url, headers=headers, transport=nlp_transport, timeout=60)
        clients["analytics"] = httpx.AsyncClient(base_url=analytics_url, headers=headers, transport=analytics_transport, timeout=5)
        # Seed only if no document is indexed. Importing collected documents is a separate authenticated operation.
        seed = ROOT / "commun/data/seed/foundation.json"
        if not store.documents() and seed.exists():
            records = json.loads(seed.read_text(encoding="utf-8"))
            passages = [Passage(**item, sha256=hashlib.sha256(item["text"].encode()).hexdigest()) for item in records]
            embedded = await encode([p.text for p in passages], "passage")
            store.upsert(passages, embedded.vectors, embedded.model)
        if not store.documents():
            raise RuntimeError("Corpus vide : vérifier SAWTNA_PROJECT_ROOT et ingérer des passages relus.")
        task = asyncio.create_task(retry_events())
        try:
            yield
        finally:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            await clients["nlp"].aclose()
            await clients["analytics"].aclose()

    app = FastAPI(title="Sawtna Assistant API", version="1.0.0", lifespan=lifespan)
    app.add_middleware(CORSMiddleware,
        allow_origins=os.getenv("SAWTNA_ALLOWED_ORIGINS", "http://localhost:5175,http://127.0.0.1:5175").split(","),
        allow_methods=["GET", "POST"], allow_headers=["Content-Type", "X-Admin-Key", "X-Service-Key"])
    app.state.store = store
    requests_by_ip = defaultdict(deque)

    @app.middleware("http")
    async def limit_requests(request, call_next):
        if request.method == "POST" and request.url.path in ("/api/ask", "/api/quiz/submit"):
            from starlette.responses import JSONResponse
            identity = request.client.host if request.client else "local"
            window = requests_by_ip[identity]
            now = time.monotonic()
            while window and now - window[0] >= 60:
                window.popleft()
            if len(window) >= int(os.getenv("SAWTNA_RATE_LIMIT", "40")):
                return JSONResponse({"detail": "Trop de requêtes. Réessayez dans une minute."}, status_code=429)
            window.append(now)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    @app.get("/", include_in_schema=False)
    async def root():
        return RedirectResponse("/docs")

    @app.get("/health")
    async def health():
        dependencies = {}
        for name, client in clients.items():
            try:
                response = await client.get("/health", timeout=4)
                dependencies[name] = response.status_code == 200
            except httpx.HTTPError:
                dependencies[name] = False
        return {"status": "ok" if all(dependencies.values()) else "degraded", "service": "backend", "database": "postgresql+pgvector" if store.pg else "sqlite", "dependencies": dependencies}

    @app.get("/api/documents")
    def documents():
        docs = store.documents()
        return {"documents": docs, "total": len(docs), "passages": sum(d["passages"] for d in docs)}

    @app.post("/api/ask")
    async def ask(body: AskRequest):
        started = time.monotonic()
        embedding = await encode([body.question], "query")
        matches = store.search(body.question, embedding.vectors[0], embedding.model)
        sources = [{**m["passage"], "relevance": m["relevance"]} for m in matches]
        prefixes = {
            "fr": "Voici les passages du corpus qui répondent à votre question. Les citations conservent la langue du document d'origine.",
            "ar": "هذه المقاطع مرتبطة بسؤالك. نحافظ على لغة المصدر الأصلي في الاقتباسات.",
            "darija": "Hado homa lma9ati3 li l9ina 3la sou2alek. L'i9tibas kayb9a b loghat lmasdar l'asli.",
        }
        empty = {
            "fr": "Je n'ai pas trouvé de source suffisante dans le corpus pour répondre à cette question.",
            "ar": "لم أجد مصدرا كافيا في الوثائق للإجابة عن هذا السؤال.",
            "darija": "Ma l9itch masdar kaykfi f lwata2i9 bach njawb 3la had sou2al.",
        }
        latency = round((time.monotonic() - started) * 1000)
        event = {"event_id": str(uuid.uuid4()), "event": "question_answered" if sources else "question_unanswered", "language": body.language, "latency_ms": latency, "score": 0}
        store.queue_event(event)
        await flush_events()
        return {"request_id": event["event_id"], "answer": prefixes[body.language] if sources else empty[body.language],
            "language": body.language, "sources": sources, "answerable": bool(sources), "latency_ms": latency,
            "mode": "extractive", "embedding_model": embedding.model, "notice": "Corpus de référence : Constitution 2011. Les échéances et les modifications législatives nécessitent des sources à jour."}

    @app.get("/api/quiz")
    def quiz(language: Literal["fr", "ar", "darija"] = "fr"):
        return public_quiz(language)

    @app.post("/api/quiz/submit")
    async def submit(body: QuizSubmission):
        valid_ids = {q["id"] for q in QUESTIONS}
        if set(body.answers) != valid_ids or any(type(v) is not int or v not in (0, 1, 2) for v in body.answers.values()):
            raise HTTPException(422, "Une réponse de 0 à 2 est requise pour chaque question.")
        result = grade(body.answers, body.language)
        store.queue_event({"event_id": str(uuid.uuid4()), "event": "quiz_completed", "language": body.language, "latency_ms": 0, "score": result["score"]})
        await flush_events()
        return result

    @app.post("/v1/ingest", dependencies=[Depends(require_service)])
    async def ingest(body: IngestRequest):
        if any(p.status != "reviewed" for p in body.passages):
            raise HTTPException(422, "L'indexation exige des passages relus (reviewed).")
        embedded = await encode([p.text for p in body.passages], "passage")
        store.upsert(body.passages, embedded.vectors, embedded.model)
        return {"indexed": len(body.passages), "model": embedded.model}

    @app.get("/api/admin/summary", dependencies=[Depends(require_admin)])
    async def summary():
        await flush_events()
        try:
            response = await clients["analytics"].get("/v1/summary")
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(503, "Le service Analytics est indisponible.") from exc
        return {**response.json(), "corpus": documents(), "services": (await health())}

    return app


app = create_app()
