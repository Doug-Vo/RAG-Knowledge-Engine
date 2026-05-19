"""
Integration tests — require real credentials in .env.
Run with: pytest -m integration
Skip in CI with: pytest -m "not integration"
"""

import os
import pytest


@pytest.mark.integration
def test_real_mongodb_ping():
    from pymongo import MongoClient
    uri = os.environ.get("MONGO_URI")
    if not uri:
        pytest.skip("MONGO_URI not set")
    client = MongoClient(uri)
    result = client.admin.command("ping")
    assert float(result.get("ok", 0)) == 1.0


@pytest.mark.integration
def test_real_embedding_generates_vector():
    from langchain_openai import OpenAIEmbeddings
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set")
    model = OpenAIEmbeddings(model="text-embedding-3-small")
    vector = model.embed_query("hello world")
    assert isinstance(vector, list)
    assert len(vector) == 1536


@pytest.mark.integration
def test_real_healthz_endpoint(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
