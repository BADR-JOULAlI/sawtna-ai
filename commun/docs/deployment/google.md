# Google Cloud — ancien emplacement NLP / Analytics

Le service NLP a été déplacé vers Azure Container Apps. Ce fichier est conservé
comme historique ; la procédure active est dans `azure-container-apps.md`.

## Ancienne procédure Cloud Run NLP

L’image de base exécute la baseline autonome. Pour l’encodeur E5 entraîné, construire commun/infra/Dockerfile.nlp : PyTorch CPU et le modèle sont inclus dans l’image pour éviter un téléchargement à chaque démarrage.
Configurer SAWTNA_SERVICE=nlp, SAWTNA_EMBEDDER, SAWTNA_SERVICE_KEY et le port fourni par Cloud Run via PORT.
Choisir une mémoire mesurée, min-instances=0, maximum d’instances et budget bornés.
L’API /v1/embeddings exige une clé même si l’origine Cloud Run est accessible. Pour une authentification IAM additionnelle, ajouter un jeton d’identité côté appelant avant de restreindre l’origine.

## Compute Engine Analytics

Construire commun/infra/Dockerfile et exécuter SAWTNA_SERVICE=analytics.
Configurer SAWTNA_ANALYTICS_DATABASE_URL ou un volume SQLite persistant, SAWTNA_BACKEND_URL, les clés et un proxy HTTPS.
Le dashboard est une application statique autonome dans partie-5-analytics/dashboard/ et est servi sur /dashboard par le service Analytics. Le frontend citoyen est déployé séparément dans Azure Static Web Apps et n’est pas inclus dans cette image.
Tester qu’un utilisateur sans clé ne lit pas les KPI, puis vérifier l’augmentation d’un compteur après une vraie question.
Choisir une rétention des identifiants techniques et sauvegarder la base avant toute mise à jour.
