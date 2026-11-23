# SAWTNA — Interface citoyenne

Responsable : Aya Sdour · Partie 4 · React / Azure Static Web Apps.

SAWTNA aide à comprendre les institutions et le vote au Maroc à partir du corpus disponible. Projet étudiant indépendant, sans affiliation politique. L’interface ne recommande aucun candidat et ne remplace pas les informations officielles à jour.

## Trois espaces

- **Assistant** : questions indépendantes, réponses extractives du backend, passages cités dans leur langue originale, liens documentaires contrôlés, abstention explicite lorsque le corpus est insuffisant. Aucune génération externe ni historique de conversation.
- **Bibliothèque** : catalogue des documents indexés, recherche locale par titre, identifiant et langue, filtres par langues effectivement présentes. Le compteur de passages suit les résultats filtrés. Les titres, passages, langues et statuts viennent du backend ; un identifiant reste affichable lorsque les métadonnées sont absentes.
- **Quiz** : questions et options reçues du serveur, choix radio natifs, progression, soumission de toutes les réponses, résultat et corrections calculés exclusivement côté backend. Un échec de soumission conserve les choix.

## Architecture conservée

React 19, React DOM, Vite 7, plugin React et Lucide ; Playwright pour le navigateur. Versions exactes verrouillées dans `package-lock.json`. Aucune nouvelle dépendance.

- `src/main.jsx` : point d’entrée, navigation par ancres `#assistant`, `#library`, `#quiz`, composants existants et dictionnaire initial.
- `src/interface-copy.js` : libellés complémentaires et messages d’erreur localisés.
- `src/api.js` : fetch public, URL de base, timeout de 65 secondes, annulation, validation des réponses et liens HTTP(S).
- `src/styles.css` : CSS natif consolidé, identité blanc/gris/rouge, tailles lisibles et propriétés logiques RTL.
- `public/staticwebapp.config.json` : fallback SPA et en-têtes statiques existants.

Aucun routeur supplémentaire. Retour/précédent utilise l’historique des ancres. La langue est conservée pendant la navigation et dans le stockage local lorsque disponible. La navigation vers un autre espace réinitialise son état temporaire, comme auparavant. Un changement de langue réinitialise le quiz et l’assistant et annule leurs requêtes en cours pour éviter un résultat dans la mauvaise langue.

## API publique

Le contrat `../commun/packages/contracts/backend.openapi.json` reste inchangé. Il définit les requêtes mais laisse les réponses HTTP 200 non typées (`schema: {}`). Les validations frontend et fixtures reposent également sur les sérialiseurs backend inspectés, sans modification de ceux-ci.

| Endpoint | Envoi | Réponse utilisée |
| --- | --- | --- |
| `POST /api/ask` | `question` : 3–1500 caractères ; `language` : `fr`, `ar`, `darija` | `answer`, `answerable`, `sources` ; références : titre, section, page, langue, statut, texte, URL lorsqu’ils sont fournis |
| `GET /api/documents` | Aucun | `documents`, `total`, `passages` ; identifiant et nombre de passages, métadonnées disponibles |
| `GET /api/quiz?language=…` | Langue | `id`, `title`, `questions[{id, question, options}]` |
| `POST /api/quiz/submit` | `language`, `answers` : identifiants → indices entiers | `correct`, `total`, `score`, `corrections` avec explications et références disponibles |

Les données illisibles, réponses HTTP en erreur, pannes réseau et délais dépassés produisent un message localisé et un réessai manuel. Aucun retry automatique, aucune substitution par des réponses factices. Aucun appel direct à NLP, PostgreSQL, ingestion, administration ou Analytics.

## Langues, présentation et accessibilité

Français LTR, arabe RTL, darija de l’interface en écriture latine (`ary-Latn`). Le backend reçoit toujours `darija`. Les contenus mixtes utilisent `dir="auto"` et les citations gardent leur langue. Les libellés arabes/darija ajoutés demandent une relecture linguistique native ; aucune traduction des documents ou réponses n’est fabriquée.

Identité SAWTNA et accent rouge préservés. L’en-tête horizontal regroupe la marque et le choix de langue ; les trois espaces sont directement visibles sur ordinateur comme sur téléphone, sans menu à ouvrir. L’assistant privilégie une lecture verticale et un bouton d’envoi explicite, le catalogue des lignes séparées, le quiz des groupes de choix. Navigation active, lien d’évitement, focus visibles, déplacement du focus vers résultats, formulaire natif, annonces de chargement, erreurs actionnables et réduction des mouvements.

Vérifications navigateur ciblées à 360, 390, 768 et 1280 px. Elles ne constituent pas une certification WCAG ni une validation exhaustive avec lecteur d’écran.

## Installation et validation

Node 22.12+ recommandé (Vite 7), npm et navigateur Playwright.

```powershell
npm ci
npm run dev
npm run build
npm test
npx playwright install chromium
npm run test:ui
```

`test:ui` démarre son propre Vite sur 5185 et intercepte les quatre API avec des fixtures uniquement dans les tests. Chrome installé peut être utilisé avec `$env:SAWTNA_BROWSER_CHANNEL='chrome'`. Captures : `work/screenshots/` ; rapport : `test-results/citizen-results.json` (ignorés par Git).

`npm run test:e2e` conserve la suite d’intégration existante, exigeant le backend réel sur 8010 et le service Analytics séparé sur 8012 pour son test historique. Cette suite écrit encore dans `commun/docs/verification/`, conformément au workflow existant ; elle ne fait pas partie des tests isolés.

Voir [GUIDE-LOCAL.md](GUIDE-LOCAL.md) pour les scénarios et [FRONTEND-REVIEW.md](FRONTEND-REVIEW.md) pour les résultats effectivement exécutés.

## Build et Azure

En développement, une base vide conserve les chemins `/api/*` et le proxy Vite vers `http://127.0.0.1:8010` (ou `SAWTNA_API_URL`). En production, fournir `VITE_API_BASE_URL` **avant** `npm run build`. L’origine HTTPS est recommandée ; une terminaison `/api` ou `/` est normalisée pour éviter `/api/api`.

La sortie à publier est `partie-4-frontend/dist`. Le dépôt inspecté ne contient pas de workflow de déploiement Azure Static Web Apps : `.github/workflows/local-stack.yml` valide la pile locale. Dans le pipeline de publication de l’équipe, la variable doit être présente dans l’environnement de l’étape qui exécute Vite ; un paramètre modifié après compilation ne réécrit pas les fichiers JavaScript. Aucun déploiement ni paramètre cloud n’a été modifié.

## Limites

Disponibilité staging annoncée : 14:00–19:00, heure du Maroc. Les appels de vérification hors plage ont expiré ; l’intégration staging et CORS restent à vérifier durant cette plage. La recherche bibliothèque est locale, sans recherche plein texte ni dates inventées. Pas de pagination serveur ajoutée. Les échéances et l’actualité législative dépendent du corpus. Le problème de compatibilité des modèles NLP reste hors périmètre.

Seules des variables publiques peuvent porter le préfixe `VITE_`. Ne jamais y placer de clé privée, d’accès serveur, de base de données ou de déploiement.
