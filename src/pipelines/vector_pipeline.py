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