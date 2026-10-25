import json
from sawtna.config import ROOT
from sawtna.contracts import Passage
from sawtna.backend import app as backend
from sawtna.nlp import app as nlp
from sawtna.analytics import app as analytics

target = ROOT / "commun/packages/contracts"
target.mkdir(parents=True,exist_ok=True)
for name, schema in [("passage.schema",Passage.model_json_schema()),("backend.openapi",backend.openapi()),("nlp.openapi",nlp.openapi()),("analytics.openapi",analytics.openapi())]:
    (target / f"{name}.json").write_text(json.dumps(schema,ensure_ascii=False,indent=2),encoding="utf-8")
print("Contrats JSON Schema / OpenAPI exportés.")
