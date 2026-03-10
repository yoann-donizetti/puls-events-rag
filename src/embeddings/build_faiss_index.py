import os
from langchain_community.vectorstores import FAISS # FAISS est une bibliothèque de Facebook AI Research pour la recherche de similarité rapide dans les grands ensembles de données vectorielles.
from langchain_huggingface import HuggingFaceEmbeddings
from src.embeddings.prepare_documents import (
    find_latest_processed_file,
    load_events,
    create_documents,
)
from src.embeddings.chunk_documents import chunk_documents
MODEL_NAME="sentence-transformers/all-MiniLM-L6-v2"
INDEX_DIR="data/vectorstore"

def build_index(chunks):
    embeddings_model=HuggingFaceEmbeddings(model_name=MODEL_NAME)
    vectorstore=FAISS.from_documents(chunks, embeddings_model)
    return vectorstore

def save_index(vectorstore) :
    os.makedirs(INDEX_DIR, exist_ok=True)
    vectorstore.save_local(INDEX_DIR)
    print(f"Index FAISS sauvegardé dans {INDEX_DIR}")


def main():
    file_path = find_latest_processed_file()
    events=load_events(file_path)
    documents=create_documents(events)
    chunks=chunk_documents(documents)
    print(f"Documents : {len(documents)}")
    print(f"Chunks : {len(chunks)}")
    vectorstore=build_index(chunks)
    save_index(vectorstore)

if __name__ == "__main__":
    main()