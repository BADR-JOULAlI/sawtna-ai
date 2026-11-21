import argparse
import json
import os
from pathlib import Path
import httpx
from sawtna.config import service_key
from data_engineering.review import verify_review_export

parser = argparse.ArgumentParser(description="Ingérer un export relu dans le backend.")
parser.add_argument("--input", type=Path, required=True)
parser.add_argument("--api", default=os.getenv("SAWTNA_API_URL", "http://127.0.0.1:8010"))
args = parser.parse_args()
try:
    passages = verify_review_export(args.input)
except (ValueError, OSError, json.JSONDecodeError) as exc:
    raise SystemExit(str(exc)) from exc
with httpx.Client(base_url=args.api, headers={"X-Service-Key":service_key()}, timeout=120) as client:
    for start in range(0, len(passages), 64):
        batch = [p.model_dump(mode="json") for p in passages[start:start+64]]
        response = client.post("/v1/ingest", json={"passages":batch})
        response.raise_for_status()
        print(response.json())
print(f"Ingestion terminée : {len(passages)} passages.")
