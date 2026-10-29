"""Explainable FR/AR review ordering. Never edits, rejects or approves a passage."""
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from .quality import text_digest


def search_text(text: str) -> str:
    # Matching only: original passages, punctuation and citation hashes stay intact.
    return " ".join("".join(c for c in unicodedata.normalize("NFKD", text.casefold())
                            if unicodedata.category(c) != "Mn" and c != "ـ").split())


RULES = {
    "elections_vote": r"\b(?:electoral\w*|election\w*|scrutin\w*|suffrage\w*|vot(?:e|es|er|ant|ants))\b|"
                      r"\b[وفبلك]?(?:ال)?(?:انتخاب\w*|اقتراع\w*|تصويت\w*|ناخب\w*)\b",
    "listes_electorales": r"\blistes? electorales?\b|\b(?:ال)?(?:لوايح|لايحة) (?:ال)?انتخاب\w*\b",
    "candidatures": r"\b(?:candidat\w*|eligibilite|ineligibilite)\b|"
                    r"\b[وفبلك]?(?:ال)?(?:ترشيح\w*|ترشح\w*|مترشح\w*|مرشح\w*)\b",
    "campagne": r"\bcampagne\w* electorale\w*\b|\b(?:ال)?حمل\w* (?:ال)?انتخاب\w*\b",
    "institutions": r"\b(?:constitution\w*|parlement\w*|chambre des representants|"
                    r"chambre des conseillers|cour constitutionnelle)\b|"
                    r"\b(?:ال)?دستور\w*\b|\bمجلس (?:النواب|المستشارين)\b|\bالمحكمة الدستورية\b",
}
LABELS = {
    "electoral_terms": "Vocabulaire électoral détecté",
    "institutional_context": "Contexte institutionnel détecté",
    "unclassified": "Sans indice lexical : à examiner",
}


def classify(text: str) -> dict:
    normalized = search_text(text)
    evidence = {name: sorted(set(re.findall(pattern, normalized)))
                for name, pattern in RULES.items()}
    evidence = {name: terms for name, terms in evidence.items() if terms}
    category = ("electoral_terms" if set(evidence) - {"institutions"} else
                "institutional_context" if evidence else "unclassified")
    return {"category": category, "evidence": evidence}


def build_triage(passages, records, warnings):
    rows, doc_counts = [], defaultdict(Counter)
    for p in passages:
        signals = classify(p.text)
        flags = warnings.get(p.id, [])
        # Technical warnings first, then electoral vocabulary, then context.
        priority = 0 if flags else {"electoral_terms": 1, "institutional_context": 2, "unclassified": 3}[signals["category"]]
        rows.append({"id": p.id, "document_id": p.document_id, "page": p.page,
                     "language": p.language, "text_sha256": text_digest(p.text),
                     "source_url": str(p.source_url), "priority": priority,
                     "flags": flags, **signals})
        doc_counts[p.document_id][signals["category"]] += 1
    # Preserve input order within each priority; no deduplication discards provenance.
    rows.sort(key=lambda row: row["priority"])
    families = defaultdict(list)
    documents = []
    for record in records:
        documents.append({"id": record["id"], "language": record.get("language"),
                          "legal_currency": record.get("legal_currency", "not_audited"),
                          "counts": dict(doc_counts[record["id"]])})
        if record.get("legal_family"):
            families[record["legal_family"]].append({"id": record["id"],
                                                     "role": record.get("document_role", "unknown"),
                                                     "language": record.get("language")})
    return {"summary": dict(Counter(row["category"] for row in rows)),
            "documents": documents, "legal_families": dict(families), "passages": rows,
            "scope": "Lexical review ordering only. No automatic relevance, legal currency or approval decision."}


def write_triage(triage, output_dir: Path):
    (output_dir / "triage.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in triage["passages"]), encoding="utf-8")
    lines = ["# Ordre de relecture proposé", "",
             "Classement lexical explicable en français et en arabe. Tous les passages sont conservés. "
             "L’absence de mot-clé ne signifie pas qu’un passage est hors sujet. "
             "Ce classement ne modifie aucune décision dans decisions.jsonl.", "",
             "Les passages signalés par l’audit arrivent d’abord, puis ceux contenant du vocabulaire électoral, "
             "le contexte institutionnel et les passages sans indice. Les mots-clés sont normalisés uniquement pour la recherche.", "",
             "## Couverture par document", "",
             "| Document | Électoral | Institutionnel | Sans indice | Actualité à vérifier |",
             "|---|---:|---:|---:|---|"]
    for doc in triage["documents"]:
        counts = doc["counts"]
        lines.append(f"| {doc['id']} | {counts.get('electoral_terms', 0)} | "
                     f"{counts.get('institutional_context', 0)} | {counts.get('unclassified', 0)} | {doc['legal_currency']} |")
    lines += ["", "## Textes à comparer", "",
              "Les familles ci-dessous sont renseignées dans le catalogue. Une liste de modifications "
              "n’est pas un texte consolidé et son exhaustivité doit être vérifiée.", ""]
    for family, members in triage["legal_families"].items():
        lines.append(f"### {family}")
        lines += ["", *[f"- {m['id']} ({m['language']}) : {m['role']}" for m in members], ""]
    lines += ["## File de relecture", ""]
    for row in triage["passages"]:
        terms = "; ".join(f"{key} : {', '.join(values)}" for key, values in row["evidence"].items()) or "aucun indice lexical"
        lines += [f"- [{row['id']}](passages.md#{row['id']}) — {row['document_id']}, "
                  f"page {row['page'] or 'HTML'}, {row['language']} — {LABELS[row['category']]}. "
                  f"Signaux : {', '.join(row['flags']) or 'aucun'}. Indices : {terms}."]
    (output_dir / "priorites.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
