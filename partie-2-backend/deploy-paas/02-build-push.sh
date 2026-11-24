#!/usr/bin/env bash
# Construit l'image sawtna-app (backend + NLP concept-hash) et la pousse dans l'ACR.
# Azure for Students interdit ACR Tasks (TasksOperationsNotAllowed) : build local avec
# Docker Desktop par défaut. CLOUD_BUILD=1 pour tenter az acr build sur un autre abonnement.
. "$(dirname "$0")/_common.sh"

TAG="$(date +%Y%m%d-%H%M)"
IMAGE="$ACR_SERVER/$IMAGE_REPO:$TAG"
DOCKERFILE="$DIR/Dockerfile.paas"
command -v cygpath >/dev/null && DOCKERFILE="$(cygpath -m "$DOCKERFILE")"

if [ "${CLOUD_BUILD:-0}" = 1 ]; then
  az acr build -r "$ACR" -t "$IMAGE_REPO:$TAG" -f "$DOCKERFILE" "$REPO"
else
  docker info >/dev/null 2>&1 || { echo "Démarrer Docker Desktop puis relancer."; exit 1; }
  docker build --platform linux/amd64 -f "$DOCKERFILE" -t "$IMAGE" "$REPO"
  az acr login -n "$ACR"
  # Les envois expirent parfois : on réessaie (les couches déjà envoyées sont ignorées).
  ok=0
  for i in 1 2 3 4 5; do docker push "$IMAGE" && { ok=1; break; }; echo "Push échoué ($i/5), nouvel essai..."; sleep 15; done
  [ $ok = 1 ] || { echo "ÉCHEC du push après 5 essais."; exit 1; }
fi

echo "$TAG" > "$TAG_FILE"
echo "Image publiée : $IMAGE. Étape suivante : ./03-deploy-apps.sh"
