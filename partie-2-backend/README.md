# Étudiant 2 — API et base de données sur Azure VM

**Responsable indiqué dans le cahier des charges : Soulayman Jdidi**  
**Modèle cloud :** Azure Virtual Machine (IaaS)  
**Objectif :** fournir l’API centrale, persister le corpus et orchestrer recherche, quiz, NLP et événements analytiques.

## Périmètre

Le backend est le seul point d’accès métier pour le frontend. Il ne doit pas exposer PostgreSQL directement au navigateur. Sa réalisation complète appartient à l’étudiant responsable; ce dépôt contient les contrats communs et un prototype local d’intégration, pas une autorisation de déploiement Azure.

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
