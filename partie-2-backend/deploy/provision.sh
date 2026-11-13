#!/usr/bin/env bash
# Crée la VM de staging du backend Sawtna sur Azure (Poland Central, B2als_v2 — seule combinaison taille+quota autorisée par Azure for Students ESI, arrêt auto 20h Rabat).
set -euo pipefail
AZ="${AZ:-/c/Program Files/Microsoft SDKs/Azure/CLI2/wbin/az.cmd}"
RG=rg-sawtna-backend-staging; LOC=polandcentral; VM=vm-sawtna-backend; SIZE=Standard_B2als_v2
KEY="$HOME/.ssh/sawtna_azure_ed25519"
DIR="$(cd "$(dirname "$0")" && pwd)"; STATE="$DIR/.secrets/azure.env"
mkdir -p "$DIR/.secrets" "$HOME/.ssh"
[ -f "$KEY" ] || ssh-keygen -t ed25519 -N "" -C sawtna-staging -f "$KEY" >/dev/null
[ -f "$STATE" ] || echo "DNS_LABEL=sawtna-api-staging-$(openssl rand -hex 3)" > "$STATE"
. "$STATE"
MYIP="${MYIP:-$(curl -s https://api.ipify.org)}"
"$AZ" group create -n $RG -l francecentral -o none
"$AZ" vm create -g $RG -n $VM -l $LOC --size $SIZE --image Ubuntu2404 \
  --admin-username azureuser --ssh-key-values "$KEY.pub" \
  --public-ip-sku Standard --public-ip-address-dns-name "$DNS_LABEL" \
  --nsg-rule NONE --os-disk-size-gb 32 -o none
NSG="${VM}NSG"
"$AZ" network nsg rule create -g $RG --nsg-name $NSG -n ssh-admin --priority 100 --access Allow --protocol Tcp --direction Inbound --source-address-prefixes "$MYIP/32" --destination-port-ranges 22 -o none
"$AZ" network nsg rule create -g $RG --nsg-name $NSG -n https --priority 110 --access Allow --protocol Tcp --direction Inbound --source-address-prefixes Internet --destination-port-ranges 80 443 -o none
# Arrêt automatique chaque soir à 20:00 heure de Rabat (UTC+1) = 19:00 UTC.
"$AZ" vm auto-shutdown -g $RG -n $VM --time 1900 -o none
FQDN=$("$AZ" vm show -d -g $RG -n $VM --query fqdns -o tsv)
echo "FQDN=$FQDN" >> "$STATE"
echo "VM prête : https://$FQDN"
