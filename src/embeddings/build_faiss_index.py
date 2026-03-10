import os
from langchain_community.vectorstores import FAISS # FAISS est une bibliothèque de Facebook AI Research pour la recherche de similarité rapide dans les grands ensembles de données vectorielles.
from langchain_huggingface import HuggingFaceEmbeddings
import json
from src.embeddings.prepare_documents import (
    find_latest_processed_file,
    load_events,
    create_documents,
)
from src.embeddings.chunk_documents import chunk_documents
MODEL_NAME="sentence-transformers/all-MiniLM-L6-v2"
INDEX_DIR="data/vectorstore"

def build_index(chunks):
    """
    Construire un index FAISS à partir des chunks de documents.
    Args:
        chunks (list): Liste de chunks de documents.
        Returns:
        vectorstore: Index FAISS construit à partir des chunks.
    """
    embeddings_model=HuggingFaceEmbeddings(model_name=MODEL_NAME)
    vectorstore=FAISS.from_documents(chunks, embeddings_model)
    return vectorstore

def save_index(vectorstore) :
    """Sauvegarder l'index FAISS localement.
    Args:
        vectorstore: Index FAISS à sauvegarder.
    """
    os.makedirs(INDEX_DIR, exist_ok=True)
    vectorstore.save_local(INDEX_DIR)
    print(f"Index FAISS sauvegardé dans {INDEX_DIR}")

def generate_index_report(events, documents, chunks,vectorstore):
    """
    Générer un rapport d'indexation pour évaluer la qualité de l'index FAISS.
    Args:
        events (list): Liste des événements d'origine.
        documents (list): Liste des documents créés à partir des événements.
        chunks (list): Liste des chunks générés à partir des documents.
        vectorstore: Index FAISS construit à partir des chunks.
    Returns:
        report (dict): Rapport d'indexation contenant des métriques clés.
    """

    indexed_vectors=vectorstore.index.ntotal
    report={
        "total_events": len(events),
        "total_documents": len(documents),
        "total_chunks": len(chunks),
        "indexed_vectors": indexed_vectors,
        "integrity_check": indexed_vectors == len(chunks)
    }
    print("\n=== RAPPORT D'INDEXATION ===")
    print(f"Événements lus : {report['total_events']}")
    print(f"Documents créés : {report['total_documents']}")
    print(f"Chunks générés : {report['total_chunks']}")
    print(f"Vecteurs indexés : {report['indexed_vectors']}")

    if report["integrity_check"]:
        print(" Intégrité OK : tous les chunks sont indexés")
    else:
        print(" Problème : certains chunks ne sont pas indexés")

    return report

def main():
    # Trouver le fichier de données le plus récent
    file_path = find_latest_processed_file()

    # Charger les événements à partir du fichier
    events=load_events(file_path)

    # Créer des documents à partir des événements
    documents=create_documents(events)

    # Diviser les documents en chunks
    chunks=chunk_documents(documents)
    print(f"Documents : {len(documents)}")
    print(f"Chunks : {len(chunks)}")

    # Construire l'index FAISS à partir des chunks
    vectorstore=build_index(chunks)

    # Générer un rapport d'indexation
    report = generate_index_report(events, documents, chunks, vectorstore)
    # Sauvegarder le rapport d'indexation au format JSON
    with open(os.path.join(INDEX_DIR, "index_report.json"), "w") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)

    # Sauvegarder l'index FAISS localement
    save_index(vectorstore)

if __name__ == "__main__":
    main()