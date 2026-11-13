#!/usr/bin/env bash
# Sauvegarde PostgreSQL du backend Sawtna : pg_dump (format custom) + SHA-256,
# copie locale (7 jours) et copie hors VM dans Azure Blob (30 jours, règle de cycle de vie).
set -euo pipefail
STORAGE=sawtnabakb9dcf2a0
CONTAINER=pg-backups; DB_CTR=sawtna-staging-db-1; DIR=/var/backups/sawtna
install -d -m 700 "$DIR"
# Au démarrage de la VM (sauvegarde rattrapée), attendre que PostgreSQL soit prêt.
for i in $(seq 1 60); do docker exec "$DB_CTR" pg_isready -U sawtna -d sawtna -q 2>/dev/null && break; sleep 5; done
TS=$(date -u +%Y%m%dT%H%M%SZ); NAME="sawtna-$TS.dump"; F="$DIR/$NAME"
docker exec "$DB_CTR" pg_dump -U sawtna -d sawtna -Fc > "$F.tmp"
mv "$F.tmp" "$F"
# Le dump doit être lisible par pg_restore, sinon la sauvegarde est considérée comme échouée.
docker exec -i "$DB_CTR" pg_restore --list < "$F" > /dev/null
(cd "$DIR" && sha256sum "$NAME" > "$NAME.sha256")
TOKEN=$(curl -sf -H Metadata:true "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://storage.azure.com/" | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')
for f in "$NAME" "$NAME.sha256"; do
  curl -sf -X PUT -T "$DIR/$f" -H "Authorization: Bearer $TOKEN" -H "x-ms-version: 2021-08-06" \
    -H "x-ms-blob-type: BlockBlob" "https://$STORAGE.blob.core.windows.net/$CONTAINER/$f"
done
find "$DIR" -name 'sawtna-*.dump*' -mtime +7 -delete
logger -t sawtna-backup "OK $NAME ($(stat -c %s "$F") octets) -> $STORAGE/$CONTAINER"
echo "$F"
