#!/usr/bin/env bash
# Chargé par tous les scripts : CLI Azure, paramètres et secrets.
set -euo pipefail
export MSYS_NO_PATHCONV=1   # Git Bash : ne pas réécrire les chemins /subscriptions/... passés à az
AZ="${AZ:-/c/Program Files/Microsoft SDKs/Azure/CLI2/wbin/az.cmd}"
az() { "$AZ" "$@"; }

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SECRETS="$DIR/.secrets/paas.env"
OLD_SECRETS="$DIR/../deploy/.secrets/staging.env"
REPO="$(cd "$DIR/../.." && pwd)"
# az.cmd et docker sont des exécutables Windows : chemin C:/... au lieu de /c/...
command -v cygpath >/dev/null && REPO="$(cygpath -m "$REPO")"

. "$DIR/config.env"

if [ ! -f "$SECRETS" ]; then
  mkdir -p "$DIR/.secrets"
  # Réutilise les clés de la VM de staging (le script d'ingestion et le frontend les connaissent déjà).
  SK=""; AK=""
  if [ -f "$OLD_SECRETS" ]; then
    SK=$(grep '^SAWTNA_SERVICE_KEY=' "$OLD_SECRETS" | cut -d= -f2-)
    AK=$(grep '^SAWTNA_ADMIN_KEY=' "$OLD_SECRETS" | cut -d= -f2-)
  fi
  umask 077
  cat > "$SECRETS" <<EOF
ACR=$ACR
PG_SERVER=$PG_SERVER
PG_PASSWORD=Sw-$(openssl rand -hex 16)
SAWTNA_SERVICE_KEY=${SK:-$(openssl rand -hex 32)}
SAWTNA_ADMIN_KEY=${AK:-$(openssl rand -hex 32)}
EOF
  echo "Secrets générés dans $SECRETS"
fi
. "$SECRETS"

DATABASE_URL="postgresql://$PG_ADMIN:$PG_PASSWORD@$PG_SERVER.postgres.database.azure.com:5432/$PG_DB?sslmode=require"
ACR_SERVER="$ACR.azurecr.io"
TAG_FILE="$DIR/.secrets/image-tag"
