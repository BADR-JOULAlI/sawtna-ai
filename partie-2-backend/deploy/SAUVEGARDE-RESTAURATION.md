# Sauvegarde et restauration — backend Sawtna (staging Azure)

Responsable : étudiant 2 (backend + PostgreSQL/pgvector, Azure VM).

## Dispositif

| Élément | Valeur |
|---|---|
| Base sauvegardée | `sawtna` (passages, vecteurs pgvector, file d'événements) dans le conteneur `sawtna-staging-db-1` |
| Méthode | `pg_dump -Fc` (format custom), contrôle de lisibilité par `pg_restore --list`, empreinte SHA-256 |
| Fréquence | Tous les jours à 19:00 heure de Rabat (timer systemd `sawtna-backup.timer`), avant l'arrêt automatique de 19:30. Si la VM était éteinte, la sauvegarde manquée s'exécute au démarrage suivant |
| Copie locale | `/var/backups/sawtna/` sur la VM (dossier 700, root), conservée 7 jours |
| Copie hors VM | Azure Blob `sawtnabakb9dcf2a0/pg-backups` (Poland Central, LRS, TLS 1.2, aucun accès public), conservée 30 jours par règle de cycle de vie |
| Authentification | Identité managée de la VM, rôle *Storage Blob Data Contributor* limité au conteneur `pg-backups` : aucune clé de stockage sur la VM |
| Journaux | `journalctl -t sawtna-backup` |

## Commandes (sur la VM, en `sudo`)

```bash
# Sauvegarde immédiate
sudo systemctl start sawtna-backup.service
sudo journalctl -t sawtna-backup -n 5 -o cat

# Prochaine exécution planifiée
systemctl list-timers sawtna-backup.timer

# Test de restauration complet (ne touche pas la production)
sudo /usr/local/bin/sawtna-restore-test.sh

# Restaurer une sauvegarde dans une base de test
sudo /usr/local/bin/sawtna-restore.sh latest                      # dernière sauvegarde hors VM
sudo /usr/local/bin/sawtna-restore.sh sawtna-20261113T183130Z.dump # sauvegarde précise

# Restaurer la PRODUCTION (incident) : arrête l'API, remplace la base, redémarre l'API
sudo /usr/local/bin/sawtna-restore.sh latest sawtna --i-know
```

Connexion à la VM : `ssh -i ~/.ssh/sawtna_azure_ed25519 azureuser@sawtna-api-staging-50fe10.polandcentral.cloudapp.azure.com`.

## Ce que vérifie le test de restauration

1. Télécharge la dernière sauvegarde **depuis Azure Blob** (pas la copie locale) et contrôle son SHA-256.
2. La restaure dans une base séparée `sawtna_restore_test`.
3. Compare production et restauration : nombre de passages et empreinte MD5 de tous les identifiants, textes, vecteurs et modèles.
4. Démarre un backend temporaire sur la base restaurée et vérifie `/health`, `/api/documents` et une question citée.
5. Supprime la base et le conteneur temporaires.

## Résultat du test — 13 novembre 2026, 18:32 UTC

```
Dernière sauvegarde hors VM : sawtna-20261113T183130Z.dump
sawtna-20261113T183130Z.dump: OK
passages restaurés: 7
Production : 7 passages, empreinte bae285640513d1f04ad9968d172967ad
Restaurée  : 7 passages, empreinte bae285640513d1f04ad9968d172967ad
COMPARAISON OK : contenu identique
Backend sur base restaurée /health : postgresql+pgvector
Documents servis : 2 | passages : 7
Question test -> source : ['constitution-portail-fr']
TEST DE RESTAURATION RÉUSSI (2026-11-13T18:32:00Z)
```

## Reconstruction totale (perte de la VM)

1. `bash provision.sh` (nouvelle VM), puis copier `compose.staging.yml`, `Caddyfile`, `.env` et lancer `setup-vm.sh`.
2. Redonner à la nouvelle identité de VM le rôle *Storage Blob Data Contributor* sur `pg-backups`, installer les scripts de `backup/`.
3. `sudo /usr/local/bin/sawtna-restore.sh latest sawtna --i-know`.

Les secrets (`.secrets/staging.env`) restent hors Git ; sans eux, générer de nouvelles clés et les communiquer aux autres services.

## Limites connues

- Stockage LRS (une seule région) : suffisant pour un staging étudiant, pas pour une production.
- Pas d'alerte automatique en cas d'échec : vérifier `journalctl -t sawtna-backup` ou le conteneur Blob.
- Coût : quelques centimes par mois (sauvegardes de quelques Ko).
