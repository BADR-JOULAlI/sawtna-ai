#!/usr/bin/env bash
# Crée le stockage hors VM des sauvegardes PostgreSQL (Azure Blob, Poland Central).
set -euo pipefail
AZ="${AZ:-/c/Program Files/Microsoft SDKs/Azure/CLI2/wbin/az.cmd}"
RG=rg-sawtna-backend-staging; LOC=polandcentral; CONTAINER=pg-backups
DIR="$(cd "$(dirname "$0")" && pwd)"; STATE="$DIR/.secrets/azure.env"; . "$STATE"
grep -q '^STORAGE=' "$STATE" || echo "STORAGE=sawtnabak$(openssl rand -hex 4)" >> "$STATE"; . "$STATE"
"$AZ" storage account create -g $RG -n "$STORAGE" -l $LOC --sku Standard_LRS --kind StorageV2 \
  --min-tls-version TLS1_2 --allow-blob-public-access false --https-only true -o none
"$AZ" storage container create --account-name "$STORAGE" -n $CONTAINER --auth-mode login -o none 2>/dev/null || \
  "$AZ" storage container create --account-name "$STORAGE" -n $CONTAINER -o none
# Rétention : suppression automatique des sauvegardes de plus de 30 jours.
cat > "$DIR/.secrets/lifecycle.json" <<JSON
{"rules":[{"enabled":true,"name":"retention-30j","type":"Lifecycle","definition":{"actions":{"baseBlob":{"delete":{"daysAfterModificationGreaterThan":30}}},"filters":{"blobTypes":["blockBlob"],"prefixMatch":["$CONTAINER/"]}}}]}
JSON
"$AZ" storage account management-policy create -g $RG --account-name "$STORAGE" --policy @"$DIR/.secrets/lifecycle.json" -o none
echo "Stockage prêt : $STORAGE/$CONTAINER"
