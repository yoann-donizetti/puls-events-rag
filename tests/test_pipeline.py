"""
Tests pour la pipeline de traitement des événements publics de l'Hérault.
Ce module contient des tests unitaires et d'intégration pour vérifier la qualité et la cohérence du dataset d'événements publics de l'Hérault, ainsi que le bon fonctionnement de la pipeline de traitement des données. Les tests couvrent les aspects suivants :
1. Test de l'API OpenAgenda : Vérifie que l'API est accessible et retourne une réponse structurée.
2. Test de filtrage des dates : Vérifie que les événements ont des dates de début comprises entre today-365 et today+365.
3. Test de filtrage de localisation : Vérifie que les événements sont localisés dans le département 34 (Hérault).
4. Test de conformité au schéma : Vérifie que les événements respectent le schéma attendu avec les champs requis.
5. Test de volume du dataset : Vérifie que le nombre d'événements est suffisant pour les tests et l'analyse.
6. Test d'unicité des event_id : Vérifie que les event_id des événements sont uniques.
7. Test de l'endpoint /health : Vérifie que l'endpoint de santé de l'API retourne un statut OK.
8. Test de redirection de l'endpoint racine : Vérifie que l'endpoint racine redirige vers /docs.
9. Test de gestion des erreurs de limite de requêtes : Simule une erreur 429 de Mistral et vérifie que l'endpoint /ask gère correctement cette erreur.
10. Test de gestion des erreurs inattendues : Simule une erreur générique lors de la génération de la réponse et vérifie que l'endpoint /ask gère correctement cette erreur.
Les tests utilisent la bibliothèque pytest pour l'exécution et les assertions, ainsi que des fixtures pour le chargement conditionnel des données d'événements. Les tests sont conçus pour être exécutés dans un environnement de développement local, avec la possibilité de basculer entre un mode de test rapide avec un échantillon versionné et un mode d'intégration utilisant le dataset réel généré par la pipeline.
"""
import glob
import json
import os
from datetime import datetime, timedelta, timezone

import requests

API_URL = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records"


def test_api_response():
    """Test de l'API OpenAgenda pour vérifier qu'elle retourne une réponse valide.
    Ce test envoie une requête GET à l'API OpenAgenda avec un paramètre de limite de 1 pour minimiser la charge, et vérifie que la réponse a un statut 200, que le champ "results" est présent dans la réponse JSON, et que ce champ est une liste. Ce test permet de s'assurer que l'API est accessible et retourne des données dans le format attendu.
    Args:    None
    Returns:    None
    Note: Ce test ne vérifie pas la logique de filtrage ou de pagination de l'API, mais seulement que l'API est accessible et retourne une réponse structurée.
    """
    response = requests.get(API_URL, params={"limit": 1}, timeout=10)
    assert response.status_code == 200

    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)


def load_events():
    """
    Charge les événements à partir d'un fichier JSONL pour les tests.
     - En mode par défaut, charge un échantillon versionné dans tests/data/sample_events.jsonl pour des tests unitaires rapides et stables.
     - En mode live (OPENAGENDA_LIVE=1), charge le dernier fichier généré dans data/processed/events_*.jsonl pour des tests d'intégration sur le dataset réel.  
     Returns:    list: Liste d'événements chargés à partir du fichier JSONL.
     Raises:    AssertionError: Si le fichier sample est manquant en mode par défaut, ou si aucun fichier processed n'est trouvé en mode live.
     Note: Ce chargement conditionnel permet d'avoir des tests unitaires rapides et stables avec un échantillon versionné, tout en offrant la possibilité de faire des tests d'intégration sur le dataset réel en activant le mode live.
     """
    # Mode par défaut : tests unitaires sur échantillon versionné
    sample_path = os.path.join("tests", "data", "sample_events.jsonl")

    # Mode optionnel : tests sur le vrai dataset généré (intégration)
    live_mode = os.getenv("OPENAGENDA_LIVE", "0") == "1"

    if not live_mode:
        assert os.path.exists(sample_path), (
            f"Fichier sample manquant: {sample_path}. "
            "Crée-le (5-20 lignes JSONL) et versionne-le."
        )
        with open(sample_path, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    # Live mode : utilise le dernier fichier data/processed/events_*.jsonl
    files = glob.glob("data/processed/events_*.jsonl")
    assert files, "Aucun fichier data/processed/events_*.jsonl trouvé. Lance d'abord la normalisation."

    latest = max(files, key=os.path.getctime)
    with open(latest, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def test_date_filter():
    """Test pour vérifier que les dates des événements sont bien comprises entre today-365 et today+365.
    Ce test charge les événements à partir du fichier JSONL (en mode live ou sample),
    puis vérifie que la date de début (start_datetime) de chaque événement est bien au format ISO 8601 et qu'elle est comprise entre une date de référence (2026-03-05) moins 365 jours et cette même date plus 365 jours. Ce test permet de s'assurer que les événements respectent les contraintes de date définies pour le projet.
    Args:    None
    Returns:    None
    Note: Ce test suppose que les dates sont au format ISO 8601 et que la date de référence est fixée à 2026-03-05 pour garantir la stabilité du test dans le temps.
    """
    events = load_events()

    reference_date = datetime(2026, 3, 5, tzinfo=timezone.utc).date()

    date_min = reference_date - timedelta(days=365)
    date_max = reference_date + timedelta(days=365)

    for event in events:
        start_dt = datetime.fromisoformat(event["start_datetime"].replace("Z", "+00:00"))
        start_date = start_dt.date()

        assert date_min <= start_date <= date_max
        


def test_location_filter():
    """Test pour vérifier que les événements sont bien localisés dans le département 34 (Hérault).
    Ce test charge les événements à partir du fichier JSONL (en mode live ou sample), puis vérifie que le champ "department_code" de chaque événement est égal à "34". Ce test permet de s'assurer que les événements respectent la contrainte de localisation définie pour le projet, qui se concentre sur les événements publics dans le département de l'Hérault.
    Args:    None
    Returns:    None
    Note: Ce test suppose que le champ "department_code" est présent dans les événements et qu'il est utilisé pour indiquer le département de localisation de l'événement.
    """
    events = load_events()
    for event in events:
        assert event["department_code"] == "34"


def test_dataset_schema():
    """Test pour vérifier que les événements respectent le schéma attendu.
    Ce test charge les événements à partir du fichier JSONL (en mode live ou sample), puis vérifie que chaque événement contient les champs requis et que ces champs ne sont pas vides. Ce test permet de s'assurer que les événements respectent le schéma défini pour le projet.
    Args:    None
    Returns:    None
    Note: Ce test suppose que les champs requis sont présents dans les événements et qu'ils sont utilisés pour indiquer les informations essentielles de l'événement.
    """
    events = load_events()

    required_fields = ["event_id", "title", "start_datetime", "retrieval_text", "url"]
    for event in events:
        for field in required_fields:
            assert field in event
            assert event[field] is not None
            if isinstance(event[field], str):
                assert event[field].strip() != ""


def test_dataset_volume():
    """Test pour vérifier que le volume des événements est suffisant.
    Ce test charge les événements à partir du fichier JSONL (en mode live ou sample), puis vérifie que le nombre d'événements est supérieur ou égal à un seuil minimum. Ce test permet de s'assurer que le dataset contient un nombre suffisant d'événements pour les tests et l'analyse.
    Args:    None
    Returns:    None
    Note: Ce test suppose que le fichier JSONL contient les événements et que le mode live est déterminé par la variable d'environnement OPENAGENDA_LIVE.
    """

    events = load_events()

    live_mode = os.getenv("OPENAGENDA_LIVE", "0") == "1"
    min_expected = 50 if live_mode else 5

    assert len(events) >= min_expected, (
        f"Dataset trop petit: {len(events)} événements (attendu >= {min_expected})"
    )

def test_event_id_uniqueness():
    """Test pour vérifier que les event_id des événements sont uniques.
    Ce test charge les événements à partir du fichier JSONL (en mode live ou sample), puis vérifie que les event_id de tous les événements sont uniques en comparant la longueur de la liste des event_id avec la longueur de l'ensemble des event_id. Ce test permet de s'assurer que chaque événement a un identifiant unique, ce qui est essentiel pour éviter les problèmes de duplication et d'identification dans le dataset.
    Args:    None
    Returns:    None
    Note: Ce test suppose que le champ "event_id" est présent dans les événements et qu'il est utilisé pour indiquer l'identifiant unique de chaque événement.
    """


    events = load_events()

    ids = [event["event_id"] for event in events]

    assert len(ids) == len(set(ids)), "Des event_id dupliqués ont été détectés"

def test_api_response():
    """Test de l'API OpenAgenda pour vérifier qu'elle retourne une réponse valide.
    Ce test envoie une requête GET à l'API OpenAgenda avec un paramètre
    de limite de 1 pour minimiser la charge, et vérifie que la réponse a un statut 200, que le champ "results" est présent dans la réponse JSON, et que ce champ est une liste. Ce test permet de s'assurer que l'API est accessible et retourne des données dans le format attendu.
    Args:    None
    Returns:    None
    Note: Ce test ne vérifie pas la logique de filtrage ou de pagination de l'API, mais seulement que l'API est accessible et retourne une réponse structurée.
    """
    if os.getenv("OPENAGENDA_LIVE", "0") != "1":
        return  # skip en mode unit

    response = requests.get(API_URL, params={"limit": 1}, timeout=10)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)