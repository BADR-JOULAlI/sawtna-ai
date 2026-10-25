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


## Exécution du service existant

# Étudiant 4 — Frontend · Azure Static Web Apps

React, Vite, Lucide. Design Swiss : Helvetica, blanc/gris neutre, accent rouge #E4002B, grille, responsive et RTL.

~~~powershell
npm ci
npm run dev
npm run build
npx playwright install chromium
npm run test:e2e
~~~

Routes : #assistant, #library, #quiz, #dashboard.
Vite utilise 5175 et refuse un autre port. Son proxy /api vise 127.0.0.1:8010.
Pour Azure, définir VITE_API_BASE_URL sur l’origine HTTPS du backend avant le build. Les variables Vite sont publiques : aucune clé de service ne doit y figurer.
Le dashboard demande une clé saisie par l’admin et ne la conserve pas dans localStorage.
Analytics sert le même build sur /dashboard. VITE_CITIZEN_URL règle les liens de retour citoyen.
