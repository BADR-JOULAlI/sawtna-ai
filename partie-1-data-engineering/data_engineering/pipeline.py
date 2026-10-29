"""Versioned, bounded official-source collector, PDF/HTML extraction and RAG export."""
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
import os
import time
import unicodedata
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup
from sawtna.config import ROOT, data_root
from sawtna.contracts import Passage
from .quality import needs_ocr, quality_flags

ALLOWED_HOSTS = {"maroc.ma", "www.maroc.ma", "sgg.gov.ma", "www.sgg.gov.ma", "www.chambredesrepresentants.ma", "www.cour-constitutionnelle.ma"}
MAX_BYTES = 25 * 1024 * 1024


def allowed_url(url: str):
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS or parsed.username or parsed.password or parsed.port not in (None, 443):
        raise ValueError("URL hors de la liste institutionnelle HTTPS autorisée.")


def clean(text):
    return re.sub(r"[ \t]+", " ", unicodedata.normalize("NFC", text).replace("\u00a0", " ")).strip()


def extract_html(content: bytes) -> list[tuple[int | None, str]]:
    soup = BeautifulSoup(content, "html.parser")
    for element in soup.select("script,style,nav,footer,header,aside,form,.visually-hidden"):
        element.decompose()
    region = soup.select_one("article") or soup.select_one("main") or soup.body or soup
    blocks = [clean(el.get_text(" ", strip=True)) for el in region.select("h1,h2,h3,p,li")]
    if not blocks:
        blocks = [clean(region.get_text(" ", strip=True))]
    return [(None, "\n\n".join(dict.fromkeys(block for block in blocks if len(block) >= 25)))]


def extract_pdf(path: Path, ocr=False, language="fr", details=None):
    if ocr and language == "ar":
        from .ocr import extract_arabic_pdf
        return [(page, clean(text)) for page, text in extract_arabic_pdf(path, details=details)]
    from pypdf import PdfReader
    reader = PdfReader(path)
    pages = [(i + 1, clean(page.extract_text(extraction_mode="layout") or "")) for i, page in enumerate(reader.pages)]
    methods = ["text"] * len(pages)
    if ocr and any(needs_ocr(text) for _, text in pages):
        import pymupdf as fitz
        tessdata = str(Path(os.getenv("SAWTNA_OCR_TESSDATA", str(data_root() / "models/tessdata"))).resolve())
        lang = "ara" if language == "ar" else "fra"
        if not (Path(tessdata) / f"{lang}.traineddata").exists():
            raise ValueError(f"Modèle OCR absent : lancez python commun/scripts/download_ocr.py --language {lang}")
        with fitz.open(path) as doc:
            for i, (_, text) in enumerate(pages):
                if needs_ocr(text):
                    page = doc[i]
                    textpage = page.get_textpage_ocr(language=lang, dpi=180, full=True, tessdata=tessdata)
                    pages[i] = (i + 1, clean(page.get_text(textpage=textpage)))
                    methods[i] = "ocr"
    if details is not None:
        details.extend({"page": page, "method": methods[i], "flags": quality_flags(text) +
                        (["ocr_review_required"] if methods[i] == "ocr" else [])}
                       for i, (page, text) in enumerate(pages))
    return pages


def split_passages(text: str, max_chars=1600, overlap=180):
    if max_chars <= overlap or overlap < 0:
        raise ValueError("Taille de passage invalide.")
    text = clean(text)
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            boundary = max(text.rfind(". ", start + max_chars // 2, end), text.rfind("\n", start + max_chars // 2, end))
            if boundary > start:
                end = boundary + 1
        chunk = text[start:end].strip()
        if len(chunk) >= 30:
            yield chunk
        if end >= len(text):
            break
        start = max(start + 1, end - overlap)


def _fetch_once(source, client):
    url = source["url"]
    allowed_url(url)
    # Validate each redirect; never silently follow a redirect to an untrusted host.
    for _ in range(5):
        with client.stream("GET", url) as response:
            if response.is_redirect:
                from urllib.parse import urljoin
                url = urljoin(url, response.headers["location"])
                allowed_url(url)
                continue
            response.raise_for_status()
            content = bytearray()
            for part in response.iter_bytes():
                content.extend(part)
                if len(content) > MAX_BYTES:
                    raise ValueError("Document supérieur à 25 Mo.")
            content = bytes(content)
            kind = "pdf" if content.startswith(b"%PDF") else "html"
            if source.get("format") == "pdf" and kind != "pdf":
                raise ValueError("Le serveur n'a pas renvoyé de PDF.")
            if kind == "html" and not any(mark in content[:5000].lower() for mark in (b"<html", b"<!doctype")):
                raise ValueError("Contenu HTML/PDF non reconnu.")
            return content, kind, url
    raise ValueError("Trop de redirections.")


def fetch(source, client, attempts=3):
    """Retry transient network errors and 429/5xx; never retry invalid content/URLs."""
    if not 1 <= attempts <= 5:
        raise ValueError("Nombre de tentatives invalide.")
    for attempt in range(attempts):
        try:
            return _fetch_once(source, client)
        except (httpx.TransportError, httpx.HTTPStatusError) as exc:
            if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code not in {429, 500, 502, 503, 504}:
                raise
            if attempt + 1 == attempts:
                raise
            time.sleep(2 ** attempt)


def verified_raw(root: Path, record: dict) -> Path:
    """Only load the exact immutable file within the selected corpus raw directory."""
    if not isinstance(record.get("path"), str) or not re.fullmatch(r"[a-f0-9]{64}", str(record.get("sha256", ""))):
        raise ValueError("Chemin ou empreinte manquant dans le manifeste.")
    raw_root = (root / "raw").resolve()
    target = (root / record["path"]).resolve()
    if not target.is_relative_to(raw_root):
        raise ValueError("Chemin du document hors du répertoire raw.")
    if hashlib.sha256(target.read_bytes()).hexdigest() != record["sha256"]:
        raise ValueError("Empreinte SHA-256 du document incohérente.")
    return target


def collect(catalog: Path, root: Path | None = None, ocr=False, reuse_manifest: Path | None = None,
            download_missing=False):
    from pypdf.errors import PdfReadError
    root = root or data_root()
    if download_missing and not reuse_manifest:
        raise ValueError("--download-missing nécessite --reuse-manifest.")
    sources = json.loads(catalog.read_text(encoding="utf-8"))
    ids = [s["id"] for s in sources]
    if len(set(ids)) != len(ids):
        raise ValueError("Identifiants de sources dupliqués dans le catalogue.")
    cached = {}
    if reuse_manifest:
        previous = json.loads(reuse_manifest.read_text(encoding="utf-8"))
        cached = {r["id"]: r for r in previous}
        if len(cached) != len(previous):
            raise ValueError("Identifiants dupliqués dans le manifeste.")
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    records, passages = [], []
    with httpx.Client(timeout=40, follow_redirects=False, headers={"User-Agent": "SawtnaAI/1.0 educational document collection"}) as client:
        for source in sources:
            now = datetime.now(timezone.utc).isoformat()
            record = {**source, "collected_at": now, "processed_at": now, "status": "pending_review"}
            try:
                if not re.fullmatch(r"[a-zA-Z0-9_.-]{1,100}", source["id"]) or source["id"] in {".", ".."}:
                    raise ValueError("Identifiant documentaire invalide.")
                prior = cached.get(source["id"])
                reused = reuse_manifest is not None and prior is not None
                if reuse_manifest and not prior and not download_missing:
                    raise ValueError("Source absente du manifeste; téléchargement non autorisé en mode hors ligne.")
                if reused:
                    if prior.get("url") != source["url"]:
                        raise ValueError("Source absente du manifeste ou URL modifiée.")
                    target = verified_raw(root, prior)
                    record["collected_at"] = prior.get("collected_at")
                    content = target.read_bytes()
                    kind = "pdf" if content.startswith(b"%PDF") else "html"
                    if source.get("format") == "pdf" and kind != "pdf":
                        raise ValueError("L’original conservé n’est pas un PDF.")
                    final_url = prior.get("final_url", source["url"])
                    allowed_url(final_url)
                else:
                    content, kind, final_url = fetch(source, client)
                digest = hashlib.sha256(content).hexdigest()
                target = root / "raw" / source["id"] / f"{digest}.{kind}"
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists():
                    target.write_bytes(content)
                page_quality = []
                pages = extract_pdf(target, ocr=ocr, language=source["language"], details=page_quality) if kind == "pdf" else extract_html(content)
                source_passages = []
                count = 0
                for page, text in pages:
                    for index, chunk in enumerate(split_passages(text)):
                        # The hash includes the page and chunk to preserve exact citation provenance.
                        part_hash = hashlib.sha256(f"{digest}|{page}|{index}|{chunk}".encode()).hexdigest()
                        match = re.search(r"(?:Article|ARTICLE)\s+(\d+)", chunk)
                        passage = Passage(id=part_hash[:40], document_id=source["id"], title=source["title"],
                            source_url=final_url, language=source["language"], text=chunk,
                            page=page, section=f"Article {match[1]}" if match else "", sha256=digest)
                        source_passages.append(passage.model_dump(mode="json"))
                        count += 1
                record.update(download_status="reused" if reused else "downloaded", sha256=digest, bytes=len(content),
                    path=target.relative_to(root).as_posix(), final_url=final_url, pages=len(pages), passages=count,
                    low_text_pages=sum(len(t) < 60 for _, t in pages),
                    extraction_status="needs_review" if any(p["flags"] for p in page_quality) or any(needs_ocr(t) for _, t in pages) else "extracted",
                    ocr_requested=ocr, page_quality=page_quality)
                passages.extend(source_passages)
            except (httpx.HTTPError, ValueError, OSError, PdfReadError, RuntimeError) as exc:
                record.update(download_status="failed", error=str(exc))
            records.append(record)
    manifest_dir = root / "manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    for name in (f"{run_id}.json", "latest.json"):
        (manifest_dir / name).write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    processed = root / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    # Persist each run; latest is a convenience pointer, never the sole version.
    serialized = "".join(json.dumps(p, ensure_ascii=False) + "\n" for p in passages)
    for name in (f"{run_id}.jsonl", "pending.jsonl"):
        (processed / name).write_text(serialized, encoding="utf-8")
    return records


def export_reviewed(input_path: Path, output_path: Path, document_ids: set[str]):
    selected = []
    for line in input_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        passage = Passage.model_validate_json(line)
        if passage.document_id in document_ids:
            passage.status = "reviewed"
            selected.append(passage.model_dump_json())
    if not selected:
        raise ValueError("Aucun passage pour les documents demandés.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(selected) + "\n", encoding="utf-8")
    return len(selected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    collector = sub.add_parser("collect")
    collector.add_argument("--catalog", type=Path, default=ROOT / "partie-1-data-engineering/sources.json")
    collector.add_argument("--ocr", action="store_true", help="OCR local des pages numérisées, modèle tessdata requis.")
    collector.add_argument("--reuse-manifest", type=Path, help="Réextraire les originaux SHA-256 vérifiés sans téléchargement.")
    collector.add_argument("--download-missing", action="store_true",
                           help="Avec --reuse-manifest : télécharger uniquement les nouvelles sources du catalogue.")
    audit_parser = sub.add_parser("audit", help="Audit technique et préparation de la revue humaine.")
    audit_parser.add_argument("--input", type=Path, default=data_root() / "processed/pending.jsonl")
    audit_parser.add_argument("--manifest", type=Path, default=data_root() / "manifests/latest.json")
    audit_parser.add_argument("--output-dir", type=Path)
    review = sub.add_parser("approve", help="Après relecture humaine uniquement.")
    review.add_argument("--input", type=Path, default=data_root() / "processed/pending.jsonl")
    review.add_argument("--output", type=Path, default=data_root() / "processed/reviewed.jsonl")
    selection = review.add_mutually_exclusive_group(required=True)
    selection.add_argument("--document", action="append", help="Ancien mode : document entier effectivement relu.")
    selection.add_argument("--decisions", type=Path, help="Décisions explicites passage par passage après audit.")
    review.add_argument("--reviewer", help="Nom du relecteur, obligatoire avec --decisions.")
    review.add_argument("--manifest", type=Path, default=data_root() / "manifests/latest.json")
    args = parser.parse_args()
    if args.command == "audit":
        from .review import audit_corpus
        out = args.output_dir or data_root() / "reviews" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        report = audit_corpus(args.input, args.manifest, data_root(), out)
        print(json.dumps({"output": str(out), **report["summary"]}, ensure_ascii=True, indent=2))
        if report["errors"]:
            raise SystemExit(1)
        return
    if args.command == "approve":
        if args.decisions:
            from .review import approve_decisions
            if not args.reviewer:
                parser.error("--reviewer est obligatoire avec --decisions.")
            count = approve_decisions(args.input, args.decisions, args.output, args.reviewer, args.manifest, data_root())
            print(f"{count} passages approuvés; journal : {args.output}.review.json")
            return
        print(f"{export_reviewed(args.input, args.output, set(args.document))} passages approuvés.")
        return
    if args.download_missing and not args.reuse_manifest:
        parser.error("--download-missing nécessite --reuse-manifest.")
    records = collect(args.catalog, ocr=args.ocr, reuse_manifest=args.reuse_manifest,
                      download_missing=args.download_missing)
    for record in records:
        print(f"{record['id']}: {record['download_status']} ({record.get('passages', 0)} passages)")
    if any(record["download_status"] == "failed" for record in records):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
