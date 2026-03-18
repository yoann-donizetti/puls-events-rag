import os
import json
from pathlib import Path

from dotenv import load_dotenv
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    Faithfulness,
    AnswerSimilarity,
    ContextPrecision,
    ContextRecall,
)

from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper

from langchain_mistralai import ChatMistralAI
from langchain_huggingface import HuggingFaceEmbeddings


load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

DATASET_PATH = Path("src/evaluation/rag_answers.json")
OUTPUT_PATH = Path("src/evaluation/evaluation_results_ragas.json")

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def load_dataset() -> Dataset:
    with DATASET_PATH.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)

    questions = []
    answers = []
    contexts = []
    ground_truths = []

    for item in data:
        questions.append(item["question"])
        answers.append(item["answer"])

        context_list = [
            " | ".join(
                filter(
                    None,
                    [
                        source.get("title"),
                        source.get("city"),
                        source.get("start_datetime"),
                        source.get("url"),
                    ],
                )
            )
            for source in item["contexts"]
        ]

        contexts.append(context_list)
        ground_truths.append(item["ground_truth"])

    return Dataset.from_dict(
        {
            "question": questions,
            "answer": answers,
            "contexts": contexts,
            "ground_truth": ground_truths,
        }
    )


def main() -> None:
    if not MISTRAL_API_KEY:
        raise ValueError("MISTRAL_API_KEY introuvable dans le fichier .env")

    print("Clé Mistral chargée :", MISTRAL_API_KEY[:8] + "...")

    ragas_dataset = load_dataset()

    mistral_llm = ChatMistralAI(
        model="mistral-small-latest",
        temperature=0,
        api_key=MISTRAL_API_KEY,
    )
    evaluator_llm = LangchainLLMWrapper(mistral_llm)

    hf_embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME
    )
    evaluator_embeddings = LangchainEmbeddingsWrapper(hf_embeddings)

    result = evaluate(
        dataset=ragas_dataset,
        metrics=[
            Faithfulness(),
            AnswerSimilarity(),
            ContextPrecision(),
            ContextRecall(),
        ],
        llm=evaluator_llm,
        embeddings=evaluator_embeddings,
    )

    print("\n===== RAGAS EVALUATION =====\n")
    print(result)

    df = result.to_pandas()
    global_scores = df.mean(numeric_only=True).to_dict()

    print("\n===== SCORES GLOBAUX =====\n")
    print(global_scores)

    output = {
        "global_scores": global_scores,
        "detailed_results": df.to_dict(orient="records"),
    }

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nRésultats sauvegardés dans : {OUTPUT_PATH}")


if __name__ == "__main__":
    main()