"""Prepare a local RAG demo corpus without turning technical checks into approval."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from data_engineering.review import inspect_corpus
from sawtna.config import ROOT, data_root


def prepare(input_path: Path, manifest_path: Path, corpus_root: Path, output_path: Path):
    passages, audit = inspect_corpus(input_path, manifest_path, corpus_root)
    if audit["errors"]:
        raise ValueError(f"Audit de provenance bloquant : {len(audit['errors'])} erreur(s).")

    # This portal page was found to mix referendum history with unrelated news/navigation.
    excluded_sources = {"constitution-portail-fr"}
    selected = [
        passage for passage in passages
        if passage.status == "pending_review"
        and not audit["warnings"].get(passage.id)
        and passage.document_id not in excluded_sources
    ]
    if not selected:
        raise ValueError("Aucun passage propre à préparer pour le mode démo local.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = "".join(p.model_dump_json() + "\n" for p in selected)
    output_path.write_text(payload, encoding="utf-8", newline="\n")

    summary = {
        "mode": "local_demo_only",
        "status": "pending_review",
        "input_sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
        "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "output_sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        "input_passages": len(passages),
        "indexed_passages": len(selected),
        "excluded_flagged_passages": len(passages) - len(selected) - sum(
            p.document_id in excluded_sources for p in passages
        ),
        "excluded_noisy_documents": sorted(excluded_sources),
        "languages": dict(Counter(p.language for p in selected)),
        "documents": len({p.document_id for p in selected}),
        "human_approved_passages": 0,
        "warning": "Local demonstration corpus; passages are not human-reviewed and must not be used as approved cloud data.",
    }
    summary_path = output_path.with_name(output_path.stem + ".summary.json")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "commun/data/corpus-mvp-20261121/processed/pending.jsonl")
    parser.add_argument("--manifest", type=Path, default=ROOT / "commun/data/corpus-mvp-20261121/manifests/latest.json")
    parser.add_argument("--corpus-root", type=Path, default=ROOT / "commun/data/corpus-mvp-20261121")
    parser.add_argument("--output", type=Path, default=data_root() / "runtime/demo/local-corpus-pending.jsonl")
    args = parser.parse_args(argv)
    summary = prepare(args.input, args.manifest, args.corpus_root, args.output)
    print(json.dumps({**summary, "output": str(args.output)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
