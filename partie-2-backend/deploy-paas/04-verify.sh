#!/usr/bin/env bash
# Vérifie le déploiement : /health, /api/documents, puis option --ingest pour charger le lot relu.
. "$(dirname "$0")/_common.sh"
. "$DIR/.secrets/api-url"

echo "== GET $API_URL/health (1er appel lent possible : démarrage à froid depuis 0 réplique)"
for i in 1 2 3 4 5 6; do
  out=$(curl -s --max-time 60 "$API_URL/health") && [ -n "$out" ] && break
  sleep 10
done
echo "$out"
echo "$out" | grep -q '"database":"postgresql+pgvector"' || { echo "ÉCHEC : base PostgreSQL non utilisée"; exit 1; }

echo "== GET $API_URL/api/documents"
curl -s --max-time 60 "$API_URL/api/documents"; echo

if [ "${1:-}" = --ingest ]; then
  win() { command -v cygpath >/dev/null && cygpath -m "$1" || echo "$1"; }
  LOT="$(win "${2:?Usage : ./04-verify.sh --ingest chemin/du/lot.jsonl}")"
  PY="$REPO/.venv/Scripts/python.exe"
  echo "== Vérification puis ingestion de $LOT"
  "$PY" "$(win "$DIR/verify_lot.py")" "$LOT"
  SAWTNA_SERVICE_KEY="$SAWTNA_SERVICE_KEY" "$PY" "$REPO/commun/scripts/ingest.py" --input "$LOT" --api "$API_URL"
  curl -s --max-time 60 "$API_URL/api/documents"; echo
fi
