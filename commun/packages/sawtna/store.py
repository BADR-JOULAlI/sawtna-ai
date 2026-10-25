"""SQLite local fallback and actual PostgreSQL/pgvector persistence."""
import json
import math
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
from pathlib import Path
import numpy as np
from .config import data_root
from .contracts import Passage
from .nlp import tokens


class Store:
    def __init__(self, name="backend", url=None):
        self.url = url or os.getenv(f"SAWTNA_{name.upper()}_DATABASE_URL") or str(data_root() / "runtime" / f"{name}.sqlite")
        self.pg = self.url.startswith(("postgresql://", "postgres://"))
        if not self.pg:
            Path(self.url).parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connection(self):
        if self.pg:
            import psycopg
            from psycopg.rows import dict_row
            conn = psycopg.connect(self.url, row_factory=dict_row)
        else:
            conn = sqlite3.connect(self.url, timeout=30)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def execute(self, conn, query, args=()):
        return conn.execute(query.replace("?", "%s") if self.pg else query, args)

    def init(self):
        with self.connection() as conn:
            if self.pg:
                conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            conn.execute("CREATE TABLE IF NOT EXISTS passages (id TEXT PRIMARY KEY, document_id TEXT NOT NULL, payload TEXT NOT NULL, embedding TEXT NOT NULL, model TEXT NOT NULL)")
            if self.pg:
                conn.execute("ALTER TABLE passages ADD COLUMN IF NOT EXISTS feature vector(384)")
            conn.execute("CREATE TABLE IF NOT EXISTS outbox (id TEXT PRIMARY KEY, payload TEXT NOT NULL, delivered INTEGER NOT NULL DEFAULT 0)")
            conn.execute("CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, day TEXT NOT NULL, event TEXT NOT NULL, language TEXT NOT NULL, latency_ms INTEGER NOT NULL, score INTEGER NOT NULL)")

    def upsert(self, passages: list[Passage], vectors: list[list[float]], model: str):
        if len(passages) != len(vectors) or any(len(v) != 384 or not all(math.isfinite(x) for x in v) for v in vectors):
            raise ValueError("Dimensions des embeddings incompatibles.")
        with self.connection() as conn:
            for passage, vector in zip(passages, vectors):
                self.execute(conn, "INSERT INTO passages (id,document_id,payload,embedding,model) VALUES (?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET document_id=excluded.document_id,payload=excluded.payload,embedding=excluded.embedding,model=excluded.model",
                    (passage.id, passage.document_id, passage.model_dump_json(), json.dumps(vector), model))
                if self.pg:
                    self.execute(conn, "UPDATE passages SET feature=?::vector WHERE id=?", (json.dumps(vector), passage.id))

    def documents(self):
        with self.connection() as conn:
            rows = self.execute(conn, "SELECT payload FROM passages ORDER BY document_id,id").fetchall()
        documents = {}
        for row in rows:
            item = json.loads(row["payload"])
            doc = documents.setdefault(item["document_id"], {k: item[k] for k in ("document_id", "title", "source_url", "language", "status")})
            doc["passages"] = doc.get("passages", 0) + 1
        return list(documents.values())

    def search(self, question, vector, model, limit=4):
        with self.connection() as conn:
            if self.pg:
                rows = self.execute(conn, "SELECT payload, embedding FROM passages WHERE model=? ORDER BY feature <=> ?::vector LIMIT 200", (model, json.dumps(vector))).fetchall()
            else:
                rows = self.execute(conn, "SELECT payload,embedding FROM passages WHERE model=?", (model,)).fetchall()
        query_tokens = set(tokens(question))
        if not rows or not query_tokens:
            return []
        corpus = [json.loads(row["payload"]) for row in rows]
        all_tokens = [tokens(p["text"] + " " + p["section"]) for p in corpus]
        n = len(corpus)
        frequency = {t: sum(t in words for words in all_tokens) for t in query_tokens}
        ranked = []
        for row, passage, words in zip(rows, corpus, all_tokens):
            common = query_tokens & set(words)
            if not common:
                continue
            idf = sum(math.log(1 + (n + .5) / (frequency[t] + .5)) for t in common)
            lexical = idf / max(sum(math.log(1 + (n + .5) / (frequency[t] + .5)) for t in query_tokens), 1e-8)
            embedding = np.asarray(json.loads(row["embedding"]))
            semantic = max(0., float(np.dot(embedding, vector) / max(np.linalg.norm(embedding) * np.linalg.norm(vector), 1e-9)))
            score = .6 * lexical + .4 * semantic
            # A single generic electoral term cannot support an unrelated question.
            if lexical < .13 or (len(common) == 1 and common <= {"concept0", "concept6"}):
                continue
            if score >= .16:
                ranked.append({"passage": passage, "relevance": round(score, 4)})
        return sorted(ranked, key=lambda item: item["relevance"], reverse=True)[:limit]

    def queue_event(self, payload):
        with self.connection() as conn:
            self.execute(conn, "INSERT INTO outbox (id,payload) VALUES (?,?) ON CONFLICT(id) DO NOTHING", (payload["event_id"], json.dumps(payload)))

    def pending_events(self):
        with self.connection() as conn:
            return [json.loads(r["payload"]) for r in self.execute(conn, "SELECT payload FROM outbox WHERE delivered=0 LIMIT 100").fetchall()]

    def mark_delivered(self, event_id):
        with self.connection() as conn:
            self.execute(conn, "UPDATE outbox SET delivered=1 WHERE id=?", (event_id,))

    def record_event(self, event):
        with self.connection() as conn:
            self.execute(conn, "INSERT INTO events VALUES (?,?,?,?,?,?) ON CONFLICT(id) DO NOTHING",
                (event.event_id, datetime.now(timezone.utc).date().isoformat(), event.event, event.language, event.latency_ms, event.score))

    def summary(self):
        with self.connection() as conn:
            rows = self.execute(conn, "SELECT day,event,language,COUNT(*) AS count,SUM(latency_ms) AS latency,SUM(score) AS score FROM events GROUP BY day,event,language ORDER BY day").fetchall()
        questions = sum(r["count"] for r in rows if r["event"].startswith("question_"))
        answered = sum(r["count"] for r in rows if r["event"] == "question_answered")
        quizzes = sum(r["count"] for r in rows if r["event"] == "quiz_completed")
        latency = sum(r["latency"] for r in rows if r["event"].startswith("question_"))
        days = [(datetime.now(timezone.utc).date() - timedelta(days=i)).isoformat() for i in reversed(range(7))]
        return {
            "questions": questions, "answered": answered, "unanswered": questions - answered,
            "answer_rate": round(100 * answered / questions, 1) if questions else 0,
            "quizzes_completed": quizzes,
            "average_quiz_score": round(sum(r["score"] for r in rows if r["event"] == "quiz_completed") / quizzes, 1) if quizzes else 0,
            "average_latency_ms": round(latency / questions) if questions else 0,
            "languages": [{"language": lang, "count": sum(r["count"] for r in rows if r["language"] == lang and r["event"].startswith("question_"))} for lang in ("fr", "ar", "darija")],
            "daily": [{"day": day, "count": sum(r["count"] for r in rows if r["day"] == day and r["event"].startswith("question_"))} for day in days],
            "privacy": "Aucune question, adresse IP, identité ou préférence politique enregistrée.",
        }
