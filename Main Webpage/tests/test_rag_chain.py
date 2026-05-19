"""Unit tests for RAG chain helpers and judge normalization logic."""

from langchain_core.documents import Document


# ---------------------------------------------------------------------------
# format_docs
# ---------------------------------------------------------------------------

def test_format_docs_joins_content():
    from app import format_docs
    docs = [
        Document(page_content="First chunk", metadata={}),
        Document(page_content="Second chunk", metadata={}),
    ]
    result = format_docs(docs)
    assert result == "First chunk\n\nSecond chunk"


def test_format_docs_empty_list():
    from app import format_docs
    assert format_docs([]) == ""


def test_format_docs_single_doc():
    from app import format_docs
    docs = [Document(page_content="Only chunk", metadata={})]
    assert format_docs(docs) == "Only chunk"


# ---------------------------------------------------------------------------
# Judge grade normalization (mirrors logic in app.py home() route)
# ---------------------------------------------------------------------------

def _normalize_grade(raw_grade: str) -> str:
    """Replicate the normalization logic from app.py lines 174-181."""
    grade = "UNKNOWN"
    if raw_grade:
        try:
            candidate = raw_grade.strip().split()[0].strip(".,").upper()
            if candidate in ("ACCURATE", "HALLUCINATION"):
                grade = candidate
        except Exception:
            grade = "UNKNOWN"
    return grade


def test_judge_accurate():
    assert _normalize_grade("ACCURATE") == "ACCURATE"


def test_judge_hallucination():
    assert _normalize_grade("HALLUCINATION") == "HALLUCINATION"


def test_judge_hallucination_with_punctuation():
    assert _normalize_grade("HALLUCINATION.") == "HALLUCINATION"


def test_judge_accurate_with_trailing_comma():
    assert _normalize_grade("ACCURATE,") == "ACCURATE"


def test_judge_garbage_input():
    assert _normalize_grade("maybe so") == "UNKNOWN"


def test_judge_empty_string():
    assert _normalize_grade("") == "UNKNOWN"


def test_judge_whitespace_only():
    assert _normalize_grade("   ") == "UNKNOWN"


def test_judge_lowercase_accurate():
    assert _normalize_grade("accurate") == "ACCURATE"


# ---------------------------------------------------------------------------
# Source deduplication in home route
# ---------------------------------------------------------------------------

def test_source_dedup():
    """Two docs with same source should produce one entry after set()."""
    docs = [
        Document(page_content="chunk 1", metadata={"source": "https://example.com", "title": "Example"}),
        Document(page_content="chunk 2", metadata={"source": "https://example.com", "title": "Example"}),
    ]
    raw_sources = []
    for doc in docs:
        url = doc.metadata.get("source", "Unknown Source")
        title = doc.metadata.get("title") or url
        raw_sources.append(f"{title} ({url})")

    source_documents = list(set(raw_sources))
    assert len(source_documents) == 1
