# SecondSelf: Phase-wise Implementation Plan (Enhanced)

This document outlines the step-by-step implementation plan for the SecondSelf project, structured across 10 distinct phases from initial setup to deployment. It incorporates robust engineering practices, modularity, and incremental processing.

## Phase 0: Setup
**Goal:** Establish the foundational project structure, modular architecture, and environment.

* Initialize a Git repository for version control.
* Scaffold the required directory structure:
  * `raw/` (for initial captures)
  * `wiki/` (for processed, linked notes)
  * `data/` (for state and generated assets: `graph.json`, `embeddings.pkl`, `index.json`)
  * `lib/` (Reusable core modules: `storage.py`, `models.py`, `embeddings.py`, `llm.py`, `extract.py`)
* Set up a Python virtual environment (`venv`).
* Create a `requirements.txt` file (including `streamlit`, `streamlit-agraph`, `sentence-transformers`, `groq`, `python-dotenv`, `PyPDF2`, `beautifulsoup4`, `requests`).
* Create boilerplate scripts: `capture.py`, `classify.py`, `link.py`, `build_graph.py`, `ask.py`, `app.py`, and `pipeline.py` (orchestrator).

**Acceptance Criteria:**
* [ ] Directory structure is created (`raw/`, `wiki/`, `data/`, `lib/`).
* [ ] Virtual environment is active and `requirements.txt` installs successfully.
* [ ] Boilerplate files are present.

---

## Phase 1-5: Implement code of the project

### Phase 1: Implement Ingestion & Extraction (`capture.py` & `lib/extract.py`)
**Aligns with:** Week 1 — The Archivist
* Build a CLI tool (`capture.py`) that accepts text strings, URLs, or file paths (PDFs, Markdown, TXT).
  * *CLI Example:* `python capture.py "https://example.com"` or `python capture.py ./document.pdf`
* Use `lib/extract.py` to parse URLs (via `requests`/`BeautifulSoup`) and PDFs (via `PyPDF2`) into clean text before saving.
* Implement **SHA-256 duplicate detection** to prevent ingesting the same content multiple times.
* Generate a unique UUID and ISO timestamp.
* Save the raw content as a text/markdown file in the `raw/` directory.
* **Error Handling:** Catch invalid URLs, empty notes, corrupt PDFs, and missing files.

**Acceptance Criteria:**
* [ ] CLI accepts URLs, local PDFs, and text strings.
* [ ] SHA-256 duplicate detection prevents duplicate captures.
* [ ] Extracted text is saved to `raw/` with a UUID and timestamp.
* [ ] Graceful error handling for corrupt inputs.

### Phase 2: Implement Classification (`classify.py` & `lib/llm.py`)
**Aligns with:** Week 2.1 — The Librarian (Auto-Classify)
* Implement **incremental processing**: Use `data/index.json` to track which raw files have already been classified to avoid reprocessing all files.
* Use `lib/llm.py` to interface with the Groq API (Llama 3).
* Prompt the LLM to extract: PARA category (Projects, Areas, Resources, or Archives), tags, and a summary.
* Save the structured output (with YAML frontmatter) into the `wiki/` directory and update `data/index.json`.
* **Error Handling:** Validate API keys, handle API rate limits, and fallback for malformed JSON responses.

**Acceptance Criteria:**
* [ ] `index.json` tracks processed files correctly.
* [ ] Only new files in `raw/` are sent to the LLM.
* [ ] Classified files are written to `wiki/` with valid YAML frontmatter.

### Phase 3: Implement Auto-Linking (`link.py` & `lib/embeddings.py`)
**Aligns with:** Week 2.2 — The Librarian (Auto-Link)
* Implement **embedding caching**: Use `data/embeddings.pkl` to store generated vectors, preventing recomputation for existing notes.
* Use `lib/embeddings.py` (with `sentence-transformers`) to generate embeddings for new notes only.
* Compute cosine similarity across all note embeddings.
* Inject bidirectional wiki-style links (e.g., `[[UUID]]`) into the markdown files in `wiki/` for similarities above the threshold.

**Acceptance Criteria:**
* [ ] Embeddings are cached in `data/embeddings.pkl`.
* [ ] Similar notes receive bidirectional `[[UUID]]` links.
* [ ] Re-running the script only computes embeddings for new/modified notes.

### Phase 4: Implement Graph Generation (`build_graph.py`)
**Aligns with:** Week 3.1 — The Cartographer (Graph Data Model)
* Parse the `wiki/` directory to build a topological map.
* Export **richer graph nodes** (id, summary, tags, preview, group/PARA category) and **graph metadata** (generated_at, node_count, edge_count).
* Serialize and export this data to `data/graph.json`.

**Acceptance Criteria:**
* [ ] `data/graph.json` contains complete nodes and edges.
* [ ] Graph nodes include rich metadata (summary, tags, group).
* [ ] Graph JSON includes top-level metadata (node_count, generated_at).

### Phase 5: Orchestration, UI & RAG Search (`pipeline.py`, `ask.py`, `app.py`)
**Aligns with:** Week 3.2 & Week 4.1 — The Cartographer & The Oracle
* **Orchestrator (`pipeline.py`):** Create a single script to sequentially run `classify.py` → `link.py` → `build_graph.py`.
* **Search Engine (`ask.py`):** Build a Retrieval-Augmented Generation (RAG) loop. 
  * *Guardrails:* Instruct the LLM to answer *only* from the retrieved notes and explicitly cite source note IDs in its response.
* **Streamlit UI (`app.py`):** 
  * Implement caching using `@st.cache_resource` (for models/DB) and `@st.cache_data` (for graph loading).
  * Build a **sidebar** with interactive controls: Capture new input, Process (trigger `pipeline.py`), Refresh Graph, and view Statistics.
  * Render the interactive graph and the RAG search bar.

**Acceptance Criteria:**
* [ ] `pipeline.py` correctly orchestrates the background jobs.
* [ ] UI includes a sidebar for controls and stats.
* [ ] Graph renders using Streamlit caching.
* [ ] RAG responses explicitly cite source UUIDs and refuse to answer out-of-domain questions.

---

## Phase 6-7: Locally test

### Phase 6: Component-Level Local Testing
**Goal:** Verify each module works in isolation with real data.
* **Test Phase 1:** Run `capture.py` on 10+ real items (mixed URLs, PDFs, strings). Verify duplicate blocking.
* **Test Phase 2 & 3:** Run `classify.py` and `link.py`. Verify `index.json` and `embeddings.pkl` are updated incrementally.
* **Test Phase 4:** Run `build_graph.py` and validate the enriched `data/graph.json`.
* **Test Phase 5:** Test `pipeline.py` end-to-end to ensure the orchestrator works without manual intervention.

**Acceptance Criteria:**
* [ ] All component tests pass without throwing unhandled exceptions.
* [ ] Incremental state (`index.json`, `.pkl`) behaves as expected during subsequent runs.

### Phase 7: End-to-End System Testing
**Goal:** Ensure the pipeline flows seamlessly from ingestion to UI.
* Run the entire pipeline via `pipeline.py` on a fresh batch of 15+ real notes.
* Launch the web interface locally using `streamlit run app.py`.
* Use the sidebar to trigger a capture and process cycle directly from the UI.
* Query the "Ask Your Brain" search bar and verify source citations.

**Acceptance Criteria:**
* [ ] E2E pipeline succeeds.
* [ ] Streamlit sidebar actions successfully execute backend scripts.
* [ ] RAG search retrieves correct context and cites sources.

---

## Phase 8-9: Deploy the project + final round of testing

### Phase 8: Deployment Setup
**Goal:** Move the system from localhost to the public web.
* Prepare a **Deployment README** containing architecture details, environment variable setup (`GROQ_API_KEY`), and local run instructions.
* Create a **Risk Register** documenting potential failure points (e.g., LLM rate limits, persistent storage limits on cloud platforms) and mitigations.
* Provision a hosting environment (e.g., Streamlit Community Cloud or Hugging Face Spaces) and connect the GitHub repository.

**Acceptance Criteria:**
* [ ] Deployment README and Risk Register are written and committed.
* [ ] Code is pushed to public GitHub repository.
* [ ] Hosting platform is configured with necessary secrets.

### Phase 9: Live Testing & Validation
**Goal:** Final sign-off on the production build.
* Wait for deployment to complete and obtain the public URL.
* Open the deployed URL across different browsers.
* Perform live searches to ensure the RAG pipeline operates efficiently in the cloud.
* Test sidebar capture/process capabilities to ensure filesystem writes (`data/`, `raw/`, `wiki/`) work in the deployed environment.

**Acceptance Criteria:**
* [ ] App is live and publicly accessible.
* [ ] RAG search works in production.
* [ ] Graph renders performantly.
