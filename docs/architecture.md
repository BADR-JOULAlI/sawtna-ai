# Architecture technique — Sawtna AI

Trois fournisseurs, trois IaaS (EC2, Azure VM, Compute Engine), deux PaaS (Cloud Run, Static Web Apps). Le remplacement de Looker Studio par Compute Engine supprime le SaaS initial.

~~~mermaid
flowchart LR
  Docs[Documents institutionnels] --> ETL[AWS EC2 : ETL]
  ETL -->|Ingestion authentifiée| API[Azure VM : API + PostgreSQL/pgvector]
  Citizen[Citoyen] --> Web[Azure Static Web Apps : React + Quiz]
  Web -->|HTTPS| API
  API -->|Embeddings| NLP[Google Cloud Run : NLP CPU]
  API -->|Événements agrégés| KPI[Google Compute Engine : Analytics + Dashboard]
  Local[RTX 5070 : préparation et évaluation] --> Git[GitHub : monorepo + CI]
  Git -.Déploiements séparés.-> ETL
  Git -.-> API
  Git -.-> NLP
  Git -.-> Web
  Git -.-> KPI
~~~

## Contrats et propriété

Chaque étudiant possède son service. Contrats et configuration sont communs.
Les passages JSON contiennent identifiant stable, document, titre, URL, langue, texte, article, page, statut de revue et SHA-256.
L’ingestion exige une clé de service et des passages relus. Les embeddings retournent vecteurs, dimensions et identifiant du modèle.
Changer de modèle exige de recalculer les vecteurs ; le backend n’utilise jamais des vecteurs de modèles différents.

## Flux documentaire

1. Téléchargement sur domaine institutionnel HTTPS autorisé, redirections contrôlées.
2. Conservation du brut par SHA-256, sans écraser les autres versions.
3. Extraction page par page, OCR facultatif des pages sans texte.
4. JSONL en attente de relecture.
5. Relecture du texte, de l’article, de la date, des amendements et du périmètre.
6. Export approuvé puis ingestion authentifiée par lots.

## Recherche

PostgreSQL/pgvector sélectionne les candidats par distance cosinus. Le classement combine similarité et recouvrement lexical pondéré par fréquence.
Le mode SQLite est une alternative locale. Le score est une pertinence de recherche, pas une probabilité de vérité.
La réponse est extractive, avec abstention hors corpus et citations dans leur langue originale.
Le mode autonome utilise une baseline de concepts multilingues ; E5 est un fournisseur entraîné optionnel.

## Analytics

Le backend envoie un identifiant aléatoire, type d’événement, langue, latence et score du quiz. Il n’envoie ni question, ni identité, ni IP, ni préférence politique.
Les réessais conservent l’identifiant ; Analytics déduplique et agrège par jour UTC.
Le dashboard utilise ces compteurs réels et exige une clé administrateur.
Le build React est partagé ; Analytics sert son dashboard indépendamment.

## Exploitation

Endpoints de santé, secrets par variables d’environnement et fichiers Docker reproductibles.
L’API exige X-Service-Key pour ingestion/NLP/Analytics et X-Admin-Key pour le dashboard.
Vite/nginx proxyfient /api ; Azure Static Web Apps utilise VITE_API_BASE_URL et une origine CORS explicite.
Les guides de déploiement prévoient HTTPS, budgets, sauvegardes et rotation des secrets. Aucun cloud n’est automatiquement provisionné.
