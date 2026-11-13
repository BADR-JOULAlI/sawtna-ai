# Déploiement et exploitation — Backend Sawtna sur Azure VM (étudiant 2)

Staging : `https://sawtna-api-staging-50fe10.polandcentral.cloudapp.azure.com` (`/health`, `/docs`).

## Architecture

```
Internet ──443──▶ Caddy (HTTPS Let's Encrypt) ──▶ backend :8000 ──▶ PostgreSQL 16 + pgvector (réseau Docker privé)
                                                     └──────────▶ NLP :8000 (provisoire, en attendant Cloud Run)
Azure Blob « pg-backups » ◀── sauvegarde quotidienne (identité managée de la VM)
Logic App ──14:00──▶ démarrage VM          minuteur systemd ──19:30──▶ désallocation VM
```

| Élément | Valeur |
|---|---|
| Abonnement / région | Azure for Students (ESI), Poland Central — seule région autorisée par l'école avec une taille disponible et du quota |
| VM | `vm-sawtna-backend`, Standard_B2als_v2 (2 vCPU, 4 Go), Ubuntu 24.04, groupe `rg-sawtna-backend-staging` |
| Réseau | NSG : 443/80 publics, 22 limité à l'IP de l'administrateur ; PostgreSQL sans port publié |
| Horaire | Démarrage 14:00, sauvegarde 19:00, désallocation 19:30 (heure de Rabat, chaque jour) |
| Coût estimé | ≈ 16,50 $/mois (VM 5h30/jour ≈ 7 $, disque P4 5,81 $, IP 3,65 $, Logic App et Blob < 0,10 $) |

## Fichiers

| Fichier | Rôle |
|---|---|
| `provision.sh` | Crée le groupe, la VM, la clé SSH, l'IP + DNS et les règles NSG |
| `setup-vm.sh` | Sur la VM : installe Docker, clone le dépôt, démarre la pile |
| `compose.staging.yml`, `Caddyfile` | Pile de staging (db, nlp, backend, caddy) |
| `auto-deallocate.sh`, `sawtna-auto-deallocate.{service,timer}` | Désallocation quotidienne à 19:30 via l'identité managée de la VM |
| `provision-autostart.sh`, `logicapp-autostart.template.json` | Démarrage quotidien à 14:00 via Logic App |
| `provision-backup.sh`, `backup/` | Stockage Blob, sauvegarde, restauration et test de restauration |
| `SAUVEGARDE-RESTAURATION.md` | Procédure et résultat du test de restauration |

## Reconstruire de zéro

1. `bash provision.sh` puis créer `.secrets/staging.env` (voir ci-dessous) ; copier `compose.staging.yml`, `Caddyfile`, `setup-vm.sh` et `.env` dans `~/sawtna-staging/` sur la VM ; lancer `bash setup-vm.sh`.
2. Arrêt auto : `az vm identity assign --role "Virtual Machine Contributor" --scope <id VM>`, installer `auto-deallocate.sh` dans `/usr/local/bin/sawtna-auto-deallocate.sh` et activer le timer.
3. Démarrage auto : `bash provision-autostart.sh`.
4. Sauvegardes : `bash provision-backup.sh`, rôle *Storage Blob Data Contributor* sur le conteneur, installer `backup/` (voir `SAUVEGARDE-RESTAURATION.md`), puis `sudo sawtna-restore.sh latest sawtna --i-know` si une sauvegarde existe.

## Secrets (jamais dans Git)

`.secrets/staging.env` sur le poste de l'administrateur et `~/sawtna-staging/.env` (chmod 600) sur la VM :

```
SAWTNA_DOMAIN=<fqdn>
SAWTNA_SERVICE_KEY=<openssl rand -hex 32>   # partagée avec ETL (Ayoub) et NLP (Badr), hors mail
SAWTNA_ADMIN_KEY=<openssl rand -hex 32>     # administrateur backend uniquement
POSTGRES_PASSWORD=<openssl rand -hex 24>
SAWTNA_ALLOWED_ORIGINS=https://<origine du frontend>
```

**Rotation d'une clé** : générer la nouvelle valeur, la mettre dans les deux fichiers `.env`, `sudo docker compose -f compose.staging.yml --env-file .env up -d`, puis transmettre la nouvelle clé de service à l'ETL et au NLP (qui doit utiliser la même valeur). Changer `POSTGRES_PASSWORD` exige aussi `ALTER USER sawtna PASSWORD ...` dans la base.

## Exploitation courante

```bash
# Démarrer / arrêter hors horaire (depuis le poste admin)
az vm start      -g rg-sawtna-backend-staging -n vm-sawtna-backend
az vm deallocate -g rg-sawtna-backend-staging -n vm-sawtna-backend

# Sur la VM
sudo docker compose -f ~/sawtna-staging/compose.staging.yml ps
sudo docker logs --tail 100 sawtna-staging-backend-1
journalctl -t sawtna-backup -t sawtna-auto-deallocate -n 20
systemctl list-timers 'sawtna-*'

# Retirer un passage (clé admin)
curl -X POST https://<fqdn>/api/admin/passages/<id>/retire -H "X-Admin-Key: <clé>" \
     -H "Content-Type: application/json" -d '{"reason":"<raison>"}'
```

Mise à jour du code : `git -C ~/sawtna-staging/sawtna-ai pull --ff-only` puis `bash setup-vm.sh` (faire une sauvegarde avant).

## Limites connues

- Staging seulement : stockage LRS, une seule VM, pas d'alerte automatique (consulter les journaux).
- NLP et Analytics ne sont pas encore déployés par leurs responsables : le NLP tourne provisoirement sur la VM, `/health` reste `degraded` sans Analytics.
- Une seule clé de service pour tous les appels interservices (limite de l'architecture commune).
