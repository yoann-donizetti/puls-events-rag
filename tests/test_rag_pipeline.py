from unittest.mock import patch

from src.rag.rag_pipeline import ask_rag


@patch("src.rag.rag_pipeline.generate_answer")
def test_ask_rag_returns_expected_structure(mock_generate_answer):
    mock_generate_answer.return_value = "Réponse simulée"

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
    result = ask_rag("")

    assert result["question"] == ""
    assert result["sources"] == []
    assert isinstance(result["answer"], str)


@patch("src.rag.rag_pipeline.generate_answer")
def test_ask_rag_valid_question_returns_results(mock_generate_answer):
    mock_generate_answer.return_value = "Réponse simulée"

    result = ask_rag("concert à Montpellier")

    assert result["n_results"] >= 1
    assert len(result["sources"]) >= 1
    assert result["answer"] == "Réponse simulée"


@patch("src.rag.rag_pipeline.generate_answer")
def test_ask_rag_unusual_question_does_not_crash(mock_generate_answer):
    mock_generate_answer.return_value = "Réponse simulée"

    result = ask_rag("festival manga sous-marin à Lodève")

    assert "question" in result
    assert "answer" in result
    assert "sources" in result
    assert "n_results" in result