# Partie 1 — Premier lot préparé le 28 octobre 2026

Rapport historique du premier lot. L’état suivant est documenté dans [le rapport d’extension du 29 octobre](RAPPORT-EXTENSION.md).

Le lot documentaire existant a été réextrait et audité en local. Il contient **474 passages francophones provenant de quatre sources officielles**, tous au statut `pending_review`. Aucun passage de ce lot n’a été approuvé ni envoyé au backend.

Les originaux avaient été téléchargés le 21 octobre 2026. Cette exécution les réutilise après vérification de leur SHA-256; elle ne constitue pas une nouvelle collecte web. La date de collecte est conservée séparément de la date de traitement.

## Inventaire

| Document | Format | Pages PDF | Passages | Pages traitées par OCR |
|---|---|---:|---:|---:|
| Constitution 2011 — édition SGG | PDF | 65 | 66 | 65 |
| Constitution 2011 — copie Maroc.ma | PDF | 28 | 82 | 28 |
| Constitution — portail Maroc.ma | HTML | — | 1 | 0 |
| Bulletin officiel n° 7000 | PDF | 85 | 325 | 0 |
| **Total** | | **178** | **474** | **93** |

Le catalogue et les URLs sont dans [sources.json](sources.json). Les deux éditions de la Constitution doivent être comparées pour sélectionner une version de référence. Le Bulletin officiel contient plusieurs textes : ses 325 passages ne constituent pas automatiquement un corpus électoral pertinent.

## Corrections réalisées

- L’OCR se déclenche aussi sur les caractères de contrôle et textes suspects. Une couverture du PDF SGG, précédemment extraite sous forme de caractères illisibles, est désormais lisible.
- Les erreurs réseau transitoires font l’objet de trois tentatives au maximum.
- La réextraction peut reprendre depuis un manifeste et des originaux vérifiés sans téléchargement.
- Les passages partiels d’un document dont le traitement échoue sont écartés.
- L’audit vérifie provenance, intégrité, contrat, pages et doublons; il prépare des copies figées et une fiche de décision par passage.
- L’export des décisions conserve un journal avec nom du relecteur et empreintes des entrées/sorties. Les décisions périmées, inconnues ou dupliquées sont refusées.

## Résultat de l’audit

- 0 erreur bloquante de provenance ou de contrat détectée.
- 17 passages signalés : 15 appartiennent à 6 groupes de textes identiques; 2 ont une faible proportion de lettres.
- Aucun caractère de contrôle détecté dans les passages de la dernière extraction.
- 474 passages restent à relire. Les autres passages peuvent aussi contenir des erreurs d’OCR non détectées par les heuristiques.

La précédente extraction contenait 475 passages. Le nouveau traitement du texte et le découpage donnent 474 passages; aucune suppression automatique de doublons ni validation juridique n’a été appliquée.

## Fichiers de travail locaux

Le dossier de revue est `commun/data/reviews/2026-10-28-lot-001/`, depuis la racine du projet. Il est exclu de Git et contient :

- `rapport.md` et `audit.json` : résultats techniques;
- `passages.md` : textes avec identifiant, source et page;
- `decisions.jsonl` : décisions à compléter;
- `pending.snapshot.jsonl` et `manifest.snapshot.json` : entrées figées de la revue.

Le [guide local](GUIDE-LOCAL.md) explique comment relire, exporter un lot approuvé et le livrer au backend. Les décisions doivent rester `pending` tant que le texte et sa pertinence n’ont pas été vérifiés.

## Vérification et suite du travail

La suite Python complète a passé 47 tests, dont 26 couvrent Data Engineering et la revue. Les cas incluent retries réseau, empreintes incohérentes, chemins hors corpus, erreurs de traitement partielles, doublons, décisions périmées et sélection explicite à l’export.

Prochaine étape : relire les passages pertinents, écarter sommaires et textes hors sujet, puis vérifier la version et les modifications des textes retenus. La collecte de sources arabes, la validation d’un premier lot pour ingestion, la planification et le déploiement EC2 restent à réaliser.
