"""Controlled outage test of this Compose project's Analytics service only."""
import json
import subprocess
import time
from datetime import datetime, timezone
import httpx
from sawtna.config import ROOT, admin_key

def compose(*args):
    subprocess.run(["docker","compose",*args],cwd=ROOT,check=True,capture_output=True)

with httpx.Client(base_url="http://127.0.0.1:8010",timeout=70) as client:
    before = client.get("/api/admin/summary",headers={"X-Admin-Key":admin_key()}).json()["questions"]
    try:
        compose("stop","analytics")
        response = client.post("/api/ask",json={"question":"Quels sont les conseils des communes ?","language":"fr"})
        response.raise_for_status()
        assert response.json()["answerable"]
    finally:
        compose("start","analytics")
    deadline = time.monotonic()+40
    after = None
    while time.monotonic()<deadline:
        try:
            summary = client.get("/api/admin/summary",headers={"X-Admin-Key":admin_key()})
            if summary.status_code==200:
                after=summary.json()["questions"]
                if after==before+1:
                    break
        except httpx.HTTPError:
            pass
        time.sleep(1)
    assert after==before+1, {"before":before,"after":after}
report={"tested_at":datetime.now(timezone.utc).isoformat(),"result":"passed","question_during_analytics_outage":"answered","recovered_events":after-before}
(ROOT / "commun/docs/verification/resilience.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps(report,indent=2))
