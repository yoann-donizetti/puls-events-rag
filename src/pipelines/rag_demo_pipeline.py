from src.rag.rag_pipeline import ask_rag


def main():
    question = ""

    result = ask_rag(question, k=3)

    print("\nQUESTION")
    print(result["question"])

    print("\nRÉPONSE GÉNÉRÉE")
    print(result["answer"])

    print("\nSOURCES")
    for source in result["sources"]:
        print("-", source["title"], "|", source["city"], "|", source["start_datetime"])


if __name__ == "__main__":
    main()