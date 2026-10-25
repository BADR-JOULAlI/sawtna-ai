"""Reindex the six shipped reference excerpts without deleting other documents."""
import hashlib
import json
import os
import httpx
from sawtna.config import ROOT, service_key

passages = json.loads((ROOT / "commun/data/seed/foundation.json").read_text(encoding="utf-8"))
for p in passages:
    p["sha256"] = hashlib.sha256(p["text"].encode()).hexdigest()
response = httpx.post(os.getenv("SAWTNA_API_URL","http://127.0.0.1:8010")+"/v1/ingest",
    headers={"X-Service-Key":service_key()},json={"passages":passages},timeout=120)
response.raise_for_status()
print(response.json())
