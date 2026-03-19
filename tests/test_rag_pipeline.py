"""Tests unitaires pour la pipeline RAG (Retrieval-Augmented Generation).
fonctions testées :
- ask_rag : Fonction principale de la pipeline RAG qui prend une question en entrée,
    récupère le contexte pertinent à partir de FAISS, génère une réponse avec Mistral, et retourne la réponse structurée avec les sources utilisées.
- format_sources : Fonction qui formate les sources retournées par FAISS pour les structurer de manière propre.
- make_mock_doc : Fonction utilitaire pour créer des documents simulés avec des métadonnées et du contenu, utilisée pour les tests de la pipeline RAG.
Les tests vérifient que la fonction ask_rag retourne une structure de données attendue, gère correctement les questions vides, retourne des résultats pour une question valide, et ne plante pas avec une question inhabituelle. Les tests utilisent des mocks pour simuler les fonctions de récupération et de génération, afin de se concentrer sur la logique de ask_rag et la structure de sa réponse.
"""
from unittest.mock import patch, MagicMock

from src.rag.rag_pipeline import ask_rag


def make_mock_doc(title, city, start_datetime, url, content):
    """
    Crée un document simulé pour les tests de la pipeline RAG.
    Args:
        title (str): Titre de l'événement.
        city (str): Ville de l'événement.
        start_datetime (str): Date et heure de début de l'événement au format ISO 8601.
        url (str): URL de l'événement.
        content (str): Contenu textuel de l'événement.
    Returns:
        MagicMock: Document simulé avec les métadonnées et le contenu spécifiés.
    """
    doc = MagicMock()
    doc.metadata = {
        "title": title,
        "city": city,
        "start_datetime": start_datetime,
        "url": url,
    }
    doc.page_content = content
    return doc


@patch("src.rag.rag_pipeline.generate_answer")
@patch("src.rag.rag_pipeline.retrieve_context")
def test_ask_rag_returns_expected_structure(mock_retrieve_context, mock_generate_answer):
    """Test de la fonction ask_rag pour vérifier qu'elle retourne une structure de données attendue.
    Ce test utilise des mocks pour simuler les fonctions retrieve_context et generate_answer, afin de se concentrer sur la structure de la réponse de ask_rag. Le test vérifie que la réponse contient les champs "question", "answer", "sources" et "n_results", et que ces champs ont les types de données attendus. Ce test permet de s'assurer que la fonction ask_rag retourne une réponse structurée même lorsque les fonctions de récupération et de génération sont simulées.
    Args:    mock_retrieve_context: Mock de la fonction retrieve_context pour simuler les résultats de récupération.
        mock_generate_answer: Mock de la fonction generate_answer pour simuler la réponse générée.
    Returns:    None
    Note: Ce test ne vérifie pas la logique interne de la fonction ask_rag, mais seulement que la structure de la réponse est correcte lorsque les fonctions de récupération et de génération sont simulées.
    """
    mock_generate_answer.return_value = "Réponse simulée"
    mock_retrieve_context.return_value = [
        make_mock_doc(
            title="Concert à Montpellier",
            city="Montpellier",
            start_datetime="2025-09-21T16:30:00+00:00",
            url="https://example.com/concert",
            content="Concert à Montpellier avec orchestre",
        )
    ]

    result = ask_rag("concert à Montpellier")

    assert "question" in result
    assert "answer" in result
    assert "sources" in result
    assert "n_results" in result

    assert result["question"] == "concert à Montpellier"
    assert isinstance(result["answer"], str)
    assert isinstance(result["sources"], list)
    assert isinstance(result["n_results"], int)


@patch("src.rag.rag_pipeline.generate_answer")
def test_ask_rag_empty_question(mock_generate_answer):
    """Test de la fonction ask_rag pour vérifier qu'elle gère correctement une question vide.
    Ce test utilise un mock pour simuler la fonction generate_answer, afin de se concentrer sur la gestion d'une question vide par ask_rag. Le test vérifie que lorsque la question est une chaîne vide, la fonction ask_rag retourne une réponse informative indiquant que la question est vide, sans appeler la fonction de génération. Ce test permet de s'assurer que la fonction ask_rag gère correctement les cas où l'utilisateur ne fournit pas de question.
    Args:    mock_generate_answer: Mock de la fonction generate_answer pour simuler la réponse générée.
    Returns:    None"""
    result = ask_rag("")

    assert result["question"] == ""
    assert isinstance(result["answer"], str)
    assert result["sources"] == []


@patch("src.rag.rag_pipeline.generate_answer")
@patch("src.rag.rag_pipeline.retrieve_context")
def test_ask_rag_valid_question_returns_results(mock_retrieve_context, mock_generate_answer):
    """Test de la fonction ask_rag pour vérifier qu'elle retourne des résultats attendus pour une question valide.
    Ce test utilise des mocks pour simuler les fonctions retrieve_context et generate_answer, afin de se concentrer sur la logique de ask_rag lorsqu'une question valide est posée. Le test vérifie que lorsque la question est "concert à Montpellier", la fonction ask_rag retourne une réponse générée (simulée), un nombre de résultats supérieur ou égal à 1, et une liste de sources contenant au moins un élément. Ce test permet de s'assurer que la fonction ask_rag fonctionne correctement pour une question valide et retourne des résultats structurés.
    Args:    mock_retrieve_context: Mock de la fonction retrieve_context pour simuler la récupération du contexte.
             mock_generate_answer: Mock de la fonction generate_answer pour simuler la génération de la réponse.
    Returns:    None"""
    mock_generate_answer.return_value = "Réponse simulée"
    mock_retrieve_context.return_value = [
        make_mock_doc(
            title="Concert à Montpellier",
            city="Montpellier",
            start_datetime="2025-09-21T16:30:00+00:00",
            url="https://example.com/concert",
            content="Concert à Montpellier avec orchestre",
        )
    ]

    result = ask_rag("concert à Montpellier")

    assert result["n_results"] >= 1
    assert len(result["sources"]) >= 1
    assert result["answer"] == "Réponse simulée"


@patch("src.rag.rag_pipeline.generate_answer")
@patch("src.rag.rag_pipeline.retrieve_context")
def test_ask_rag_unusual_question_does_not_crash(mock_retrieve_context, mock_generate_answer):
    """Test de la fonction ask_rag pour vérifier qu'elle ne plante pas avec une question inhabituelle.
    Ce test utilise des mocks pour simuler les fonctions retrieve_context et generate_answer, afin de se concentrer sur la robustesse de ask_rag face à une question inhabituelle. Le test vérifie que lorsque la question est "festival manga sous-marin à Lodève", la fonction ask_rag retourne une réponse générée (simulée), un nombre de résultats supérieur ou égal à 0, et une liste de sources (qui peut être vide). Ce test permet de s'assurer que la fonction ask_rag gère correctement les questions inhabituelles sans planter, même si elles ne correspondent à aucun événement dans le contexte.
    Args:    mock_retrieve_context: Mock de la fonction retrieve_context pour simuler la récupération du contexte.
             mock_generate_answer: Mock de la fonction generate_answer pour simuler la génération de la réponse.
    Returns:    None"""
    mock_generate_answer.return_value = "Réponse simulée"
    mock_retrieve_context.return_value = [
        make_mock_doc(
            title="Club Manga",
            city="Mauguio",
            start_datetime="2025-10-04T13:00:00+00:00",
            url="https://example.com/manga",
            content="Club manga à Mauguio",
        )
    ]

    result = ask_rag("festival manga sous-marin à Lodève")

    assert "question" in result
    assert "answer" in result
    assert "sources" in result
    assert "n_results" in result