# Google Cloud — NLP et Analytics

## Cloud Run NLP

L’image de base exécute la baseline autonome. Pour l’encodeur E5 entraîné, construire commun/infra/Dockerfile.nlp : PyTorch CPU et le modèle sont inclus dans l’image pour éviter un téléchargement à chaque démarrage.
Configurer SAWTNA_SERVICE=nlp, SAWTNA_EMBEDDER, SAWTNA_SERVICE_KEY et le port fourni par Cloud Run via PORT.
Choisir une mémoire mesurée, min-instances=0, maximum d’instances et budget bornés.
L’API /v1/embeddings exige une clé même si l’origine Cloud Run est accessible. Pour une authentification IAM additionnelle, ajouter un jeton d’identité côté appelant avant de restreindre l’origine.

## Compute Engine Analytics

Construire commun/infra/Dockerfile et exécuter SAWTNA_SERVICE=analytics.
Configurer SAWTNA_ANALYTICS_DATABASE_URL ou un volume SQLite persistant, SAWTNA_BACKEND_URL, les clés et un proxy HTTPS.
Le dashboard est servi sur /dashboard ; les assets sont inclus dans l’image. VITE_CITIZEN_URL doit être réglé au build si l’origine citoyenne diffère de localhost.
Tester qu’un utilisateur sans clé ne lit pas les KPI, puis vérifier l’augmentation d’un compteur après une vraie question.
Choisir une rétention des identifiants techniques et sauvegarder la base avant toute mise à jour.
