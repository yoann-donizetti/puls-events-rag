"""
Ce script prépare les documents à vectoriser à partir des événements traités.
Il suppose que les événements traités sont stockés dans un fichier JSONL dans data/processed/ avec le pattern events_*.jsonl.
Il effectue les étapes suivantes : 
1. Trouver le fichier le plus récent dans data/processed/ avec le pattern events_*.jsonl
2. Charger les événements à partir du fichier JSONL
3. Créer une liste de documents LangChain à partir des événements, en utilisant le texte de récupération et les métadonnées de chaque événement.
4. Afficher un résumé de la préparation des documents, y compris un exemple de document créé.
"""

import json
import os
import glob # pour trouver le fichier le plus récent dans data/processed/
from langchain_core.documents import Document

PROCESSED_DIR = "data/processed/"

def find_latest_processed_file():
    """
    Trouve le fichier le plus récent dans data/processed/ avec le pattern events_*.jsonl
    Retourne le chemin du fichier le plus récent.
    """
    # Trouver le fichier le plus récent dans data/processed/
    files = glob.glob(os.path.join(PROCESSED_DIR, "events_*.jsonl"))
    if not files:
        raise FileNotFoundError("Aucun fichier traité trouvé dans data/processed/")
    
    latest_file = max(files, key=os.path.getctime)
    return latest_file

def load_events(file_path):
    """
    Charge les événements à partir d'un fichier JSONL.
    Retourne une liste d'événements.
    """
    events = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            event = json.loads(line)
            events.append(event)
    return events


def create_documents(events):
    """Crée une liste de documents LangChain à partir des événements.
    Chaque document contient le texte de récupération et les métadonnées de l'événement.
    """
    documents = []
    for event in events:
        text=event.get("retrieval_text", "").strip()
        if not text:
            continue  # ignorer les événements sans texte de récupération

        metadata = {
            "event_id": event.get("event_id"),
            "title": event.get("title"),
            "start_datetime": event.get("start_datetime"),
            "end_datetime": event.get("end_datetime"),
            "location_name": event.get("location_name"),
            "city": event.get("city"),
            "postal_code": event.get("postal_code"),
            "department_code": event.get("department_code"),
            "url": event.get("url"),
            "source": event.get("source"),
        }


        # Créer un document LangChain avec le texte de récupération et les métadonnées
        doc = Document(
            page_content=text,
            metadata=metadata
        )
        documents.append(doc)
    return documents



def main ():
    print("Préparation des documents à vectoriser")
    file_path = find_latest_processed_file()
    print(f"Dataset utilisé : {file_path}")
    events = load_events(file_path)
    print(f"{len(events)} événements chargés")
    documents = create_documents(events)
    print(f"{len(documents)} documents créés à partir des événements")
    print("\nExemple document :")
    print(documents[0].page_content[:200])
    print(documents[0].metadata)
if __name__ == "__main__":
    main()

