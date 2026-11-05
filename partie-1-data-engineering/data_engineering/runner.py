"""One-shot ETL runner for local execution and AWS EC2.

The runner collects/reuses official originals, prepares passages and creates a
new technical review lot. It deliberately stops before human approval and RAG
ingestion.
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from sawtna.config import ROOT, data_root

from .pipeline import collect
from .review import audit_corpus


def run(catalog: Path, root: Path, ocr: bool = False, offline: bool = False,
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
    if review_dir is None:
        review_dir = root / "reviews" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    report = audit_corpus(input_path, manifest_path, root, review_dir)
    if report["errors"]:
        raise RuntimeError(f"Audit bloquant : {len(report['errors'])} erreur(s)")
    result = {
        "status": "prepared",
        "mode": "offline-reuse" if offline else ("incremental" if has_manifest else "initial"),
        "catalog": str(catalog),
        "manifest": str(manifest_path),
        "pending": str(input_path),
        "review_dir": str(review_dir),
        "documents": report["summary"]["documents"],
        "passages": report["summary"]["passages"],
        "languages": report["summary"]["languages"],
        "flagged_passages": report["summary"]["flagged_passages"],
        "next_action": "human_review_then_approve_then_ingest",
    }
    (review_dir / "run-summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Collecte, préparation et audit ETL Sawtna; s'arrête avant approbation.")
    parser.add_argument("--catalog", type=Path, default=ROOT / "partie-1-data-engineering/sources.json")
    parser.add_argument("--data-dir", type=Path, default=data_root(), help="Racine persistante contenant raw/, manifests/, processed/ et reviews/.")
    parser.add_argument("--manifest", type=Path, help="Manifeste existant à réutiliser; latest.json par défaut si présent.")
    parser.add_argument("--review-dir", type=Path, help="Dossier de revue nouveau ou vide.")
    parser.add_argument("--ocr", dest="ocr", action="store_true", help="Activer explicitement l'OCR local français/arabe (activé par défaut).")
    parser.add_argument("--no-ocr", dest="ocr", action="store_false", help="Désactiver l'OCR; réservé aux tests rapides.")
    parser.set_defaults(ocr=True)
    parser.add_argument("--offline", action="store_true", help="Réutiliser uniquement les originaux du manifeste; aucun téléchargement.")
    args = parser.parse_args(argv)
    result = run(args.catalog, args.data_dir, args.ocr, args.offline, args.manifest, args.review_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
