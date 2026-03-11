import requests

BASE_URL = "http://127.0.0.1:8000"


def run_ask_check(question: str):
    response = requests.post(
        f"{BASE_URL}/ask",
        json={"question": question}
    )

    print("\n=== CHECK /ask ===")
    print("Status code :", response.status_code)
    print("Réponse JSON :")
    print(response.json())


def run_rebuild_check():
    response = requests.post(f"{BASE_URL}/rebuild")

    print("\n=== CHECK /rebuild ===")
    print("Status code :", response.status_code)
    print("Réponse JSON :")
    print(response.json())


if __name__ == "__main__":
    run_ask_check("concert à Montpellier")
    run_ask_check("")
    run_rebuild_check()