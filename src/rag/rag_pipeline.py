from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from src.rag.prompt_builder import build_prompt
from src.rag.mistral_client import generate_answer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
INDEX_DIR = "data/vectorstore"
DEFAULT_TOP_K = 5


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


def normalize_text(text: str) -> str:
    if not text:
        return ""
    return (
        text.lower()
        .replace("é", "e")
        .replace("è", "e")
        .replace("ê", "e")
        .replace("à", "a")
        .replace("ù", "u")
        .replace("ô", "o")
        .replace("î", "i")
        .replace("ï", "i")
    )


def deduplicate_results(results):
    """
    Supprime les doublons sur la base de l'URL ou du triplet titre+ville+date.
    """
    unique_results = []
    seen = set()

    for doc in results:
        key = (
            doc.metadata.get("url")
            or f"{doc.metadata.get('title')}|{doc.metadata.get('city')}|{doc.metadata.get('start_datetime')}"
        )

        if key not in seen:
            seen.add(key)
            unique_results.append(doc)

    return unique_results


def extract_month_filter(question: str) -> str | None:
    """
    Détecte quelques filtres temporels simples.
    Retourne un préfixe YYYY-MM si identifié.
    """
    q = normalize_text(question)

    month_map = {
        "janvier 2025": "2025-01",
        "fevrier 2025": "2025-02",
        "mars 2025": "2025-03",
        "avril 2025": "2025-04",
        "mai 2025": "2025-05",
        "juin 2025": "2025-06",
        "juillet 2025": "2025-07",
        "aout 2025": "2025-08",
        "septembre 2025": "2025-09",
        "octobre 2025": "2025-10",
        "novembre 2025": "2025-11",
        "decembre 2025": "2025-12",
    }

    for key, value in month_map.items():
        if key in q:
            return value

    return None


def apply_month_filter(results, month_filter: str | None):
    """
    Garde les documents dont la date commence par YYYY-MM.
    Si aucun document ne correspond, on garde les résultats initiaux.
    """
    if not month_filter:
        return results

    filtered = []

    for doc in results:
        start_datetime = doc.metadata.get("start_datetime") or ""
        if start_datetime.startswith(month_filter):
            filtered.append(doc)

    return filtered if filtered else results


def retrieve_context(question: str, k: int = DEFAULT_TOP_K):
    """
    Récupère les chunks les plus pertinents depuis FAISS,
    puis applique déduplication et filtre temporel simple.
    """
    vectorstore = load_vectorstore()

    # On récupère un peu plus large pour pouvoir nettoyer ensuite
    raw_results = vectorstore.similarity_search(question, k=max(k * 3, 9))

    # Déduplication
    results = deduplicate_results(raw_results)

    # Filtre temporel simple
    month_filter = extract_month_filter(question)
    results = apply_month_filter(results, month_filter)

    # Réduction du bruit : on limite fort à la fin
    return results[:k]


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
Contenu : {doc.page_content}
"""
        context_parts.append(part)

    return "\n\n".join(context_parts)


def format_sources(results) -> list[dict]:
    """
    Formate les sources retournées pour avoir une sortie propre.
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
    Pipeline RAG complet.
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