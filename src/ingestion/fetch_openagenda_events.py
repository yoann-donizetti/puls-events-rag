'''
Objectif : Récupérer les événements depuis l'API OpenAgenda et les stocker dans un fichier JSON.
Étapes :
1. Importer les bibliothèques nécessaires.
2. Définir une fonction pour récupérer les événements depuis l'API OpenAgenda :
- Définir l'endpoint base (Explore API v2.1). il est disponible dans la documentation de l'API.(docs/openagenda_query_params.md)
- Définir les paramètres fixes :
     - refine.location_department= Hérault
     - order_by=firstdate_begin ASC
     - limit=100
- Définir la période :
        - calculer date_min = today - 365 jours
        - calculer date_max = today + 365 jours
        - préparer la condition de filtre date (via where sur firstdate_begin)

3. Préparer la sortie (RAW) :
- Créer un dossier data/raw/ s'il n'existe pas
- Construire le nom de fichier : data/raw/openagenda_events_YYYY-MM-DD.jsonl
- Ouvrir le fichier en mode écriture (UTF-8)

4. Récupérer les événements par boucle de pagination :
- Initialiser offset = 0.
- Boucler tant qu’on reçoit des résultats :
    - envoyer une requête API avec :
        - limit
        - offset
        - refine.location_department
        - filtre de dates
        - order_by
    - récupérer la liste d’événements renvoyée.

5. Ecrire le RAW en JSONL :
- Pour chaque événement renvoyé :
    - écrire l’objet JSONL brut sur une ligne du fichier
    - sans transformation (pas de nettoyage, pas de mapping, pas de renommage)
    - éventuellement ajouter un séparateur newline propre.

6. Gestion basique de robustesse :
- Si erreur réseau / timeout : retry (x fois)
- Si 429 (rate limit) : attendre puis retry
- Ajouter un petit délai entre requêtes (ex. 200 ms).

7. Résumé de fin d'exécution :
- Afficher le nombre total d’événements récupérés
- Afficher le chemin du fichier de sortie
- Nombre de pages récupérées
- periode utilisée (date_min, date_max)

8 Controles minimaux :
- Si total d’événements récupérés = 0 : 
    - Afficher un message d’avertissement
- Sinon :
   - Confirmer que le fichier de sortie a été créé et contient des données (ex. taille > 0)
'''

import os
import json
import time
import requests
from datetime import datetime, timedelta

API_URL = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records"
COUNTRY_CODE = "FR"
DEPARTMENT = "Hérault"
LIMIT = 100
ORDER_BY = "firstdate_begin ASC"
RETRY_MAX = 3
RETRY_DELAY = 2
REQUEST_DELAY = 0.2

def get_date_range():
    today = datetime.now()
    date_min = (today - timedelta(days=365)).strftime("%Y-%m-%d")
    date_max = (today + timedelta(days=365)).strftime("%Y-%m-%d")
    return date_min, date_max

def fetch_events():
    date_min, date_max = get_date_range()
    params = {
        "order_by": ORDER_BY,
        "limit": LIMIT,
        "where": (
            f'location_countrycode = "{COUNTRY_CODE}" '
            f'AND location_department = "{DEPARTMENT}" '
            f"AND firstdate_begin >= date'{date_min}' "
            f"AND firstdate_begin <= date'{date_max}'"
        )
    }
    offset = 0
    total_events = 0
    page_count = 0
    raw_dir = os.path.join("data", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    out_path = os.path.join(raw_dir, f"openagenda_events_{datetime.now().strftime('%Y-%m-%d')}.jsonl")

    with open(out_path, "w", encoding="utf-8", errors="replace") as f:
        while True:
            params["offset"] = offset
            for attempt in range(RETRY_MAX):
                try:
                    response = requests.get(API_URL, params=params, timeout=10)
                    if response.status_code == 400:
                        print(
                            f"[STOP] 400 Bad Request (requête refusée). "
                            f"Souvent lié à une limite de pagination/offset ou à un filtre invalide. "
                            f"offset={offset}. URL={response.url}"
                        )
                        return  # arrêt propre
                    if response.status_code == 429:
                        print("Rate limit atteint, attente...")
                        time.sleep(RETRY_DELAY)
                        continue
                    response.raise_for_status()
                    data = response.json()
                    page_events = data.get("results", [])
                    if not page_events:
                        break
                    for event in page_events:
                        f.write(json.dumps(event, ensure_ascii=False) + "\n")
                        total_events += 1
                    page_count += 1
                    offset += LIMIT
                    time.sleep(REQUEST_DELAY)
                    break
                except requests.RequestException as e:
                    print(f"Erreur réseau : {e}, retry {attempt+1}/{RETRY_MAX}")
                    time.sleep(RETRY_DELAY)
            else:
                print("Abandon après plusieurs échecs réseau.")
                break
            if not page_events:
                break

    print(f"\nRécupération terminée.")
    print(f"Total événements récupérés : {total_events}")
    print(f"Fichier de sortie : {out_path}")
    print(f"Nombre de pages : {page_count}")
    print(f"Période utilisée : {date_min} -> {date_max}")
    if total_events == 0:
        print("Avertissement : aucun événement récupéré.")
    else:
        if os.path.getsize(out_path) > 0:
            print("Le fichier de sortie contient des données.")
        else:
            print("Le fichier de sortie est vide !")

if __name__ == "__main__":
    fetch_events()