from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

MODEL_NAME="sentence-transformers/all-MiniLM-L6-v2"
INDEX_DIR="data/vectorstore"

def load_vectorstore():
    """
    Charger l'index FAISS localement.
    allow_dangerous_deserialization=True est nécessaire
    pour éviter les erreurs de désérialisation 
    lors du chargement de l'index FAISS,
    en particulier si l'index a été créé avec une version différente de la bibliothèque
    ou si des modifications ont été apportées à la structure des données.
    Returns:
        vectorstore: Index FAISS chargé à partir du stockage local.
    """
    embeddings_model=HuggingFaceEmbeddings(model_name=MODEL_NAME)
    vectorstore=FAISS.load_local(
        INDEX_DIR,
        embeddings_model,
        allow_dangerous_deserialization=True
        )
    return vectorstore

def search_query(vectorstore, query, k=5):

    results = vectorstore.similarity_search(query, k=k)

    print("\n==============================")
    print(f"REQUÊTE : {query}")
    print("==============================")

    for i, doc in enumerate(results, 1):

        print(f"\nRésultat {i}")

        print("Titre :", doc.metadata.get("title"))

        print("Ville :", doc.metadata.get("city"))

        print("Date :", doc.metadata.get("start_datetime"))

        print("URL :", doc.metadata.get("url"))

        print("Extrait :", doc.page_content[:200], "...")

def main():
    vectorstore=load_vectorstore()
    queries = [
        "concert à Montpellier",
        "emploi tourisme Hérault",
        "atelier cuisine Béziers",
        "événement en ligne",
        "salon voyage",
    ]
    for query in queries:
        search_query(vectorstore, query)

if __name__ == "__main__":
    main()

