# Sawtna AI

Assistant documentaire d’éducation électorale au Maroc. Monorepo pour cinq étudiants : ETL AWS, backend Azure, NLP Cloud Run, frontend Azure et Analytics Compute Engine.

Le projet complet se trouve directement dans ce dossier `s/`, relié au dépôt GitHub `BADR-JOULAlI/sawtna-ai`. Exécuter les commandes ci-dessous depuis cette racine. Les cinq parties et les éléments communs sont versionnés ensemble.

## Organisation des fichiers

```text
s/
├── partie-1-data-engineering/   # Ayoub — AWS EC2
│   ├── data_engineering/       # Collecte, extraction et découpage
│   ├── sources.json
│   └── README.md
├── partie-2-backend/            # Soulayman — Azure VM
│   ├── backend_service/        # API et quiz
│   └── README.md
├── partie-3-nlp/                # Badr — Google Cloud Run
│   ├── nlp_service/            # Embeddings
│   └── README.md
├── partie-4-frontend/           # Aya — Azure Static Web Apps
│   ├── src/                   # Application React
│   ├── public/
│   ├── tests/
│   └── README.md
├── partie-5-analytics/          # Ijlal — Google Compute Engine
│   ├── analytics_service/      # KPI et hébergement du dashboard
│   └── README.md
├── commun/                     # Ressources communes aux cinq parties
│   ├── data/                  # Corpus, modèles et données locales
│   ├── docs/                  # Architecture et guides cloud
│   ├── infra/                 # Docker, nginx et initialisation SQL
│   ├── packages/              # Contrats et bibliothèque partagée
│   ├── scripts/               # Lancement, ingestion et vérification
│   └── tests/                 # Tests Python et intégration
├── .github/                    # CI GitHub Actions
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

Les cinq parties contiennent leur implémentation. `commun/` regroupe ce qui est partagé; les fichiers de configuration restent à la racine pour lancer le projet.

## Docker Desktop

Depuis ce dossier :

~~~powershell
docker compose up --build --detach --wait
~~~

| Application | Adresse |
|---|---|
| Interface citoyen | http://127.0.0.1:5175 |
| Dashboard Analytics | http://127.0.0.1:8012/dashboard |
| API interactive | http://127.0.0.1:8010/docs |
| État des services | http://127.0.0.1:8010/health |

Clé du dashboard pour la démonstration locale : `local-sawtna-admin-only`.
Définir des clés différentes dans .env avant de rendre les services accessibles.
Les ports hôte sont liés à 127.0.0.1. Ouvrir localhost ou 127.0.0.1 dans le navigateur.
Arrêter sans effacer les données : `docker compose stop`.

## Python/Node, avec SQLite

Python 3.11+ et Node 22+ :

~~~powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
npm --prefix partie-4-frontend ci
npm --prefix partie-4-frontend run build
python -m sawtna.launcher
~~~

Le lanceur démarre NLP, Analytics, backend puis Vite. Il refuse un port occupé et arrête ses enfants avec Ctrl+C. Journaux : commun/data/runtime/logs/.
PostgreSQL/pgvector est utilisé par Docker ; SQLite est une alternative locale explicite.

## Fonctionnalités

- Recherche hybride : similarité des vecteurs et recouvrement lexical pondéré.
- Réponses extractives avec liens et articles, sans génération libre.
- Interface FR, arabe RTL et Darija ; citations dans la langue du document.
- Bibliothèque du corpus réellement indexé.
- Quiz corrigé côté serveur avec références.
- Analytics indépendant, déduplication, file de réessai et dashboard protégé.
- Collecte bornée, contrôle des domaines/redirections, SHA-256, versions, extraction PDF/HTML, OCR et revue avant ingestion.

`concept-hash-v1` est une baseline déterministe avec lexique multilingue, pas un modèle appris.
Le véritable encodeur entraîné `intfloat/multilingual-e5-small` est implémenté en option : voir le README NLP.
Le petit corpus initial contient six extraits de la Constitution 2011. Il ne couvre pas tout le droit électoral ni les échéances actuelles.

## Répartition

| Étudiant | Dossier | Cible |
|---|---|---|
| 1 | partie-1-data-engineering/ | AWS EC2 · IaaS |
| 2 | partie-2-backend/ | Azure VM · IaaS |
| 3 | partie-3-nlp/ | Google Cloud Run · PaaS |
| 4 | partie-4-frontend/ | Azure Static Web Apps · PaaS |
| 5 | partie-5-analytics/ | Google Compute Engine · IaaS |

commun/packages/sawtna/ contient contrats, configuration, persistance et points d’entrée.
Les implémentations appartiennent aux dossiers des services.
Le dashboard réutilise React et est aussi servi indépendamment par Analytics.

## Collecter et ingérer

~~~powershell
python -m pip install -e ".[ocr]"
python commun/scripts/download_ocr.py --language fra
python commun/scripts/download_ocr.py --language ara --variant best
python -m sawtna.data_engineering collect --ocr
~~~

Préparer un audit et un dossier de revue avec snapshots et décisions par passage :

~~~powershell
python -m sawtna.data_engineering audit
~~~

Relire les passages et compléter les décisions avant export et ingestion. Le [guide de la partie 1](partie-1-data-engineering/GUIDE-LOCAL.md) détaille la procédure. Le téléchargement et l’audit technique ne certifient pas l’actualité juridique. Les fichiers bruts, revues, bases et modèles sont exclus de Git.

## Vérifier

~~~powershell
python -m pytest
npm --prefix partie-4-frontend run build
python commun/scripts/smoke.py
python commun/scripts/evaluate.py
cd partie-4-frontend
npx playwright install chromium
npm run test:e2e
~~~

Les services doivent être démarrés pour les tests HTTP/navigateur.
Les tests Python raccordent les vraies applications ASGI dans des bases temporaires.
Les rapports et captures des tests exécutés sont dans commun/docs/verification/.

## GitHub et cloud

Les cinq parties, les ressources communes, Docker Compose et la CI sont publiés ensemble dans ce monorepo. Les modifications se commitent et se poussent directement depuis cette racine. La CI vérifie les tests Python, le démarrage Docker, les API et les parcours navigateur.
Les fichiers `.env`, dépendances installées, caches, corpus collectés, modèles et bases locales sont exclus par `.gitignore`. `.env.example` fournit uniquement les valeurs de démonstration locale.
Les guides de commun/docs/deployment/ n’exécutent aucune création de ressource cloud.

## Parties du projet

- `partie-1-data-engineering/` — Ayoub Chenguir, AWS EC2
- `partie-2-backend/` — Soulayman Jdidi, Azure VM
- `partie-3-nlp/` — Badr Joulali, Google Cloud Run
- `partie-4-frontend/` — Aya Sdour, Azure Static Web Apps
- `partie-5-analytics/` — Ijlal Sellak, Google Compute Engine

Chaque dossier contient le README détaillé du responsable et le code de sa partie. Le dashboard réutilise actuellement le build React de la partie 4, servi indépendamment par la partie 5.
