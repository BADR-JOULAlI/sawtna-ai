"""Verify a reviewed lot against its review log before ingestion."""
import hashlib, json, sys
from pathlib import Path
from sawtna.contracts import Passage

lot = Path(sys.argv[1]); log = Path(str(lot) + ".review.json")
data = lot.read_bytes(); review = json.loads(log.read_text(encoding="utf-8"))
ok = True
def check(cond, msg):
    global ok
    print(("OK   " if cond else "FAIL ") + msg); ok &= cond
check(hashlib.sha256(data).hexdigest() == review["output_sha256"], "file hash == output_sha256 in review log")
passages = [Passage.model_validate_json(l) for l in data.decode("utf-8").splitlines() if l.strip()]
check(True, f"{len(passages)} passage(s) valid against Passage contract")
approved = {d["id"]: d for d in review["decisions"] if d["decision"] == "approve"}
check(len(passages) == review["approved_passages"] == len(approved), "passage count == approved count")
for p in passages:
    d = approved.get(p.id)
    check(d is not None, f"{p.id} is approved in the log")
    if d:
        check(hashlib.sha256(p.text.encode()).hexdigest() == d["text_sha256"], f"{p.id} text_sha256 matches")
        check(p.sha256 == d["sha256"] and p.document_id == d["document_id"] and p.page == d["page"], f"{p.id} source fingerprint matches")
    check(p.status == "reviewed", f"{p.id} status == reviewed")
sys.exit(0 if ok else 1)
