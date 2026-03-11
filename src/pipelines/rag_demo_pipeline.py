from src.rag.rag_pipeline import ask_rag


def main():

    question = "concert à Montpellier"

    result = ask_rag(question)

    print("\nQUESTION")
    print(result["question"])

    print("\nRÉPONSE GÉNÉRÉE")
    print(result["answer"])

    print("\nSOURCES")
    for doc in result["sources"]:
        print("-", doc.metadata.get("title"))


if __name__ == "__main__":
    main()