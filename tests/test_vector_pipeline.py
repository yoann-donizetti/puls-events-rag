import json
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from src.embeddings.prepare_documents import create_documents
from src.embeddings.chunk_documents import chunk_documents

MODEL_NAME="sentence-transformers/all-MiniLM-L6-v2"

def load_sample_events():
    """Charger un échantillon d'événements à partir d'un fichier JSONL pour les tests.
    Returns:
        events (list): Liste d'événements chargés à partir du fichier JSONL.
    """
    path = Path("tests/data/sample_events.jsonl")
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def test_chunks_generated():
    """Tester que les chunks sont générés correctement à partir des documents.
    Cette fonction vérifie que les événements sont chargés, 
    que les documents sont créés à partir de ces événements, 
    et que les chunks sont générés à partir des documents.
    """
    events = load_sample_events()
    documents = create_documents(events)
    chunks = chunk_documents(documents)
    assert len(chunks) > 0, "Aucun chunk n'a été généré à partir des documents."

def test_build_faiss_index():
    """Tester la construction de l'index FAISS à partir des chunks de documents.
    Cette fonction vérifie que l'index FAISS est construit correctement à partir des chunks,
    et que le nombre de vecteurs indexés correspond au nombre de chunks générés.
    """
    events = load_sample_events()
    documents = create_documents(events)
    chunks = chunk_documents(documents)
    embeddings_model = HuggingFaceEmbeddings(model_name=MODEL_NAME)
    vectorstore = FAISS.from_documents(chunks, embeddings_model)
    assert vectorstore is not None, "L'index FAISS n'a pas été construit correctement."
    assert vectorstore.index.ntotal == len(chunks), "Le nombre de vecteurs indexés ne correspond pas au nombre de chunks générés."

def test_semantic_search_returns_results():
    """Tester que la recherche sémantique retourne des résultats pertinents pour une requête donnée.
    Cette fonction vérifie que la recherche sémantique retourne des résultats pour une requête spécifique,
    et que ces résultats sont pertinents par rapport à la requête."""
    events = load_sample_events()
    documents = create_documents(events)
    chunks = chunk_documents(documents)
    embeddings_model = HuggingFaceEmbeddings(model_name=MODEL_NAME)
    vectorstore = FAISS.from_documents(chunks, embeddings_model)

    query = "concert à Montpellier"
    results = vectorstore.similarity_search(query, k=5)
    assert len(results) > 0, "La recherche sémantique n'a retourné aucun résultat pour la requête."

def test_metadata_present():
    """Tester que les métadonnées sont présentes dans les résultats de la recherche sémantique.
    Cette fonction vérifie que les résultats de la recherche sémantique contiennent les métadonnées attendues,
    telles que le titre, la ville, la date et l'URL de l'événement."""
    events = load_sample_events()
    documents = create_documents(events)
    chunks = chunk_documents(documents)
    embeddings_model = HuggingFaceEmbeddings(model_name=MODEL_NAME)
    vectorstore = FAISS.from_documents(chunks, embeddings_model)

    query = "concert à Montpellier"
    results = vectorstore.similarity_search(query, k=5)
    for doc in results:
        assert "title" in doc.metadata, "Le champ 'title' est manquant dans les métadonnées du résultat."
        assert "city" in doc.metadata, "Le champ 'city' est manquant dans les métadonnées du résultat."
        assert "start_datetime" in doc.metadata, "Le champ 'start_datetime' est manquant dans les métadonnées du résultat."
        assert "url" in doc.metadata, "Le champ 'url' est manquant dans les métadonnées du résultat."
        assert "event_id" in doc.metadata, "Le champ 'event_id' est manquant dans les métadonnées du résultat."