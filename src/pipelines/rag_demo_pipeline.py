from src.rag.rag_pipeline import ask_rag


def main():

    question = "concert à Montpellier"

    result = ask_rag(question)

    print("\nQUESTION")
    print(result["question"])

    print("\nRÉPONSE GÉNÉRÉE")
    print(result["answer"])

    print("\nNOMBRE DE RÉSULTATS")
    print(result["n_results"])

    print("\nSOURCES")
    for source in result["sources"]:
        print("-", source["title"], "|", source["city"], "|", source["start_datetime"])


if __name__ == "__main__":
    main()