# Étudiant 2 — Backend · Azure VM

Code : backend_service/main.py et quiz.py. Persistance : commun/packages/sawtna/store.py.

~~~powershell
python -m uvicorn sawtna.backend:app --host 127.0.0.1 --port 8010 --no-access-log
python -m pytest commun/tests/test_backend.py
~~~

Démarrer NLP et Analytics avant le backend.
Variables : SAWTNA_NLP_URL, SAWTNA_ANALYTICS_URL, SAWTNA_SERVICE_KEY, SAWTNA_ADMIN_KEY, SAWTNA_BACKEND_DATABASE_URL et SAWTNA_ALLOWED_ORIGINS.
Sans URL PostgreSQL, SQLite est utilisé. Avec PostgreSQL, l’extension vector et les vecteurs 384D sont réels.
Changer de modèle exige une réindexation.
Endpoints : /api/ask, /api/documents, /api/quiz, /api/quiz/submit, /api/admin/summary, /v1/ingest et /health.
Les événements Analytics sont conservés dans une file de réessai. Hors développement, exposer derrière HTTPS et changer les clés.
