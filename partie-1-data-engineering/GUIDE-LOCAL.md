# Partie 1 — Collecter, contrôler et préparer le corpus RAG

Exécuter les commandes depuis la racine `s/`. Catalogue : `partie-1-data-engineering/sources.json`. Les originaux, extractions et revues locales sont conservés dans `commun/data/` et exclus de Git.

## 1. Collecter

~~~powershell
python -m pip install -e ".[test,ocr]"
python commun/scripts/download_ocr.py --language fra
python commun/scripts/download_ocr.py --language ara --variant best
python -m sawtna.data_engineering collect --ocr
~~~

Le téléchargement contrôle HTTPS, domaines, redirections, taille maximale de 25 Mo et signature PDF. Les erreurs de transport et les réponses 429/500/502/503/504 sont réessayées au maximum trois fois avec des pauses de 1 puis 2 secondes. Les autres erreurs HTTP ou de contenu ne sont pas réessayées.

Chaque original est conservé sous son SHA-256. Chaque collecte produit un manifeste daté et un fichier JSONL daté, plus `manifests/latest.json` et `processed/pending.jsonl`. Les passages restent `pending_review`. Si un document échoue, ses passages partiels sont écartés et le programme retourne un code d’échec; les autres documents sont traités.

## 2. Réextraire les originaux conservés

~~~powershell
python -m sawtna.data_engineering collect --ocr --reuse-manifest commun/data/manifests/latest.json
~~~

Le chemin et l’empreinte de chaque original sont vérifiés avant lecture. Aucun téléchargement n’est effectué. L’OCR français traite les pages courtes ou suspectes : caractères de contrôle, caractères de remplacement ou proportion très faible de lettres. `page_quality` indique la méthode utilisée et les signaux restants. Ces heuristiques ne détectent pas toutes les erreurs : colonnes mélangées, mots fusionnés et chiffres nécessitent une relecture.

Pour étendre le catalogue en conservant les originaux déjà collectés :

~~~powershell
python -m sawtna.data_engineering collect --ocr --reuse-manifest commun/data/manifests/latest.json --download-missing
~~~

Seules les sources dont l’identifiant est absent du manifeste sont téléchargées. Un original corrompu ou une URL modifiée reste une erreur, sans remplacement silencieux. Les anciens documents conservent leur `collected_at`; tous reçoivent un nouveau `processed_at`. Pour rafraîchir les documents sur le site officiel, lancer une collecte sans `--reuse-manifest`.

Avec `--ocr`, les PDF arabes sont entièrement reconnus à 300 DPI par Tesseract via `tesserocr`, avec le modèle `tessdata_best` version 4.1.0. Le texte Unicode est récupéré directement, sans repasser par une couche texte PDF susceptible de mélanger les colonnes ou d’inverser l’arabe. Le modèle français existant reste utilisé par PyMuPDF pour les pages suspectes en français.

Chaque page OCR porte `ocr_review_required`. L’arabe enregistre aussi l’empreinte du modèle, la résolution, la version du moteur et `mean_confidence`; une valeur inférieure à 80 ajoute `low_ocr_confidence`. Ce score est une estimation du moteur, pas une mesure d’exactitude. L’OCR peut encore omettre des lignes ou altérer des chiffres. `SAWTNA_OCR_AR_TESSDATA` permet de choisir un autre dossier contenant `ara.traineddata`; son empreinte reste enregistrée.

## 3. Préparer la revue

~~~powershell
python -m sawtna.data_engineering audit
~~~

La commande affiche un nouveau dossier `commun/data/reviews/<date>/` :

| Fichier | Usage |
|---|---|
| `rapport.md` | Synthèse des documents et erreurs |
| `audit.json` | Résultats détaillés, doublons et signaux par passage |
| `passages.md` | Texte complet, URL source, page et identifiant |
| `pending.snapshot.jsonl` | Copie figée des passages audités |
| `manifest.snapshot.json` | Copie figée du manifeste associé |
| `decisions.jsonl` | Décisions individuelles à compléter |
| `priorites.md` | File de relecture FR/AR et textes d’une même famille à comparer |
| `triage.jsonl` | Catégorie lexicale, mots-clés détectés, signaux et empreinte par passage |

L’audit vérifie le contrat des passages, les identifiants, le lien au manifeste, les pages PDF et les empreintes des originaux. Il signale les textes identiques après normalisation des espaces et de la casse. Les erreurs techniques rendent la commande non réussie. Aucun indicateur ne certifie l’actualité juridique d’un document.

Un dossier de revue non vide n’est jamais écrasé. Conserver les snapshots associés, même après une nouvelle collecte.

Le triage place d’abord les passages avec alertes techniques, puis le vocabulaire électoral, le contexte institutionnel et les textes sans indice lexical. Il ne supprime aucun passage et ne renseigne aucune décision. Les accents, signes vocaliques arabes et allongements sont normalisés uniquement pour cette recherche; le texte documentaire demeure inchangé. Les familles et rôles renseignés dans `sources.json` rapprochent textes originaux et modifications sans prétendre produire une version consolidée.

## 4. Relire et sélectionner

Ouvrir `passages.md` et comparer chaque passage au document officiel : page, articles, chiffres et éventuelles modifications ultérieures du texte. Dans `decisions.jsonl`, modifier seulement :

- `decision` : `pending`, `approve` ou `reject`;
- `comment` : motif de la décision ou observations.

Conserver identifiants, empreintes et textes. Une correction de texte impose de préparer une nouvelle revue à partir du corpus corrigé. Les sommaires, pages hors sujet, tableaux mal extraits et doublons peuvent être rejetés. Pour un Bulletin officiel, sélectionner les passages utiles plutôt que valider toutes ses pages.

## 5. Exporter après relecture

Remplacer le chemin de revue et le nom du relecteur. Choisir un nom d’export nouveau : un export existant et son journal ne sont pas écrasés.

~~~powershell
$revue = 'commun/data/reviews/<date-affichee-par-audit>'
python -m sawtna.data_engineering approve --input "$revue/pending.snapshot.jsonl" --manifest "$revue/manifest.snapshot.json" --decisions "$revue/decisions.jsonl" --reviewer "Nom du relecteur" --output commun/data/processed/reviewed-lot-001.jsonl
~~~

Seules les décisions `approve` produisent des passages `reviewed`. Les empreintes du texte et du document sont revérifiées; les identifiants inconnus, dupliqués et décisions périmées sont refusés. Le journal `reviewed-lot-001.jsonl.review.json` conserve relecteur, date, empreintes d’entrée/sortie et décisions. Il trace une déclaration de revue; ce n’est pas une signature électronique authentifiée.

L’ancien mode `approve --document` demeure compatible, mais concerne un document entier déjà relu. Pour les nouveaux lots, utiliser les décisions par passage avec journal.

## 6. Livrer au backend

~~~powershell
python commun/scripts/ingest.py --input commun/data/processed/reviewed-lot-001.jsonl
~~~

Le backend doit être lancé. L’URL et la clé interservice sont configurées avec `SAWTNA_API_URL` et `SAWTNA_SERVICE_KEY`. Les passages en attente ne sont pas envoyés.

## Vérification et travail suivant

~~~powershell
python -m pytest commun/tests/test_data_engineering.py commun/tests/test_data_review.py commun/tests/test_data_expansion.py commun/tests/test_data_ocr.py
~~~

Le catalogue contient maintenant des sources françaises et arabes. La sélection des passages, la correction des erreurs OCR et la vérification de l’actualité des textes restent nécessaires. Voir [le rapport d’extension](RAPPORT-EXTENSION.md).

## Exécuter la partie 1 dans Docker

Le profil `etl` utilise son propre Dockerfile avec l’extension OCR. Le volume `commun/data/` conserve modèles, originaux et revues.

~~~powershell
docker compose --profile etl build etl
docker compose --profile etl run --rm --no-deps etl --help
docker compose --profile etl run --rm --no-deps --entrypoint python etl commun/scripts/download_ocr.py --language fra
docker compose --profile etl run --rm --no-deps --entrypoint python etl commun/scripts/download_ocr.py --language ara --variant best
docker compose --profile etl run --rm --no-deps etl collect --ocr
docker compose --profile etl run --rm --no-deps etl audit
~~~

Ces commandes fonctionnent localement sans identifiants AWS. Le déploiement EC2 et sa planification restent à réaliser.
