# Puls-Events — POC RAG

## Objectif

Réaliser un Proof of Concept (POC) d’un système **RAG (Retrieval Augmented Generation)** permettant de répondre à des questions sur des événements culturels.

Le système s’appuie sur :

- **OpenAgenda** pour la récupération des événements
- **LangChain** pour l’orchestration du pipeline RAG
- **FAISS** pour la recherche vectorielle
- **Mistral** pour la génération de réponses

---

# Pipeline du projet

Le projet est organisé en plusieurs étapes :

1. **Configuration de l’environnement**
2. **Collecte et préparation des données OpenAgenda**
3. **Vectorisation et indexation FAISS**
4. **Construction du pipeline RAG**
5. **Exposition via API**
6. **Évaluation du système**

---

# Prérequis

- Python >= 3.8
- Git

---

# Installation


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

# Test de l'environnement


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

# Collecte des événements OpenAgenda

Les événements sont récupérés via l'API **OpenAgenda**.

Le périmètre de collecte est défini dans :

docs/openagenda_scope.md

### Localisation

Département de **l’Hérault (34), France**

### Période

- Historique : **aujourd’hui - 365 jours**
- À venir : **aujourd’hui + 365 jours**

### Type d'événements

Tous les types d'événements sont inclus pour ce POC.

Les données récupérées seront ensuite :

1. nettoyées
2. structurées
3. préparées pour la vectorisation
4. indexées dans FAISS

---

# Secrets

Ne pas versionner la clé API Mistral.

Créer un fichier `.env` (ignoré par Git) ou utiliser une variable d’environnement.

Exemple :

MISTRAL_API_KEY=...