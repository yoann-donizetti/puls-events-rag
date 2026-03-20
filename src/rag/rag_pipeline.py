"""Pipeline de question-réponse avec récupération de contexte (RAG) pour le système Puls-Events.
Ce module implémente la fonction ask_rag qui prend une question en entrée, récupère les documents pertinents depuis l'index FAISS, construit un contexte à partir de ces documents, génère un prompt structuré et envoie ce prompt au modèle de langage Mistral pour obtenir une réponse générée. La fonction gère également les cas où la question est vide, où aucun résultat n'est trouvé ou où le contexte ne peut pas être construit, en retournant des réponses informatives sans appeler le LLM dans ces cas.
Étapes :
1. Validation de la question : Vérifie que la question n'est pas vide ou composée uniquement d'espaces.
2. Récupération des documents pertinents : Utilise la fonction retrieve_context pour obtenir les documents les plus pertinents depuis l'index FAISS, avec déduplication et reranking simple.
3. Construction du contexte : Transforme les documents récupérés en un texte de contexte structuré.
4. Génération du prompt : Utilise la fonction build_prompt pour créer un prompt structuré à partir de la question et du contexte.
5. Appel au modèle de langage : Envoie le prompt au modèle Mistral via la fonction generate_answer et retourne la réponse générée.
6. Formatage des sources : Formate les sources utilisées pour la réponse afin de les inclure dans la sortie finale.
Le module utilise les bibliothèques LangChain pour la gestion de l'index FAISS et des embeddings, ainsi que la bibliothèque mistralai pour interagir avec le modèle de langage Mistral. Les fonctions de ce module sont conçues pour être facilement testables et maintenables, avec une séparation claire des responsabilités entre la récupération de contexte, la construction du prompt et l'appel au modèle de langage."""
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


def deduplicate_results(results):
    """Déduplication des résultats basés sur l'URL ou une combinaison de titre, ville et date.
    Args:        results (list): Liste de documents retournés par la recherche de similarité.
    Returns:        list: Liste de documents dédupliqués.
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


def simple_score(question: str, doc) -> int:
    """Score simple basé sur la présence de mots de la question dans le titre et le contenu du document.
    Args:        question (str): La question posée par l'utilisateur.
        doc: Document LangChain avec page_content et metadata.
    Returns:        int: Score de pertinence simple pour le document.
    Note: Ce score est très basique et peut être amélioré avec des techniques plus sophistiquées de reranking."""
    q_words = set(question.lower().split())
    
    title = doc.metadata.get("title", "").lower()
    content = doc.page_content.lower()

    score = 0

    # boost titre
    score += sum(2 for w in q_words if w in title)

    # contenu normal
    score += sum(1 for w in q_words if w in content)

    return score



def retrieve_context(question: str, k: int = DEFAULT_TOP_K):
    """
    Récupère les documents les plus pertinents avec déduplication + reranking simple.
    """
    vectorstore = load_vectorstore()

    # On récupère plus large pour filtrer ensuite
    raw_results = vectorstore.similarity_search(question, k=max(k * 3, 9))

    # Déduplication
    results = deduplicate_results(raw_results)

    # Reranking simple (basé sur les mots de la question)
    results = sorted(results, key=lambda doc: simple_score(question, doc), reverse=True)

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