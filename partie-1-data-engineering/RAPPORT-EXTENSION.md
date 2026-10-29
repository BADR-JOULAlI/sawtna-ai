# Partie 1 — Extension bilingue du 29 octobre 2026

Le corpus local contient **704 passages issus de 10 sources officielles : 539 en français et 165 en arabe**. Ils restent tous `pending_review`. Aucun passage de ce lot n’a été approuvé ou envoyé au backend; le corpus de démonstration de l’application reste distinct.

Six PDF supplémentaires ont été téléchargés depuis le SGG le 29 octobre. Les quatre originaux du premier lot, collectés le 21 octobre, ont été réutilisés après vérification SHA-256. Une deuxième extraction locale a ensuite repris les dix originaux pour améliorer le traitement de l’arabe, sans nouveau téléchargement.

## Documents

| Source | Langue | Pages PDF | Passages | Pages OCR |
|---|---|---:|---:|---:|
| Constitution 2011, édition SGG | fr | 65 | 66 | 65 |
| Constitution 2011, copie Maroc.ma | fr | 28 | 82 | 28 |
| Constitution, portail Maroc.ma | fr | — | 1 | 0 |
| Bulletin officiel n° 7000 | fr | 85 | 325 | 0 |
| Constitution 2011, édition SGG | ar | 82 | 83 | 82 |
| Loi organique 27.11, texte de 2011 | fr | 15 | 65 | 15 |
| Loi organique 27.11, texte de 2011 | ar | 17 | 45 | 17 |
| Loi organique 20.16 | ar | 2 | 3 | 2 |
| Loi organique 04.21 | ar | 5 | 13 | 5 |
| Loi organique 53.25 | ar | 8 | 21 | 8 |
| **Total** | **fr + ar** | **307** | **704** | **222** |

Les nouvelles URLs proviennent des catalogues institutionnels [SGG français](https://www.sgg.gov.ma/textesimportants.aspx) et [SGG arabe](https://www.sgg.gov.ma/arabe/textesimportants.aspx). Elles sont conservées avec leur page de découverte dans [sources.json](sources.json). Le regroupement de la loi 27.11 avec les modifications référencées 20.16, 04.21 et 53.25 prépare une comparaison documentaire; il ne constitue ni une consolidation juridique ni une liste certifiée exhaustive des modifications.

## Corrections et capacités ajoutées

- Extension du catalogue avec `--reuse-manifest ... --download-missing` : seuls les nouveaux identifiants sont téléchargés; un ancien fichier corrompu ou une URL modifiée reste une erreur explicite.
- OCR arabe direct via Tesseract, modèle `tessdata_best` 4.1.0, à 300 DPI. L’empreinte du modèle, la version de `tesserocr` et la confiance moyenne sont enregistrées par page.
- Propagation des alertes de page vers chaque passage correspondant. Tout texte OCR porte désormais `ocr_review_required`, même s’il semble lisible.
- Triage lexical français/arabe avec les mots déclencheurs, sans modification du texte, suppression de passage ni décision automatique.
- Image Docker ETL dédiée avec l’extension OCR, vérifiée sous Linux; commandes d’exploitation dans [GUIDE-LOCAL.md](GUIDE-LOCAL.md).

## Contrôles et limites observées

L’audit final détecte **0 erreur bloquante de provenance ou de contrat** et **395 passages avec au moins un signal**. Les catégories se recouvrent :

- 378 passages issus d’une page OCR, à vérifier;
- 20 passages sur 17 pages arabes dont la confiance moyenne du moteur est inférieure à 80;
- 7 passages à faible proportion de lettres;
- 15 passages appartenant à 6 groupes de textes identiques.

Le premier essai arabe utilisait une couche texte PDF reconstruite par l’OCR; un contrôle visuel a montré des colonnes entremêlées et des inversions. La récupération directe du texte Unicode améliore l’ordre sur l’échantillon contrôlé. Elle ne corrige pas toutes les erreurs de reconnaissance : les pages comparées de la Constitution et de la loi 53.25 présentent encore des chiffres altérés et des lignes omises. Un score de confiance élevé ne garantit donc pas la fidélité du passage. Aucune correction manuelle non tracée n’a été appliquée au texte.

Le lot intermédiaire contenait 711 passages; la nouvelle extraction en produit 704. Cette variation provient du texte reconnu et de son découpage, pas d’une déduplication éditoriale. Les deux versions sont conservées.

Le triage final répartit les passages en **261 avec vocabulaire électoral**, **92 avec contexte institutionnel** et **351 sans indice lexical**. Ces nombres servent à organiser la relecture : un passage sans indice peut être pertinent, et un mot-clé peut apparaître dans un sommaire ou un texte hors périmètre.

## Livrable local à relire

Dossier depuis la racine du projet : `commun/data/reviews/2026-10-29-lot-003/`.

- `priorites.md` : couverture par document, familles de textes et file de relecture;
- `passages.md` : textes complets, source et page;
- `triage.jsonl` : raisons du classement et empreintes;
- `decisions.jsonl` : 704 décisions initialisées à `pending`;
- `audit.json`, `rapport.md` et les deux snapshots : preuve technique et entrées figées.

Le lot `2026-10-29-lot-002/` conserve le premier essai arabe; ne pas le confondre avec la dernière extraction. Ces dossiers, les PDF et les modèles restent exclus de Git. Le dépôt contient le code, le catalogue, les tests et la documentation.

## Vérification

- **62 tests Python réussis**, dont 41 pour la collecte, la revue, l’extension bilingue et l’OCR; deux avertissements de dépréciation de dépendances préexistants.
- Construction de `sawtna-etl:1.0` réussie et CLI exécutée dans Docker.
- OCR réel d’une page arabe exécuté sous Linux dans cette image, en plus de la collecte complète locale sous Windows.
- Audit complet du lot final et configuration Compose valides.

La chaîne CI inclut maintenant la construction et le démarrage du CLI ETL ainsi que l’import du moteur OCR, en complément des vérifications existantes de l’application. Les tests unitaires utilisent des fixtures contrôlées; ils ne mesurent pas la précision de l’OCR sur l’ensemble du corpus.

## Étape suivante

Comparer les passages sélectionnés à leurs PDF, corriger et tracer les erreurs, écarter sommaires/doublons/textes hors sujet, puis vérifier les versions juridiques avant d’approuver un premier lot pour ingestion. Le déploiement EC2 et sa planification ne sont pas réalisés.
