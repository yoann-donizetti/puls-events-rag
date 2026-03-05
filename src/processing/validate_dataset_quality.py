"""
module validate_dataset_quality.py

Ce module contient la fonction validate_dataset_quality qui vérifie la qualité
du dataset d'événements normalisés en effectuant les validations suivantes :

1) Champs manquants (par champ) sur une liste de champs importants.
2) Dates : start_datetime doit être ISO 8601 et compris entre today-365 et today+365.
3) Géo : department_code == "34" et, si lat/lon présents, coordonnées dans une bbox.
Le rapport est écrit dans data/processed/data_quality_report.json
"""

import json
import glob
import os
from datetime import datetime, timedelta, timezone


PROCESSED_DIR = "data/processed/"

IMPORTANT_FIELDS = [
    "title",
    "description",
    "start_datetime",
    "city",
    "postal_code",
    "lat",
    "lon",
    "url",
]

LAT_MIN = 43.1
LAT_MAX = 43.8
LON_MIN = 2.0
LON_MAX = 4.0


def find_latest_processed_file(processed_dir: str = PROCESSED_DIR) -> str:
    """
    Trouve le fichier processed le plus récent dans le répertoire data/processed/
    en se basant sur la date de création du fichier.

    Returns:
        str: chemin du fichier le plus récent

    Raises:
        FileNotFoundError: si aucun fichier n'est trouvé
    """
    processed_files = glob.glob(os.path.join(processed_dir, "events_*.jsonl"))
    if not processed_files:
        raise FileNotFoundError("Aucun fichier processed trouvé dans data/processed/")
    return max(processed_files, key=os.path.getctime)


def is_missing(value) -> bool:
    """True si la valeur est considérée manquante (None ou string vide)."""
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def _parse_iso_datetime(dt_str: str) -> datetime:
    """
    Parse un datetime ISO 8601.
    Si la date est "naïve" (sans timezone), on l'assume UTC pour éviter les comparaisons incohérentes.
    """
    dt = datetime.fromisoformat(dt_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def validate_dataset_quality(input_file: str, output_file: str) -> None:
    """
    Valide la qualité du dataset en vérifiant les champs essentiels, les dates et la cohérence géographique.

    Args:
        input_file (str): Chemin du fichier d'entrée contenant les événements normalisés (JSONL).
        output_file (str): Chemin du fichier de sortie où le rapport sera enregistré (JSON).

    Returns:
        None
    """
    # Lecture JSONL
    with open(input_file, "r", encoding="utf-8") as f:
        events = [json.loads(line) for line in f if line.strip()]

    total_events = len(events)

    # Champs manquants (par champ)
    missing_counts = {field: 0 for field in IMPORTANT_FIELDS}

    # Dates
    invalid_dates_count = 0

    # Géo (détaillé)
    dept_not_34_count = 0
    bbox_outside_count = 0
    geo_parse_error_count = 0  # lat/lon non convertibles

    # IMPORTANT : bornes timezone-aware (UTC), pour comparer avec start_datetime (+00:00)
    now_utc = datetime.now(timezone.utc)
    date_min = now_utc - timedelta(days=365)
    date_max = now_utc + timedelta(days=365)

    for event in events:
        # 1) Champs manquants par champ
        for field in IMPORTANT_FIELDS:
            if is_missing(event.get(field)):
                missing_counts[field] += 1

        # 2) Dates
        try:
            start_dt = _parse_iso_datetime(event["start_datetime"])
            if not (date_min <= start_dt <= date_max):
                invalid_dates_count += 1
        except Exception:
            invalid_dates_count += 1

        # 3) Géo
        if event.get("department_code") != "34":
            dept_not_34_count += 1
        else:
            lat = event.get("lat")
            lon = event.get("lon")

            # Si lat/lon présents, on contrôle la bbox
            if lat is not None and lon is not None:
                try:
                    lat_f = float(lat)
                    lon_f = float(lon)
                    if not (LAT_MIN <= lat_f <= LAT_MAX and LON_MIN <= lon_f <= LON_MAX):
                        bbox_outside_count += 1
                except Exception:
                    geo_parse_error_count += 1

    # Rapport champs manquants
    missing_fields_report = {
        field: {
            "count": count,
            "rate": (count / total_events) if total_events > 0 else 0,
        }
        for field, count in missing_counts.items()
    }

    inconsistent_geo_total = dept_not_34_count + bbox_outside_count + geo_parse_error_count

    report = {
        "dataset_summary": {
            "total_events": total_events,
        },
        "missing_fields": missing_fields_report,
        "date_validation": {
            "invalid_dates": invalid_dates_count,
            "rate": (invalid_dates_count / total_events) if total_events > 0 else 0,
            "window_utc": {
                "date_min": date_min.isoformat(),
                "date_max": date_max.isoformat(),
            },
        },
        "geo_validation": {
            "inconsistent_geo": inconsistent_geo_total,
            "rate": (inconsistent_geo_total / total_events) if total_events > 0 else 0,
            "details": {
                "dept_not_34": dept_not_34_count,
                "bbox_outside": bbox_outside_count,
                "geo_parse_error": geo_parse_error_count,
                "bbox": {
                    "lat_min": LAT_MIN,
                    "lat_max": LAT_MAX,
                    "lon_min": LON_MIN,
                    "lon_max": LON_MAX,
                },
            },
        },
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)

    print("Validation qualité terminée")
    print(f"Fichier analysé : {input_file}")
    print(f"Rapport généré  : {output_file}")


def main() -> None:
    input_file = find_latest_processed_file(PROCESSED_DIR)
    output_file = os.path.join(PROCESSED_DIR, "data_quality_report.json")
    validate_dataset_quality(input_file, output_file)


if __name__ == "__main__":
    main()