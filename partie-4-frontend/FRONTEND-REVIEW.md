# Livraison frontend SAWTNA — 22 novembre 2026

## 1. Dépôt et audit initial

Travail réalisé dans la copie locale **`sawtna-citizen`**, branche `main`, base `4bbf0ee` (`docs(nlp): add deployment diagrams and API contract`). Le dossier initial ouvert contenait NovaShop. Une extraction Git partielle de SAWTNA a permis de travailler sans télécharger les modèles OCR et corpus volumineux. Aucun changement non commité préexistant dans cette copie, aucune instruction `AGENTS.md` dans l’arbre inspecté. Aucun commit, push, merge ou déploiement effectué.

Lecture de `main.jsx`, `styles.css`, package/lockfile, Vite, README, GUIDE-LOCAL, index HTML, configuration statique, tests Playwright, workflow local et contrat OpenAPI. Lecture complémentaire des sérialiseurs backend et du quiz, sans modification.

Architecture existante : React/Vite, Lucide, CSS natif, quatre composants principaux dans le point d’entrée, dictionnaire FR/AR/darija, navigation par hash. Les trois parcours et les appels publics existaient déjà. La bibliothèque renvoie bien des métadonnées : il aurait été incorrect de la limiter d’office aux identifiants. OpenAPI définit les requêtes, mais les réponses 200 sont laissées non typées ; les validations ajoutées suivent les sérialiseurs observés.

Audit visuel avant modification : identité suisse blanc/gris/rouge déjà cohérente à préserver ; titre disproportionné, textes fréquemment à 9–12 px, contrastes secondaires faibles, réponse comprimée en deux colonnes, CSS surchargé et règles Analytics inutilisées. Risques fonctionnels : icône `RefreshCw` non importée dans les erreurs, ancien résultat conservé lors d’une nouvelle demande, réponses non validées, chargement bibliothèque confondu avec vide, absence d’annulation et risques de réponses dans l’ancienne langue, quiz réinitialisé au réessai, menu mobile et lien d’évitement fragiles.

## 2. Fonctionnalités préservées

Logo SAWTNA, accent rouge, navigation par ancres, trois langues, suggestions de questions, réponses extractives, citations et avertissements de revue, recherche documentaire locale, quiz corrigé par le serveur, liens de référence et séparation complète d’Analytics. Point d’entrée React, Vite, port local, proxy et configuration statique conservés. Aucune dépendance ajoutée et aucun fichier de verrouillage modifié.

## 3. Fichiers livrés

| Fichier | Modification |
| --- | --- |
| `src/main.jsx` | Composants existants améliorés : états, annulation, navigation, formulaires, résultats, métadonnées et liens sûrs |
| `src/styles.css` | Consolidation du CSS natif, suppression des règles inutilisées, typographie, contrastes, dispositions propres aux parcours et RTL |
| `src/api.js` | Helper fetch extrait et renforcé : base URL, timeout, erreurs, validation et protocoles de liens |
| `src/interface-copy.js` | Compléments FR/AR/darija et erreurs localisées ; aucune traduction des sources |
| `package.json` | Scripts `test` et `test:ui`, sans nouvelle dépendance |
| `playwright.frontend.config.js` | Suite citoyenne isolée sur le port 5185 |
| `playwright.config.js` | Suite historique explicitement sélectionnée, option de navigateur installé |
| `tests/api.test.js` | Cas API, URL, payloads malformés, erreurs et timeout |
| `tests/citizen.spec.js`, `tests/fixtures.js` | Parcours, langues, dimensions, erreurs, clavier, courses et quiz complet ; données strictement réservées aux tests |
| `tests/app.spec.js` | Attentes adaptées au nouveau titre, à la navigation directe et au message d’erreur localisé ; intégration historique conservée |
| `README.md`, `GUIDE-LOCAL.md` | Architecture réelle, contrats observés, usage, tests, build Azure et limites |
| `FRONTEND-REVIEW.md` | Présent rapport |

## 4. Design et parcours

Direction : une interface civique sobre, alignée sur l’identité existante. Titres réduits, corps de texte lisible, bordures discrètes, couleurs fonctionnelles, sans dégradés ni cartes décoratives. Accent de marque conservé ; rouge des petits textes/actions légèrement assombri pour améliorer le contraste.

**Assistant** : saisie rapprochée du début de page, périmètre consultable dans un élément natif dépliable, avertissement adjacent à la question, lecture des réponses en pleine largeur. Question et réponse distinguées, citations numérotées, paragraphes conservés, lien page PDF sûr, focus sur le résultat, envoi clavier avec gestion de composition, blocage des doublons, effacement du résultat périmé, erreurs et abstention explicites. L’affirmation absolue de confidentialité a été remplacée par une description vérifiable du traitement indépendant des questions.

**Bibliothèque** : catalogue en lignes, recherche visible par métadonnées effectivement disponibles, recherche insensible aux accents latins, compteur, titres mixtes alignés sur la page et direction du texte respectée. Chargement, panne, bibliothèque vide et filtre sans résultat distingués. Les champs absents ne produisent ni exception ni titre/lien inventé.

**Quiz** : questionnaire continu conservé, titre serveur, instructions, progression native, groupes radio et cibles confortables, prévention des doublons, score serveur uniquement, corrections après soumission, focus du résultat et redémarrage. Le réessai après échec conserve les réponses. Aucune question ou correction codée en dur dans l’application.

## 5. Langues et accessibilité

Interface FR, AR RTL et darija latine `ary-Latn`, paramètre API toujours `darija`. Langue conservée dans la navigation et le stockage local quand disponible. Requêtes obsolètes annulées au changement de langue. Contenus mixtes avec `dir="auto"`, langue des citations et de la réponse extractive issue de la source quand connue. Pas de traduction des documents officiels.

Lien d’évitement corrigé, `aria-current`, contrôles nommés, focus visibles, navigation horizontale directement accessible sur mobile, déplacement du focus lors de navigation et résultats, annonces asynchrones, labels natifs, radio utilisables aux flèches et respect de la préférence de réduction des mouvements. Vérification pratique, sans prétendre à une certification WCAG complète.

## 6. Vérifications exécutées

| Vérification | Résultat réel |
| --- | --- |
| `npm ci` | Réussi, 69 paquets ajoutés, audit npm : 0 vulnérabilité signalée à l’exécution |
| Build initial `npm run build` | Réussi avant branchement des changements |
| Suite historique initiale avec Chrome, timeout borné à 5 s | 7 échecs ; services backend/Analytics absents et états d’erreur initiaux fragiles. Ce n’est pas une validation d’intégration réussie |
| `npm test` | 5 tests réussis, dont timeout simulé à 65 s et page source malformée |
| `SAWTNA_BROWSER_CHANNEL=chrome npm run test:ui` | 23 tests réussis ; 12 combinaisons langue/largeur couvrent chacune les trois parcours et leurs résultats |
| Build de production avec URL staging | Réussi ; présence de l’origine publique dans le bundle confirmée |
| Build final sans variable staging | Réussi ; configuration de développement/proxy conservée |
| `git diff --check` | Réussi ; seuls des avertissements Windows de normalisation CRLF/LF, pas d’erreur de whitespace |
| Lint | Aucun script/configuration lint existant ; non exécuté |

Tests navigateur : absence de débordement horizontal aux quatre largeurs, absence d’erreurs JS/console sur les parcours valides, payloads envoyés, sélection des trois langues, état vide/chargement/erreur, JSON illisible, sources dangereuses, réessai, double envoi, langue changée pendant une requête, historique, focus, radio clavier, texte long RTL, quiz à quatre questions et absence de score client. Les pannes réseau intentionnelles font partie des scénarios d’erreur et ne sont pas dissimulées.

Captures générées : 60 vues finales dans `work/screenshots/` (assistant, réponse, bibliothèque, quiz, résultat × 3 langues × 4 largeurs). Revue visuelle effectivement réalisée sur des captures desktop, tablette et mobile, notamment français 1280/390, arabe 1280/360 et darija 768. Cette revue a entraîné des corrections supplémentaires de densité mobile, placement de l’avertissement, lien d’évitement et alignement de titres mixtes. Les captures utilisent des fixtures de test, pas un corpus staging vérifié.

## 7. Intégration réelle, limites et statuts

**Implémenté et testé** : frontend, URL de base, requêtes et réponses représentatives des sérialiseurs inspectés, états et navigation, français/arabe/darija, tailles demandées, clavier et build. Les fixtures ne peuvent pas remplacer silencieusement une API en production car elles sont importées uniquement dans les tests.

**Bloqué par disponibilité externe** : deux GET réels vers staging (`/api/documents`, `/api/quiz?language=ar`) ont expiré après 15 s chacun le 22 novembre, hors plage annoncée 14:00–19:00 Maroc. Aucun succès d’intégration distante n’est revendiqué. POST ask/submit réels, CORS de production et chaîne NLP restent non vérifiés.

**Implémenté mais non validé exhaustivement** : nouvelles formulations arabes/darija à relire par une personne native ; expérience lecteur d’écran, Safari/Firefox, claviers mobiles réels et zoom navigateur non couverts par cette passe Chrome desktop à viewports simulés.

**Non implémenté car hors périmètre** : modification backend/NLP/ETL/Analytics, contrats, modèles et DB ; pagination ou métadonnées serveur supplémentaires ; nouvelle API IA ; déploiement Azure. Le dépôt ne contient pas de workflow de publication Azure à modifier. La configuration de son pipeline externe reste à confirmer avec son responsable.

## 8. Actions restantes pour Aya

1. Ouvrir la copie `sawtna-citizen/partie-4-frontend`, suivre `GUIDE-LOCAL.md` et examiner les captures dans `work/screenshots/`.
2. Faire relire les libellés arabes/darija ; confirmer le choix de darija latine déjà présent dans l’application.
3. Pendant la disponibilité staging, vérifier les trois parcours réels et CORS depuis l’origine frontend autorisée ; relancer la suite historique lorsque tous ses services sont disponibles.
4. Avant une éventuelle publication autorisée, fournir `VITE_API_BASE_URL` à l’étape de build du pipeline Azure ; publier `dist`, sans clé privée dans les variables Vite.

Commit suggéré, non exécuté : `feat(frontend): refine citizen journeys, accessibility and multilingual resilience`.

## 9. Seconde passe de présentation

Après la demande complémentaire d’amélioration, l’en-tête a été simplifié : marque et langue sur une première ligne, puis les trois liens de navigation toujours visibles. Cette évolution libère l’espace occupé par la barre latérale et rend les parcours accessibles directement sur téléphone. Les styles du volet précédent ont été retirés, sans nouvelle bibliothèque ni routeur.

Le bouton d’envoi affiche désormais un libellé dans les trois langues. Les indications clavier et le compteur disposent de lignes adaptées au petit écran. Le périmètre de l’assistant reste consultable via un élément dépliable natif.

La bibliothèque possède des filtres construits à partir des langues réellement présentes dans les données. Ils se combinent avec la recherche ; le total des passages suit les documents affichés. Un état sans résultat permet de réinitialiser simultanément recherche et langue. Aucun appel backend supplémentaire.

Validation de cette passe : `npm run build` réussi ; `npm run test:ui` avec Chrome, 23 tests réussis, dont le nouveau scénario combinant recherche, filtre et compteur. Revue effective des captures françaises desktop/mobile et arabes RTL, notamment bibliothèque et assistant. `git diff --check` réussi et aucun changement hors frontend. Le serveur local sur 5175 répond HTTP 200 et sert le nouvel en-tête. README et guide local actualisés. Les limites d’intégration réelle et de relecture linguistique de la section 7 restent applicables.
