from src.rag.rag_pipeline import ask_rag


def main():
    question = "concert à Montpellier"
    result = ask_rag(question)

    print("\nQUESTION")
    print(result["question"])

    print("\nCONTEXTE")
    print(result["context"][:1200])

    print("\nPROMPT FINAL")
    print(result["prompt"][:2000])


if __name__ == "__main__":
    main()