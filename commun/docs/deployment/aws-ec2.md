# EC2 — ETL

Sur une VM Linux déjà autorisée et disposant de Docker, cloner le monorepo et lancer depuis sa racine :

~~~bash
docker build -f partie-1-data-engineering/Dockerfile -t sawtna-etl .
docker run --rm -v "$PWD/commun/data:/app/commun/data" sawtna-etl
~~~

La tâche collecte et extrait ; elle n’approuve pas les textes. Utiliser un volume persistant pour les versions.
Pour l’OCR, télécharger le modèle fra avant la collecte avec --ocr.
Après relecture, fournir SAWTNA_API_URL et SAWTNA_SERVICE_KEY au script d’ingestion. Le secret appartient à l’environnement de la VM.
Planifier via un timer systemd quand la fréquence et les coûts sont définis ; pas de service Web entrant nécessaire.
Arrêter les ressources inutilisées en tenant compte du stockage et des IP encore alloués.
