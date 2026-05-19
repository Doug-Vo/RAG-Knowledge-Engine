"""
Shared pytest fixtures for the AI Document Workbench test suite.

Because loading_doc_helper.py and app.py both initialize MongoDB clients,
OpenAI models, and Talisman at module import time, all heavy dependencies
must be patched BEFORE any module is imported. The session-scoped
mock_external_deps fixture handles this.
"""

import pytest
from unittest.mock import MagicMock, patch


def _make_mock_llm():
    mock = MagicMock()
    mock.return_value = mock
    mock.invoke.return_value = MagicMock(content="Test answer")
    return mock


def _make_mock_embeddings():
    mock = MagicMock()
    mock.return_value = mock
    mock.embed_query.return_value = [0.0] * 1536
    mock.embed_documents.return_value = [[0.0] * 1536]
    return mock


def _make_mock_vector_store():
    mock = MagicMock()
    mock.return_value = mock
    retriever = MagicMock()
    retriever.invoke.return_value = []
    mock.as_retriever.return_value = retriever
    mock.from_documents.return_value = None
    return mock


def _make_mock_talisman():
    """Talisman(app, ...) returns an instance; calling that instance with kwargs
    (e.g. @talisman(force_https=False)) must return a passthrough decorator."""
    passthrough = lambda f: f
    instance = MagicMock()
    instance.return_value = passthrough   # instance(force_https=False) → decorator
    cls = MagicMock(return_value=instance)
    return cls


def _make_mock_mongo():
    collection = MagicMock()
    collection.find_one.return_value = None
    db = MagicMock()
    db.__getitem__.return_value = collection
    client = MagicMock()
    client.__getitem__.return_value = db
    client.admin.command.return_value = {"ok": 1.0}
    return MagicMock(return_value=client)


@pytest.fixture(scope="session", autouse=True)
def mock_external_deps():
    """Patch all network/API dependencies before any app module is imported."""
    with patch("pymongo.MongoClient", _make_mock_mongo()), \
         patch("langchain_openai.OpenAIEmbeddings", _make_mock_embeddings()), \
         patch("langchain_openai.ChatOpenAI", _make_mock_llm()), \
         patch("langchain_mongodb.MongoDBAtlasVectorSearch", _make_mock_vector_store()), \
         patch("flask_talisman.Talisman", _make_mock_talisman()):
        yield


@pytest.fixture()
def flask_app(mock_external_deps):
    from app import app
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret"
    app.config["WTF_CSRF_ENABLED"] = False
    return app


@pytest.fixture()
def client(flask_app):
    with flask_app.test_client() as c:
        yield c
