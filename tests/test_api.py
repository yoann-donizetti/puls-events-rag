__test__ = False
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_ask_endpoint():
    response = client.post(
        "/ask",
        json={"question": "concert à Montpellier"}
    )

    assert response.status_code == 200

    data = response.json()

    assert "question" in data
    assert "answer" in data
    assert "sources" in data
    assert "n_results" in data

    assert data["question"] == "concert à Montpellier"
    assert isinstance(data["answer"], str)
    assert isinstance(data["sources"], list)
    assert isinstance(data["n_results"], int)


def test_ask_empty_question():
    response = client.post(
        "/ask",
        json={"question": ""}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "La question est vide."


def test_rebuild_endpoint():
    response = client.post("/rebuild")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert "message" in data

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}