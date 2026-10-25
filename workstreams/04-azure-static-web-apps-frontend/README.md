# Étudiant 4 — Interface citoyen React sur Azure Static Web Apps

**Responsable indiqué dans le cahier des charges : Aya Sdour**  
**Modèle cloud :** Azure Static Web Apps (PaaS)  
**Objectif :** donner aux citoyens une interface accessible pour poser des questions, consulter les sources et répondre à un quiz.

## Périmètre

L’application React communique avec le backend par HTTPS. Elle ne contient aucun secret serveur, ne se connecte pas directement à PostgreSQL et distingue clairement les réponses, les citations et les erreurs.

### Tâches

1. Concevoir les parcours assistant, bibliothèque de sources et quiz, avec navigation cohérente sur mobile et ordinateur.
2. Appeler les endpoints backend documentés; gérer chargement, absence de résultats, délais, erreurs et nouvelle tentative.
3. Afficher les références fournies par l’API (titre, organisme, lien, article/page, langue) sans les fabriquer.
4. Gérer français et arabe avec mise en page RTL; rendre les contenus et libellés compréhensibles et cohérents.
5. Respecter l’accessibilité clavier, les libellés, le contraste, les états de focus et la sémantique HTML.
6. Configurer URL d’API par environnement, CORS requis, routes statiques et variables publiques non sensibles.
7. Ajouter build et vérifications navigateur dans GitHub Actions; configurer un déploiement Azure Static Web Apps après décision de l’équipe.

## Livrables

- Application React compilable et configuration de build.
- Pages assistant, sources et quiz intégrées à l’API.
- Interface responsive et RTL vérifiée.
- Tests des parcours principaux et des erreurs d’API.
- Guide de configuration locale et de publication Azure, sans secrets.

## Critères de validation

- Les questions sont envoyées au backend sans inclure de clé privée.
- Les citations affichées correspondent à la réponse de l’API et ouvrent la source attendue.
- Le quiz révèle la correction uniquement après soumission.
- Navigation clavier, RTL et affichage mobile sont vérifiés dans un navigateur.
- L’application présente un état utile si le backend est lent ou indisponible.

## Dépendances

Le contrat du backend est la source de vérité pour les payloads. Les URLs et origines autorisées sont configurées par environnement; aucun endpoint interne ou secret n’est codé en dur.
