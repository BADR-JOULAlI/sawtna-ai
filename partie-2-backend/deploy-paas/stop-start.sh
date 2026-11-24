#!/usr/bin/env bash
# Économies : les Container Apps descendent seules à 0 réplique ; seule la base se facture
# en continu. Usage : ./stop-start.sh stop | start | status
# Azure redémarre automatiquement un serveur Flexible arrêté depuis 7 jours.
. "$(dirname "$0")/_common.sh"
case "${1:-status}" in
  stop)   az postgres flexible-server stop  -g "$RG" -n "$PG_SERVER" -o none && echo "Base arrêtée" ;;
  start)  az postgres flexible-server start -g "$RG" -n "$PG_SERVER" -o none && echo "Base démarrée" ;;
  status) az postgres flexible-server show -g "$RG" -n "$PG_SERVER" --query state -o tsv
          az containerapp list -g "$RG" --query "[].{app:name,etat:properties.runningStatus,url:properties.configuration.ingress.fqdn}" -o table ;;
  *) echo "Usage : $0 stop|start|status"; exit 1 ;;
esac
