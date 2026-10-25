import json
import os
from datetime import datetime, timezone
import httpx
from sawtna.config import ROOT

questions = json.loads((ROOT / "commun/data/evaluation/questions.json").read_text(encoding="utf-8"))
rows = []
with httpx.Client(base_url=os.getenv("SAWTNA_API_URL","http://127.0.0.1:8010"),timeout=70) as client:
    for case in questions:
        response = client.post("/api/ask",json={k:case[k] for k in ("question","language")})
        response.raise_for_status()
        body = response.json()
        ids = [s["id"] for s in body["sources"]]
        rank = ids.index(case["expected"])+1 if case["expected"] in ids else None
        rows.append({**case,"retrieved":ids,"rank":rank,"model":body["embedding_model"]})
metrics = {}
for language in ("fr","ar","darija"):
    cases = [r for r in rows if r["language"]==language]
    metrics[language] = {"n":len(cases),"recall_at_4":sum(r["rank"] is not None for r in cases)/len(cases),"mrr":sum(1/r["rank"] if r["rank"] else 0 for r in cases)/len(cases)}
report = {"evaluated_at":datetime.now(timezone.utc).isoformat(),"scope":"Small authored regression set, not a general accuracy benchmark","metrics":metrics,"cases":rows}
target = ROOT / "commun/docs/verification/retrieval-evaluation.json"
target.parent.mkdir(parents=True,exist_ok=True)
target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(metrics,indent=2))
if any(m["recall_at_4"]<1 for m in metrics.values()):
    raise SystemExit(1)
