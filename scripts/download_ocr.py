"""Download a versioned Tesseract language model for local PDF OCR."""
import argparse
import hashlib
import json
import httpx
from sawtna.config import data_root

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--language", choices=["fra","ara"], default="fra")
args = parser.parse_args()
target = data_root() / "models/tessdata" / f"{args.language}.traineddata"
target.parent.mkdir(parents=True, exist_ok=True)
url = f"https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/4.1.0/{args.language}.traineddata"
response = httpx.get(url, timeout=60, follow_redirects=True)
response.raise_for_status()
if len(response.content) < 100000:
    raise SystemExit("Modèle OCR invalide.")
target.write_bytes(response.content)
target.with_suffix(".metadata.json").write_text(json.dumps({"url":url,"sha256":hashlib.sha256(response.content).hexdigest()},indent=2),encoding="utf-8")
print(f"Modèle OCR {args.language} : {len(response.content)} octets")
