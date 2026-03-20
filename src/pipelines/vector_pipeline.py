"""Pipeline de création de l'index vectoriel pour le système RAG Puls-Events.
Étapes :
1. Chargement du dataset d'événements depuis le fichier JSON le plus récent
2. Création de documents à partir des événements
3. Division des documents en chunks
4. Construction de l'index FAISS à partir des chunks
5. Sauvegarde de l'index FAISS localement
6. Génération d'un rapport d'indexation pour évaluer la qualité de l'index
"""
from src.embeddings.prepare_documents import (
    find_latest_processed_file,
    load_events,
    create_documents,
)

from src.embeddings.chunk_documents import chunk_documents
from src.embeddings.build_faiss_index import build_index, save_index


def main():

    print("Chargement dataset")

    file_path = find_latest_processed_file()
    events = load_events(file_path)

    documents = create_documents(events)
    chunks = chunk_documents(documents)

    print(f"Documents : {len(documents)}")
    print(f"Chunks : {len(chunks)}")

    vectorstore = build_index(chunks)

    save_index(vectorstore)

    print("Pipeline vectoriel terminé")


if __name__ == "__main__":
    main()