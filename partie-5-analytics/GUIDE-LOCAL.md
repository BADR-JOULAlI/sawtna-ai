# Étudiant 5 — Analytics · Google Compute Engine

Code : analytics_service/main.py. Le dashboard réutilise le build React et est servi sur /dashboard.

~~~powershell
npm --prefix partie-4-frontend run build
python -m uvicorn sawtna.analytics:app --host 127.0.0.1 --port 8012 --no-access-log
python -m pytest commun/tests/test_nlp_analytics.py
~~~

POST /v1/events est idempotent sur event_id, authentifié par X-Service-Key.
GET /v1/summary agrège questions, taux de réponses sourcées, quiz, scores, latences et langues par jour UTC.
Le dashboard exige X-Admin-Key. SAWTNA_BACKEND_URL permet de consulter le corpus et l’état des dépendances.
Aucun texte de question ni identifiant de personne n’est accepté.
Choisir une politique de rétention/purge avant exploitation publique.
