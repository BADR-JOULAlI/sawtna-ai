#!/usr/bin/env bash
# Test de restauration : restaure la dernière sauvegarde HORS VM dans une base séparée,
# compare avec la production, puis démarre un backend temporaire sur la base restaurée.
set -euo pipefail
DB_CTR=sawtna-staging-db-1; ENV=/home/azureuser/sawtna-staging/.env
q() { docker exec "$DB_CTR" psql -U sawtna -d "$1" -tAc "$2"; }
FP="SELECT count(*) || ' passages, empreinte ' || md5(string_agg(id || payload || embedding || model, '|' ORDER BY id)) FROM passages"
/usr/local/bin/sawtna-restore.sh latest sawtna_restore_test
PROD=$(q sawtna "$FP"); REST=$(q sawtna_restore_test "$FP")
echo "Production : $PROD"; echo "Restaurée  : $REST"
[ "$PROD" = "$REST" ] && echo "COMPARAISON OK : contenu identique" || { echo "ÉCART entre production et restauration"; exit 1; }
set -a; . "$ENV"; set +a
docker rm -f sawtna-restore-check >/dev/null 2>&1 || true
docker run -d --name sawtna-restore-check --network sawtna-staging_default \
  -e SAWTNA_SERVICE=backend -e SAWTNA_SERVICE_KEY="$SAWTNA_SERVICE_KEY" -e SAWTNA_ADMIN_KEY="$SAWTNA_ADMIN_KEY" \
  -e SAWTNA_BACKEND_DATABASE_URL="postgresql://sawtna:$POSTGRES_PASSWORD@db:5432/sawtna_restore_test" \
  -e SAWTNA_NLP_URL=http://nlp:8000 -e SAWTNA_ANALYTICS_URL=http://analytics.invalid:8000 sawtna-app:staging >/dev/null
for i in $(seq 1 30); do docker exec sawtna-restore-check python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" 2>/dev/null && break; sleep 2; done
docker exec -i sawtna-restore-check python - <<'PY'
import json, urllib.request
base = "http://localhost:8000"
print("Backend sur base restaurée /health :", json.load(urllib.request.urlopen(base + "/health"))["database"])
docs = json.load(urllib.request.urlopen(base + "/api/documents"))
print("Documents servis :", docs["total"], "| passages :", docs["passages"])
req = urllib.request.Request(base + "/api/ask", data=json.dumps({"question": "Quand a eu lieu le référendum constitutionnel de 1962 ?"}).encode(), headers={"Content-Type": "application/json"})
ans = json.load(urllib.request.urlopen(req))
print("Question test -> source :", [s["document_id"] for s in ans["sources"][:2]])
PY
docker rm -f sawtna-restore-check >/dev/null
q postgres "DROP DATABASE sawtna_restore_test WITH (FORCE);" >/dev/null
echo "TEST DE RESTAURATION RÉUSSI ($(date -u +%FT%TZ))"
