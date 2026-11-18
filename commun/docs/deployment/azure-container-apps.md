# Service NLP — Azure Container Apps

Le microservice NLP de Badr est déployé dans Azure Container Apps. Le backend
de Soulayman l’appelle par HTTPS ; le frontend ne contacte jamais directement
le service NLP.

## Construire l’image dans Azure Container Registry

Depuis la racine du dépôt :

~~~powershell
az login
az group create --name sawtna-rg --location westeurope
az acr create --resource-group sawtna-rg --name sawtnaacr --sku Basic
az acr build --registry sawtnaacr --image sawtna-nlp:v1 --file commun/infra/Dockerfile.nlp .
~~~

## Déployer le conteneur

~~~powershell
az extension add --name containerapp --upgrade
az containerapp up `
  --name sawtna-nlp `
  --resource-group sawtna-rg `
  --location westeurope `
  --image sawtnaacr.azurecr.io/sawtna-nlp:v1 `
  --target-port 8000 `
  --ingress external
~~~

Configurer ensuite les variables et secrets sans les commiter :

~~~text
SAWTNA_SERVICE=nlp
SAWTNA_EMBEDDER=multilingual-e5-small
SAWTNA_MODEL_DEVICE=cpu
SAWTNA_SERVICE_KEY=<secret>
~~~

Le service expose `/health` et `/v1/embeddings`. Le header `X-Service-Key`
reste obligatoire. Utiliser une clé différente de la valeur locale et limiter
les instances et la mémoire selon les mesures de charge.

## Connexion du backend

Dans l’environnement Azure VM de Soulayman :

~~~text
SAWTNA_NLP_URL=https://<fqdn-container-app>
SAWTNA_SERVICE_KEY=<même-secret>
~~~

Le contrat `commun/packages/contracts/nlp.openapi.json` ne change pas. Tester
la santé, l’authentification, la dimension 384 et les erreurs avant de relier
la recherche backend.
