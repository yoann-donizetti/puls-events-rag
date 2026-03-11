from src.rag.rag_pipeline import retrieve_context, build_context


def main():
    question = "concert à Montpellier"

    results = retrieve_context(question, k=3)

    print("\nQUESTION")
    print(question)

    print("\nRÉSULTATS BRUTS")
    for i, doc in enumerate(results, start=1):
        print(f"\nRésultat {i}")
        print("Titre :", doc.metadata.get("title"))
        print("Ville :", doc.metadata.get("city"))
        print("Date :", doc.metadata.get("start_datetime"))
        print("URL :", doc.metadata.get("url"))
        print("Extrait :", doc.page_content[:200], "...")

    context = build_context(results)

    print("\nCONTEXTE CONSTRUIT")
    print(context[:1000])


if __name__ == "__main__":
    main()