"""Versioned, bounded official-source collector, PDF/HTML extraction and RAG export."""
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
import os
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup
from sawtna.config import ROOT, data_root
from sawtna.contracts import Passage

ALLOWED_HOSTS = {"maroc.ma", "www.maroc.ma", "sgg.gov.ma", "www.sgg.gov.ma", "www.chambredesrepresentants.ma", "www.cour-constitutionnelle.ma"}
MAX_BYTES = 25 * 1024 * 1024


def allowed_url(url: str):
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS or parsed.username or parsed.password or parsed.port not in (None, 443):
        raise ValueError("URL hors de la liste institutionnelle HTTPS autorisée.")


def clean(text):
    return re.sub(r"[ \t]+", " ", text.replace("\x00", "")).strip()


def extract_html(content: bytes) -> list[tuple[int | None, str]]:
    soup = BeautifulSoup(content, "html.parser")
    for element in soup.select("script,style,nav,footer,header,aside,form,.visually-hidden"):
        element.decompose()
    region = soup.select_one("article") or soup.select_one("main") or soup.body or soup
    blocks = [clean(el.get_text(" ", strip=True)) for el in region.select("h1,h2,h3,p,li")]
    if not blocks:
        blocks = [clean(region.get_text(" ", strip=True))]
    return [(None, "\n\n".join(dict.fromkeys(block for block in blocks if len(block) >= 25)))]


def extract_pdf(path: Path, ocr=False, language="fr"):
    from pypdf import PdfReader
    reader = PdfReader(path)
    pages = [(i + 1, clean(page.extract_text(extraction_mode="layout") or "")) for i, page in enumerate(reader.pages)]
    if ocr and any(len(text) < 60 for _, text in pages):
        import pymupdf as fitz
        tessdata = str(Path(os.getenv("SAWTNA_OCR_TESSDATA", str(data_root() / "models/tessdata"))).resolve())
        lang = "ara" if language == "ar" else "fra"
        if not (Path(tessdata) / f"{lang}.traineddata").exists():
            raise ValueError(f"Modèle OCR absent : lancez python commun/scripts/download_ocr.py --language {lang}")
        with fitz.open(path) as doc:
            for i, (_, text) in enumerate(pages):
                if len(text) < 60:
                    page = doc[i]
                    textpage = page.get_textpage_ocr(language=lang, dpi=180, full=True, tessdata=tessdata)
                    pages[i] = (i + 1, clean(page.get_text(textpage=textpage)))
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


def fetch(source, client):
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


def collect(catalog: Path, root: Path | None = None, ocr=False):
    root = root or data_root()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    records, passages = [], []
    with httpx.Client(timeout=40, follow_redirects=False, headers={"User-Agent": "SawtnaAI/1.0 educational document collection"}) as client:
        for source in json.loads(catalog.read_text(encoding="utf-8")):
            record = {**source, "collected_at": datetime.now(timezone.utc).isoformat(), "status": "pending_review"}
            try:
                if not re.fullmatch(r"[a-zA-Z0-9_.-]{1,100}", source["id"]) or source["id"] in {".", ".."}:
                    raise ValueError("Identifiant documentaire invalide.")
                content, kind, final_url = fetch(source, client)
                digest = hashlib.sha256(content).hexdigest()
                target = root / "raw" / source["id"] / f"{digest}.{kind}"
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists():
                    target.write_bytes(content)
                pages = extract_pdf(target, ocr=ocr, language=source["language"]) if kind == "pdf" else extract_html(content)
                count = 0
                for page, text in pages:
                    for index, chunk in enumerate(split_passages(text)):
                        # The hash includes the page and chunk to preserve exact citation provenance.
                        part_hash = hashlib.sha256(f"{digest}|{page}|{index}|{chunk}".encode()).hexdigest()
                        match = re.search(r"(?:Article|ARTICLE)\s+(\d+)", chunk)
                        passage = Passage(id=part_hash[:40], document_id=source["id"], title=source["title"],
                            source_url=final_url, language=source["language"], text=chunk,
                            page=page, section=f"Article {match[1]}" if match else "", sha256=digest)
                        passages.append(passage.model_dump(mode="json"))
                        count += 1
                record.update(download_status="downloaded", sha256=digest, bytes=len(content),
                    path=target.relative_to(root).as_posix(), final_url=final_url, pages=len(pages), passages=count,
                    low_text_pages=sum(len(t) < 60 for _, t in pages),
                    extraction_status="ocr_required" if any(len(t) < 60 for _, t in pages) else "extracted",
                    ocr_requested=ocr)
            except (httpx.HTTPError, ValueError, OSError) as exc:
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
    review = sub.add_parser("approve", help="Après relecture humaine uniquement.")
    review.add_argument("--input", type=Path, default=data_root() / "processed/pending.jsonl")
    review.add_argument("--output", type=Path, default=data_root() / "processed/reviewed.jsonl")
    review.add_argument("--document", action="append", required=True)
    args = parser.parse_args()
    if args.command == "approve":
        print(f"{export_reviewed(args.input, args.output, set(args.document))} passages approuvés.")
        return
    records = collect(args.catalog, ocr=args.ocr)
    for record in records:
        print(f"{record['id']}: {record['download_status']} ({record.get('passages', 0)} passages)")
    if any(record["download_status"] == "failed" for record in records):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
