import json
from pathlib import Path

from src.rag.rag_pipeline import ask_rag


INPUT_PATH = Path("src/evaluation/qa_dataset.json")
OUTPUT_PATH = Path("src/evaluation/rag_answers.json")


def generate_answers():

    with INPUT_PATH.open("r", encoding="utf-8-sig") as f:
        qa_data = json.load(f)

    results = []

    for item in qa_data:

        question = item["question"]
        reference = item["reference_answer"]

        print(f"Question : {question}")

        rag_result = ask_rag(question)
        time.sleep(2)
        results.append({
            "question": question,
            "answer": rag_result["answer"],
            "contexts": rag_result["sources"],
            "ground_truth": reference
        })

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nRéponses sauvegardées dans : {OUTPUT_PATH}")


if __name__ == "__main__":
    generate_answers()