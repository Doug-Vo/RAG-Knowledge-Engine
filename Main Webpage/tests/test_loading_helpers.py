"""Unit tests for loading_doc_helper.py — all I/O is mocked."""

from unittest.mock import patch
from langchain_core.documents import Document


# ---------------------------------------------------------------------------
# load_pdf
# ---------------------------------------------------------------------------

def test_load_pdf_non_pdf_returns_empty():
    from loading_doc_helper import load_pdf
    assert load_pdf("document.txt") == []


def test_load_pdf_happy_path():
    mock_doc = Document(page_content="Hello PDF", metadata={"source": "file.pdf"})
    with patch("loading_doc_helper.PyPDFLoader") as mock_loader_cls:
        mock_loader_cls.return_value.load.return_value = [mock_doc]
        from loading_doc_helper import load_pdf
        result = load_pdf("file.pdf")
    assert result == [mock_doc]


# ---------------------------------------------------------------------------
# load_link
# ---------------------------------------------------------------------------

def test_load_link_non_https_returns_empty():
    from loading_doc_helper import load_link
    assert load_link("http://example.com") == []


def test_load_link_happy_path():
    mock_doc = Document(page_content="Web content", metadata={"source": "https://example.com"})
    with patch("loading_doc_helper.WebBaseLoader") as mock_loader_cls:
        mock_loader_cls.return_value.load.return_value = [mock_doc]
        from loading_doc_helper import load_link
        result = load_link("https://example.com")
    assert result == [mock_doc]


# ---------------------------------------------------------------------------
# split_text
# ---------------------------------------------------------------------------

def test_split_text_empty_returns_empty():
    from loading_doc_helper import split_text
    assert split_text([]) == []


def test_split_text_creates_chunks():
    from loading_doc_helper import split_text
    big_doc = Document(page_content="word " * 500, metadata={"source": "test.pdf"})
    chunks = split_text([big_doc])
    assert len(chunks) > 1


def test_split_text_preserves_metadata():
    from loading_doc_helper import split_text
    doc = Document(page_content="x " * 300, metadata={"source": "my.pdf", "title": "Test"})
    chunks = split_text([doc])
    for chunk in chunks:
        assert chunk.metadata.get("source") == "my.pdf"
        assert chunk.metadata.get("title") == "Test"


# ---------------------------------------------------------------------------
# embed_and_upload
# ---------------------------------------------------------------------------

def test_embed_and_upload_empty_is_noop():
    with patch("loading_doc_helper.MongoDBAtlasVectorSearch") as mock_vs:
        from loading_doc_helper import embed_and_upload
        embed_and_upload([])
        mock_vs.from_documents.assert_not_called()


def test_embed_and_upload_sets_metadata():
    doc = Document(page_content="content", metadata={"source": "f.pdf"})
    with patch("loading_doc_helper.MongoDBAtlasVectorSearch") as mock_vs:
        mock_vs.from_documents.return_value = None
        from loading_doc_helper import embed_and_upload
        embed_and_upload([doc])
    assert "created_at" in doc.metadata
    assert doc.metadata["is_persistent"] is False


# ---------------------------------------------------------------------------
# check_if_source_exists
# ---------------------------------------------------------------------------

def test_check_if_source_exists_true():
    from loading_doc_helper import check_if_source_exists, client, DB_NAME, COLLECTION_NAME
    collection = client[DB_NAME][COLLECTION_NAME]
    collection.find_one.return_value = {"_id": "abc", "metadata": {"source": "file.pdf"}}
    assert check_if_source_exists("file.pdf") is True


def test_check_if_source_exists_false():
    from loading_doc_helper import check_if_source_exists, client, DB_NAME, COLLECTION_NAME
    collection = client[DB_NAME][COLLECTION_NAME]
    collection.find_one.return_value = None
    assert check_if_source_exists("new_file.pdf") is False


def test_check_if_source_exists_queries_metadata_field():
    """Verify the query uses metadata.source, not source."""
    from loading_doc_helper import check_if_source_exists, client, DB_NAME, COLLECTION_NAME
    collection = client[DB_NAME][COLLECTION_NAME]
    collection.find_one.return_value = None
    check_if_source_exists("some_path.pdf")
    collection.find_one.assert_called_with({"metadata.source": "some_path.pdf"})


