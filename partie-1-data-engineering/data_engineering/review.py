"""Audit provenance and prepare explicit, fingerprint-bound human review decisions."""
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from sawtna.contracts import Passage
from .pipeline import allowed_url, verified_raw
from .quality import quality_flags, text_digest


def read_passages(path):
    passages, errors = [], []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            passages.append(Passage.model_validate_json(line))
        except ValueError as exc:
            errors.append(f"Ligne {line_number}: passage non conforme ({type(exc).__name__}).")
    return passages, errors


def inspect_corpus(input_path: Path, manifest_path: Path, root: Path):
    passages, errors = read_passages(input_path)
    records = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(records, list) or not all(isinstance(r, dict) and "id" in r for r in records):
        raise ValueError("Le manifeste doit contenir une liste de documents identifiés.")
    documents = {r["id"]: r for r in records}
    if len(documents) != len(records):
        errors.append("Identifiants documentaires dupliqués dans le manifeste.")
    for record in records:
        try:
            if record.get("download_status") not in {"downloaded", "reused"}:
                raise ValueError("Collecte échouée ou non réalisée.")
            verified_raw(root, record)
            allowed_url(record["final_url"])
        except (ValueError, OSError, KeyError) as exc:
            errors.append(f"Document {record['id']}: {exc}")

    ids, texts, warnings, counts = Counter(), defaultdict(list), {}, Counter()
    for p in passages:
        ids[p.id] += 1
        counts[p.document_id] += 1
        record = documents.get(p.document_id)
        if not record:
            errors.append(f"Passage {p.id}: document absent du manifeste.")
        else:
            if p.sha256 != record.get("sha256") or str(p.source_url) != record.get("final_url"):
                errors.append(f"Passage {p.id}: source ou empreinte incohérente avec le manifeste.")
            if record.get("format") == "pdf" and (p.page is None or p.page > record.get("pages", 0)):
                errors.append(f"Passage {p.id}: page PDF absente ou hors limites.")
        if p.status == "synthetic":
            errors.append(f"Passage {p.id}: contenu synthétique interdit dans ce corpus officiel.")
        warnings[p.id] = quality_flags(p.text)
        if record:
            for page in record.get("page_quality", []):
                if page.get("page") == p.page:
                    warnings[p.id].extend(page.get("flags", []))
                    if page.get("method") == "ocr":
                        warnings[p.id].append("ocr_review_required")
            warnings[p.id] = list(dict.fromkeys(warnings[p.id]))
        texts[text_digest(" ".join(p.text.casefold().split()))].append(p.id)
    for pid, count in ids.items():
        if count > 1:
            errors.append(f"Identifiant de passage dupliqué : {pid}.")
    for record in records:
        if counts[record["id"]] != record.get("passages", 0):
            errors.append(f"Document {record['id']}: nombre de passages différent du manifeste.")
    duplicate_groups = [group for group in texts.values() if len(group) > 1]
    for group in duplicate_groups:
        for pid in group:
            warnings[pid].append("duplicate_text")
    if not passages:
        errors.append("Le corpus ne contient aucun passage valide.")
    report = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "input_sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
        "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "summary": {"documents": len(records), "passages": len(passages),
                    "languages": dict(Counter(p.language for p in passages)),
                    "statuses": dict(Counter(p.status for p in passages)),
                    "flagged_passages": sum(bool(v) for v in warnings.values()),
                    "duplicate_groups": len(duplicate_groups), "errors": len(errors)},
        "documents": [{"id": r["id"], "title": r.get("title"), "url": r.get("final_url"),
                       "passages": counts[r["id"]], "pages": r.get("pages"),
                       "legal_currency": r.get("legal_currency", "not_audited"),
                       "flagged_pages": sum(bool(p.get("flags")) for p in r.get("page_quality", []))}
                      for r in records],
        "errors": errors, "warnings": {k: v for k, v in warnings.items() if v},
        "duplicate_groups": duplicate_groups,
        "scope": "Technical checks only. Human review of text, relevance and legal currency remains required.",
    }
    return passages, report


def fingerprint(p):
    return {"id": p.id, "document_id": p.document_id, "page": p.page,
            "sha256": p.sha256, "text_sha256": text_digest(p.text)}


def audit_corpus(input_path: Path, manifest_path: Path, root: Path, output_dir: Path):
    passages, report = inspect_corpus(input_path, manifest_path, root)
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError("Le dossier de revue doit être nouveau ou vide pour préserver les décisions.")
    output_dir.mkdir(parents=True, exist_ok=True)
    from .triage import build_triage, write_triage
    records = json.loads(manifest_path.read_text(encoding="utf-8"))
    triage = build_triage(passages, records, report["warnings"])
    report["triage_summary"] = triage["summary"]
    report["legal_families"] = triage["legal_families"]
    write_triage(triage, output_dir)
    (output_dir / "audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    # Snapshots bind the review to this run, even if the latest collection changes.
    (output_dir / "pending.snapshot.jsonl").write_bytes(input_path.read_bytes())
    (output_dir / "manifest.snapshot.json").write_bytes(manifest_path.read_bytes())
    decisions = [{**fingerprint(p), "decision": "pending", "comment": "",
                  "flags": report["warnings"].get(p.id, []), "text": p.text,
                  "source_url": str(p.source_url)} for p in passages]
    (output_dir / "decisions.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in decisions), encoding="utf-8")
    lines = ["# Audit du corpus documentaire", "", f"Date : {report['created_at']}", "",
             f"{len(passages)} passages, {len(report['documents'])} documents, "
             f"{len(report['errors'])} erreurs bloquantes, {report['summary']['flagged_passages']} passages signalés.", "",
             "Aucun passage n’est approuvé automatiquement. Les signaux techniques ne garantissent ni la qualité de l’OCR ni l’actualité juridique.", "",
             "## Documents", ""]
    for doc in report["documents"]:
        lines.append(f"- {doc['id']} : {doc['passages']} passages; actualité : {doc['legal_currency']}.")
    lines += ["", "## Erreurs bloquantes", ""] + (report["errors"] or ["Aucune erreur technique détectée."])
    lines += ["", "## Relecture", "",
              "Dans decisions.jsonl, passer decision de pending à approve ou reject uniquement après relecture. "
              "Compléter comment; conserver id, empreintes et text. Utiliser les snapshots avec la commande approve. "
              "Les sommaires, publicités, pages non pertinentes et doublons doivent être écartés. "
              "Le fichier passages.md contient tous les passages, y compris ceux sans signal automatique.", ""]
    (output_dir / "rapport.md").write_text("\n".join(lines), encoding="utf-8")
    review_lines = ["# Passages à relire", "", "Utiliser les identifiants pour compléter decisions.jsonl.", ""]
    for p in passages:
        review_lines += [f"## {p.id}", "", f"Document : {p.document_id} — page : {p.page or 'HTML'}", "",
                         f"Source : {p.source_url}", "", f"Signaux : {', '.join(report['warnings'].get(p.id, [])) or 'aucun'}", "",
                         *["> " + line for line in p.text.splitlines()], ""]
    (output_dir / "passages.md").write_text("\n".join(review_lines), encoding="utf-8")
    return report


def approve_decisions(input_path: Path, decisions_path: Path, output_path: Path, reviewer: str,
                      manifest_path: Path, root: Path):
    if not reviewer.strip():
        raise ValueError("Le relecteur doit être identifié.")
    log_path = output_path.with_name(output_path.name + ".review.json")
    if output_path.exists() or log_path.exists():
        raise ValueError("L’export ou son journal existe déjà; choisir un nouveau nom.")
    passages, report = inspect_corpus(input_path, manifest_path, root)
    if report["errors"]:
        raise ValueError("Audit bloquant : " + "; ".join(report["errors"][:5]))
    by_id = {p.id: p for p in passages}
    selected, seen, decisions = [], set(), []
    for line in decisions_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError("Décision non conforme.")
        pid = row.get("id")
        if pid not in by_id or pid in seen:
            raise ValueError("Identifiant de décision inconnu ou dupliqué.")
        seen.add(pid)
        p = by_id[pid]
        if any(row.get(key) != value for key, value in fingerprint(p).items()) or row.get("text", p.text) != p.text:
            raise ValueError("Décision périmée ou texte modifié : préparer une nouvelle revue.")
        if row.get("decision") not in {"pending", "approve", "reject"}:
            raise ValueError("La décision doit être pending, approve ou reject.")
        if not isinstance(row.get("comment", ""), str):
            raise ValueError("Le commentaire doit être un texte.")
        decisions.append({**fingerprint(p), "decision": row["decision"], "comment": row.get("comment", "")})
        if row["decision"] == "approve":
            selected.append(p.model_copy(update={"status": "reviewed"}).model_dump_json())
    if not selected:
        raise ValueError("Aucun passage explicitement approuvé.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = "\n".join(selected) + "\n"
    journal = {"reviewer": reviewer.strip(), "reviewed_at": datetime.now(timezone.utc).isoformat(),
               "input_sha256": report["input_sha256"], "manifest_sha256": report["manifest_sha256"],
               "decisions_sha256": hashlib.sha256(decisions_path.read_bytes()).hexdigest(),
               "output_sha256": text_digest(payload), "approved_passages": len(selected), "decisions": decisions}
    with log_path.open("x", encoding="utf-8") as f:
        json.dump(journal, f, ensure_ascii=False, indent=2)
    with output_path.open("x", encoding="utf-8", newline="\n") as f:
        f.write(payload)
    return len(selected)
