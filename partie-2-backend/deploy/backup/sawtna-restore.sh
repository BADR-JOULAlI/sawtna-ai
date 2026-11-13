#!/usr/bin/env bash
# Restaure une sauvegarde dans une base PostgreSQL.
# Usage : sawtna-restore.sh <fichier.dump | nom-du-blob | latest> [base-cible]
#   base-cible par défaut : sawtna_restore_test (la base de production n'est pas touchée).
#   Restaurer la production : sawtna-restore.sh latest sawtna --i-know
set -euo pipefail
STORAGE=sawtnabakb9dcf2a0
CONTAINER=pg-backups; DB_CTR=sawtna-staging-db-1; DIR=/var/backups/sawtna
SRC="${1:?fichier, blob ou latest}"; TARGET="${2:-sawtna_restore_test}"
if [ "$TARGET" = sawtna ] && [ "${3:-}" != --i-know ]; then
  echo "Refus : restaurer la base de production exige --i-know." >&2; exit 2; fi
TOKEN=$(curl -sf -H Metadata:true "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://storage.azure.com/" | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')
H=(-H "Authorization: Bearer $TOKEN" -H "x-ms-version: 2021-08-06")
URL="https://$STORAGE.blob.core.windows.net/$CONTAINER"
if [ "$SRC" = latest ]; then
  SRC=$(curl -sf "${H[@]}" "$URL?restype=container&comp=list&prefix=sawtna-" | grep -o '<Name>[^<]*\.dump</Name>' | sed 's/<[^>]*>//g' | sort | tail -1)
  echo "Dernière sauvegarde hors VM : $SRC"
fi
if [ -f "$SRC" ]; then F="$SRC"; else
  WORK=$(mktemp -d); F="$WORK/$SRC"
  curl -sf "${H[@]}" "$URL/$SRC" -o "$F"; curl -sf "${H[@]}" "$URL/$SRC.sha256" -o "$F.sha256"
  (cd "$WORK" && sha256sum -c "$SRC.sha256")
fi
if [ "$TARGET" = sawtna ]; then docker stop sawtna-staging-caddy-1 sawtna-staging-backend-1 >/dev/null; fi
docker exec "$DB_CTR" psql -U sawtna -d postgres -v ON_ERROR_STOP=1 -q \
  -c "DROP DATABASE IF EXISTS $TARGET WITH (FORCE);" -c "CREATE DATABASE $TARGET;"
docker exec -i "$DB_CTR" pg_restore -U sawtna -d "$TARGET" --no-owner --exit-on-error < "$F"
if [ "$TARGET" = sawtna ]; then docker start sawtna-staging-backend-1 sawtna-staging-caddy-1 >/dev/null; fi
docker exec "$DB_CTR" psql -U sawtna -d "$TARGET" -tAc "SELECT 'passages restaurés: ' || count(*) FROM passages"
