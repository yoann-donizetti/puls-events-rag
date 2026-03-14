import json
from pathlib import Path

from dotenv import load_dotenv
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import answer_similarity
from ragas.metrics import (
    Faithfulness,
    AnswerSimilarity,
    ContextPrecision,
    ContextRecall,
    _ContextRelevance,
)
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper

from langchain_mistralai import ChatMistralAI
from langchain_huggingface import HuggingFaceEmbeddings

from src.rag.rag_pipeline import ask_rag


load_dotenv()

DATASET_PATH = Path("src/evaluation/qa_dataset.json")
OUTPUT_PATH = Path("src/evaluation/evaluation_results_ragas.json")

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def load_dataset() -> list[dict]:
    with DATASET_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_ragas_dataset(qa_data: list[dict]) -> Dataset:
    questions = []
    answers = []
    contexts = []
    ground_truths = []

    for item in qa_data:
        question = item["question"]
        reference = item["reference_answer"]

        rag_result = ask_rag(question)

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
            for source in rag_result["sources"]
        ]

        questions.append(question)
        answers.append(rag_result["answer"])
        contexts.append(context_list)
        ground_truths.append(reference)

    return Dataset.from_dict(
        {
            "question": questions,
            "answer": answers,
            "contexts": contexts,
            "ground_truth": ground_truths,
        }
    )


def main() -> None:
    qa_data = load_dataset()
    ragas_dataset = build_ragas_dataset(qa_data)

    mistral_llm = ChatMistralAI(
        model="mistral-small-latest",
        temperature=0,
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
            _ContextRelevance(),
        ],
        llm=evaluator_llm,
        embeddings=evaluator_embeddings,
    )

    print("\n===== RAGAS EVALUATION =====\n")
    print(result)

    # Sauvegarde propre via pandas
    df = result.to_pandas()
    df.to_json(OUTPUT_PATH, orient="records", force_ascii=False, indent=2)

    print(f"\nRésultats sauvegardés dans : {OUTPUT_PATH}")


if __name__ == "__main__":
    main()