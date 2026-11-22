# Données

seed/foundation.json contient six extraits constitutionnels de démonstration à références officielles. Les espaces et apostrophes typographiques peuvent être normalisés, sans paraphraser le texte.
Ce petit corpus ne certifie pas l’état complet des lois électorales.

Pour la démonstration locale multi-document, préparer d’abord la collecte étendue (conservée hors Git), puis lancer :

~~~powershell
python commun/scripts/prepare_local_demo.py --input commun/data/corpus-mvp-20261121/processed/pending.jsonl --manifest commun/data/corpus-mvp-20261121/manifests/latest.json --corpus-root commun/data/corpus-mvp-20261121
python -m sawtna.launcher
~~~

Le lanceur utilise une base SQLite locale dédiée au corpus, ajoute les passages encore `pending_review` à l’index de démonstration et les signale dans l’interface. Cette voie ne change pas l’endpoint d’ingestion : le backend continue de refuser les passages non relus pour l’index cloud. Le corpus de démonstration ne doit pas être présenté comme approuvé.

Dossiers générés exclus de Git : raw/ (originaux versionnés), manifests/ (provenance et erreurs), processed/ (JSONL), reviews/ (snapshots, triage et décisions), runtime/ (bases et logs), models/ (OCR et modèles).
Les documents collectés sont des données documentaires, jamais des instructions à exécuter.
