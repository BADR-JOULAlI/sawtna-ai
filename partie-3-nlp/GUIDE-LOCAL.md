# Étudiant 3 — NLP · Cloud Run

Code : nlp_service/main.py.

~~~powershell
python -m uvicorn sawtna.nlp:app --host 127.0.0.1 --port 8011 --no-access-log
python -m pytest commun/tests/test_nlp_analytics.py
~~~

POST /v1/embeddings : jusqu’à 64 textes, 12000 caractères chacun, kind=query ou passage, clé X-Service-Key. Sortie : vecteurs normalisés 384D et modèle.

- SAWTNA_EMBEDDER=concept-hash-v1 : baseline déterministe autonome. Ce n’est pas un modèle appris.
- SAWTNA_EMBEDDER=multilingual-e5-small : véritable encodeur intfloat/multilingual-e5-small. Installation :

~~~powershell
python -m pip install -e ".[ml]"
$env:SAWTNA_EMBEDDER = "multilingual-e5-small"
$env:SAWTNA_MODEL_DEVICE = "cpu"
~~~

Le premier lancement télécharge le modèle. CPU dans Cloud Run ; cuda peut être choisi en local si PyTorch et le pilote sont compatibles.
Ne jamais mélanger des modèles dans le même index de recherche.
Le benchmark Darija complet doit être constitué avec l’équipe ; le petit jeu de régression ne certifie pas la qualité générale.
