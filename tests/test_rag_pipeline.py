from unittest.mock import patch, MagicMock

from src.rag.rag_pipeline import ask_rag


def make_mock_doc(title, city, start_datetime, url, content):
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
    result = ask_rag("")

    assert result["question"] == ""
    assert isinstance(result["answer"], str)
    assert result["sources"] == []


@patch("src.rag.rag_pipeline.generate_answer")
@patch("src.rag.rag_pipeline.retrieve_context")
def test_ask_rag_valid_question_returns_results(mock_retrieve_context, mock_generate_answer):
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