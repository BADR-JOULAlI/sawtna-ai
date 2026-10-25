# Vérification de la réorganisation du 25 octobre 2026

Le code des cinq services a été déplacé depuis `services/` vers les cinq dossiers `partie-*` à la racine. Le dossier `services/` a été retiré une fois vide. Les ressources partagées sont dans `commun/` : données, docs, infrastructure, packages, scripts et tests.

Les chemins ont été adaptés dans le packaging Python, les imports de lancement, la collecte, le dashboard, les images Docker, Docker Compose, les scripts, la CI et les tests navigateur. Les contenus existants et les données locales ont été conservés. Les anciens caches ont été rangés dans `commun/.cache/`.

Vérifications exécutées après migration :

- Installation éditable du monorepo : réussie.
- Tests Python : 31 réussis.
- Build Vite : réussi depuis `partie-4-frontend/`.
- Reconstruction Docker Compose : réussie; cinq conteneurs sains, PostgreSQL/pgvector utilisé.
- Contrôles HTTP : 9 réussis, y compris les deux points d’entrée web.
- Tests Playwright : 8 réussis.
- Paquet Data Engineering exporté : construit, installé dans un environnement séparé, 10 tests réussis.
- Export GitHub vérifié à cette étape : Data Engineering et fiches des cinq parties. Cette restriction a ensuite été levée pour publier les cinq implémentations dans le monorepo.

Le build React du dashboard reste partagé avec le frontend citoyen; la partie 5 le sert sur son propre endpoint. Cette réorganisation ne constitue pas un déploiement cloud.
