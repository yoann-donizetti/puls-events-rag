"""
Ce script génère les embeddings à partir des chunks de documents créés à partir des événements. 
Il utilise le modèle "sentence-transformers/all-MiniLM-L6-v2" pour créer des vecteurs d'embeddings
 à partir du contenu textuel des chunks. 
 Les embeddings générés sont ensuite affichés avec leur dimension 
 et un aperçu du début du premier vecteur.
"""


from dotenv import load_dotenv
import os

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")# Hugging Face API token pour accéder aux modèles d'embeddings.

if HF_TOKEN:
    os.environ["HF_TOKEN"] = HF_TOKEN

from langchain_huggingface import HuggingFaceEmbeddings

from src.embeddings.prepare_documents import (
    find_latest_processed_file,
    load_events,
    create_documents,
)

from src.embeddings.chunk_documents import chunk_documents


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def generate_embeddings(chunks):
    """
    Génère des embeddings à partir des chunks de documents en utilisant le modèle spécifié.
    Args:
        chunks (list): Liste de chunks de documents.
    Returns:
        list: Liste de vecteurs d'embeddings générés à partir des chunks.
    """
    embeddings_model = HuggingFaceEmbeddings(
    model_name=MODEL_NAME
)

    texts = [chunk.page_content for chunk in chunks]
    vectors = embeddings_model.embed_documents(texts)

    return vectors


def main():
    file_path = find_latest_processed_file()

    print(f"Dataset utilisé : {file_path}")

    events = load_events(file_path)
    print(f"Événements lus : {len(events)}")

    documents = create_documents(events)
    print(f"Documents créés : {len(documents)}")

    chunks = chunk_documents(documents)
    print(f"Chunks générés : {len(chunks)}")

    vectors = generate_embeddings(chunks)
    print(f"Embeddings générés : {len(vectors)}")

    if vectors:
        print(f"Dimension d'un vecteur : {len(vectors[0])}")
        print(f"Début du premier vecteur : {vectors[0][:10]}")


if __name__ == "__main__":
    main()