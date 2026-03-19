"""Pipeline de démonstration du système RAG Puls-Events.
Ce pipeline permet de tester le système RAG en posant une question d'exemple et en affichant la réponse générée, les sources utilisées et le nombre de résultats récupérés dans FAISS.
Étapes :
1. Pose une question d'exemple (ex: "concert à Montpellier")
2. Appelle la fonction ask_rag pour obtenir la réponse générée par le système RAG
3. Affiche la question, la réponse, le nombre de résultats et les sources utilisées
"""
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