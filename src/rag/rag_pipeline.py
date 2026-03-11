from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from src.rag.prompt_builder import build_prompt
from src.rag.mistral_client import generate_answer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
INDEX_DIR = "data/vectorstore"
DEFAULT_TOP_K = 3


def load_vectorstore():
    """
    Charge l'index FAISS sauvegardé localement.
    raise une erreur si l'index n'est pas trouvé ou si la désérialisation échoue.
        
    """
    embeddings_model = HuggingFaceEmbeddings(model_name=MODEL_NAME)

    vectorstore = FAISS.load_local(
        INDEX_DIR,
        embeddings_model,
        allow_dangerous_deserialization=True
    )

    return vectorstore


def retrieve_context(question: str, k: int = DEFAULT_TOP_K):
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


def format_sources(results) -> list[dict]:
    """
    Formate les sources retournées pour avoir une sortie propre.
    sortie : une liste de dictionnaires avec les champs title, city, start_datetime et url.
    """
    sources = []

    for doc in results:
        sources.append(
            {
                "title": doc.metadata.get("title"),
                "city": doc.metadata.get("city"),
                "start_datetime": doc.metadata.get("start_datetime"),
                "url": doc.metadata.get("url"),
            }
        )

    return sources


def ask_rag(question: str, k: int = DEFAULT_TOP_K) -> dict:
    """
    Pipeline RAG complet :
    question -> retrieval -> contexte -> prompt -> génération
    retourne un dictionnaire avec les champs question, answer, sources et n_results.
    gère les cas où la question est vide, où aucun résultat n'est trouvé ou où le contexte ne peut pas être construit.
    dans ces cas, retourne une réponse informative sans appeler le LLM.
    """

    if not question or not question.strip():
        return {
            "question": question,
            "answer": "La question est vide. Merci de saisir une demande.",
            "sources": [],
        }

    results = retrieve_context(question.strip(), k=k)

    if not results:
        return {
            "question": question,
            "answer": "Je n'ai trouvé aucun événement correspondant à votre demande.",
            "sources": [],
        }

    context = build_context(results)

    if not context.strip():
        return {
            "question": question,
            "answer": "Je n'ai pas pu construire de contexte exploitable à partir des résultats trouvés.",
            "sources": [],
        }

    prompt = build_prompt(question, context)
    answer = generate_answer(prompt)

    return {
        "question": question,
        "answer": answer,
        "sources": format_sources(results),
        "n_results": len(results),
    }