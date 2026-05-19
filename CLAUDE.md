# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Document Workbench — a Flask + RAG application that lets users chat with uploaded documents (PDF and URL). The working directory for the app is `Main Webpage/`.

## Commands

```bash
# Run locally (from Main Webpage/)
cd "Main Webpage"
py -3.12 -m pip install -r requirements.txt
py -3.12 app.py
# Serves at http://127.0.0.1:5000

# Docker
docker build -t rag-app .
docker run -p 8080:8080 --env-file .env rag-app
```

No test runner is configured. Evaluation notebooks are in `Main Webpage/Proof_of_concept.ipynb` (RAGAS framework) and `Main Webpage/test.ipynb`.

## Required Environment Variables

```env
MONGO_URI=mongodb+srv://...
OPENAI_API_KEY=sk-proj-...
SECRET_KEY=<random-string>
FLASK_DEBUG=false   # optional
```

## Architecture

### RAG Pipeline (Ingestion → Retrieval → Generation)

**Ingestion** (`loading_doc_helper.py`):
- `load_pdf()`, `load_link()` → raw documents
- `RecursiveCharacterTextSplitter` (1000-char chunks, 150-char overlap)
- `check_if_source_exists()` guards against duplicate ingestion
- `embed_and_upload()` batches chunks to MongoDB Atlas Vector Search

**Retrieval + Generation** (`app.py`):
- LCEL chain: `RunnableParallel(context=retriever, input=passthrough)` → prompt → `gpt-4o-mini` → `StrOutputParser`
- Judge chain runs on top of the answer to label it `ACCURATE` or `HALLUCINATION`
- Retriever: MongoDB Atlas Vector Search, cosine similarity, k=4, `default` index on `documents` collection in `ai_workbench` DB

**Models**:
- Generation + Judge: `gpt-4o-mini` (temperature=0)
- Embeddings: `text-embedding-3-small` (1536 dimensions)

### Flask Routes (`app.py`)

| Route | Method | Purpose |
|---|---|---|
| `/` | GET/POST | Main QA interface — POST triggers the full RAG chain |
| `/ingest` | POST | Ingestion endpoint — accepts PDF file or URL |
| `/healthz` | GET | Azure health check — pings MongoDB admin command |

### Key Design Decisions

- **Plain-text answers only**: system prompt explicitly forbids Markdown so the UI renders cleanly.
- **Parallel retrieval**: `RunnableParallel` captures both the answer and the source context docs so the judge chain can evaluate them together.
- **API embeddings**: OpenAI embeddings (not local sentence-transformers) to keep compute low on Azure B1.
- **Temp file cleanup**: `try/finally` in `/ingest` ensures uploaded PDFs are deleted even on error.
- **Security**: `flask-talisman` enforces HTTPS and sets secure cookie flags.

## Deployment

Azure Web App via ACR. See `Main Webpage/deploy.md` for full commands.
- Registry: `ragregistryunique123`
- Resource group: `rag-rg-swe` (Sweden Central)
- Health endpoint: `https://rag-application.azurewebsites.net/healthz`
- Gunicorn timeout is set to 600s to accommodate slow LLM calls.
