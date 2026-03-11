from src.rag.prompt_builder import build_prompt
from src.rag.mistral_client import generate_answer


def retrieve_context(question: str, k: int = 3):
    """
    Placeholder pour la récupération des chunks pertinents depuis FAISS.
    """
    return []


def build_context(results) -> str:
    """
    Transforme les résultats récupérés en texte de contexte.
    """
    return ""


def ask_rag(question: str) -> dict:
    """
    Pipeline RAG complet :
    question -> retrieval -> contexte -> prompt -> génération
    """
    results = retrieve_context(question)
    context = build_context(results)
    prompt = build_prompt(question, context)
    answer = generate_answer(prompt)

    return {
        "question": question,
        "answer": answer,
        "sources": results,
    }