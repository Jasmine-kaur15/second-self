# SecondSelf: System Architecture

This document outlines the architecture for the SecondSelf project, an AI-powered personal knowledge management system.

## 1. System Overview
SecondSelf is an end-to-end pipeline that takes unstructured inputs (notes, files, links), processes them using LLMs for classification and embeddings for similarity linking, and serves the resulting knowledge graph via a web application with semantic search capabilities.

## 2. Core Components & Data Flow

The system is broken down into distinct processing stages, acting as a data pipeline.

### Stage 1: Ingestion (`capture.py`)
- **Input:** User provides text, a URL, or a file path via the command line.
- **Processing:** Assigns a unique UUID and an ISO timestamp.
- **Output:** Saves the raw data as a text/markdown file in the `raw/` directory.

### Stage 2: Classification (`classify.py`)
- **Input:** Unprocessed files in the `raw/` directory.
- **Processing:** Reads raw content and prompts a fast LLM (e.g., Groq / Llama 3) to extract:
  - **Category:** Based on the PARA method (Projects, Areas, Resources, Archives).
  - **Tags:** Relevant keywords.
  - **Summary:** A concise one-liner.
- **Output:** Creates a structured markdown file with YAML frontmatter in the `wiki/` directory.

### Stage 3: Auto-Linking (`link.py`)
- **Input:** Markdown files in the `wiki/` directory.
- **Processing:** 
  - Generates dense vector embeddings for the content of each note using a local model (e.g., `sentence-transformers/all-MiniLM-L6-v2`).
  - Computes cosine similarity between all pairs of notes.
  - If the similarity score exceeds a defined threshold, an implicit bidirectional link is established.
- **Output:** Updates the markdown files in `wiki/` to include references (e.g., `[[UUID]]`) to related notes.

### Stage 4: Graph Generation (`build_graph.py`)
- **Input:** Processed and linked files in the `wiki/` directory.
- **Processing:** Parses the markdown files and their metadata to build a topological map.
  - **Nodes:** Represent individual notes (ID, title, summary, category).
  - **Edges:** Represent the similarities/links injected in Stage 3.
- **Output:** A static `graph.json` file representing the entire network structure.

### Stage 5: The Interface & Query Engine (`app.py` & `ask.py`)
- **UI Framework:** Streamlit.
- **Interactive Graph:** Renders `graph.json` using a network visualization library wrapper for Streamlit (e.g., `streamlit-agraph` utilizing `vis-network`). Supports physics simulations, zooming, and node hover events to display the summaries.
- **Query Engine (`ask.py`):** Implements a Retrieval-Augmented Generation (RAG) loop.
  1. Embeds the user's plain-English question.
  2. Queries the vector index (or runs cosine similarity against cached embeddings) to find the top-K most relevant notes.
  3. Feeds the context from these notes + the user's question to the LLM.
  4. Streams the synthesized response back to the Streamlit UI.

## 3. Technology Stack

| Component | Technology Choice | Rationale |
| :--- | :--- | :--- |
| **Language** | Python 3.10+ | Best ecosystem for AI, data pipelines, and Streamlit. |
| **LLM Inference** | Groq API (Llama 3) | Blazing fast generation, free tier available, excellent for classification and RAG synthesis. |
| **Embeddings** | `sentence-transformers` | Runs locally, free, no API keys needed, sufficient for personal data scales. |
| **Data Storage** | Local Filesystem (`raw/`, `wiki/`) | Transparent, portable, acts as a flat-file database (Markdown + YAML frontmatter). |
| **Frontend UI** | Streamlit | Rapid prototyping of Python apps, built-in layout management. |
| **Graph Visuals** | `streamlit-agraph` / `vis.js` | Interactive, force-directed graphs that work directly within Streamlit. |
| **Deployment** | Streamlit Community Cloud / Hugging Face Spaces | Free, native hosting for Streamlit applications, easy public URL generation. |

## 4. Directory Structure
```text
secondself/
├── raw/                  # Unprocessed notes (Stage 1 output)
├── wiki/                 # Classified & linked notes (Stage 2/3 output)
├── capture.py            # CLI script to ingest data
├── classify.py           # LLM categorization pipeline
├── link.py               # Embedding generation and similarity linking
├── build_graph.py        # Graph JSON compiler
├── graph.json            # Compiled nodes and edges
├── ask.py                # RAG synthesis engine
├── app.py                # Main Streamlit dashboard
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```
