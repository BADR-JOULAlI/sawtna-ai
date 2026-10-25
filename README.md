# Sawtna AI — Data Engineering

Ce dépôt contient la partie de l’étudiant 1 et l’architecture commune. Les implémentations backend, NLP, frontend et Analytics appartiennent aux autres étudiants et ne sont pas incluses.

## Architecture

Documents officiels → AWS EC2 ETL → Azure VM API/PostgreSQL/pgvector → Azure Static Web Apps.
L’API utilise Google Cloud Run pour les embeddings et envoie des compteurs anonymes vers Analytics sur Google Compute Engine.
Voir docs/architecture.md et docs/work-packages.md. Les contrats de collaboration sont dans packages/contracts/.

## Dossiers de travail des cinq étudiants

Chaque dossier `workstreams/` contient le README détaillé d’un responsable : périmètre, tâches, livrables, critères de validation et dépendances. Les fiches décrivent la répartition du projet; le code des services est développé par leurs responsables et intégré selon les contrats communs.

## Installation et collecte locale

~~~powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
python scripts/download_ocr.py --language fra
python -m sawtna.data_engineering collect --ocr
python -m pytest
~~~

Sources : Constitution 2011 (SGG et Maroc.ma), page constitutionnelle Maroc.ma, Bulletin officiel contenant la loi organique 06-21.
Le catalogue est modifiable dans services/data-engineering-aws/sources.json.
La collecte contrôle domaines HTTPS, redirections, taille et format. Chaque original est conservé par SHA-256, avec manifest daté et passages JSONL citables.
Les pages numérisées sont signalées et peuvent être traitées par OCR local.

## Revue et livraison au backend

Les passages collectés sont pending_review. Relire les textes, les articles, la date et les modifications avant approbation.
Ne pas approuver un Bulletin officiel complet sans isoler les textes et pages utiles.

~~~powershell
python -m sawtna.data_engineering approve --document constitution-2011-sgg-fr
$env:SAWTNA_API_URL = "https://adresse-du-backend"
$env:SAWTNA_SERVICE_KEY = "secret-fourni-par-le-responsable-backend"
python scripts/ingest.py --input data/processed/reviewed.jsonl
~~~

Le backend est une dépendance externe définie par contrat. La CI teste ce module, sans connexion cloud et sans clé.
Les originaux, fichiers extraits, modèles, bases et secrets sont exclus de Git.
Le guide AWS est dans docs/deployment/aws-ec2.md. Aucun déploiement cloud automatique.
