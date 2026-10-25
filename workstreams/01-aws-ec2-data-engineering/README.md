# Étudiant 1 — Ingestion documentaire sur AWS EC2

**Responsable indiqué dans le cahier des charges : Ayoub Chenguir**  
**Modèle cloud :** AWS EC2 (IaaS)  
**Objectif :** transformer des documents électoraux officiels en passages structurés, traçables et prêts à être validés puis ingérés par l’API.

## Périmètre

Ce dossier décrit le travail de Data Engineering. Le code de référence est actuellement dans `services/data-engineering-aws/`, `packages/sawtna/data_engineering.py` et `scripts/`. Éviter de maintenir une seconde implémentation ici : ce dossier est le guide du propriétaire du service.

### Tâches

1. Tenir un catalogue de sources officielles autorisées (URL, organisme, titre, langue, date/version et type de document).
2. Collecter les PDF et pages web par HTTPS; valider les domaines, redirections, taille et type réel du fichier.
3. Conserver chaque original de façon immuable avec son SHA-256 et un manifeste horodaté.
4. Extraire le texte par page, nettoyer les artefacts, dédupliquer et signaler les pages nécessitant un OCR.
5. Découper les textes en passages sans perdre les titres, articles, pages, langue, URL, statut de revue et empreinte.
6. Produire des données en attente de revue humaine; traiter les corrections et versions mises à jour sans écraser l’historique.
7. Après revue, transmettre les passages approuvés à l’API Azure par lots authentifiés et gérer les erreurs/reprises.
8. Documenter l’exécution locale et la cible EC2, les journaux, les permissions minimales et la supervision.

## Contrat de sortie

Chaque passage suit `packages/contracts/passage.schema.json`. Champs centraux : identifiant stable, identifiant du document, titre, URL source, langue (`fr`, `ar`, `darija`), texte, article/section, page, statut de revue et SHA-256. Ne jamais envoyer au RAG un passage encore `pending_review`.

## Livrables

- Catalogue versionné et pipeline ETL reproductible.
- Originaux et manifestes traçables, exclus de Git si volumineux ou protégés.
- Passages JSONL normalisés, contrôles de qualité et rapport d’exécution.
- Tests couvrant format, doublons, erreurs réseau, limites de taille et reprise.
- Guide de déploiement et d’exploitation EC2, sans secrets dans le dépôt.

## Critères de validation

- Une source peut être retracée jusqu’à son URL, sa version, sa page et son empreinte.
- Une collecte interrompue peut reprendre sans corrompre ou remplacer les originaux.
- Les passages incomplets ou OCR incertains restent explicitement à vérifier.
- L’ingestion n’accepte que des données approuvées et utilise le contrat partagé.
- Une exécution locale documentée fonctionne sans identifiants AWS.

## Dépendances d’intégration

Le backend fournit l’URL d’ingestion, l’authentification `X-Service-Key` et les limites de lots. Les changements de schéma se coordonnent dans `packages/contracts/` avant modification du producteur ou du consommateur.

## Démarrage

Voir le guide principal et `services/data-engineering-aws/README.md`. Développement et vérification se font en local; aucun déploiement AWS n’est implicite.
