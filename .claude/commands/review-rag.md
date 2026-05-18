# Review RAG pipeline health

Check the two core pipeline files for correctness and consistency.

Review the following in order:

1. **`Main Webpage/loading_doc_helper.py`** — ingestion pipeline
   - `check_if_source_exists()` must query `metadata.source` field (not `_id`)
   - `embed_and_upload()` must set `created_at` and `is_persistent` on every chunk before upload
   - `load_link()` must reject non-https URLs (security boundary)
   - `load_youtube()` is intentionally disabled — the raise Exception is correct, do not remove it

2. **`Main Webpage/app.py`** — retrieval + generation
   - `rag_chain` must use `RunnableParallel` so both `context` (docs) and `answer` (str) are captured
   - Judge chain must receive the same `formatted_context` passed to the QA chain
   - `grade` normalization: only accept `"ACCURATE"` or `"HALLUCINATION"`, default to `"UNKNOWN"`
   - `/ingest` route must have `try/finally` cleanup for uploaded PDF temp files
   - `/healthz` must have `@talisman(force_https=False)` — Azure pings it over HTTP

Report any violations of the above, then summarize overall pipeline health.
