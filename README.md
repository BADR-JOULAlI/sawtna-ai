# Sawtna AI — Data Engineering

Ce dépôt contient la partie de l’étudiant 1 et l’architecture commune. Les implémentations backend, NLP, frontend et Analytics appartiennent aux autres étudiants et ne sont pas incluses.

## Architecture

Documents officiels → AWS EC2 ETL → Azure VM API/PostgreSQL/pgvector → Azure Static Web Apps.
L’API utilise Google Cloud Run pour les embeddings et envoie des compteurs anonymes vers Analytics sur Google Compute Engine.
Voir commun/docs/architecture.md et commun/docs/work-packages.md. Les contrats de collaboration sont dans commun/packages/contracts/.

## Parties du projet

```text
sawtna-ai/
├── partie-1-data-engineering/  # Code ETL + README
├── partie-2-backend/           # README de Soulayman
├── partie-3-nlp/               # README de Badr
├── partie-4-frontend/          # README d’Aya
├── partie-5-analytics/         # README d’Ijlal
├── commun/                    # Contrats, docs, données, scripts et tests communs
├── .github/                   # CI
└── README.md
```

Le monorepo local complet possède la même répartition, avec le code des cinq services dans leurs parties respectives.

- `partie-1-data-engineering/` — Ayoub Chenguir, AWS EC2
- `partie-2-backend/` — Soulayman Jdidi, Azure VM
- `partie-3-nlp/` — Badr Joulali, Google Cloud Run
- `partie-4-frontend/` — Aya Sdour, Azure Static Web Apps
- `partie-5-analytics/` — Ijlal Sellak, Google Compute Engine

La partie 1 contient son code et son README. Les parties 2 à 5 contiennent leur README de répartition; leur code complet est disponible dans le monorepo local. Les ressources communes sont dans `commun/`. Chaque fiche détaille : périmètre, tâches, livrables, critères de validation et dépendances. Le code des services est développé par leurs responsables et intégré selon les contrats communs.

## Installation et collecte locale

~~~powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
python commun/scripts/download_ocr.py --language fra
python -m sawtna.data_engineering collect --ocr
python -m pytest
~~~

Sources : Constitution 2011 (SGG et Maroc.ma), page constitutionnelle Maroc.ma, Bulletin officiel contenant la loi organique 06-21.
Le catalogue est modifiable dans partie-1-data-engineering/sources.json.
La collecte contrôle domaines HTTPS, redirections, taille et format. Chaque original est conservé par SHA-256, avec manifest daté et passages JSONL citables.
Les pages numérisées sont signalées et peuvent être traitées par OCR local.

## Revue et livraison au backend

Les passages collectés sont pending_review. Relire les textes, les articles, la date et les modifications avant approbation.
Ne pas approuver un Bulletin officiel complet sans isoler les textes et pages utiles.

~~~powershell
python -m sawtna.data_engineering approve --document constitution-2011-sgg-fr
$env:SAWTNA_API_URL = "https://adresse-du-backend"
$env:SAWTNA_SERVICE_KEY = "secret-fourni-par-le-responsable-backend"
python commun/scripts/ingest.py --input commun/data/processed/reviewed.jsonl
~~~

Le backend est une dépendance externe définie par contrat. La CI teste ce module, sans connexion cloud et sans clé.
Les originaux, fichiers extraits, modèles, bases et secrets sont exclus de Git.
Le guide AWS est dans commun/docs/deployment/aws-ec2.md. Aucun déploiement cloud automatique.
