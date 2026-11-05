"""One-shot MVP ETL runner for local execution and AWS EC2.

The runner collects/reuses official originals, prepares passages, performs the
technical checks, and exports a reviewed JSONL ready for the MVP ingestion.
The human review workflow remains available as a separate advanced command,
but is intentionally skipped by this MVP runner.
"""
import argparse
import json
from pathlib import Path

from sawtna.config import ROOT, data_root

from .pipeline import collect
from .review import inspect_corpus
from sawtna.contracts import Passage


def run(catalog: Path, root: Path, ocr: bool = True, offline: bool = False,
        manifest: Path | None = None, review_dir: Path | None = None) -> dict:
    root.mkdir(parents=True, exist_ok=True)
    latest = manifest or root / "manifests/latest.json"
    has_manifest = latest.is_file()
    if offline and not has_manifest:
        raise ValueError(f"Manifeste absent pour le mode hors ligne : {latest}")

    records = collect(catalog=catalog, root=root, ocr=ocr,
                      reuse_manifest=latest if has_manifest else None,
                      download_missing=has_manifest and not offline)
    failed = [record for record in records if record.get("download_status") == "failed"]
    if failed:
        ids = ", ".join(record["id"] for record in failed)
        raise RuntimeError(f"La collecte a échoué pour : {ids}")

    manifest_path = root / "manifests/latest.json"
    input_path = root / "processed/pending.jsonl"
    passages, report = inspect_corpus(input_path, manifest_path, root)
    if report["errors"]:
        raise RuntimeError(f"Audit bloquant : {len(report['errors'])} erreur(s)")
    output_path = root / "processed/reviewed.jsonl"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = "".join(
        p.model_copy(update={"status": "reviewed"}).model_dump_json() + "\n"
        for p in passages
    )
    output_path.write_text(payload, encoding="utf-8")
    result = {
        "status": "ready_for_mvp_ingestion",
        "mode": "offline-reuse" if offline else ("incremental" if has_manifest else "initial"),
        "catalog": str(catalog),
        "manifest": str(manifest_path),
        "input": str(input_path),
        "output": str(output_path),
        "documents": report["summary"]["documents"],
        "passages": report["summary"]["passages"],
        "languages": report["summary"]["languages"],
        "flagged_passages": report["summary"]["flagged_passages"],
        "next_action": "ingest_reviewed_jsonl",
    }
    (root / "processed/etl-summary.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Collecte, nettoyage et préparation ETL Sawtna pour le MVP.")
    parser.add_argument("--catalog", type=Path, default=ROOT / "partie-1-data-engineering/sources.json")
    parser.add_argument("--data-dir", type=Path, default=data_root(), help="Racine persistante contenant raw/, manifests/ et processed/.")
    parser.add_argument("--manifest", type=Path, help="Manifeste existant à réutiliser; latest.json par défaut si présent.")
    parser.add_argument("--review-dir", type=Path, help="Compatibilité ancienne; ignoré par le runner MVP.")
    parser.add_argument("--ocr", dest="ocr", action="store_true", help="Activer explicitement l'OCR local français/arabe (activé par défaut).")
    parser.add_argument("--no-ocr", dest="ocr", action="store_false", help="Désactiver l'OCR; réservé aux tests rapides.")
    parser.set_defaults(ocr=True)
    parser.add_argument("--offline", action="store_true", help="Réutiliser uniquement les originaux du manifeste; aucun téléchargement.")
    args = parser.parse_args(argv)
    result = run(args.catalog, args.data_dir, args.ocr, args.offline, args.manifest, args.review_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
