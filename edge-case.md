# SecondSelf: Edge Cases & Corner Scenarios

This document outlines potential edge cases, failure modes, and corner scenarios for the SecondSelf project, categorized by the phase of implementation. Identifying these early will help in building a robust, modular system.

## 1. Ingestion & Extraction (`capture.py` & `lib/extract.py`)
* **Scanned PDFs & Images:** `PyPDF2` relies on a text layer. It will fail to extract text from scanned documents or images.
  * *Mitigation:* Catch empty extraction results and notify the user that OCR is required or log a warning.
* **Single Page Applications (SPAs):** Using `requests` and `BeautifulSoup` on modern JS-heavy sites (React/Vue) often returns empty `<div id="root"></div>` bodies instead of actual content.
  * *Mitigation:* If content length is suspiciously low for a URL, warn the user. (A future fix would involve Playwright/Selenium).
* **SHA-256 Duplicates (Slight Modifications):** The duplicate detection is rigid. If a user captures a URL twice but the site's dynamically generated timestamp changed, the hash will differ.
  * *Mitigation:* Allow this; the downstream RAG engine will handle minor redundancies. Strict deduplication is primarily meant for blocking exact file/string copies.

## 2. Classification & Incremental State (`classify.py` & `index.json`)
* **State Drift (The `index.json` Problem):** A user manually deletes a bad note from `wiki/`, but its UUID remains tracked as "processed" in `data/index.json`. If they attempt to recapture it, the system silently skips it.
  * *Mitigation:* Implement a quick synchronization check at the start of `classify.py` to ensure all IDs in `index.json` actually have corresponding files in `wiki/`.
* **LLM API Rate Limits & Malformed Output:** The Groq API rate limit is exceeded, or it returns conversational text instead of strict YAML/JSON.
  * *Mitigation:* Implement exponential backoff in `lib/llm.py` and strict regex fallbacks if JSON parsing fails. Default to an "Uncategorized" bucket.

## 3. Auto-Linking & Caching (`link.py` & `embeddings.pkl`)
* **Corrupt Cache File:** The `data/embeddings.pkl` file gets corrupted due to a sudden crash during a write operation.
  * *Mitigation:* Always write the cache to a temporary file first, then use `os.replace()` for an atomic swap. Catch `pickle.UnpicklingError` and trigger a full recomputation if corrupt.
* **Model Dimension Mismatches:** If the underlying `sentence-transformers` model is changed later, the new vectors won't match the dimensions of the cached vectors in `.pkl`.
  * *Mitigation:* Store the model name alongside the embeddings in the `.pkl` dictionary and invalidate the cache if the model name changes.
* **The "Hairball" Graph (Threshold Too Low):** If the cosine similarity threshold is set too low, everything links to everything.
  * *Mitigation:* Make the threshold configurable (e.g., `> 0.85`). Only link the Top-N highest scoring matches per note to keep the graph legible.

## 4. Graph Generation (`build_graph.py`)
* **Broken Links:** A note links to a UUID that has been deleted or corrupted.
  * *Mitigation:* The graph builder must verify the existence of the target node in its memory map before creating the JSON edge.
* **Corrupted Markdown Metadata:** A user manually edits a note in `wiki/` and breaks the YAML frontmatter syntax.
  * *Mitigation:* Wrap YAML parsing in `try-except`. Quarantine unparseable files and log an error to the UI sidebar so the user can fix it manually.

## 5. UI, Orchestration & RAG (`app.py`, `pipeline.py`, `ask.py`)
* **Concurrency in the UI:** The user clicks "Process" in the Streamlit sidebar multiple times in rapid succession, launching parallel `pipeline.py` threads that race to write to `index.json` and `embeddings.pkl`.
  * *Mitigation:* Implement a simple `.lock` file mechanism in the `data/` directory. If the lock exists, the UI disables or ignores the "Process" button.
* **Out-of-Domain Queries:** The user asks a question unrelated to their notes (e.g., "What is the capital of France?").
  * *Mitigation:* Strict RAG guardrails in `ask.py`: *"Answer ONLY using the provided context. If the answer is missing, say 'I cannot answer this based on your notes.'"*
* **Streamlit State Resets:** Interacting with the graph forces a full Streamlit app rerun, resetting the physics layout.
  * *Mitigation:* Use `@st.cache_data` effectively and ensure the graph component retains its internal state on the client side without triggering constant Python reruns.

## 6. Deployment (`Risk Register`)
* **Ephemeral File Systems:** Deploying to platforms like Heroku or the free-tier of Hugging Face Spaces often means the local file system (`data/`, `wiki/`, `raw/`) is wiped on restart.
  * *Mitigation:* Document this explicitly in the Risk Register. For a permanent cloud deployment, the architecture would need to be updated to swap local files for an S3 bucket or an attached persistent volume.
