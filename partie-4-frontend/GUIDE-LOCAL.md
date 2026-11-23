# Guide local — SAWTNA citoyen

## Préparer

Depuis `partie-4-frontend`, avec Node 22.12+ et npm :

```powershell
npm ci
npm run dev
```

Ouvrir http://127.0.0.1:5175. Vite refuse un port déjà occupé ; ne pas arrêter un service existant sans l’identifier. Le backend local doit être démarré selon le guide de l’équipe backend. Le frontend n’exige ni clé serveur ni connexion directe à la base.

## Backend local

Sans `VITE_API_BASE_URL`, les requêtes `/api/*` passent par le proxy Vite vers `http://127.0.0.1:8010`. Pour un backend local sur un autre port :

```powershell
$env:SAWTNA_API_URL='http://127.0.0.1:8010'
npm run dev
```

Le proxy n’est pas inclus dans les fichiers de production.

## Backend staging

Créer un fichier local `.env.local` (ignoré par Git) :

```dotenv
VITE_API_BASE_URL=https://sawtna-api-staging-50fe10.polandcentral.cloudapp.azure.com
```

Redémarrer Vite après un changement. Le navigateur contacte alors directement cette origine ; le backend doit autoriser l’origine du frontend via CORS. Aucun contournement de CORS ou secret ne doit être ajouté dans React.

Disponibilité annoncée : **14:00–19:00, heure locale du Maroc**. Un timeout hors plage ne démontre pas un défaut frontend. Pour revenir au proxy local, retirer cette ligne ou vider sa valeur, puis redémarrer Vite.

## Vérifier les parcours

1. **Assistant** : choisir une suggestion ou saisir une question ; Entrée envoie, Maj+Entrée ajoute une ligne. Vérifier chargement, réponse, passage, page et lien source. Essayer une question hors corpus : une abstention ne doit pas devenir une réponse inventée. Réessayer après une erreur. Les questions sont indépendantes.
2. **Bibliothèque** : contrôler les métadonnées reçues, rechercher un titre/identifiant/langue, combiner la recherche avec un filtre de langue. Les filtres ne montrent que les langues réellement présentes. Vérifier que le nombre de passages correspond aux documents affichés. Rechercher un terme absent puis réinitialiser les filtres. Vérifier l’avertissement de revue et les liens disponibles.
3. **Quiz** : répondre à toutes les questions ; le bouton reste indisponible tant qu’il en manque. Vérifier le score serveur et les références après soumission. Recommencer. En cas d’erreur, le réessai conserve les choix.
4. **Langues** : tester français, arabe et darija depuis chaque espace. Vérifier le RTL arabe, les citations dans leur langue et le texte mixte darija. La langue persiste au rechargement ; changement de langue = nouveau quiz / nouvelle question.
5. **Clavier** : Tab vers « Aller au contenu », liens, sélecteur et formulaire. Les trois liens de navigation sont visibles directement, même sur mobile. Les flèches changent les options radio ; Entrée active un filtre documentaire. Tester retour/précédent du navigateur.
6. **Responsive** : 360, 390, 768 et 1280 px ; vérifier longs titres, citations, recherche, résultats et RTL. Tester le réglage système de réduction des animations.

## Tests isolés et compilation

```powershell
npm test
npx playwright install chromium
npm run test:ui
npm run build
```

Si Chrome est déjà installé :

```powershell
$env:SAWTNA_BROWSER_CHANNEL='chrome'
npm run test:ui
```

Les tests isolés utilisent Vite sur **5185**, avec une base API vide propre à ce serveur. Ce port doit être libre. Les fixtures se trouvent exclusivement dans `tests/fixtures.js` et les tests Playwright ; elles ne sont pas importées par `src`. Aucun backend n’est nécessaire pour cette suite. Les captures générées incluent les trois langues et quatre largeurs dans `work/screenshots/`. Le résultat JSON se trouve dans `test-results/citizen-results.json`.

La suite historique `npm run test:e2e` nécessite la pile réelle déjà démarrée, y compris Analytics pour son test autonome. Elle conserve les vérifications initiales et les sorties du workflow partagé. Ne pas confondre sa validation d’intégration réelle avec `test:ui`. Aucun script lint n’est configuré dans ce projet.

## Build destiné à Azure Static Web Apps

Exemple de compilation locale, **sans publication** :

```powershell
$env:VITE_API_BASE_URL='https://sawtna-api-staging-50fe10.polandcentral.cloudapp.azure.com'
npm run build
npm run preview
```

`preview` sert les fichiers compilés ; il ne fournit pas de proxy backend. La variable Vite est figée dans le bundle. Pour le pipeline Azure de l’équipe, la définir dans l’environnement de l’étape de build (application `partie-4-frontend`, sortie `dist`). Le dépôt inspecté n’inclut pas le workflow de publication : confirmer sa configuration avec son responsable. Changer une variable cloud après le build ne change pas le bundle déjà publié. Aucun déploiement n’est requis pour tester ces modifications.

## Dépannage

- **Connexion impossible** : vérifier l’onglet Réseau, le backend local ou la plage de disponibilité staging. Le frontend propose un réessai manuel.
- **HTTP 429** : attendre une minute avant de réessayer.
- **HTTP 503** : dépendance backend indisponible ; ne pas appeler directement NLP depuis le navigateur.
- **Réponse incomplète** : vérifier que l’URL retourne du JSON et non une page HTML de proxy ; comparer le payload aux sérialiseurs backend. Ne pas inventer un résultat de secours.
- **Délai dépassé** : le client borne l’attente à 65 secondes. Aucun retry automatique.
- **CORS** : faire vérifier les origines autorisées côté backend par son responsable. Les tests isolés ne valident pas CORS réel.
- **Bibliothèque vide** : absence réelle de documents, distincte d’une panne ou d’un filtre sans correspondance.
- **Langue non mémorisée** : le stockage local peut être désactivé ; le sélecteur fonctionne toujours pendant la session.
- **NLP / modèles incompatibles** : hors périmètre frontend ; transmettre au responsable backend/NLP.

Toutes les variables `VITE_*` sont visibles par le navigateur. Ne jamais y placer de clés de service/admin, credentials NLP/DB ou secrets Azure. Aucune clé n’est nécessaire pour les quatre endpoints citoyens.

Les résultats exécutés et les limites de vérification sont consignés dans [FRONTEND-REVIEW.md](FRONTEND-REVIEW.md).
