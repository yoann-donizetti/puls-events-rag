from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_ask_endpoint(monkeypatch):
    def mock_ask_rag(question):
        return {
            "question": question,
            "answer": "Réponse simulée",
            "sources": [],
            "n_results": 0,
        }

    monkeypatch.setattr("src.api.main.ask_rag", mock_ask_rag)

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


def test_rebuild_endpoint(monkeypatch):
    def mock_rebuild_vectorstore():
        return None

    monkeypatch.setattr("src.api.main.rebuild_vectorstore", mock_rebuild_vectorstore)

    response = client.post("/rebuild")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert "message" in data


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (307, 302)
    assert response.headers["location"] == "/docs"


def test_ask_rate_limit(monkeypatch):
    class FakeSDKError(Exception):
        pass

    monkeypatch.setattr("src.api.main.SDKError", FakeSDKError)

    def mock_ask_rag(question):
        raise FakeSDKError("API error occurred: Status 429. Body: rate limit exceeded")

    monkeypatch.setattr("src.api.main.ask_rag", mock_ask_rag)

    response = client.post("/ask", json={"question": "concert à Montpellier"})

    assert response.status_code == 429
    assert "Limite de requêtes atteinte" in response.json()["detail"]


def test_ask_sdk_error_generic(monkeypatch):
    class FakeSDKError(Exception):
        pass

    monkeypatch.setattr("src.api.main.SDKError", FakeSDKError)

    def mock_ask_rag(question):
        raise FakeSDKError("Unauthorized")

    monkeypatch.setattr("src.api.main.ask_rag", mock_ask_rag)

    response = client.post("/ask", json={"question": "concert à Montpellier"})

    assert response.status_code == 500
    assert response.json()["detail"] == "Erreur SDK Mistral lors de la génération de la réponse."


def test_rebuild_endpoint_error(monkeypatch):
    def mock_rebuild_vectorstore():
        raise Exception("boom")

    monkeypatch.setattr("src.api.main.rebuild_vectorstore", mock_rebuild_vectorstore)

    response = client.post("/rebuild")

    assert response.status_code == 500
    assert response.json()["detail"] == "Une erreur est survenue lors de la reconstruction de l'index."

def test_ask_unexpected_error(monkeypatch):
    def mock_ask_rag(question):
        raise Exception("unexpected")

    monkeypatch.setattr("src.api.main.ask_rag", mock_ask_rag)

    response = client.post("/ask", json={"question": "concert à Montpellier"})

    assert response.status_code == 500
    assert response.json()["detail"] == "Une erreur est survenue lors de la génération de la réponse."