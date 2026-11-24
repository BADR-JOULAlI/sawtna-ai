#!/usr/bin/env bash
# Crée l'infrastructure PaaS : groupe de ressources, ACR, PostgreSQL Flexible (+pgvector),
# environnement Container Apps. Idempotent : peut être relancé.
. "$(dirname "$0")/_common.sh"

for p in Microsoft.App Microsoft.ContainerRegistry Microsoft.DBforPostgreSQL Microsoft.OperationalInsights; do
  az provider register -n "$p" -o none
done
az extension add --name containerapp --upgrade -y -o none 2>/dev/null || true

echo "== Groupe de ressources $RG ($RG_LOC)"
az group create -n "$RG" -l "$RG_LOC" -o none

echo "== Registre $ACR_SERVER"
az acr show -n "$ACR" -o none 2>/dev/null || az acr create -g "$RG" -n "$ACR" --sku Basic -l "$LOC" -o none   # ACR Tasks (az acr build) indisponible en austriaeast

echo "== PostgreSQL Flexible $PG_SERVER (peut prendre ~5 min)"
if ! az postgres flexible-server show -g "$RG" -n "$PG_SERVER" -o none 2>/dev/null; then
  az postgres flexible-server create -g "$RG" -n "$PG_SERVER" -l "$LOC" \
    --tier "$PG_TIER" --sku-name "$PG_SKU" --storage-size "$PG_STORAGE_GB" --version "$PG_VERSION" \
    --admin-user "$PG_ADMIN" --admin-password "$PG_PASSWORD" \
    --public-access Disabled --backup-retention 7 --yes -o none
fi
# Sans VNet, Container Apps joint la base par son point d'accès public : on l'active,
# puis le pare-feu ne laisse passer que les services Azure (aucune IP Internet).
az postgres flexible-server update -g "$RG" -n "$PG_SERVER" --public-access Enabled -o none
# Autorise uniquement les services Azure (dont Container Apps) ; pas d'accès depuis Internet.
az postgres flexible-server firewall-rule create -g "$RG" --server-name "$PG_SERVER" \
  --name allow-azure-services --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0 -o none
# pgvector doit être mis en liste blanche avant que le backend fasse CREATE EXTENSION vector.
az postgres flexible-server parameter set -g "$RG" -s "$PG_SERVER" --name azure.extensions --value VECTOR -o none
az postgres flexible-server db show -g "$RG" --server-name "$PG_SERVER" --name "$PG_DB" -o none 2>/dev/null \
  || az postgres flexible-server db create -g "$RG" --server-name "$PG_SERVER" --name "$PG_DB" -o none

echo "== Environnement Container Apps $ACA_ENV"
az containerapp env show -g "$RG" -n "$ACA_ENV" -o none 2>/dev/null \
  || az containerapp env create -g "$RG" -n "$ACA_ENV" -l "$LOC" --logs-destination none -o none

echo "Infrastructure prête. Étape suivante : ./02-build-push.sh"
