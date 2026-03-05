import faiss
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

from mistralai.client import MistralClient


def main():
    print("OK: faiss")
    print("OK: langchain FAISS")
    print("OK: HuggingFaceEmbeddings")
    print("OK: MistralClient")


if __name__ == "__main__":
    main()