#!/usr/bin/env bash
# Désalloue cette VM via son identité managée (rôle Virtual Machine Contributor limité à elle-même).
# Journalise le code HTTP et la réponse d'Azure, réessaie 3 fois.
set -uo pipefail
IMDS=http://169.254.169.254/metadata
log() { logger -t sawtna-auto-deallocate "$*"; echo "$*"; }
ID=$(curl -s --max-time 10 -H Metadata:true "$IMDS/instance/compute/resourceId?api-version=2021-02-01&format=text")
for attempt in 1 2 3; do
  TOKEN=$(curl -s --max-time 10 -H Metadata:true "$IMDS/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/" \
    | python3 -c 'import sys,json; print(json.load(sys.stdin).get("access_token",""))' 2>/dev/null)
  if [ -z "$TOKEN" ]; then log "Tentative $attempt : jeton IMDS indisponible"; sleep 20; continue; fi
  OUT=$(curl -s --max-time 60 -o /tmp/dealloc.body -w "%{http_code}" -X POST -H "Authorization: Bearer $TOKEN" \
    -H "Content-Length: 0" "https://management.azure.com${ID}/deallocate?api-version=2024-07-01")
  log "Tentative $attempt : HTTP ${OUT:-000} $(head -c 300 /tmp/dealloc.body 2>/dev/null)"
  case "$OUT" in 200|202) log "Désallocation acceptée par Azure"; exit 0;; esac
  sleep 20
done
log "ÉCHEC de la désallocation après 3 tentatives"; exit 1
