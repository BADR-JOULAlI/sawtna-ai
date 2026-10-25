"""Live HTTP smoke tests; requires the local stack to be running."""
import json
import os
import uuid
from datetime import datetime, timezone
import httpx
from sawtna.config import ROOT, admin_key, service_key

api = os.getenv("SAWTNA_API_URL","http://127.0.0.1:8010")
checks = []
with httpx.Client(base_url=api, timeout=70) as client:
    health = client.get("/health").json()
    assert health["status"] == "ok", health
    checks.append("backend and dependencies healthy")
    docs = client.get("/api/documents").json()
    assert docs["passages"] >= 6
    for language,question in [("fr","Comment sont élus les membres de la Chambre des représentants ?"),("ar","كيف يتم انتخاب أعضاء مجلس النواب؟"),("darija","Kifach kaytntakhbo nowab?")]:
        response = client.post("/api/ask",json={"question":question,"language":language})
        response.raise_for_status()
        assert "constitution:62" in [s["id"] for s in response.json()["sources"]]
        checks.append(f"retrieval with citations: {language}")
    empty = client.post("/api/ask",json={"question":"Quel est le prix du carburant demain ?"}).json()
    assert not empty["answerable"] and not empty["sources"]
    checks.append("out-of-corpus abstention")
    assert client.post("/api/ask",json={"question":"  "}).status_code == 422
    assert client.get("/api/admin/summary").status_code == 401
    checks.append("input validation and admin authentication")
    quiz = client.post("/api/quiz/submit",json={"answers":{"vote":0,"chambers":1,"mandate":2,"territories":0}}).json()
    assert quiz["score"] == 100
    checks.append("server-side quiz grading")
    summary = client.get("/api/admin/summary",headers={"X-Admin-Key":admin_key()})
    summary.raise_for_status()
    assert summary.json()["questions"] >= 4
    checks.append("live analytics")
with httpx.Client(timeout=10) as client:
    assert client.get("http://127.0.0.1:5175").status_code == 200
    assert client.get("http://127.0.0.1:8012/dashboard").status_code == 200
checks.append("both frontend entry points")
report = {"tested_at":datetime.now(timezone.utc).isoformat(),"database":health["database"],"passed":checks,"total":len(checks)}
out = ROOT / "commun/docs/verification/smoke.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(report,ensure_ascii=True,indent=2))
