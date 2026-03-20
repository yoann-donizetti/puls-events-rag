"""
Tests unitaires pour les endpoints de l'API FastAPI du système RAG Puls-Events.
Ce module utilise la bibliothèque pytest pour définir des tests unitaires qui vérifient le bon fonctionnement des endpoints de l'API, notamment /ask, /rebuild, /health et la redirection de la racine vers /docs. Les tests utilisent la fixture TestClient de FastAPI pour simuler des requêtes HTTP vers l'API et vérifier les réponses retournées. Certains tests utilisent également la fixture monkeypatch pour simuler le comportement de fonctions internes (comme ask_rag ou rebuild_vectorstore) afin de tester les endpoints sans dépendre de la logique interne ou des services externes comme Mistral.
Les tests couvrent les cas suivants :   - Test de l'endpoint /ask avec une question d'exemple pour vérifier la structure de la réponse.
- Test de l'endpoint /ask avec une question vide pour vérifier la gestion des erreurs.  
- Test de l'endpoint /rebuild pour vérifier qu'il retourne une réponse de succès.
- Test de l'endpoint /health pour vérifier qu'il retourne un statut OK. 
- Test de la redirection de la racine vers /docs.
- Test de l'endpoint /ask pour simuler une erreur de limite de requêtes (429) de Mistral.
- Test de l'endpoint /ask pour simuler une erreur générique de type SDKError de Mistral.
- Test de l'endpoint /rebuild pour simuler une erreur lors de la reconstruction de l'index FAISS.
- Test de l'endpoint /ask pour simuler une erreur inattendue lors de la génération de la réponse.
"""
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_ask_endpoint(monkeypatch):
    """Test de l'endpoint /ask avec une question d'exemple.
Ce test vérifie que l'endpoint /ask retourne une réponse structurée avec les champs attend
és (question, answer, sources, n_results) et que les types de ces champs sont corrects. Le test utilise monkeypatch pour simuler la fonction ask_rag et éviter d'appeler le modèle de langage Mistral pendant le test.
Args:    monkeypatch: Fixture de pytest pour remplacer temporairement des fonctions ou des objets pendant le test.
Returns:    None
Note: Ce test ne vérifie pas la logique interne de la fonction ask_rag, mais seulement que l'endpoint /ask gère correctement les réponses et les erreurs.
"""
    def mock_ask_rag(question):
        """Simule la fonction ask_rag pour retourner une réponse fixe sans appeler le modèle de langage Mistral.
        Args:            question (str): La question posée par l'utilisateur.
        Returns:            dict: Une réponse simulée avec les champs question, answer, sources et n_results.
        """
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
    """Test de l'endpoint /ask avec une question vide.
Ce test vérifie que l'endpoint /ask retourne une erreur 400 avec un message detail indiquant que la question est vide lorsque l'utilisateur envoie une question composée uniquement d'espaces ou d'une chaîne vide.
Args:    None
Returns:    None
Note: Ce test ne vérifie pas la logique interne de la fonction ask_rag, mais seulement que l'endpoint /ask gère correctement le cas d'une question vide.
"""
    response = client.post(
        "/ask",
        json={"question": ""}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "La question est vide."


def test_rebuild_endpoint(monkeypatch):
    """Test de l'endpoint /rebuild pour vérifier qu'il retourne une réponse de succès.
Ce test utilise monkeypatch pour simuler la fonction rebuild_vectorstore et éviter d'exécuter la logique de reconstruction de l'index FAISS pendant le test. Le test vérifie que l'endpoint /rebuild retourne une réponse avec un statut "success" et un message de confirmation.
Args:    monkeypatch: Fixture de pytest pour remplacer temporairement des fonctions ou des objets pendant le test.
Returns:    None
Note: Ce test ne vérifie pas la logique interne de la fonction rebuild_vectorstore, mais seulement que l'endpoint /rebuild gère correctement les réponses et les erreurs.
"""
    def mock_rebuild_vectorstore():
        return None

    monkeypatch.setattr("src.api.main.rebuild_vectorstore", mock_rebuild_vectorstore)

    response = client.post("/rebuild")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert "message" in data


def test_health():
    """Test de l'endpoint /health pour vérifier qu'il retourne un statut OK.
Args:    None
Returns:    None
Note: Ce test ne vérifie pas la logique interne de l'endpoint /health, mais seulement qu'il retourne un statut OK.
"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_redirect():
    """Test de l'endpoint racine pour vérifier qu'il redirige vers /docs.
        Args:    None
        Returns:    None
        Note: Ce test vérifie que l'endpoint racine ("/") redirige correctement vers la documentation de l'API ("/docs") avec un code de statut 307 ou 302.
        """
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (307, 302)
    assert response.headers["location"] == "/docs"


def test_ask_rate_limit(monkeypatch):
    """Test de l'endpoint /ask pour simuler une erreur de limite de requêtes (429) de Mistral.
Ce test utilise monkeypatch pour simuler la fonction ask_rag et faire en sorte qu'elle lève une exception de type SDKError avec un message indiquant une erreur 429. Le test vérifie que l'endpoint /ask retourne une erreur 429 avec un message detail approprié lorsque la fonction ask_rag simule une erreur de limite de requêtes.
Args:    monkeypatch: Fixture de pytest pour remplacer temporairement des fonctions ou des objets pendant le test.
Returns:    None
Note: Ce test ne vérifie pas la logique interne de la fonction ask_rag, mais seulement que l'endpoint /ask gère correctement les erreurs de limite de requêtes.
"""
    class FakeSDKError(Exception):
        pass

    monkeypatch.setattr("src.api.main.SDKError", FakeSDKError)

    def mock_ask_rag(question):
        """Simule une erreur de limite de requêtes en levant une exception FakeSDKError avec un message contenant "429" ou "rate limit".
        Args:            question (str): La question posée par l'utilisateur.
        Returns:            None
        Note: Le message de l'exception doit contenir "429" ou "rate limit" pour que l'endpoint /ask puisse identifier correctement le type d'erreur et retourner une réponse 429.
        """

        raise FakeSDKError("API error occurred: Status 429. Body: rate limit exceeded")

    monkeypatch.setattr("src.api.main.ask_rag", mock_ask_rag)

    response = client.post("/ask", json={"question": "concert à Montpellier"})

    assert response.status_code == 429
    assert "Limite de requêtes atteinte" in response.json()["detail"]


def test_ask_sdk_error_generic(monkeypatch):
    """Test de l'endpoint /ask pour simuler une erreur générique de type SDKError de Mistral.
        Ce test utilise monkeypatch pour simuler la fonction ask_rag et faire en sorte qu'ellelève une exception de type SDKError avec un message indiquant une erreur générique (par exemple "Unauthorized"). Le test vérifie que l'endpoint /ask retourne une erreur 500 avec un message detail approprié lorsque la fonction ask_rag simule une erreur générique de type SDKError.
        Args:    monkeypatch: Fixture de pytest pour remplacer temporairement des fonctions ou des objets pendant le test.
        Returns:    None
        Note: Ce test ne vérifie pas la logique interne de la fonction ask_rag, mais seulement que l'endpoint /ask gère correctement les erreurs génériques de type SDKError.
        """
    class FakeSDKError(Exception):
        pass

    monkeypatch.setattr("src.api.main.SDKError", FakeSDKError)

    def mock_ask_rag(question):
        """Simule une erreur générique de type SDKError en levant une exception FakeSDKError avec un message ne contenant pas "429" ou "rate limit".
        Args:            question (str): La question posée par l'utilisateur.
        Returns:            None
        Note: Le message de l'exception ne doit pas contenir "429" ou "rate limit" pour que l'endpoint /ask puisse identifier correctement le type d'erreur et retourner une réponse 500.
        """
        raise FakeSDKError("Unauthorized")

    monkeypatch.setattr("src.api.main.ask_rag", mock_ask_rag)

    response = client.post("/ask", json={"question": "concert à Montpellier"})

    assert response.status_code == 500
    assert response.json()["detail"] == "Erreur SDK Mistral lors de la génération de la réponse."


def test_rebuild_endpoint_error(monkeypatch):
    """Test de l'endpoint /rebuild pour simuler une erreur lors de la reconstruction de l'index FAISS.
        Ce test utilise monkeypatch pour simuler la fonction rebuild_vectorstore et faire en sorte qu'elle lève une exception générique. Le test vérifie que l'endpoint /rebuild retourne une erreur 500 avec un message detail approprié lorsque la fonction rebuild_vectorstore simule une erreur.
        Args:    monkeypatch: Fixture de pytest pour remplacer temporairement des fonctions ou des objets pendant le test.
        Returns:    None
        Note: Ce test ne vérifie pas la logique interne de la fonction rebuild_vectorstore, mais seulement que l'endpoint /rebuild gère correctement les erreurs.
        """
    def mock_rebuild_vectorstore():
        """Simule une erreur générique en levant une exception avec un message d'erreur.
        Args:            None
        Returns:            None
        Note: Le message de l'exception peut être quelconque, car l'endpoint /rebuild doit retourner une réponse 500 pour toute exception levée par la fonction rebuild_vectorstore.
        """
        raise Exception("boom")

    monkeypatch.setattr("src.api.main.rebuild_vectorstore", mock_rebuild_vectorstore)

    response = client.post("/rebuild")

    assert response.status_code == 500
    assert response.json()["detail"] == "Une erreur est survenue lors de la reconstruction de l'index."

def test_ask_unexpected_error(monkeypatch):
    """Test de l'endpoint /ask pour simuler une erreur inattendue lors de la génération de la réponse.
        Ce test utilise monkeypatch pour simuler la fonction ask_rag et faire en sorte qu'ellelève une exception générique (par exemple "unexpected"). Le test vérifie que l'endpoint /ask retourne une erreur 500 avec un message detail approprié lorsque la fonction ask_rag simule une erreur inattendue.
        Args:    monkeypatch: Fixture de pytest pour remplacer temporairement des fonctions ou des objets pendant le test.
        Returns:    None
        Note: Ce test ne vérifie pas la logique interne de la fonction ask_rag, mais seulement que l'endpoint /ask gère correctement les erreurs inattendues.
    """
    def mock_ask_rag(question):
        raise Exception("unexpected")

    monkeypatch.setattr("src.api.main.ask_rag", mock_ask_rag)

    response = client.post("/ask", json={"question": "concert à Montpellier"})

    assert response.status_code == 500
    assert response.json()["detail"] == "Une erreur est survenue lors de la génération de la réponse."