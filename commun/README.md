# Éléments communs aux cinq étudiants

Ce dossier regroupe le corpus et les ressources utilisées par plusieurs parties.

| Dossier | Contenu | Responsabilité |
|---|---|---|
| `data/` | Sources, passages, corpus de référence, modèles et données locales | Collecte par la partie 1, exploitation convenue avec les parties 2 et 3 |
| `docs/` | Architecture, déploiement et rapports | Équipe |
| `infra/` | Images Docker, nginx, initialisation SQL | Chaque propriétaire relit la configuration de son service |
| `packages/` | Contrats API et bibliothèque Python partagée | Modifications coordonnées entre producteurs et consommateurs |
| `scripts/` | Lancement, ingestion et vérifications | Équipe |
| `tests/` | Tests Python et intégration | Propriétaires des services concernés |

Les dossiers de code sont `partie-1-data-engineering/`, `partie-2-backend/`, `partie-3-nlp/`, `partie-4-frontend/` et `partie-5-analytics/`, directement à la racine du monorepo local.

Le dépôt GitHub contient les cinq implémentations et ces ressources communes. Chaque étudiant peut travailler sur sa partie dans une branche puis proposer son intégration.

Les caches, dépendances, originaux collectés et bases locales sont générés pendant l’exécution et exclus de Git. Toutes les commandes des guides s’exécutent depuis la racine, sauf indication explicite.
