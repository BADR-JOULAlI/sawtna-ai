# Partie 1 — Collecter, contrôler et préparer le corpus RAG

Exécuter les commandes depuis la racine `s/`. Catalogue : `partie-1-data-engineering/sources.json`. Les originaux, extractions et revues locales sont conservés dans `commun/data/` et exclus de Git.

## 1. Collecter

~~~powershell
python -m pip install -e ".[test]"
python commun/scripts/download_ocr.py --language fra
python -m sawtna.data_engineering collect --ocr
~~~

Le téléchargement contrôle HTTPS, domaines, redirections, taille maximale de 25 Mo et signature PDF. Les erreurs de transport et les réponses 429/500/502/503/504 sont réessayées au maximum trois fois avec des pauses de 1 puis 2 secondes. Les autres erreurs HTTP ou de contenu ne sont pas réessayées.

Chaque original est conservé sous son SHA-256. Chaque collecte produit un manifeste daté et un fichier JSONL daté, plus `manifests/latest.json` et `processed/pending.jsonl`. Les passages restent `pending_review`. Si un document échoue, ses passages partiels sont écartés et le programme retourne un code d’échec; les autres documents sont traités.

## 2. Réextraire les originaux conservés

~~~powershell
python -m sawtna.data_engineering collect --ocr --reuse-manifest commun/data/manifests/latest.json
~~~

Le chemin et l’empreinte de chaque original sont vérifiés avant lecture. Aucun téléchargement n’est effectué. L’OCR traite les pages courtes ou suspectes : caractères de contrôle, caractères de remplacement ou proportion très faible de lettres. `page_quality` indique la méthode utilisée et les signaux restants. Ces heuristiques ne détectent pas toutes les erreurs : colonnes mélangées, mots fusionnés et chiffres nécessitent une relecture.

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

L’audit vérifie le contrat des passages, les identifiants, le lien au manifeste, les pages PDF et les empreintes des originaux. Il signale les textes identiques après normalisation des espaces et de la casse. Les erreurs techniques rendent la commande non réussie. Aucun indicateur ne certifie l’actualité juridique d’un document.

Un dossier de revue non vide n’est jamais écrasé. Conserver les snapshots associés, même après une nouvelle collecte.

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
python -m pytest commun/tests/test_data_engineering.py commun/tests/test_data_review.py
~~~

Le corpus actuel est francophone. Les sources arabes, la sélection précise des textes électoraux et leur actualité restent à compléter. Le déploiement AWS EC2 sera traité après validation locale du pipeline et du corpus.
