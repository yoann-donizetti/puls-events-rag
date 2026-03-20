"""Pipeline de traitement des données pour le système RAG Puls-Events.
Étapes :
1. Ingestion : Récupération des événements depuis l'API OpenAgenda
2. Normalisation : Transformation des données brutes en un format structuré et cohérent
3. Validation qualité : Vérification de la qualité des données normalisées
"""
from src.ingestion.fetch_openagenda_events import fetch_events
from src.processing.normalize_openagenda_events import main as normalize_events
from src.processing.validate_dataset_quality import main as validate_quality


def main():

    print("Étape 1 — Ingestion OpenAgenda")
    fetch_events()

    print("Étape 2 — Normalisation")
    normalize_events()

    print("Étape 3 — Validation qualité")
    validate_quality()

    print("Pipeline data terminé")


if __name__ == "__main__":
    main()