# Security check for Translation-Project

Audit `Main Webpage/app.py` and `Main Webpage/loading_doc_helper.py` against these project-specific rules:

## Must-pass checks

| # | Rule | Location |
|---|------|----------|
| 1 | `SECRET_KEY` loaded from env — never hardcoded | `app.py` |
| 2 | `secure_filename()` applied to every PDF upload before saving | `app.py /ingest` |
| 3 | PDF temp file deleted in `finally` block (not just on success) | `app.py /ingest` |
| 4 | `load_link()` rejects non-https URLs before loading | `loading_doc_helper.py` |
| 5 | `flask-talisman` active with `force_https=True` in production config | `app.py` |
| 6 | Session cookies have `Secure`, `HttpOnly`, `SameSite=Lax` | `app.py` |
| 7 | YouTube pipeline raises an explicit Exception (intentionally disabled) | `loading_doc_helper.py` |
| 8 | No API keys, tokens, or credentials in any source file | all files |
| 9 | `/healthz` uses `@talisman(force_https=False)` only — no other route bypasses talisman | `app.py` |
| 10 | User input to the RAG chain is not sanitized beyond strip — confirm LLM prompt injection risk is acceptable | `app.py home()` |

Read each file and report PASS / FAIL / NOTE for every check. Flag any new issues not covered above.
