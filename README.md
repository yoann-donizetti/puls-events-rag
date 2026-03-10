
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
|   ├── pipelines/
|   │   ├── data_pipeline.py
|   │   └── vector_pipeline.py
│   │
│   ├── rag/
│   └── api/
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
python src/test_imports.py
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

Les tests utilisent un dataset fictif versionné :


tests/data/sample_events.jsonl

### Lancer les tests
```bash
python -m pytest
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
Documents pertinents
      ↓
Contexte envoyé au LLM (Mistral)
      ↓
Réponse générée

---

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


## Roadmap
Étapes du projet :
[x] Ingestion OpenAgenda
[x] Normalisation du dataset
[x] Validation qualité des données
[x] Vectorisation
[x] Index FAISS
[ ] Pipeline RAG
[ ] API
[ ] Évaluation
