# Étudiant 2 — API et base de données sur Azure VM

**Responsable indiqué dans le cahier des charges : Soulayman Jdidi**  
**Modèle cloud :** Azure Virtual Machine (IaaS)  
**Objectif :** fournir l’API centrale, persister le corpus et orchestrer recherche, quiz, NLP et événements analytiques.

## Périmètre

Le backend est le seul point d’accès métier pour le frontend. Il ne doit pas exposer PostgreSQL directement au navigateur. Le code local est présent dans `backend_service/`; le déploiement Azure reste à réaliser.

### Tâches

1. Définir et documenter les routes HTTPS, schémas, codes d’erreur, limites et versions d’API.
2. Recevoir les passages approuvés du pipeline AWS, valider le contrat et rendre l’ingestion idempotente.
3. Installer PostgreSQL avec pgvector; stocker textes, métadonnées, références et vecteurs avec identifiant de modèle.
4. Appeler le service NLP authentifié pour embeddings et recherche; traiter délais, erreurs, indisponibilité et versions de modèle.
5. Implémenter recherche documentaire, réponses ancrées dans les passages, références visibles et abstention si le corpus ne suffit pas.
6. Servir les quiz sans révéler les réponses avant soumission; valider et noter côté serveur.
7. Envoyer à Analytics uniquement les événements minimaux autorisés, avec identifiants aléatoires et reprise idempotente.
8. Protéger les secrets, appliquer le moindre privilège, TLS, mises à jour OS, sauvegardes et restauration testée.

## Interfaces communes

- Contrat des passages : `commun/packages/contracts/passage.schema.json`.
- Contrats d’API : `commun/packages/contracts/backend.openapi.json` et contrats NLP/Analytics associés.
- Ingestion et appels interservices : clé de service côté serveur; clés absentes du frontend.
- Réponse du chatbot : texte, langue, passages cités et métadonnées de référence; pas de score présenté comme probabilité de vérité.

## Livrables

- API documentée et versionnée avec endpoints de santé.
- Schéma PostgreSQL/pgvector, migrations et procédure de restauration.
- Déploiement conteneurisé ou scripté reproductible sur VM.
- Tests unitaires et d’intégration : ingestion, recherche, citation, quiz, authentification et dépendances en panne.
- Guide d’exploitation Azure VM, sauvegarde, rotation des secrets, journaux et alertes.

## Critères de validation

- Seuls des passages conformes et approuvés peuvent alimenter le corpus.
- Les réponses citent des sources existantes et l’API s’abstient hors corpus.
- Les écritures répétées ne créent pas de doublons.
- Les événements analytiques ne contiennent ni question, ni identité, ni adresse IP.
- Une restauration de sauvegarde et le parcours complet sont démontrés en environnement de test.

## Dépendances

L’étudiant 1 fournit les passages approuvés; l’étudiant 3 publie le contrat d’embeddings; l’étudiant 4 consomme l’API; l’étudiant 5 consomme les agrégats. Les contrats se valident collectivement avant intégration.


## Exécution du service existant

# Étudiant 2 — Backend · Azure VM

Code : backend_service/main.py et quiz.py. Persistance : commun/packages/sawtna/store.py.

~~~powershell
python -m uvicorn sawtna.backend:app --host 127.0.0.1 --port 8010 --no-access-log
python -m pytest commun/tests/test_backend.py
~~~

Démarrer NLP et Analytics avant le backend.
Variables : SAWTNA_NLP_URL, SAWTNA_ANALYTICS_URL, SAWTNA_SERVICE_KEY, SAWTNA_ADMIN_KEY, SAWTNA_BACKEND_DATABASE_URL et SAWTNA_ALLOWED_ORIGINS.
Sans URL PostgreSQL, SQLite est utilisé. Avec PostgreSQL, l’extension vector et les vecteurs 384D sont réels.
Changer de modèle exige une réindexation.
Endpoints : /api/ask, /api/documents, /api/quiz, /api/quiz/submit, /api/admin/summary, /v1/ingest et /health.
Les événements Analytics sont conservés dans une file de réessai. Hors développement, exposer derrière HTTPS et changer les clés.
