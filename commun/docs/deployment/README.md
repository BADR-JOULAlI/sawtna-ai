# Déploiements après validation locale

Ces procédures sont des livrables à exécuter séparément après choix des comptes, régions et budgets. Aucun service cloud n’a été provisionné par les tests locaux.

| Propriétaire | Unité | Configuration indispensable |
|---|---|---|
| P1 EC2 | image ETL, tâche manuelle ou systemd timer | catalogue officiel, volume persistant, clé ingestion backend |
| P2 Azure VM | API + PostgreSQL/pgvector | secrets, HTTPS, base privée, sauvegardes, URLs NLP/Analytics |
| P3 Cloud Run | conteneur NLP CPU | port PORT, mémoire mesurée, clé service, min-instances=0 |
| P4 Static Web Apps | build partie-4-frontend/dist | VITE_API_BASE_URL, origine CORS côté backend |
| P5 Compute Engine | Analytics + dashboard | base persistante, SAWTNA_BACKEND_URL, clés, HTTPS |

Ne pas publier PostgreSQL sur Internet. Les exemples de mots de passe sont locaux.
Mesurer mémoire, CPU, latence et trafic avant de choisir les tailles des VM.
Les comptes Azure des étudiants 2 et 4 sont indépendants : les appels passent par HTTPS.
Les VMs, disques, IP et trafic inter-cloud peuvent avoir des coûts indépendants.
