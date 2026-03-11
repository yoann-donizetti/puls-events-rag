"""
Objectif ;
Créer un script qui :
- charque qa_dataset.json
-exécute ask_rag() pour chaque question
-récupere la réponse générée
- sauvegare les résultats dans un fichier evaluation_results.json
"""
import json
from pathlib import Path

from src.rag.rag_pipeline import ask_rag


DATASET_PATH = Path("src/evaluation/qa_dataset.json")
OUTPUT_PATH = Path("src/evaluation/evaluation_results.json")


def load_qa_dataset(path: Path) -> list[dict]:
    """
    Charge le jeu de questions/réponses de référence.
    """
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_results(results: list[dict], path: Path) -> None:
    """
    Sauvegarde les résultats d'évaluation dans un fichier JSON.
    """
    with path.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


def evaluate_rag() -> list[dict]:
    """
    Exécute le pipeline RAG sur chaque question du dataset
    et retourne les résultats.
    """
    qa_dataset = load_qa_dataset(DATASET_PATH)
    results = []

    for item in qa_dataset:
        question = item["question"]
        reference_answer = item["reference_answer"]
        question_type = item["type"]

        rag_result = ask_rag(question)

        results.append(
            {
                "question": question,
                "reference_answer": reference_answer,
                "type": question_type,
                "generated_answer": rag_result["answer"],
                "sources": rag_result["sources"],
                "n_results": rag_result["n_results"],
            }
        )

    return results


def main():
    results = evaluate_rag()
    save_results(results, OUTPUT_PATH)

    print(f"Évaluation terminée : {len(results)} questions traitées.")
    print(f"Résultats sauvegardés dans : {OUTPUT_PATH}")


if __name__ == "__main__":
    main()