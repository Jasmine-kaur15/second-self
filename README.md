# SecondSelf

**SecondSelf** is your intelligent, self-organizing personal knowledge base. It captures your notes, automatically classifies them using the PARA methodology, links them based on semantic similarity, and provides a Retrieval-Augmented Generation (RAG) search engine to query your own brain.

## Features

- **Capture:** Ingest text, URLs, or PDFs. Automatic duplicate detection using SHA-256.
- **Auto-Classify:** Uses Llama-3 (via Groq) to categorize notes into Projects, Areas, Resources, or Archives (PARA) and extracts relevant tags.
- **Auto-Link:** Generates embeddings using `sentence-transformers` and injects bidirectional links (`[[UUID]]`) for semantically similar notes.
- **Interactive Graph:** Visualizes your growing knowledge base with an interactive, physics-based network graph.
- **Ask Your Brain:** A RAG-powered search engine. Ask questions and get answers synthesized purely from your own notes, complete with source citations.

## Setup Instructions

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <your-repo-url>
   cd SECOND-SELF
   ```

2. **Create a virtual environment and activate it**:
   - Windows: `python -m venv venv` then `.\venv\Scripts\Activate.ps1`
   - Mac/Linux: `python3 -m venv venv` then `source venv/bin/activate`

3. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your environment variables**:
   Create a `.env` file in the root directory and add your Groq API key:
   ```env
   GROQ_API_KEY=your_api_key_here
   ```

## Usage

You can use the entire system via the **Streamlit Application**:

```bash
streamlit run app.py
```

This will launch a local web server (usually at `http://localhost:8501`).
From the UI sidebar, you can:
- **Capture:** Paste text or URLs to add to your brain.
- **Process Pipeline:** Click to run the background orchestrator (`classify.py` → `link.py` → `build_graph.py`).
- **Ask & Explore:** Use the "Ask Your Brain" tab to query your notes, or view the "Interactive Graph".

### CLI Usage (Optional)
If you prefer the command line:
- Capture: `python capture.py "https://example.com"`
- Run Pipeline: `python pipeline.py`
- Ask: `python ask.py "What is my current project?"`

## Deployment

To deploy this application to Streamlit Community Cloud:
1. Push this code to a public GitHub repository.
2. Sign in to [Streamlit Cloud](https://share.streamlit.io/).
3. Click "New App", select your repository, and set the main file path to `app.py`.
4. In the Streamlit Cloud advanced settings, add your `GROQ_API_KEY` to the Secrets section.
5. Deploy!
