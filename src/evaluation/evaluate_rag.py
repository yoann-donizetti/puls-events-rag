"""Ce module contient le code d'évaluation du pipeline RAG.
Il charge un dataset de questions-réponses, exécute le pipeline RAG pour chaque question, compare la réponse générée avec la réponse de référence et calcule une étiquette automatique de succès ou d'échec.
Les résultats de l'évaluation sont sauvegardés dans un fichier JSON pour une analyse ultérieure."""
import json
import time
from pathlib import Path

from mistralai.models.sdkerror import SDKError

from src.rag.rag_pipeline import ask_rag


DATASET_PATH = Path("src/evaluation/qa_dataset.json")
OUTPUT_PATH = Path("src/evaluation/evaluation_results.json")

FALLBACK_ANSWER = "je ne trouve pas cette information dans les données disponibles."


def load_qa_dataset(path: Path) -> list[dict]:
    """Charge le dataset de questions-réponses à partir d'un fichier JSON.
    Le fichier doit être une liste de dictionnaires avec les champs question, reference_answer et type (positive/negative).
    """
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_results(results: list[dict], path: Path) -> None:
    """Sauvegarde les résultats de l'évaluation dans un fichier JSON.
    Le fichier contiendra une liste de dictionnaires avec les champs question, reference_answer, type, generated_answer, sources, n_results et auto_label.
    """
    with path.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


def is_negative_answer_valid(answer: str) -> bool:
    """Vérifie si la réponse générée pour une question négative est cohérente avec l'absence d'information.
    Considère que la réponse est valide si elle contient des expressions indiquant clairement que l'information n'est pas trouvée ou n'existe pas dans le contexte.
    """
    answer_lower = answer.lower().strip()

    negative_patterns = [
        "pas d'information",
        "n'existe pas",
        "aucun événement",
        "aucune information",
        "pas présent dans le contexte",
        "pas dans le contexte",
        "je n'ai trouvé aucun",
        "je n’ai trouvé aucun",
        "ne mentionne aucun",
        FALLBACK_ANSWER,
    ]

    return any(pattern in answer_lower for pattern in negative_patterns)


def is_fallback(answer: str) -> bool:
    """Vérifie si la réponse générée correspond à la réponse de fallback indiquant que l'information n'est pas trouvée dans les données disponibles.
    Cette fonction est utilisée pour évaluer les questions positives où une réponse de fallback indique un échec.
    """
    return answer.lower().strip() == FALLBACK_ANSWER


def compute_auto_label(question_type: str, generated_answer: str, n_results: int) -> str:
    """Calcule une étiquette automatique de succès ou d'échec pour une question donnée.
    Pour les questions positives, considère que c'est un succès si le nombre de résultats est supérieur à 0 et que la réponse générée n'est pas un fallback.
    Pour les questions négatives, considère que c'est un succès si la réponse générée est valide selon la fonction is_negative_answer_valid.
    Retourne "success" ou "failure" en fonction de l'évaluation.
    """
    if question_type == "positive":
        if is_fallback(generated_answer):
            return "failure"
        return "success" if n_results > 0 else "failure"

    if question_type == "negative":
        return "success" if is_negative_answer_valid(generated_answer) else "failure"

    return "failure"


def safe_ask_rag(question: str, max_retries: int = 3, base_sleep: int = 2) -> dict:
    """
    Appelle ask_rag avec retry en cas d'erreur temporaire côté Mistral.
    Si toutes les tentatives échouent, retourne une réponse d'erreur contrôlée.
    """
    for attempt in range(max_retries):
        try:
            return ask_rag(question)

        except SDKError as e:
            wait_time = base_sleep ** attempt
            print(
                f"[SDKError] Question: {question} | "
                f"Tentative {attempt + 1}/{max_retries} | Erreur: {e}"
            )

            if attempt < max_retries - 1:
                print(f"Nouvel essai dans {wait_time} seconde(s)...")
                time.sleep(wait_time)
            else:
                print("Échec définitif après plusieurs tentatives.")

        except Exception as e:
            print(
                f"[Erreur inattendue] Question: {question} | "
                f"Tentative {attempt + 1}/{max_retries} | Erreur: {e}"
            )

            if attempt < max_retries - 1:
                wait_time = base_sleep ** attempt
                print(f"Nouvel essai dans {wait_time} seconde(s)...")
                time.sleep(wait_time)
            else:
                print("Échec définitif après plusieurs tentatives.")

    return {
        "question": question,
        "answer": "Erreur temporaire lors de la génération de la réponse.",
        "sources": [],
        "n_results": 0,
    }


def evaluate_rag() -> list[dict]:
    """Évalue le pipeline RAG sur un dataset de questions-réponses.
    Pour chaque question du dataset, exécute le pipeline RAG et compare la réponse générée avec la réponse de référence.
    Calcule une étiquette automatique de succès ou d'échec pour chaque question en fonction du type de question (positive ou negative) et du contenu de la réponse générée.
    Retourne une liste de dictionnaires contenant les résultats de l'évaluation pour chaque question."""
    qa_dataset = load_qa_dataset(DATASET_PATH)
    results = []

    for item in qa_dataset:
        question = item["question"]
        reference_answer = item["reference_answer"]
        question_type = item["type"]

        print(f"\nTraitement : {question}")

        rag_result = safe_ask_rag(question)

        auto_label = compute_auto_label(
            question_type=question_type,
            generated_answer=rag_result["answer"],
            n_results=rag_result["n_results"],
        )

        results.append(
            {
                "question": question,
                "reference_answer": reference_answer,
                "type": question_type,
                "generated_answer": rag_result["answer"],
                "sources": rag_result["sources"],
                "n_results": rag_result["n_results"],
                "auto_label": auto_label,
            }
        )

    return results


def main():
    results = evaluate_rag()
    save_results(results, OUTPUT_PATH)

    total = len(results)
    success_count = sum(1 for r in results if r["auto_label"] == "success")
    accuracy = success_count / total if total > 0 else 0

    print(f"\nÉvaluation terminée : {total} questions traitées.")
    print(f"Succès : {success_count}/{total}")
    print(f"Accuracy automatique : {accuracy:.2%}")
    print(f"Résultats sauvegardés dans : {OUTPUT_PATH}")


if __name__ == "__main__":
    main()