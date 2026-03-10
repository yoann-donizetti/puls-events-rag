# Puls-Events — POC RAG

## Objectif

Réaliser un Proof of Concept (POC) d’un système **RAG (Retrieval Augmented Generation)** permettant de répondre à des questions sur des événements culturels.

Le système s’appuie sur :

- **OpenAgenda** pour la récupération des événements
- **LangChain** pour l’orchestration du pipeline RAG
- **FAISS** pour la recherche vectorielle
- **Mistral** pour la génération de réponses

---

## Structure du projet

```bash
puls-events-rag/

├── src/
│   ├── ingestion/
│   │   └── fetch_openagenda_events.py
│   │
│   ├── processing/
│   │   ├── normalize_openagenda_events.py
│   │   └── validate_dataset_quality.py
│   │
│   ├── embeddings/
│   │   ├── prepare_documents.py
│   │   ├── chunk_documents.py
│   │   ├── generate_embeddings.py
│   │   └── build_faiss_index.py
│   │
│   ├── retrieval/
│   │   └── semantic_search_demo.py
│   │
│   ├── rag/
│   └── api/
│
├── tests/
│   ├── test_pipeline.py
│   ├── test_vector_pipeline.py
│   └── data/
│       └── sample_events.jsonl
│
├── docs/
│   ├── dataset_schema.md
│   ├── openagenda_scope.md
│   ├── openagenda_query_params.md
│   └── data_quality_report_example.md
│
├── requirements.txt
└── README.md
```
---


## Pipeline du projet

Le projet est organisé en plusieurs étapes :

1. **Configuration de l’environnement**
2. **Collecte et préparation des données OpenAgenda**
3. **Vectorisation et indexation FAISS**
4. **Construction du pipeline RAG**
5. **Exposition via API**
6. **Évaluation du système**

---

## Prérequis

- Python >= 3.8
- Git

---

## Installation


Cloner le dépôt :

```bash
git clone https://github.com/yoann-donizetti/puls-events-rag.git
cd puls-events-rag
```


Créer l'environnement virtuel :

```bash
python -m venv .venv
```


Activer (Windows / PowerShell) :

```powershell
.\.venv\Scripts\Activate.ps1
```


Installer les dépendances :

```bash
pip install -r requirements.txt
```

Note : `requirements.txt` a été généré via `pip freeze` pour garantir la reproductibilité de l'environnement.

---

## Test de l'environnement


Vérifier que les dépendances sont correctement installées :

```bash
python src/test_imports.py
```

Ce script vérifie les imports des bibliothèques principales :

- FAISS
- LangChain
- HuggingFaceEmbeddings
- Mistral

---

## Collecte des événements OpenAgenda

Les événements sont récupérés via l'API **OpenAgenda**.

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

- `docs/openagenda_query_params.md`

Ce document décrit :

- l’endpoint utilisé
- les filtres géographiques (département de l’Hérault)
- la période des événements
- la stratégie de pagination
- la convention de sauvegarde des données brutes

Les données brutes récupérées depuis l’API sont stockées localement dans :

data/raw/

Chaque événement est sauvegardé au format JSONL afin de conserver une copie brute des données avant toute transformation.

---

## Schéma du dataset

La structure cible du dataset (champs obligatoires, optionnels, règles de normalisation et champ `retrieval_text`) est définie ici :
- [docs/data_quality_report_example.md](docs/dataset_schema.md)


Ce schéma décrit la structure du jeu de données **nettoyé et structuré** attendu à la fin de l’étape 2, prêt pour l’indexation vectorielle (étape 3).



Les données récupérées seront ensuite :

1. nettoyées
2. structurées
3. préparées pour la vectorisation
4. indexées dans FAISS

--- 

## Pipeline data

Le pipeline de préparation des données est structuré en plusieurs étapes :

1. **Ingestion**
   - récupération des événements via l’API OpenAgenda
   - sauvegarde brute au format JSONL

2. **Normalisation**
   - nettoyage des champs
   - harmonisation des dates
   - structuration du dataset selon `dataset_schema.md`

3. **Validation qualité**
   - contrôle des champs manquants
   - validation des dates
   - cohérence géographique
   - génération d’un rapport de qualité des données

### Exécution du pipeline

Récupérer les événements :

```bash
python src/ingestion/fetch_openagenda_events.py
```

Normaliser les données :
```bash
python src/processing/normalize_openagenda_events.py
```

Vérifier la qualité des données :

```bash
python src/processing/validate_dataset_quality.py
```

--- 


## Validation qualité des données

Une étape de validation vérifie l'intégrité du dataset normalisé :

- taux de champs manquants
- validité des dates
- cohérence géographique
- détection d'anomalies



Voir le rapport complet : [docs/data_quality_report_example.md](docs/data_quality_report_example.md)

---
## Vectorisation et indexation FAISS

Les événements normalisés sont transformés en représentations vectorielles (embeddings) afin de permettre une recherche sémantique.

Le pipeline de vectorisation est le suivant :

events → documents → chunks → embeddings → index FAISS

### Découpage des textes

Les textes sont découpés avant vectorisation avec les paramètres :

- chunk_size = 500
- chunk_overlap = 50

Ce découpage permet :

- d’améliorer la précision de la recherche sémantique
- de limiter la taille des textes envoyés au modèle d’embedding
- de conserver du contexte entre les segments de texte

### Modèle d’embedding utilisé

sentence-transformers/all-MiniLM-L6-v2
Ce modèle produit des vecteurs de dimension **384** optimisés pour la similarité sémantique.

### Construction de l’index

Les embeddings sont indexés dans **FAISS** afin de permettre une recherche rapide par similarité vectorielle.

Commande :

```bash
python -m src.embeddings.build_faiss_index
```

L’index est sauvegardé localement dans :

data/vectorstore

## Test de recherche sémantique

Un script permet de tester la pertinence de la recherche vectorielle.

Script :

src/retrieval/semantic_search_demo.py

Exécution :

```bash
python -m src.retrieval.semantic_search_demo
```
Exemples de requêtes testées :
- concert à Montpellier
- emploi tourisme Hérault
- atelier cuisine Béziers
- événement en ligne
- salon voyage

Le script affiche :
- le titre de l’événement
- la ville
- la date
- l’URL
- un extrait du texte indexé

---

## Tests

Une suite de tests permet de vérifier automatiquement la validité du pipeline.


Les tests sont situés dans :

tests/

### Tests pipeline data
Ils vérifient :

- connexion à l’API OpenAgenda
- filtrage temporel des événements
- filtrage géographique (département de l’Hérault)
- présence des champs obligatoires du dataset
- volumétrie minimale du dataset
- absence de doublons d’événements

### Tests pipeline vectoriel

Vérifients :
- génération des chunks
- création de l’index FAISS
- recherche sémantique
- présence des métadonnées

Les tests utilisent un **dataset fictif versionné** (`tests/data/sample_events.jsonl`) afin de garantir la reproductibilité du projet.

### Lancer les tests
Installer pytest si nécessaire

```bash
pip install pytest
```

pui exécuter les tests :
```bash
pytest
```


---

## Architecture RAG

Le système RAG fonctionne selon le pipeline suivant :

Question utilisateur  
↓  
Embedding de la question  
↓  
Recherche vectorielle dans FAISS  
↓  
Récupération des événements pertinents  
↓  
Envoi du contexte au LLM (Mistral)  
↓  
Génération de la réponse

---

## Vectorisation et indexation

Les événements normalisés sont transformés en embeddings à l’aide de :

HuggingFaceEmbeddings

Ces embeddings sont indexés dans :

**FAISS**

Le champ utilisé pour l’indexation est :

`retrieval_text`

---

## Secrets

Ne pas versionner la clé API Mistral.

Créer un fichier `.env` (ignoré par Git) ou utiliser une variable d’environnement.

Exemple :

```env
MISTRAL_API_KEY=your_api_key_here
```


## Dataset

Les données OpenAgenda récupérées ne sont pas versionnées dans le dépôt afin de limiter la taille du repository.

Un dataset fictif minimal est fourni dans :

tests/data/sample_events.jsonl


Il permet d’exécuter les tests sans dépendre de l’API OpenAgenda.

## Roadmap

Étapes du projet :

- [x] Ingestion OpenAgenda
- [x] Normalisation du dataset
- [x] Validation qualité des données
- [x] Vectorisation
- [x] Index FAISS
- [ ] Pipeline RAG
- [ ] API
- [ ] Évaluation
