import requests

BASE_URL = "http://127.0.0.1:8000"


def test_ask(question: str):
    """
    Teste l'endpoint POST /ask
    """
    response = requests.post(
        f"{BASE_URL}/ask",
        json={"question": question}
    )

    print("\n=== TEST /ask ===")
    print("Status code :", response.status_code)
    print("Réponse JSON :")
    print(response.json())


def test_rebuild():
    """
    Teste l'endpoint POST /rebuild
    """
    response = requests.post(f"{BASE_URL}/rebuild")

    print("\n=== TEST /rebuild ===")
    print("Status code :", response.status_code)
    print("Réponse JSON :")
    print(response.json())


if __name__ == "__main__":
    test_ask("concert à Montpellier")
    test_rebuild()