
"""
Script de normalisation des événements OpenAgenda
-------------------------------------------------

Ce script Python normalise les données d'événements issues d'OpenAgenda.
Il lit les fichiers RAW générés précédemment, extrait et nettoie les informations pertinentes de chaque événement,
puis écrit les événements normalisés dans un nouveau fichier JSONL prêt à être utilisé pour l'indexation ou l'affichage.

Fonctionnalités principales :
- Nettoyage des descriptions d'événements (suppression des balises HTML, conversion des entités HTML, normalisation des espaces)
- Construction d'un texte de récupération pour faciliter la recherche
- Vérification de la validité des événements avant enregistrement
- Gestion des doublons
- Affichage d'un résumé du processus (nombre d'événements traités, gardés, rejetés, doublons)
"""



import os #os est utilisé pour la gestion des fichiers et des chemins
import json #json est utilisé pour lire et écrire des données au format JSON
import glob #glob est utilisé pour trouver tous les fichiers correspondant à un motif spécifique dans un répertoire
import re #re est utilisé pour les opérations de traitement de texte, notamment pour supprimer les balises HTML et nettoyer les espaces dans les descriptions des événements
from datetime import datetime #datetime est utilisé pour obtenir la date actuelle et formater les noms de fichiers de sortie
from html import unescape #unescape est utilisé pour convertir les entités HTML en caractères normaux, ce qui est utile pour nettoyer les descriptions des événements qui peuvent contenir des balises HTML ou des entités


RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
SOURCE = "openagenda"
DEPARTMENT_CODE = "34"


UNUSUAL_LINE_SEPARATORS = [
    "\u2028",  # LS
    "\u2029",  # PS
    "\u0085",  # NEL (Next Line)
    "\u000b",  # VT (Vertical Tab)
    "\u000c",  # FF (Form Feed)
]

def sanitize_line_separators(text: str) -> str:
    '''
    Remplace les caractères de saut de ligne Unicode inhabituels par des espaces dans une chaîne de texte.  
    Args:
        text (str): Chaîne de texte potentiellement contenant des caractères de saut de ligne Unicode inhabituels.

    Returns:
        str: Chaîne de texte avec les caractères de saut de ligne inhabituels remplacés par des espaces.
    '''
    if not text:
        return ""
    for ch in UNUSUAL_LINE_SEPARATORS:
        text = text.replace(ch, " ")
    return text


def strip_html(text):
    """
    Nettoie une chaîne de texte en supprimant les balises HTML, en convertissant les entités HTML
    et en normalisant les espaces. Retourne une chaîne prête à être utilisée dans les descriptions d'événements.

    Args:
        text (str): Texte potentiellement contenant du HTML ou des entités HTML.

    Returns:
        str: Texte nettoyé, sans balises HTML, sans entités HTML, et avec espaces normalisés.
    """
    # Si le texte est vide ou None, retourner une chaîne vide
    if not text:
        return ""
    # Supprimer toutes les balises HTML en les remplaçant par un espace
    text = re.sub("<.*?>", " ", text)
    # Convertir les entités HTML en caractères normaux (ex: &amp; -> &)
    text = unescape(text)
    # Remplacer les caractères de saut de ligne Unicode par des espaces pour éviter les problèmes d'affichage ou de traitement ultérieur
    text = sanitize_line_separators(text)
    # Remplacer les espaces multiples, retours à la ligne, tabulations, etc. par un seul espace et supprimer les espaces en début/fin
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_retrieval_text(event):
    """
    Construit une chaîne de texte concaténant les informations principales d'un événement pour faciliter la recherche ou l'indexation.

    Args:
        event (dict): Dictionnaire contenant les champs d'un événement normalisé.

    Returns:
        str: Texte concaténé avec titre, description, localisation, dates et tags.
    """
    parts = []

    parts.append(event.get("title", ""))#Ajouter le titre de l'événement à la liste des parties du texte de récupération. Si le titre n'est pas présent, ajouter une chaîne vide pour éviter les erreurs.
    parts.append(event.get("description", ""))#Ajouter la description de l'événement à la liste des parties du texte de récupération. Si la description n'est pas présente, ajouter une chaîne vide pour éviter les erreurs.

    location = " ".join(filter(None, [
        #Construire une chaîne de localisation en concaténant les différents champs de localisation de l'événement. 
        # Utiliser filter(None, [...]) pour ignorer les champs vides ou None.
        event.get("location_name"),
        event.get("city"),
        event.get("postal_code"),
        event.get("department_code")
    ]))

    parts.append(location)
    #Ajouter la date de début de l'événement à la liste des parties du texte de récupération si elle est présente.
    if event.get("start_datetime"):
        parts.append(event["start_datetime"])

    #Ajouter la date de fin de l'événement à la liste des parties du texte de récupération si elle est présente.
    if event.get("end_datetime"):
        parts.append(event["end_datetime"])

    #Ajouter les tags de l'événement à la liste des parties du texte de récupération si ils sont présents.
    # Les tags sont joints en une seule chaîne séparée par des virgules pour éviter d'avoir une liste de tags dans le texte de récupération, ce qui pourrait compliquer la recherche.
    if event.get("tags"):
        parts.append(", ".join(event["tags"]))

    return sanitize_line_separators(" ".join(filter(None, parts)).strip())


def find_latest_raw_file():
    '''
    Trouve le fichier RAW le plus récent dans le répertoire data/raw/ en utilisant glob pour lister les fichiers correspondant au motif "openagenda_events_*.jsonl" et en sélectionnant celui avec la date de création la plus récente.
    Returns:
        str: Chemin du fichier RAW le plus récent.
        Raises:
            FileNotFoundError: Si aucun fichier RAW n'est trouvé dans le répertoire data/raw/.
            '''
    #Utiliser glob pour trouver tous les fichiers dans le répertoire data/raw/ qui correspondent au motif "openagenda_events_*.jsonl". 
    # Cela permet de lister tous les fichiers RAW générés précédemment.
    files = glob.glob(os.path.join(RAW_DIR, "openagenda_events_*.jsonl"))
    if not files:
        raise FileNotFoundError("Aucun fichier RAW trouvé dans data/raw/")
    return max(files, key=os.path.getctime)


def normalize_event(raw):
    '''
    Normalise un événement brut provenant d'OpenAgenda en extrayant les champs pertinents,
    en nettoyant les descriptions et en construisant une structure d'événement standardisée.
    Args:        raw (dict): Dictionnaire contenant les données brutes d'un événement tel que récupéré depuis OpenAgenda.
    Returns:    dict: Dictionnaire contenant les champs normalisés de l'événement, prêt à être utilisé pour l'indexation ou l'affichage.

    '''
    # Extraire l'identifiant de l'événement à partir du champ "uid" du dictionnaire brut. 
    # Cet identifiant est utilisé pour assurer l'unicité de chaque événement dans le processus de normalisation.
    event_id = raw.get("uid")
    # Nettoyer le titre de l'événement en supprimant les balises HTML et en convertissant les entités HTML. 
    # Si le champ "title_fr" n'est pas présent, utiliser une chaîne vide pour éviter les erreurs.
    title = strip_html(raw.get("title_fr", ""))


    # Construire la description complète de l'événement en concaténant les champs "description_fr" 
    # et "longdescription_fr" après les avoir nettoyés.
    description = " ".join([
        strip_html(raw.get("description_fr")),
        strip_html(raw.get("longdescription_fr"))
    ]).strip()

    # Extraire les dates de début et de fin de l'événement à partir des champs "firstdate_begin" et "firstdate_end" du dictionnaire brut.
    start_datetime = raw.get("firstdate_begin")
    end_datetime = raw.get("firstdate_end")

    # Extraire les coordonnées de localisation de l'événement à partir du champ "location_coordinates".
    location = raw.get("location_coordinates") or {}

    # Construire un dictionnaire d'événement normalisé en extrayant les champs pertinents du dictionnaire brut,
    # en nettoyant les descriptions et en ajoutant des champs supplémentaires comme "retrieval_text" pour faciliter la recherche.
    event = {
        "event_id": event_id,
        "title": title,
        "description": description,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "location_name": raw.get("location_name"),
        "city": raw.get("location_city"),
        "postal_code": raw.get("location_postalcode"),
        "department_code": DEPARTMENT_CODE,
        "lat": location.get("lat"),
        "lon": location.get("lon"),
        "url": raw.get("canonicalurl"),
        "tags": raw.get("keywords_fr") or [],
        "source": SOURCE,
        "summary": strip_html(raw.get("description_fr")),
        "organizer": raw.get("contributor_organization"),
        "image_url": raw.get("image"),
        "price": raw.get("conditions_fr"),
        "accessibility": raw.get("accessibility_label_fr"),
        "updated_at": raw.get("updatedat"),
        "language": "fr"
    }

    # Construire le champ "retrieval_text" en concaténant 
    # les informations principales de l'événement pour faciliter la recherche ou l'indexation.
    event["retrieval_text"] = build_retrieval_text(event)

    return event


def is_valid(event):
    '''
    vérifie que les champs essentiels d'un événement sont présents et non vides.
    Args:        event (dict): Dictionnaire contenant les champs normalisés d'un événement.
    Returns:    bool: True si tous les champs essentiels sont présents et non vides, False sinon.
    '''
    required = [
        event.get("event_id"),
        event.get("title"),
        event.get("start_datetime"),
        event.get("url"),
    ]
    return all(required)


def main():
    '''
    Point d'entrée principal du script de normalisation des événements OpenAgenda.
    Ce script effectue les étapes suivantes :
    1. Crée le répertoire de sortie s'il n'existe pas. 
    2. Trouve le fichier RAW le plus récent dans le répertoire data/raw/.
    3. Lit chaque ligne du fichier RAW, normalise les données de l'événement, et vérifie leur validité.
    4. Écrit les événements valides dans un nouveau fichier JSONL dans le répertoire data/processed/, en évitant les doublons basés sur l'identifiant de l'événement.
    5. Affiche un résumé du processus de normalisation, y compris le nombre total d'événements lus, le nombre d'événements gardés, rejetés et les doublons détectés, ainsi que le chemin du fichier généré. 

    '''
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    raw_file = find_latest_raw_file()

    date_str = datetime.now().strftime("%Y-%m-%d")

    processed_path = os.path.join(
        PROCESSED_DIR,
        f"events_{date_str}.jsonl"
    )

    seen_ids = set()

    total = 0
    kept = 0
    rejected = 0
    duplicates = 0

    with open(raw_file, "r", encoding="utf-8") as fin, \
         open(processed_path, "w", encoding="utf-8") as fout:

        for line in fin:

            total += 1

            raw = json.loads(line)

            event = normalize_event(raw)

            if not is_valid(event):
                rejected += 1
                continue

            if event["event_id"] in seen_ids:
                duplicates += 1
                continue

            seen_ids.add(event["event_id"])

            fout.write(json.dumps(event, ensure_ascii=False) + "\n")

            kept += 1

    print("\nNormalisation terminée\n")

    print(f"RAW lus          : {total}")
    print(f"Événements gardés: {kept}")
    print(f"Rejetés          : {rejected}")
    print(f"Doublons         : {duplicates}")

    print(f"\nFichier généré : {processed_path}")


if __name__ == "__main__":
    main()