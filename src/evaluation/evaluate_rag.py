import json
from pathlib import Path

from src.rag.rag_pipeline import ask_rag


DATASET_PATH = Path("src/evaluation/qa_dataset.json")
OUTPUT_PATH = Path("src/evaluation/evaluation_results.json")


def load_qa_dataset(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_results(results: list[dict], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


def is_negative_answer_valid(answer: str) -> bool:
    answer_lower = answer.lower()

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
    ]

    return any(pattern in answer_lower for pattern in negative_patterns)


def compute_auto_label(question_type: str, generated_answer: str, n_results: int) -> str:
    if question_type == "positive":
        return "success" if n_results > 0 else "failure"

    if question_type == "negative":
        return "success" if is_negative_answer_valid(generated_answer) else "failure"

    return "failure"


def evaluate_rag() -> list[dict]:
    qa_dataset = load_qa_dataset(DATASET_PATH)
    results = []

    for item in qa_dataset:
        question = item["question"]
        reference_answer = item["reference_answer"]
        question_type = item["type"]

        rag_result = ask_rag(question)

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

    print(f"Évaluation terminée : {total} questions traitées.")
    print(f"Succès : {success_count}/{total}")
    print(f"Accuracy automatique : {accuracy:.2%}")
    print(f"Résultats sauvegardés dans : {OUTPUT_PATH}")


if __name__ == "__main__":
    main()