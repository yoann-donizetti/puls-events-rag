# Puls-Events — POC RAG (Setup)

Objectif : préparer un environnement reproductible pour un POC RAG (LangChain + Mistral + FAISS).

## Prérequis
- Python >= 3.8
- Git

## Installation

Cloner le dépôt :
git clone https://github.com/yoann-donizetti/puls-events-rag.git
cd <repo>

Créer l'environnement virtuel :
python -m venv .env

Activer (Windows) :
.\.env\Scripts\activate

Installer les dépendances :
pip install -r requirements.txt

## Test des imports
python src/test_imports.py

## Secrets
Ne pas versionner la clé Mistral.
Créer un fichier `.env` (ignoré par Git) ou définir une variable d’environnement.

Exemple :
MISTRAL_API_KEY=...