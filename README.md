# Puls-Events — POC RAG

## Objectif

Réaliser un Proof of Concept (POC) d’un système **RAG (Retrieval Augmented Generation)** permettant de répondre à des questions sur des événements culturels.

Le système s’appuie sur :

- **OpenAgenda** pour la récupération des événements
- **LangChain** pour l’orchestration du pipeline RAG
- **FAISS** pour la recherche vectorielle
- **Mistral** pour la génération de réponses

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

## Schéma du dataset

La structure cible du dataset (champs obligatoires, optionnels, règles de normalisation et champ `retrieval_text`) est définie ici :

- `docs/dataset_schema.md`

Ce schéma décrit la structure du jeu de données **nettoyé et structuré** attendu à la fin de l’étape 2, prêt pour l’indexation vectorielle (étape 3).

---

Les données récupérées seront ensuite :

1. nettoyées
2. structurées
3. préparées pour la vectorisation
4. indexées dans FAISS


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

## Secrets

Ne pas versionner la clé API Mistral.

Créer un fichier `.env` (ignoré par Git) ou utiliser une variable d’environnement.

Exemple :

```env
MISTRAL_API_KEY=your_api_key_here
```