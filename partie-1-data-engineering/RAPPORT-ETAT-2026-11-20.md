# État de la Partie 1 — 20 novembre 2026

## Résumé de la collecte

| Mesure | Résultat |
|---|---:|
| Documents au catalogue | 32 |
| Documents collectés et extraits dans le corpus local | 15 |
| Passages préparés | 1 266 |
| Passages approuvés par une revue humaine traçable | 0 |
| Passages en attente de revue | 1 266 |
| Langue française | 1 038 passages (82,0 %) |
| Langue arabe | 228 passages (18,0 %) |
| Passages en darija issus de sources officielles | 0 |
| Erreurs bloquantes de provenance/contrat dans l’audit | 0 |
| Passages signalés par les contrôles techniques | 456 |
| Groupes de textes identiques à comparer | 7 |

Les 15 documents comprennent 10 documents déjà collectés auparavant et 5 nouveaux documents traités dans cette extension. Les 32 entrées du catalogue ne sont donc pas toutes présentes dans le corpus local.

## Couverture primaire par thème

Chaque passage est compté une seule fois selon le thème principal de son document; les thèmes peuvent se chevaucher dans le contenu réel.

| Thème principal | Passages | Français | Arabe |
|---|---:|---:|---:|
| Constitution et institutions | 232 | 149 | 83 |
| Élections et représentation parlementaire | 472 | 390 | 82 |
| Droit et organisation des partis | 52 | 0 | 52 |
| Programmes de partis et politiques publiques | 510 | 499 | 11 |

La nouvelle collecte ajoute le programme 2026 du PAM en arabe, le programme électoral 2026 de l’USFP en français et le programme gouvernemental 2027–2031 du PPS en français. Les textes sont conservés comme positions déclarées par leurs partis, jamais comme faits ou résultats publics vérifiés.

Sources primaires collectées : [SGG — texte consolidé de la loi 29.11](https://www.sgg.gov.ma/Portals/1/textesconsolides/29_11.pdf), [SGG — loi 54.25](https://www.sgg.gov.ma/Portals/1/lois/Loi_organique_54.25_ar.pdf), [programme du PAM](https://pam.ma/programme-electoral/), [programme complet de l’USFP](https://www.usfp.ma/fr/wp-content/uploads/2026/09/usfp-programme-fr.pdf) et [programme du PPS](https://pps.ma/fr/9715/). Les autres documents du corpus proviennent des sources officielles SGG, Bulletin officiel et Maroc.ma déjà cataloguées dans `sources.json`.

## Revue, OCR et qualité

- Les 1 266 passages du nouveau corpus intégré restent `pending_review`. Les 456 signaux sont des indicateurs techniques, pas des erreurs confirmées : ils comprennent notamment les passages issus de pages OCR.
- L’audit relève 7 groupes de textes identiques. Aucun passage n’a été supprimé automatiquement; les deux éditions françaises de la Constitution et des textes réimprimés doivent être comparés par une personne.
- L’extension rapporte 0 passage rejeté pour longueur insuffisante et 2 pages extraites vides. Les collectes historiques ne conservaient pas ce compteur; leur nombre de rejets n’est donc pas reconstituable avec certitude.
- Le corpus final contient 262 pages traitées par OCR. Les anciens manifestes ne précisent pas tous le moteur : 114 pages portent explicitement `tesserocr-2.12.0`, 33 portent explicitement `ocr_engine_fallback`, et 115 ne donnent pas ce détail. Dix-sept pages ont un signal `low_ocr_confidence`; 5 passages ont `low_letter_ratio`.
- L’OCR a utilisé les modèles locaux. `tesserocr` et le fallback PyMuPDF/Tesseract sont des traitements CPU; l’RTX 5070 n’a pas été utilisée pour l’OCR. Le binaire `tesseract` n’est pas disponible dans le PATH Windows, mais le fallback via PyMuPDF fonctionne avec les modèles déjà présents.

## Revue humaine et anciens fichiers `reviewed`

L’inspection de toutes les files de décisions sous `commun/data/reviews/` montre que leurs décisions sont encore `pending`; aucun journal `.review.json` n’atteste une approbation. Pourtant, d’anciens fichiers contiennent respectivement 704, 1 et 704 passages marqués `reviewed`. Ils ne sont pas des passages approuvés et n’ont pas été modifiés afin de préserver les archives historiques.

Le runner ETL ne transforme plus les passages en `reviewed`. Le script d’ingestion exige maintenant un journal de revue correspondant, une empreinte de sortie valide et des décisions `approve` pour chaque passage. Les anciens exports sans journal sont refusés.

## Collectes non abouties et limites

- La page du programme 2026 du PJD est inscrite au catalogue, mais le serveur a répondu HTTP 526 pendant la collecte locale. Le PDF officiel devra être téléchargé quand la source sera à nouveau accessible.
- Le PDF 2026 d’Istiqlal dépasse la limite de collecte actuelle de 25 Mo. Il reste au catalogue mais n’a pas été téléchargé.
- Aucune source de programme officielle en darija n’a été trouvée; la darija n’existe donc que dans le jeu de questions de test, pas dans les documents ni les passages.
- Le corpus reste très inégal : les documents longs dominent, notamment le Bulletin officiel n° 7000 (325 passages) et le programme intégral du PPS (413). Les lois des collectivités territoriales, les listes électorales consolidées, les calendriers administratifs récents et les activités parlementaires détaillées sont encore peu ou pas représentés.
- Le droit consolidé des partis récupéré sur le SGG est en arabe et daté de 2023; il est conservé séparément de l’amendement 54.25 publié en 2026. Il ne faut pas le présenter comme une version consolidée postérieure à cet amendement.
- Le schéma Passage existant ne transporte pas l’autorité éditrice, la date du document, son rôle, sa période de validité ni ses thèmes. Ces métadonnées restent dans le manifeste; le backend et son schéma n’ont pas été modifiés.
- La base locale actuellement utilisée par le MVP contient 7 passages et 2 documents (6 passages `constitution-2011-fr`, 1 passage `constitution-portail-fr`). Le corpus étendu préparé ici n’est pas encore indexé par le MVP.

## Benchmark de recherche et d’abstention

Le benchmark contient 15 questions : 5 en français, 5 en arabe et 5 en darija. Douze ont un passage cible avec `document_id`, page, langue de la source et URL; trois sont sans réponse attendue dans cette version du corpus. Il sert à tester le rappel de passages et l’abstention. Les questions darija testent une requête translittérée vers des sources arabes ou françaises; elles ne constituent pas un corpus darija.

## Fichiers et commandes

- Catalogue : `partie-1-data-engineering/sources.json` (32 entrées).
- Corpus local intégré, toujours en attente : `commun/data/combined-20261120-v3/processed/corpus-pending.jsonl`.
- Manifeste et empreintes : `commun/data/combined-20261120-v3/manifests/latest.json`.
- File de revue générée par l’audit : `commun/data/combined-20261120-v3/reviews/lot-20261120/`.
- Benchmark : `commun/data/combined-20261120-v3/evaluation/benchmark.json`.
- Dossier de transfert local pour Ayoub : `sawtna-data-handoff/partie-1-lot-20261120/`. L’export `processed/reviewed.jsonl` y est volontairement vide puisque 0 passage n’a été approuvé.

Réextraction locale après correction de la langue du PDF SGG, sans nouvelle requête réseau :

~~~powershell
python -m data_engineering.runner --catalog commun/data/expansion-20261120-final/catalog-v2.json --data-dir commun/data/expansion-20261120-final --offline
~~~

Tests exécutés :

~~~powershell
\.venv\Scripts\python.exe -m pytest commun\tests\test_data_runner.py commun\tests\test_data_engineering.py commun\tests\test_data_expansion.py commun\tests\test_data_review.py commun\tests\test_data_ocr.py -q
~~~

Résultat : **52 tests réussis**. L’avertissement restant provient de `Starlette`/`httpx` dans la dépendance de test; aucun échec de test.

Le contrat d’ingestion et la compatibilité API ont aussi été vérifiés avec :

~~~powershell
\.venv\Scripts\python.exe -m pytest commun\tests\test_backend.py -q
~~~

Résultat : **22 tests réussis**. Total exécuté pour cette vérification : **74 tests réussis**.

## Intervention nécessaire avant toute ingestion

Une personne doit comparer les doublons et relire les pages OCR, en particulier les passages signalés, vérifier la portée juridique des lois amendées, puis décider explicitement passage par passage. Le dépôt Git contient déjà des PDF bruts et des modèles OCR suivis dans l’historique; les nouveaux lots locaux sont ignorés par `.gitignore`, mais les anciens fichiers déjà suivis nécessitent un nettoyage Git dédié avant tout futur push. Aucun push n’a été réalisé.
