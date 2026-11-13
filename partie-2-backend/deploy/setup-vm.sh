#!/usr/bin/env bash
# Exécuté sur la VM : installe Docker, récupère le monorepo et démarre le staging.
set -euo pipefail
if ! command -v docker >/dev/null; then
  curl -fsSL https://get.docker.com | sudo sh
  sudo usermod -aG docker "$USER"
fi
sudo apt-get install -y -q unattended-upgrades >/dev/null
cd ~/sawtna-staging
[ -d sawtna-ai ] || git clone --depth 1 https://github.com/BADR-JOULAlI/sawtna-ai.git
git -C sawtna-ai pull --ff-only
sudo docker compose -f compose.staging.yml --env-file .env up --build --detach --wait
sudo docker compose -f compose.staging.yml ps
