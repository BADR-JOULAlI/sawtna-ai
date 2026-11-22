# Service NLP — Azure Container Apps

Déploiement courant du microservice NLP de Sawtna. Le frontend ne contacte pas
directement ce service : le backend l’appelle en HTTPS.

## Ressources déployées

| Élément | Valeur |
|---|---|
| Groupe de ressources | `sawtna-rg` |
| Région | `Austria East` (`austriaeast`) |
| Azure Container Registry | `sawtnaacr21nov26.azurecr.io` (Basic) |
| Image | `sawtnaacr21nov26.azurecr.io/sawtna-nlp:v1` |
| Environnement Container Apps | `sawtna-aca-env` |
| Container App | `sawtna-nlp` |
| URL | `https://sawtna-nlp.purplebush-3bda44a9.austriaeast.azurecontainerapps.io` |
| Port / ingress | `8000` / HTTPS externe |
| Ressources | 1 vCPU, 2 GiB RAM, 0–1 réplique |
| Modèle | `intfloat/multilingual-e5-small`, CPU, vecteurs 384D |
| Identité de pull ACR | `sawtna-nlp-acrpull`, rôle `AcrPull` sur le registre |

Le minimum de répliques à zéro limite la consommation hors requêtes; le premier
appel après une période d’inactivité peut subir un démarrage à froid. Le registre
ACR Basic reste une ressource facturée tant qu’il existe.

## Routes

- `GET /health` : contrôle de santé sans authentification.
- `POST /v1/embeddings` : exige `X-Service-Key`; accepte `texts` et `kind`
  (`query` ou `passage`), retourne des vecteurs 384D et le nom du modèle.

## Clé de service

La valeur est stockée dans le secret Container Apps `service-key`. Une copie
locale de la valeur actuelle se trouve dans `.secrets/sawtna-service-key.txt`;
`.secrets/` est exclu de Git. Ne jamais mettre la valeur dans le code, les
fichiers de configuration suivis par Git ou les journaux.

Le backend doit utiliser exactement la même valeur dans `SAWTNA_SERVICE_KEY`
et pointer `SAWTNA_NLP_URL` vers l’URL ci-dessus. Le backend de staging est
hébergé séparément sur une VM en Poland Central; cette Container App a donc un
ingress HTTPS externe. La clé doit être transmise au responsable du backend par
un canal sécurisé et configurée sur la VM avant le test d’intégration.

## Reconstruire et publier une version

Depuis la racine du dépôt, avec Docker Desktop et Azure CLI connectés :

```powershell
docker build -f commun/infra/Dockerfile.nlp -t sawtna-nlp:v2 .
az acr login --name sawtnaacr21nov26
docker tag sawtna-nlp:v2 sawtnaacr21nov26.azurecr.io/sawtna-nlp:v2
docker push sawtnaacr21nov26.azurecr.io/sawtna-nlp:v2
az containerapp update --name sawtna-nlp --resource-group sawtna-rg --image sawtnaacr21nov26.azurecr.io/sawtna-nlp:v2
```

Utiliser un nouveau tag à chaque version publiée pour garder les déploiements
traçables. Ne pas activer les identifiants administrateur ACR; l’application
tire l’image avec son identité managée.

## Vérifier le service

```powershell
$baseUrl = 'https://sawtna-nlp.purplebush-3bda44a9.austriaeast.azurecontainerapps.io'
Invoke-RestMethod "$baseUrl/health"
```

Pour vérifier `POST /v1/embeddings`, envoyer un JSON conforme au contrat
`commun/packages/contracts/nlp.openapi.json` avec le header `X-Service-Key`.
Une requête sans clé doit recevoir `401`.
