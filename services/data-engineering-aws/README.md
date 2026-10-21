# Étudiant 1 — Data Engineering · AWS EC2

Code : data_engineering/pipeline.py. Depuis la racine :

~~~powershell
python -m pip install -e ".[test]"
python scripts/download_ocr.py --language fra
python -m sawtna.data_engineering collect --ocr
python -m pytest tests/test_data_engineering.py
~~~

Catalogue : sources.json. Une source indique identifiant, URL institutionnelle, langue, format, autorité, date et état d’actualité juridique.
Les redirections hors allowlist et les documents de plus de 25 Mo sont rejetés.
Les bruts sont dans data/raw/document/sha256.format, les manifests datés dans data/manifests/, les passages dans data/processed/.
Les pages avec moins de 60 caractères sont signalées OCR requis. --ocr utilise PyMuPDF/Tesseract localement ; les résultats restent à relire.

Après relecture humaine :

~~~powershell
python -m sawtna.data_engineering approve --document constitution-2011-sgg-fr
python scripts/ingest.py --input data/processed/reviewed.jsonl
~~~

Pour un Bulletin officiel multi-thèmes, isoler les pages pertinentes et les relire avant approbation.
Les sources brutes et modèles sont hors Git. L’ETL est une tâche manuelle ou planifiée sur EC2.
