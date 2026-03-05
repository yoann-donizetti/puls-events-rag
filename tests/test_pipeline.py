import glob
import json
import os
from datetime import datetime, timedelta, timezone

import requests

API_URL = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records"


def test_api_response():
    response = requests.get(API_URL, params={"limit": 1}, timeout=10)
    assert response.status_code == 200

    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)


def load_events():
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
    events = load_events()

    today = datetime.now(timezone.utc).date()
    date_min = today - timedelta(days=365)
    date_max = today + timedelta(days=365)

    for event in events:
        start_dt = datetime.fromisoformat(event["start_datetime"].replace("Z", "+00:00"))
        start_date = start_dt.date()
        assert date_min <= start_date <= date_max


def test_location_filter():
    events = load_events()
    for event in events:
        assert event["department_code"] == "34"


def test_dataset_schema():
    events = load_events()

    required_fields = ["event_id", "title", "start_datetime", "retrieval_text", "url"]
    for event in events:
        for field in required_fields:
            assert field in event
            assert event[field] is not None
            if isinstance(event[field], str):
                assert event[field].strip() != ""


def test_dataset_volume():
    events = load_events()

    live_mode = os.getenv("OPENAGENDA_LIVE", "0") == "1"
    min_expected = 50 if live_mode else 5

    assert len(events) >= min_expected, (
        f"Dataset trop petit: {len(events)} événements (attendu >= {min_expected})"
    )

def test_event_id_uniqueness():

    events = load_events()

    ids = [event["event_id"] for event in events]

    assert len(ids) == len(set(ids)), "Des event_id dupliqués ont été détectés"

def test_api_response():
    if os.getenv("OPENAGENDA_LIVE", "0") != "1":
        return  # skip en mode unit

    response = requests.get(API_URL, params={"limit": 1}, timeout=10)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)