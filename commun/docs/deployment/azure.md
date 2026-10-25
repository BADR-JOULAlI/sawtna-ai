# Azure — backend et frontend

## VM backend

Construire commun/infra/Dockerfile, choisir SAWTNA_SERVICE=backend et PORT=8000.
Configurer une base PostgreSQL/pgvector privée, SAWTNA_BACKEND_DATABASE_URL, les URLs NLP/Analytics et les secrets.
Placer un reverse proxy HTTPS devant l’API ; limiter les ports réseau au proxy, à l’administration autorisée et au réseau privé PostgreSQL.
Valider /health, une question citée, le quiz, les événements et la restauration d’une sauvegarde.

## Static Web Apps

Racine app : partie-4-frontend. Commandes npm ci puis npm run build ; sortie dist.
Avant le build, VITE_API_BASE_URL doit contenir l’origine HTTPS de la VM backend.
SAWTNA_ALLOWED_ORIGINS du backend doit contenir exactement l’origine Static Web Apps.
Les variables Vite sont incluses dans JavaScript : aucun secret ne doit y être placé.
Valider clavier, mobile, arabe RTL et les appels HTTPS réels sur les comptes des deux étudiants.
