from langchain_text_splitters import RecursiveCharacterTextSplitter # recursive character text splitter pour diviser les documents en chunks de taille gérable

from src.embeddings.prepare_documents import (
    find_latest_processed_file,
    load_events,
    create_documents
)



def chunk_documents(documents):
    """
    Divise les documents en chunks de taille gérable pour l'indexation.
    chunk_size : nombre de caractères par chunk (500 est une taille courante pour les modèles de langage)
    chunk_overlap : nombre de caractères de chevauchement entre les chunks pour maintenir le contexte (50 est une valeur courante pour éviter de perdre trop de contexte entre les chunks)
    Args:
        documents (list): Liste de documents à chunker.
    Returns:
        list: Liste de chunks générés à partir des documents.
    
    """
    # Utilisation de RecursiveCharacterTextSplitter pour diviser les documents en chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = splitter.split_documents(documents)

    return chunks


def main():

    file_path = find_latest_processed_file()

    print(f"Dataset utilisé : {file_path}")

    events = load_events(file_path)

    print(f"Événements lus : {len(events)}")

    documents = create_documents(events)

    print(f"Documents créés : {len(documents)}")

    chunks = chunk_documents(documents)

    print(f"Chunks générés : {len(chunks)}")

    print("\nExemple chunk :\n")
    print(chunks[0].page_content[:300])
    print("\nMetadata :", chunks[0].metadata)


if __name__ == "__main__":
    main()