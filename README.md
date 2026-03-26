# Puls-Events — POC RAG


![CI](https://github.com/yoann-donizetti/puls-events-rag/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10-blue)
![Tests](https://img.shields.io/badge/tests-pytest-green)
![Vector Search](https://img.shields.io/badge/vector%20search-FAISS-purple)
![RAG](https://img.shields.io/badge/RAG-LangChain-orange)
![LLM](https://img.shields.io/badge/LLM-Mistral-red)
![API](https://img.shields.io/badge/API-FastAPI-009688)
![Docker](https://img.shields.io/badge/docker-ready-blue)


POC de système **Retrieval Augmented Generation (RAG)** permettant de répondre à des questions en langage naturel sur des événements culturels à partir des données OpenAgenda.

Ce projet démontre la faisabilité d’un moteur de recherche intelligent basé sur des données réelles, prêt à être intégré dans une application métier.

Le système combine :

- recherche vectorielle **FAISS**
- orchestration **LangChain**
- génération **Mistral**
- API **FastAPI**
- conteneurisation **Docker**

---

## Sommaire 
- [Contexte métier](#contexte-métier)
- [Demo rapide](#démo-rapide)
- [Objectif](#objectif)
- [Choix techniques](#choix-techniques)
- [Structure du projet](#structure-du-projet)
- [Pipeline du projet](#pipeline-du-projet)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Collecte des événements OpenAgenda](#collecte-des-événements-openagenda)
- [Paramètres d'ingestion OpenAgenda](#paramètres-dingestion-openagenda)
- [Schéma du dataset](#schéma-du-dataset)
- [Pipeline data](#pipeline-data)
- [Validation qualité des données](#validation-qualité-des-données)
- [Vectorisation et indexation FAISS](#vectorisation-et-indexation-faiss)
- [Pipeline RAG](#pipeline-rag)
- [Pipeplines automatisés](#pipelines-automatisés)
- [API REST](#api-rest)
- [Tests](#tests)
- [Architecture  globale](#architecture-globale)
- [Schéma UML de l'architecture](#schéma-uml-de-larchitecture)
- [Architecture RAG](#architecture-rag)
- [Evaluation du système RAG](#évaluation-du-système-rag)
- [Résultat globaux RAGAS](#résultats-globaux-ragas)
- [Secrets](#secrets)
- [Dataset](#dataset)
- [Exécution avec Docker](#exécution-avec-docker)
- [Roadmap](#roadmap)


## Contexte métier

Les plateformes d’événements culturels proposent souvent un grand volume d’informations difficile à exploiter pour un utilisateur.

L’objectif est de permettre à un utilisateur de poser une question en langage naturel (ex : "atelier cuisine à Béziers") et d’obtenir une réponse pertinente basée sur des événements réels issus d’OpenAgenda.

---

## Démo rapide

```bash
docker build -t puls-events-rag .
docker run --env-file .env -p 8000:8000 puls-events-rag
```


## Objectif

Réaliser un Proof of Concept (POC) d’un système **RAG (Retrieval Augmented Generation)** permettant de répondre à des questions sur des événements culturels.

Le système s’appuie sur :

- **OpenAgenda** pour la récupération des événements
- **LangChain** pour l’orchestration du pipeline RAG
- **FAISS** pour la recherche vectorielle
- **Mistral** pour la génération de réponses

---

## Choix techniques

Les choix technologiques ont été faits pour répondre aux contraintes de performance, de simplicité et de reproductibilité :

- FAISS : moteur de recherche vectorielle rapide et local, adapté à un POC
- LangChain : orchestration du pipeline RAG
- Mistral : modèle de génération performant avec un bon compromis coût/qualité
- sentence-transformers/all-MiniLM-L6-v2 : embeddings rapides et efficaces
- FastAPI : API légère avec documentation automatique
- Docker : reproductibilité de l’environnement

---


## Structure du projet

```bash
puls-events-rag/
├── .github/
│   └── workflows/
│       └── ci.yml
├── data/
│   ├── processed/
│   │   ├── data_quality_report.json
│   │   ├── data_quality_report.md
│   │   └── events_2026-03-18.jsonl
│   ├── raw/
│   │   └── openagenda_events_2026-03-18.jsonl
│   └── vectorstore/
│       ├── index.faiss
│       └── index.pkl
├── docs/
│   ├── dataset_schema.md
│   ├── data_quality_report_example.md
│   ├── openagenda_query_params.md
│   ├── openagenda_scope.md
│   └── vectorization_strategy.md
├── src/
│   ├── api/
│   │   ├── main.py
│   │   ├── manual_api_check.py
│   │   └── schemas.py
│   ├── embeddings/
│   │   ├── build_faiss_index.py
│   │   ├── chunk_documents.py
│   │   ├── generate_embeddings.py
│   │   └── prepare_documents.py
│   ├── evaluation/
│   │   ├── evaluate_rag.py
│   │   ├── evaluate_rag_ragas.py
│   │   ├── evaluation_results.json
│   │   ├── evaluation_results_ragas.json
│   │   ├── generate_rag_answers.py
│   │   ├── qa_dataset.json
│   │   └── rag_answers.json
│   ├── ingestion/
│   │   └── fetch_openagenda_events.py
│   ├── pipelines/
│   │   ├── data_pipeline.py
│   │   ├── rag_demo_pipeline.py
│   │   └── vector_pipeline.py
│   ├── processing/
│   │   ├── normalize_openagenda_events.py
│   │   └── validate_dataset_quality.py
│   ├── rag/
│   │   ├── mistral_client.py
│   │   ├── prompt_builder.py
│   │   └── rag_pipeline.py
│   ├── retrieval/
│   │   └── semantic_search_demo.py
│   ├── check_imports.py
│   └── __init__.py
├── tests/
│   ├── data/
│   │   └── sample_events.jsonl
│   ├── test_api.py
│   ├── test_pipeline.py
│   ├── test_rag_pipeline.py
│   └── test_vector_pipeline.py
├── .coveragerc
├── .gitignore
├── Dockerfile
├── README.md
└── requirements.txt


```
---

## Pipeline du projet

Le projet est organisé en plusieurs étapes :
- Configuration de l’environnement
- Collecte et préparation des données OpenAgenda
- Vectorisation et indexation FAISS
- Construction du pipeline RAG
- Exposition via API
- Évaluation du système

---


## Prérequis
Python >= 3.8
Git

## Installation
### Cloner le dépôt :

```bash
git clone https://github.com/yoann-donizetti/puls-events-rag.git
cd puls-events-rag
```


### Créer l'environnement virtuel :
```bash
python -m venv .venv
```

Activer (Windows / PowerShell) :

```powershell
.\.venv\Scripts\Activate.ps1
```

### Installer les dépendances :

```bash
pip install -r requirements.txt
```
**Note** : *requirements.txt *a été généré via pip freeze afin de garantir la reproductibilité de l'environnement.

### Test de l'environnement
Vérifier que les dépendances sont correctement installées :

```bash
python src/check_imports.py
```

Ce script vérifie les imports des bibliothèques principales :

- FAISS
- LangChain
- HuggingFaceEmbeddings
- Mistral

---

## Collecte des événements OpenAgenda
Les événements sont récupérés via l'API OpenAgenda.

Le périmètre de collecte est défini dans :
- `docs/openagenda_scope.md`

### Localisation
Département de **l’Hérault (34), France**
### Période

- Historique : **aujourd’hui - 365 jours**
- À venir : **aujourd’hui + 365 jours**

### Type d'événements

Tous les types d'événements sont inclus pour ce POC.

---

## Paramètres d’ingestion OpenAgenda
Les paramètres utilisés pour récupérer les événements via l’API OpenAgenda sont documentés dans :


`docs/openagenda_query_params.md`

Ce document décrit :
- l’endpoint utilisé
- les filtres géographiques
- la période des événements
- la stratégie de pagination
- la convention de sauvegarde des données brutes


Les données brutes récupérées sont stockées localement dans :


data/raw/
Chaque événement est sauvegardé au format JSONL afin de conserver une copie brute avant transformation.

--- 

## Schéma du dataset
La structure cible du dataset est décrite ici :


`docs/dataset_schema.md`

Ce schéma définit :
- les champs obligatoires
- les champs optionnels
- les règles de normalisation
- le champ retrieval_text utilisé pour la recherche vectorielle.

## Pipeline data
Le pipeline de préparation des données comporte trois étapes :
1. Ingestion
   - récupération des événements via OpenAgenda
   - sauvegarde brute en JSONL
2. Normalisation
   - nettoyage des champs
   - harmonisation des dates
structuration selon dataset_schema.md
3. Validation qualité
   - contrôle des champs manquants
   - validation des dates
   - cohérence géographique
   - génération d’un rapport qualité

### Exécution du pipeline
Récupérer les événements :
```bash
python src/ingestion/fetch_openagenda_events.py
```

Normaliser les données :
```bash
python src/processing/normalize_openagenda_events.py
```

Valider la qualité :
```bash
python src/processing/validate_dataset_quality.py
```
---

## Validation qualité des données
Une étape vérifie l’intégrité du dataset :
- taux de champs manquants
- validité des dates
- cohérence géographique
- détection d’anomalies

Exemple de rapport :


`docs/data_quality_report_example.md`

---

## Vectorisation et indexation FAISS
Les événements normalisés sont transformés en embeddings sémantiques afin de permettre la recherche vectorielle.
Les embeddings sont générés avec le modèle :
sentence-transformers/all-MiniLM-L6-v2

Le modèle Mistral est utilisé uniquement pour la génération de réponses.


events → documents → chunks → embeddings → index FAISS

### Découpage des textes
Paramètres utilisés :
- chunk_size = 500
- chunk_overlap = 50

Cela permet :
- d’améliorer la précision de la recherche
- de conserver du contexte
- de limiter la taille des textes vectorisés.

### Modèle d’embedding

sentence-transformers/all-MiniLM-L6-v2

Ce modèle produit des vecteurs de dimension 384 optimisés pour la similarité sémantique.

### Construction de l’index
Commande :

```bash
python -m src.embeddings.build_faiss_index
```

L’index est sauvegardé dans :

data/vectorstore

### Test de recherche sémantique
Script :


src/retrieval/semantic_search_demo.py

Exécution :
```bash
python -m src.retrieval.semantic_search_demo
```

**Exemples de requêtes** :
- concert à Montpellier
- emploi tourisme Hérault
- atelier cuisine Béziers
- événement en ligne
- salon voyage

Le script affiche :
- titre de l’événement
- ville
- date
- URL
- extrait du texte indexé.

---


## Pipeline RAG

Le projet intègre désormais un pipeline RAG (Retrieval-Augmented Generation) permettant de générer une réponse naturelle à partir des événements retrouvés dans l’index FAISS.

Le fonctionnement est le suivant :

question utilisateur  
↓  
recherche sémantique dans FAISS  
↓  
récupération des chunks les plus pertinents  
↓  
construction d’un contexte  
↓  
génération d’une réponse avec Mistral  

### Composants

Le pipeline RAG est structuré dans :

- `src/rag/rag_pipeline.py`
- `src/rag/prompt_builder.py`
- `src/rag/mistral_client.py`

Un script de démonstration permet de tester localement le chatbot :

```bash
python -m src.pipelines.rag_demo_pipeline
```
### Sortie du pipeline

Le pipeline retourne une structure exploitable par l’API :
- question
- answer
- sources
- n_results

### Gestion des cas particuliers
Le pipeline gère également :
- les questions vides
- les cas où aucun contexte exploitable n’est disponible
- le formatage des sources pour l’affichage

---

## Pipelines automatisés

Afin de simplifier l’exécution du projet, deux pipelines permettent d’enchaîner automatiquement les différentes étapes.

### Pipeline data

Le pipeline data exécute les étapes de préparation du dataset :

1. récupération des événements OpenAgenda
2. normalisation des données
3. validation qualité du dataset

Script :

src/pipelines/data_pipeline.py

Exécution :

```bash
python -m src.pipelines.data_pipeline
```
Ce pipeline permet de reconstruire entièrement le dataset à partir de l’API OpenAgenda.

### Pipeline vectoriel
Le pipeline vectoriel exécute les étapes de vectorisation :
- création des documents
- découpage en chunks
- génération des embeddings
- construction de l’index FAISS

Script :
src/pipelines/vector_pipeline.py
Exécution :

```bash
python -m src.pipelines.vector_pipeline
```
Ce pipeline permet de reconstruire l’index vectoriel à partir du dataset traité.


### Pipeline RAG

Le pipeline RAG permet de tester le chatbot en combinant :

- la recherche sémantique dans FAISS
- la construction du contexte
- la génération de réponse avec le LLM Mistral

Script :

src/pipelines/rag_demo_pipeline.py

Exécution :

```bash
python -m src.pipelines.rag_demo_pipeline
```

Ce script permet de tester le chatbot localement avec une question exemple et d’observer :
- la question
- la réponse générée
- les sources utilisées

### Vue d’ensemble du système

OpenAgenda API
↓
Data pipeline
↓
Dataset normalisé
↓
Vector pipeline
↓
Index FAISS
↓
Recherche sémantique
↓
LLM (Mistral)

---

## API REST

Le système RAG est exposé via une API REST construite avec FastAPI afin de permettre aux équipes produit et métier de tester facilement le chatbot.
L’API permet de poser une question sur les événements culturels et de recevoir une réponse générée à partir des données indexées.

L’API est conçue pour être directement exploitable par des applications métiers (frontend, chatbot, outils internes) via des réponses JSON structurées.

L’API permet une intégration simple avec tout type d’application (web, chatbot, outils internes).

### Lancer l'API
```bash
uvicorn src.api.main:app --reload
```

L'API est accessible par défaut sur :
http://127.0.0.1:8000

La documentation interactive est disponible ici :

http://127.0.0.1:8000/docs

Cette interface Swagger permet de tester les endpoints directement depuis le navigateur.

### Endpoints disponibles

#### **GET /health**
Permet de vérifier que l’API est disponible.

Exemple de réponse :
```json
{
  "status": "ok"
}
```

#### **POST /ask**
Permet de poser une question au système RAG.
Exemple de requête
```json

{
  "question": "concert à Montpellier"
}
```
Exemple de réponse

```json
{
  "question": "concert à Montpellier",
  "answer": "Voici les concerts à Montpellier mentionnés dans le contexte...",
  "sources": [
    {
      "title": "Concert par l'ensemble instrumental universitaire de Montpellier",
      "city": "Montpellier",
      "start_datetime": "2025-09-21T16:30:00+00:00"
    }
  ],
  "n_results": 3
}
```
#### **POST /rebuild**
Permet de reconstruire l’index vectoriel FAISS à partir du dataset traité.
Cela exécute automatiquement le pipeline de vectorisation.
Exemple de réponse
```json
{
  "status": "success",
  "message": "Index FAISS reconstruit avec succès."
}
```


---

## Tests
Les tests sont situés dans :


tests/

### Tests pipeline data
Ils vérifient :
- connexion à l’API OpenAgenda
- filtrage temporel
- filtrage géographique
- présence des champs obligatoires
- volumétrie minimale
- absence de doublons

### Tests pipeline vectoriel
Ils vérifient :
- génération des chunks
- création de l’index FAISS
- recherche sémantique
- présence des métadonnées



### Tests pipeline RAG
Ils vérifient :
- le fonctionnement de la fonction centrale ask_rag()
- la récupération des documents pertinents depuis FAISS
- la construction correcte du contexte envoyé au LLM
- la structure de la réponse générée (question, answer, sources, n_results)

Pour garantir la reproductibilité des tests, l’appel au modèle Mistral est mocké afin d’éviter une dépendance à l’API externe.


### Tests API
Ils vérifient :
- le bon fonctionnement du endpoint POST /ask
- la validation des requêtes (ex : question vide)
- la structure des réponses renvoyées par l’API
- le fonctionnement du endpoint POST /rebuild

Ces tests utilisent **FastAPI TestClient** afin de tester l’API sans avoir besoin de lancer un serveur.
Une couverture de tests supérieure à 90% a été atteinte sur l’API, garantissant la robustesse des endpoints et la gestion des cas limites.

### Dataset de test
Les tests utilisent un dataset fictif versionné :


tests/data/sample_events.jsonl

Cela permet :
- d’exécuter les tests sans dépendre de l’API OpenAgenda
- d’assurer la reproductibilité des tests
- de réduire le temps d’exécution du pipeline


### Lancer les tests
```bash
python -m pytest
```
---

## Architecture globale 


```text
OpenAgenda API
    ↓
Ingestion
(fetch_openagenda_events.py)
    ↓
Normalisation
(normalize_openagenda_events.py)
    ↓
Validation qualité
(validate_dataset_quality.py)
    ↓
Documents
(prepare_documents.py)
    ↓
Chunks
(chunk_documents.py)
    ↓
Embeddings
(generate_embeddings.py)
    ↓
Index FAISS
(build_faiss_index.py)
    ↓
Pipeline RAG
(rag_pipeline.py)
    ├── recherche sémantique
    ├── construction du contexte
    └── génération de réponse Mistral
    ↓
API FastAPI
(/ask, /rebuild)
    ↓
Utilisateur
```

---

## Schéma UML de l’architecture

```mermaid
flowchart TD
    U[Utilisateur] --> A[API FastAPI]
    A --> H[/GET health/]
    A --> Q[/POST ask/]
    A --> R[/POST rebuild/]

    Q --> RP[RAG Pipeline]
    RP --> RET[Retrieval FAISS]
    RP --> PB[Prompt Builder]
    RP --> MC[Mistral Client]
    RET --> VS[Index vectoriel FAISS]
    VS --> DOC[Documents et chunks OpenAgenda]
    MC --> ANS[Réponse générée]

    R --> VP[Vector Pipeline]
    VP --> PD[Préparation des documents]
    PD --> CH[Découpage en chunks]
    CH --> EMB[Embeddings]
    EMB --> VS
```
---



## Architecture RAG
Le système RAG fonctionne selon le pipeline suivant :


Question utilisateur
↓
Embedding de la question
↓
Recherche vectorielle FAISS
↓
Chunks les plus pertinents
↓
Construction du contexte
↓
LLM Mistral
↓
Réponse générée

---

## Évaluation du système RAG

Afin d’évaluer automatiquement la qualité des réponses générées par le système RAG, une étape d’évaluation a été mise en place avec la bibliothèque **Ragas**.

L’objectif est de mesurer :

- la fidélité des réponses au contexte récupéré
- la pertinence des réponses générées
- la qualité du retrieval (précision et rappel)

### Jeu de test

Un dataset de questions-réponses a été créé dans :
src/evaluation/qa_dataset.json


Chaque entrée contient :
```json
{ "question": "...", "reference_answer": "...", "type": "positive | negative" }
```


- **positive** : la réponse doit être trouvée dans les données
- **negative** : la réponse doit indiquer qu'aucune information pertinente n'existe



### Métriques utilisées

Quatre métriques principales ont été utilisées :

**Faithfulness** : 
- Mesure si la réponse générée est fidèle au contexte récupéré.
- Un score élevé signifie peu d’hallucinations.
**Answer Similarity**
- Mesure la similarité sémantique entre la réponse générée et la réponse de référence.
**Context Precision**
- Mesure la proportion de documents récupérés réellement utiles.
**Context Recall**
- Mesure la capacité à retrouver les bons documents.



### Exécution de l'évaluation

Le script d'évaluation est situé dans :
src/evaluation/evaluate_rag_ragas.py


Lancer l'évaluation :

```bash
python -m src.evaluation.evaluate_rag_ragas
```
Les résultats sont sauvegardés dans :


src/evaluation/evaluation_results_ragas.json


### Optimisations réalisées

Plusieurs améliorations ont été testées de manière itérative.
**Retrieval** : 
- enrichissement du champ retrieval_text
- duplication du titre pour renforcer son poids sémantique
- séparation des champs city et location_name
- ajustement du paramètre top_k
- ajout d’un reranking simple avec pondération du titre
**Génération** :
- amélioration du prompt pour limiter les hallucinations
- réglage de la température pour stabiliser les réponses

### Configuration retenue 

La meilleure configuration observée est :

- top_k = 3
- temperature = 0,2
- top_p = 0.9
- titre renforcé dans le retrieval
- reranking avec boost sur le titre

Exemple de résultats :

```json
{
  "faithfulness": 0.7581,
  "answer_similarity": 0.6506,
  "context_precision": 0.4083,
  "context_recall": 0.6000
}
```
## Résultats globaux RAGAS

Le système obtient les scores suivants :

- Faithfulness : 0.748
- Answer Similarity : 0.693
- Context Precision : 0.433
- Context Recall : 0.600

Ces résultats montrent un bon compromis entre pertinence des réponses et qualité du retrieval.

Les résultats d’évaluation du système RAG sont disponibles dans le dossier [`src/evaluation`](./src/evaluation/) :

- [`evaluation_results.json`](./src/evaluation/evaluation_results.json)
- [`evaluation_results_ragas.json`](./src/evaluation/evaluation_results_ragas.json)
- [`rag_answers.json`](./src/evaluation/rag_answers.json)

Ces fichiers permettent d’analyser les performances du système et d’identifier les axes d’amélioration.

### Interprétation des résultats

Globalement, le système répond correctement, limite les hallucinations, mais peut encore améliorer la pertinence des résultats récupérés.

**Points forts** :
- bonne fidélité des réponses au contexte (faithfulness = 0.758), ce qui traduit un faible niveau d’hallucination ;
- réponses globalement cohérentes avec les attentes (answer similarity = 0.651) ;
- rappel satisfaisant (context recall = 0.600), montrant que le système retrouve une partie importante des informations pertinentes.
**Limites** :
- la précision du contexte reste perfectible (context precision = 0.408), ce qui indique la présence de bruit dans certains résultats récupérés ;
- certaines requêtes larges, temporelles ou ambiguës restent plus difficiles à traiter ;
- les performances dépendent fortement de la qualité et de la spécialisation des données indexées.


Le choix de top_k = 3 permet de conserver un bon équilibre entre :
- récupération de contexte pertinent (recall)
- limitation du bruit (precision)

Le réglage temperature = 0.2 et top_p = 0.9 permet de trouver un équilibre entre stabilité et naturalité des réponses.

Cela améliore la fluidité du langage tout en conservant une bonne fidélité au contexte.

### Pistes d'amélioration
Plusieurs axes d’amélioration ont été identifiés :

- Améliorer le classement des résultats (reranking)  
  → utiliser des méthodes plus avancées pour mieux prioriser les événements pertinents

- Renforcer le filtrage des documents  
  → réduire les résultats hors sujet et le bruit

- Optimiser le découpage des textes (chunking)  
  → mieux segmenter les données pour améliorer la recherche

- Enrichir le dataset d’évaluation  
  → ajouter davantage de questions pour tester le système dans des cas variés

- Étendre les métriques d’évaluation (RAGAS)  
  → analyser plus finement la qualité des réponses

- Améliorer la reproductibilité  
  → garantir une reconstruction fiable des index FAISS

## Secrets
Ne pas versionner la clé API Mistral.
Créer un fichier `.env` :

```env
MISTRAL_API_KEY=your_api_key_here
```
---

## Dataset
Les données OpenAgenda ne sont pas versionnées dans le dépôt afin de limiter la taille du repository.
Un dataset fictif minimal est fourni dans :


tests/data/sample_events.jsonl

Il permet d’exécuter les tests sans dépendre de l’API.


---

## Exécution avec Docker

Le projet peut être exécuté localement via un conteneur Docker afin de garantir un environnement reproductible.

### Prérequis
Docker installé sur la machine.

Vérifier l'installation :

```bash
docker --version
```

### Construction de l'image

Depuis la racine du projet

```bash
docker build -t puls-events-rag .
```
Cette commande :
- installe les dépendances Python
- copie le projet dans l’image
- configure l’API FastAPI

### Lancer le conteneur

La clé API Mistral n'est pas incluse dans l'image Docker pour des raisons de sécurité.
Créer un fichier .env :

```env
MISTRAL_API_KEY=your_api_key_here
```
Puis lancer le conteneur  :

```bash
docker run --name puls-events-rag-container --env-file .env -p 8000:8000 puls-events-rag
```

### Accès à l'API

Une fois le conteneur lancé :
API FastAPI :

http://localhost:8000

Documentation Swagger :
http://localhost:8000/docs

Cette interface Swagger permet de tester directement les endpoints.

### Reconstruction de l’index vectoriel
Si nécessaire, l’index FAISS peut être reconstruit via l’API :

POST /rebuild

Cela exécute automatiquement le pipeline de vectorisation.

---

### Démonstration type 

Exemple de requête :
```json
{
  "question": "atelier cuisine à Béziers"
}
```

Le système :
- recherche les événements pertinents dans l’index FAISS
- construit un contexte
- génère une réponse avec le modèle Mistral

---

## Roadmap
Étapes du projet :
- [x] Ingestion OpenAgenda
- [x] Normalisation du dataset
- [x] Validation qualité des données
- [x] Vectorisation
- [x] Index FAISS
- [x] Pipeline RAG
- [x] API
- [x] Évaluation
- [x] Dockerisation
