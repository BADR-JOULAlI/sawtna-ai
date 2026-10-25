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
