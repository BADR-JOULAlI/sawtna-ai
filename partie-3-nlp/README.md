# Étudiant 3 — Microservice NLP sur Google Cloud Run

**Responsable indiqué dans le cahier des charges : Badr Joulali**  
**Modèle cloud :** Google Cloud Run (PaaS)  
**Objectif :** fournir au backend un service NLP conteneurisé et versionné pour préparer les textes et calculer des embeddings multilingues.

## Périmètre

Le service reste indépendant du backend et expose une interface stable. L’exécution locale et l’évaluation précèdent tout déploiement Cloud Run. Le service n’accède pas directement à la base de données.

### Tâches

1. Préciser les langues couvertes (français, arabe, darija), leurs limites et les cas connus de faible qualité.
2. Implémenter le prétraitement sans supprimer les informations nécessaires aux citations ou au sens juridique.
3. Choisir et versionner le modèle d’embeddings; enregistrer nom, version, dimension, normalisation et empreinte.
4. Exposer des endpoints protégés et validés selon `commun/packages/contracts/nlp.openapi.json`.
5. Garantir que requêtes et documents utilisent le même modèle et la même dimension; refuser les incompatibilités.
6. Conteneuriser pour Cloud Run, régler mémoire, CPU, concurrence, démarrage à froid et taille maximale des lots.
7. Mesurer latence et qualité de recherche sur un jeu de questions annotées, séparé par langue.
8. Ajouter limites, journalisation sans contenu sensible, réponses d’erreur et comportement en cas de modèle indisponible.

## Livrables

- Microservice NLP exécutable localement et image conteneur reproductible.
- Documentation des routes, authentification, limites et version du modèle.
- Évaluation documentée par langue (rappel/rang des passages pertinents, latence et limites).
- Tests de schéma, dimension, normalisation, authentification et erreurs.
- Configuration Cloud Run et consignes de coût/sécurité, sans clé commise.

## Critères de validation

- Les réponses respectent exactement les schémas communs et les vecteurs ont la dimension déclarée.
- Le backend peut détecter le modèle utilisé et ne mélange pas des espaces vectoriels incompatibles.
- Les cas français, arabe et darija sont testés avec des exemples relus.
- Les mesures indiquent le matériel, le corpus, la méthode et les limites; une baseline n’est pas présentée comme un modèle entraîné.
- Le conteneur démarre et passe le contrôle de santé en local.

## Dépendances

Le backend Azure appelle le service avec une identité ou clé de service fournie hors frontend. Le pipeline de l’étudiant 1 alimente les textes; l’évaluation doit employer des passages dont les sources ont été revues.


## Exécution du service existant

# Étudiant 3 — NLP · Cloud Run

Code : nlp_service/main.py.

~~~powershell
python -m uvicorn sawtna.nlp:app --host 127.0.0.1 --port 8011 --no-access-log
python -m pytest commun/tests/test_nlp_analytics.py
~~~

POST /v1/embeddings : jusqu’à 64 textes, 12000 caractères chacun, kind=query ou passage, clé X-Service-Key. Sortie : vecteurs normalisés 384D et modèle.

- SAWTNA_EMBEDDER=concept-hash-v1 : baseline déterministe autonome. Ce n’est pas un modèle appris.
- SAWTNA_EMBEDDER=multilingual-e5-small : véritable encodeur intfloat/multilingual-e5-small. Installation :

~~~powershell
python -m pip install -e ".[ml]"
$env:SAWTNA_EMBEDDER = "multilingual-e5-small"
$env:SAWTNA_MODEL_DEVICE = "cpu"
~~~

Le premier lancement télécharge le modèle. CPU dans Cloud Run ; cuda peut être choisi en local si PyTorch et le pilote sont compatibles.
Ne jamais mélanger des modèles dans le même index de recherche.
Le benchmark Darija complet doit être constitué avec l’équipe ; le petit jeu de régression ne certifie pas la qualité générale.
