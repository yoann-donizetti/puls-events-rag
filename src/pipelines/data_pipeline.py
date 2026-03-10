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