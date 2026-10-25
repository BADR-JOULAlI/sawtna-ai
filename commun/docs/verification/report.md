# Vérification locale — 21 octobre 2026

La version de démonstration s’exécute avec les cinq responsabilités étudiantes. Les processus permanents sont PostgreSQL, NLP, backend, frontend citoyen et Analytics/dashboard ; l’ETL s’exécute comme tâche.

| Vérification exécutée | Résultat |
|---|---|
| Tests Python locaux, vraies applications ASGI et bases temporaires | 31 réussis |
| Build React/Vite | réussi |
| Parcours Playwright Chromium | 8 réussis |
| Tests HTTP sur la pile Docker | 9 contrôles réussis |
| PostgreSQL + extension pgvector | utilisés par la pile réelle |
| Recherche FR/AR/Darija, jeu de régression de 12 questions | source attendue retrouvée dans 12 cas sur 12 |
| Arrêt d’Analytics pendant une question | réponse maintenue, événement livré une seule fois après reprise |
| Démarrage Windows Python/Node + SQLite | API, recherche et deux interfaces accessibles |
| Module Data Engineering seul dans un environnement Python séparé | 10 tests réussis |
| GitHub Actions du dépôt publié | réussi |

## Accès actuel

- Citoyen : http://127.0.0.1:5175
- Dashboard indépendant : http://127.0.0.1:8012/dashboard
- Clé de démonstration locale : local-sawtna-admin-only
- API : http://127.0.0.1:8010/docs

Les conteneurs sont laissés démarrés. Les processus du test natif alternatif ont été arrêtés.
Les statistiques du dashboard proviennent des interactions de test effectuées ici, pas d’une audience publique.

## Preuves

pytest.xml, browser-results.json, smoke.json, retrieval-evaluation.json et resilience.json contiennent les résultats enregistrés.
Les captures accueil-desktop.png, assistant-desktop.png, assistant-mobile.png et dashboard-desktop.png ont été produites par les tests navigateur. Les trois vues desktop/mobile ont été inspectées visuellement.
La configuration Docker conserve les versions Python vérifiées dans requirements.lock.txt ; npm ci utilise package-lock.json.

## Données et portée

Quatre sources institutionnelles ont été téléchargées et traitées, dont trois PDF. L’OCR/extraction a produit 475 passages en attente de revue. Le corpus chargé au démarrage contient seulement les six extraits constitutionnels de référence.
Une collecte réussie et un résultat OCR ne prouvent ni l’actualité juridique ni la fidélité de chaque passage. Le Bulletin officiel contient plusieurs textes ; sélectionner les pages utiles avant approbation.

La recherche testée utilise la baseline concept-hash-v1. Le fournisseur entraîné E5 et son Dockerfile sont fournis en option, mais n’ont pas été chargés dans cette validation.
Le jeu de douze questions est une régression éditoriale, pas une mesure générale de précision ni le corpus d’évaluation de 125 questions prévu pour l’équipe.
Les citations restent dans la langue du document. Le projet n’effectue pas de traduction ou de génération libre.
Les déploiements AWS, Azure et Google Cloud, la validation juridique et les tests de charge à grande échelle restent des étapes distinctes.
Deux avertissements de dépréciation de bibliothèques apparaissent dans les tests Python ; ils n’ont pas provoqué d’échec.

## Publication

Dépôt privé : https://github.com/BADR-JOULAlI/sawtna-ai

État historique de la publication initiale : commit 9cf78897cdeac8b0d7be91cf208738b57692e53e. Le périmètre a depuis été étendu aux cinq parties; voir le README actuel.
CI : https://github.com/BADR-JOULAlI/sawtna-ai/actions/runs/39637131994

Lors de cette vérification initiale, le dépôt contenait uniquement Data Engineering, architecture et contrats partagés; les quatre autres services étaient alors disponibles localement. La publication actuelle couvre le projet complet.
