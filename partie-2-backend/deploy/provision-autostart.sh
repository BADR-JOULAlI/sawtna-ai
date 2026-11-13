#!/usr/bin/env bash
# Démarrage automatique de la VM chaque jour à 14:00 (heure du Maroc) via une Logic App.
# (Azure Automation est refusé aux abonnements Student dans les régions autorisées par l'ESI.)
set -euo pipefail
AZ="${AZ:-/c/Program Files/Microsoft SDKs/Azure/CLI2/wbin/az.cmd}"
RG=rg-sawtna-backend-staging; VM=vm-sawtna-backend; LA=la-sawtna-autostart
DIR="$(cd "$(dirname "$0")" && pwd)"; mkdir -p "$DIR/.secrets"
"$AZ" provider register --namespace Microsoft.Logic --wait -o none
VMID=$("$AZ" vm show -g $RG -n $VM --query id -o tsv | tr -d '\r')
sed "s#__VM_ID__#$VMID#" "$DIR/logicapp-autostart.template.json" > "$DIR/.secrets/logicapp-autostart.json"
PRINCIPAL=$("$AZ" resource create -g $RG -n $LA --resource-type Microsoft.Logic/workflows --is-full-object \
  --properties @"$DIR/.secrets/logicapp-autostart.json" --query identity.principalId -o tsv | tr -d '\r')
# Droit minimal : Virtual Machine Contributor sur CETTE VM uniquement.
"$AZ" role assignment create --assignee-object-id "$PRINCIPAL" --assignee-principal-type ServicePrincipal \
  --role "Virtual Machine Contributor" --scope "$VMID" -o none
echo "Logic App $LA prête (démarrage quotidien 14:00, Morocco Standard Time)."
