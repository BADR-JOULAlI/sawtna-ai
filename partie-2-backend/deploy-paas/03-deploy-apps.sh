#!/usr/bin/env bash
# Déploie (ou met à jour) les Container Apps :
#   - sawtna-nlp-hash : NLP concept-hash-v1, ingress INTERNE (si NLP_MODE=internal)
#   - sawtna-backend  : API publique HTTPS, base = PostgreSQL Flexible
. "$(dirname "$0")/_common.sh"

[ -f "$TAG_FILE" ] || { echo "Aucune image : lancer ./02-build-push.sh d'abord."; exit 1; }
IMAGE="$ACR_SERVER/$IMAGE_REPO:$(cat "$TAG_FILE")"

exists() { az containerapp show -g "$RG" -n "$1" -o none 2>/dev/null; }

# Identité managée utilisateur pour tirer l'image (l'identité système n'est pas
# acceptée par les environnements « express ») : rôle AcrPull sur le registre seulement.
UAI=sawtna-backend-acrpull
az identity show -g "$RG" -n "$UAI" -o none 2>/dev/null || az identity create -g "$RG" -n "$UAI" -l "$LOC" -o none
UAI_ID=$(az identity show -g "$RG" -n "$UAI" --query id -o tsv)
UAI_PRINCIPAL=$(az identity show -g "$RG" -n "$UAI" --query principalId -o tsv)
ACR_ID=$(az acr show -n "$ACR" --query id -o tsv)
if [ -z "$(az role assignment list --assignee "$UAI_PRINCIPAL" --scope "$ACR_ID" --role AcrPull --query [].id -o tsv)" ]; then
  az role assignment create --assignee-object-id "$UAI_PRINCIPAL" --assignee-principal-type ServicePrincipal \
    --role AcrPull --scope "$ACR_ID" -o none
  echo "Rôle AcrPull attribué, attente de la propagation (60 s)..."; sleep 60
fi

# deploy <app> <ingress> <cpu> <mem> <secrets...> -- <env vars...>
deploy() {
  local app=$1 ingress=$2 cpu=$3 mem=$4; shift 4
  local secrets=() envs=()
  while [ "$1" != "--" ]; do secrets+=("$1"); shift; done; shift
  envs=("$@")
  if exists "$app"; then
    echo "== Mise à jour $app"
    az containerapp secret set -g "$RG" -n "$app" --secrets "${secrets[@]}" -o none
    az containerapp ingress enable -g "$RG" -n "$app" --type "$ingress" --target-port 8000 -o none
    az containerapp update -g "$RG" -n "$app" --image "$IMAGE" --set-env-vars "${envs[@]}" -o none
  else
    echo "== Création $app"
    az containerapp create -g "$RG" -n "$app" --environment "$ACA_ENV" --image "$IMAGE" \
      --user-assigned "$UAI_ID" --registry-server "$ACR_SERVER" --registry-identity "$UAI_ID" \
      --ingress "$ingress" --target-port 8000 \
      --cpu "$cpu" --memory "$mem" --min-replicas 0 --max-replicas 1 \
      --secrets "${secrets[@]}" --env-vars "${envs[@]}" -o none
  fi
}

if [ "$NLP_MODE" = internal ]; then
  # Ingress EXTERNE : en environnement « express », l'ingress interne répond 404 même aux
  # autres apps de l'environnement, et aucune IP sortante n'est exposée pour filtrer.
  # /v1/embeddings reste protégé par X-Service-Key (même modèle que le NLP de Badr).
  deploy "$APP_NLP" external 0.25 0.5Gi \
    "service-key=$SAWTNA_SERVICE_KEY" -- \
    SAWTNA_SERVICE=nlp SAWTNA_EMBEDDER=concept-hash-v1 SAWTNA_SERVICE_KEY=secretref:service-key
  NLP_URL="https://$(az containerapp show -g "$RG" -n "$APP_NLP" --query properties.configuration.ingress.fqdn -o tsv)"
else
  NLP_URL="$SHARED_NLP_URL"          # la clé doit être celle du secret service-key de Badr
fi

deploy "$APP_BACKEND" external 0.5 1Gi \
  "service-key=$SAWTNA_SERVICE_KEY" "admin-key=$SAWTNA_ADMIN_KEY" "database-url=$DATABASE_URL" "analytics-key=${SAWTNA_ANALYTICS_KEY:-$SAWTNA_SERVICE_KEY}" -- \
  SAWTNA_SERVICE=backend \
  SAWTNA_SERVICE_KEY=secretref:service-key \
  SAWTNA_ADMIN_KEY=secretref:admin-key \
  SAWTNA_ANALYTICS_KEY=secretref:analytics-key \
  SAWTNA_BACKEND_DATABASE_URL=secretref:database-url \
  SAWTNA_NLP_URL="$NLP_URL" \
  SAWTNA_ANALYTICS_URL="$SAWTNA_ANALYTICS_URL" \
  SAWTNA_ALLOWED_ORIGINS="$SAWTNA_ALLOWED_ORIGINS"

FQDN=$(az containerapp show -g "$RG" -n "$APP_BACKEND" --query properties.configuration.ingress.fqdn -o tsv)
echo "API_URL=https://$FQDN" > "$DIR/.secrets/api-url"
echo "Backend déployé : https://$FQDN  (NLP : $NLP_URL). Étape suivante : ./04-verify.sh"
