from src.rag.rag_pipeline import ask_rag


def main():
    question = "Quels concerts ont lieu à Montpellier ?"
    result = ask_rag(question)

    print("\nQUESTION")
    print(result["question"])

    print("\nRÉPONSE")
    print(result["answer"])

    print("\nSOURCES")
    print(result["sources"])


if __name__ == "__main__":
    main()