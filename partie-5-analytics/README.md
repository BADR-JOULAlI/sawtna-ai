# Étudiant 5 — Analytics et tableau de bord sur Google Compute Engine

**Responsable indiqué dans le cahier des charges : Ijlal Sellak**  
**Modèle cloud :** Google Compute Engine (IaaS)  
**Objectif :** afficher des indicateurs opérationnels agrégés à partir des événements explicitement autorisés par l’équipe.

## Périmètre

Le dashboard est destiné au suivi interne et reste séparé de l’interface citoyen. Il n’ingère que les données minimales définies dans `commun/packages/contracts/analytics.openapi.json`. Il ne doit pas recevoir ni conserver les questions des citoyens, leurs identités ou leurs adresses IP.

### Tâches

1. Définir avec l’équipe chaque KPI, sa formule, période, fuseau horaire, source et limites d’interprétation.
2. Recevoir des événements autorisés du backend; valider les schémas et dédupliquer avec un identifiant d’événement stable.
3. Agréger les données utiles (activité, langues, quiz, latence et volumes disponibles) sans conserver de contenu de question.
4. Construire un dashboard lisible avec filtres temporels, états sans données et horodatage de mise à jour.
5. Protéger l’accès administrateur, limiter les ports et comptes système, configurer HTTPS, mises à jour et sauvegardes nécessaires.
6. Déployer le service et son dashboard sur une VM GCE reproductible; superviser disponibilité, erreurs et consommation.
7. Documenter les procédures de mise à jour, restauration et désactivation des accès.

## Livrables

- Catalogue des KPI et définitions calculables.
- API ou ingestion d’événements idempotente et stockage agrégé.
- Dashboard avec visualisations liées aux données réellement reçues.
- Tests de validation, déduplication, agrégation et contrôle d’accès.
- Guide GCE d’installation, exploitation et mise à jour.

## Critères de validation

- Un événement rejoué n’incrémente pas deux fois les KPI.
- Les graphiques correspondent aux formules documentées et affichent les périodes réelles.
- Les routes administratives refusent les accès non autorisés.
- Aucun texte de question, compte utilisateur, adresse IP ou préférence politique n’est stocké.
- L’interface indique clairement l’absence ou l’ancienneté des données au lieu d’afficher des valeurs inventées.

## Dépendances

Le backend fournit uniquement les événements convenus et leurs agrégats. Le dashboard ne lit jamais directement la base opérationnelle PostgreSQL sans contrat et autorisation explicites.


## Exécution du service existant

# Étudiant 5 — Analytics · Google Compute Engine

Code : analytics_service/main.py. Le dashboard réutilise le build React et est servi sur /dashboard.

~~~powershell
npm --prefix partie-4-frontend run build
python -m uvicorn sawtna.analytics:app --host 127.0.0.1 --port 8012 --no-access-log
python -m pytest commun/tests/test_nlp_analytics.py
~~~

POST /v1/events est idempotent sur event_id, authentifié par X-Service-Key.
GET /v1/summary agrège questions, taux de réponses sourcées, quiz, scores, latences et langues par jour UTC.
Le dashboard exige X-Admin-Key. SAWTNA_BACKEND_URL permet de consulter le corpus et l’état des dépendances.
Aucun texte de question ni identifiant de personne n’est accepté.
Choisir une politique de rétention/purge avant exploitation publique.
