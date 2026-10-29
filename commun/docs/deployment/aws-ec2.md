# EC2 — ETL

Sur une VM Linux déjà autorisée et disposant de Docker, cloner le monorepo et lancer depuis sa racine :

~~~bash
docker compose --profile etl build etl
docker compose --profile etl run --rm --no-deps --entrypoint python etl commun/scripts/download_ocr.py --language fra
docker compose --profile etl run --rm --no-deps --entrypoint python etl commun/scripts/download_ocr.py --language ara --variant best
docker compose --profile etl run --rm --no-deps etl collect --ocr
docker compose --profile etl run --rm --no-deps etl audit
~~~

La tâche collecte et extrait ; elle n’approuve pas les textes. Utiliser un volume persistant pour les versions.
L’image ETL inclut `tesserocr`; les modèles sont conservés dans le volume de données. L’OCR arabe utilise 300 DPI et garde des scores de confiance pour la relecture. Les commandes ont été vérifiées en Docker local; aucune VM EC2 n’a encore été déployée.
Après relecture, fournir SAWTNA_API_URL et SAWTNA_SERVICE_KEY au script d’ingestion. Le secret appartient à l’environnement de la VM.
Planifier via un timer systemd quand la fréquence et les coûts sont définis ; pas de service Web entrant nécessaire.
Arrêter les ressources inutilisées en tenant compte du stockage et des IP encore alloués.
