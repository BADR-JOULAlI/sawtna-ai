# Répartition

| Étudiant | Livrables | Validation |
|---|---|---|
| 1 — ETL | catalogue, collecte, extraction/OCR, manifests, JSONL, ingestion | intégrité, domaines, redirections, découpage et revue |
| 2 — Backend | API, PostgreSQL/pgvector, recherche, citations, quiz serveur, file Analytics | contrats, abstention, ingestion et erreurs |
| 3 — NLP | API CPU, baseline, fournisseur E5, lexique Darija, évaluation | dimensions, normalisation, cohérence modèle et rappel |
| 4 — Frontend | assistant, bibliothèque, quiz, traductions, RTL et responsive | build et navigateur desktop/mobile |
| 5 — Analytics | événements idempotents, KPI, dashboard et hébergement | compteurs, déduplication et confidentialité |

Les 125 questions d’évaluation restent un travail éditorial collectif (25 par étudiant). Le jeu de régression fourni ne remplace pas cette évaluation.
Les cibles cloud sont à déployer et vérifier par chaque étudiant après autorisation.
Le monorepo publié contient les cinq parties et les ressources communes. Chaque responsable maintient son dossier et coordonne les changements de contrats avec les autres étudiants.
Les cinq dossiers `partie-*` contiennent le code dans le monorepo local et les fiches de responsabilités. Les éléments partagés sont regroupés dans `commun/`.
