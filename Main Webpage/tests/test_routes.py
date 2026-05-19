"""Flask route tests for /, /ingest, and /healthz."""

import io
from unittest.mock import patch
from langchain_core.documents import Document


# ---------------------------------------------------------------------------
# GET /
# ---------------------------------------------------------------------------

def test_home_get_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_home_get_contains_html(client):
    response = client.get("/")
    assert b"html" in response.data.lower()


def test_home_get_tab_query_param(client):
    response = client.get("/?tab=query")
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# POST /
# ---------------------------------------------------------------------------

def test_home_post_no_question_returns_200(client):
    response = client.post("/", data={"question": ""})
    assert response.status_code == 200


def test_home_post_with_question_returns_answer(client):
    mock_doc = Document(page_content="Some context", metadata={"source": "test.pdf"})
    mock_result = {"answer": "The answer is 42", "context": [mock_doc]}

    with patch("app.rag_chain") as mock_chain, patch("app.judge_chain") as mock_judge:
        mock_chain.invoke.return_value = mock_result
        mock_judge.invoke.return_value = "ACCURATE"
        response = client.post("/", data={"question": "What is the answer?"})

    assert response.status_code == 200
    assert b"The answer is 42" in response.data


def test_home_post_grade_accurate(client, monkeypatch):
    from unittest.mock import MagicMock
    mock_result = {"answer": "Correct answer", "context": []}
    monkeypatch.setattr("app.rag_chain", MagicMock(invoke=MagicMock(return_value=mock_result)))
    monkeypatch.setattr("app.judge_chain", MagicMock(invoke=MagicMock(return_value="ACCURATE")))
    response = client.post("/", data={"question": "test"})
    assert b"Accurate" in response.data  # template renders "Accurate", not "ACCURATE"


def test_home_post_grade_hallucination(client, monkeypatch):
    from unittest.mock import MagicMock
    mock_result = {"answer": "Made up answer", "context": []}
    monkeypatch.setattr("app.rag_chain", MagicMock(invoke=MagicMock(return_value=mock_result)))
    monkeypatch.setattr("app.judge_chain", MagicMock(invoke=MagicMock(return_value="HALLUCINATION")))
    response = client.post("/", data={"question": "test"})
    assert b"Potential Hallucination" in response.data  # template renders "Potential Hallucination"


def test_home_post_rag_exception_shows_error(client):
    with patch("app.rag_chain") as mock_chain:
        mock_chain.invoke.side_effect = Exception("OpenAI down")
        response = client.post("/", data={"question": "anything"})
    assert response.status_code == 200
    assert b"something went wrong" in response.data


# ---------------------------------------------------------------------------
# POST /ingest
# ---------------------------------------------------------------------------

def test_ingest_no_input_redirects(client):
    response = client.post("/ingest", data={})
    assert response.status_code == 302


def test_ingest_no_input_flashes_warning(client):
    with client.session_transaction():
        pass
    response = client.post("/ingest", data={}, follow_redirects=True)
    assert b"No valid input provided" in response.data


def test_ingest_pdf_happy_path(client):
    pdf_bytes = b"%PDF-1.4 fake content"
    mock_doc = Document(page_content="PDF text", metadata={"source": "test.pdf"})

    with patch("app.check_if_source_exists", return_value=False), \
         patch("app.load_pdf", return_value=[mock_doc]), \
         patch("app.split_text", return_value=[mock_doc]), \
         patch("app.embed_and_upload"):
        response = client.post(
            "/ingest",
            data={"pdf_file": (io.BytesIO(pdf_bytes), "test.pdf")},
            content_type="multipart/form-data",
            follow_redirects=True,
        )
    assert b"Successfully ingested" in response.data


def test_ingest_duplicate_flashes_warning(client):
    with patch("app.check_if_source_exists", return_value=True):
        response = client.post(
            "/ingest",
            data={"source_url": "https://example.com"},
            follow_redirects=True,
        )
    assert b"Already exists" in response.data


def test_ingest_url_web_happy_path(client):
    mock_doc = Document(page_content="Web text", metadata={"source": "https://example.com"})
    with patch("app.check_if_source_exists", return_value=False), \
         patch("app.load_link", return_value=[mock_doc]), \
         patch("app.split_text", return_value=[mock_doc]), \
         patch("app.embed_and_upload"):
        response = client.post(
            "/ingest",
            data={"source_url": "https://example.com"},
            follow_redirects=True,
        )
    assert b"Successfully ingested" in response.data


def test_ingest_youtube_url_shows_unsupported_warning(client):
    response = client.post(
        "/ingest",
        data={"source_url": "https://www.youtube.com/watch?v=abc"},
        follow_redirects=True,
    )
    assert b"YouTube ingestion is no longer supported" in response.data


# ---------------------------------------------------------------------------
# GET /healthz
# ---------------------------------------------------------------------------

def test_healthz_healthy(client):
    with patch("app.client") as mock_mongo:
        mock_mongo.admin.command.return_value = {"ok": 1.0}
        response = client.get("/healthz")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"


def test_healthz_mongo_failure_returns_500(client):
    with patch("app.client") as mock_mongo:
        mock_mongo.admin.command.side_effect = Exception("connection refused")
        response = client.get("/healthz")
    assert response.status_code == 500
    data = response.get_json()
    assert data["status"] == "unhealthy"
