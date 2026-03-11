from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from src.rag.prompt_builder import build_prompt
from src.rag.mistral_client import generate_answer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
INDEX_DIR = "data/vectorstore"


def load_vectorstore():
    """
    Charge l'index FAISS sauvegardé localement.
    """
    embeddings_model = HuggingFaceEmbeddings(model_name=MODEL_NAME)

    vectorstore = FAISS.load_local(
        INDEX_DIR,
        embeddings_model,
        allow_dangerous_deserialization=True
    )

    return vectorstore


def retrieve_context(question: str, k: int = 3):
    """
    Récupère les k chunks les plus pertinents depuis FAISS.
    """
    vectorstore = load_vectorstore()
    results = vectorstore.similarity_search(question, k=k)
    return results


def build_context(results) -> str:
    """
    Transforme les résultats en texte de contexte.
    """
    if not results:
        return ""

    context_parts = []

    for i, doc in enumerate(results, start=1):
        part = f"""Événement {i}
Titre : {doc.metadata.get("title", "Non renseigné")}
Ville : {doc.metadata.get("city", "Non renseignée")}
Date : {doc.metadata.get("start_datetime", "Non renseignée")}
URL : {doc.metadata.get("url", "Non renseignée")}
Contenu : {doc.page_content}
"""
        context_parts.append(part)

    return "\n\n".join(context_parts)


def ask_rag(question: str) -> dict:
    """
    Pipeline RAG complet.
    """
    results = retrieve_context(question)
    context = build_context(results)
    prompt = build_prompt(question, context)

    return {
        "question": question,
        "context": context,
        "prompt": prompt,
        "sources": results,
    }