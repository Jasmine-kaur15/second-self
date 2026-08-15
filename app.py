import streamlit as st
import json
import os
import uuid
from datetime import datetime, timezone
from streamlit_agraph import agraph, Node, Edge, Config

# Import internal modules
from ask import ask
import pipeline
from lib.extract import extract_content, get_sha256
from lib.storage import is_duplicate, add_hash, save_raw_capture

# Set page config
st.set_page_config(
    page_title="SecondSelf",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
# Adding modern, clean, rich aesthetics
st.markdown("""
<style>
    .main {
        background-color: #0E1117;
    }
    h1 {
        background: -webkit-linear-gradient(45deg, #FF4B2B, #FF416C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 3.5rem;
    }
    .stButton>button {
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 75, 43, 0.3);
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    .metric-label {
        font-size: 0.9rem;
        color: #A0AEC0;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #FFFFFF;
    }
    .answer-box {
        background: rgba(255, 255, 255, 0.03);
        border-left: 4px solid #FF416C;
        padding: 20px;
        border-radius: 0 8px 8px 0;
        margin-top: 10px;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
GRAPH_FILE = os.path.join("data", "graph.json")

@st.cache_data(ttl=5) # Cache for 5 seconds to allow refresh
def load_graph_data():
    if not os.path.exists(GRAPH_FILE):
        return None
    try:
        with open(GRAPH_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

graph_data = load_graph_data()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 📥 Capture")
    
    capture_input = st.text_area("Enter Text, URL, or Filepath to capture:", height=100)
    if st.button("Save to Brain", type="primary", use_container_width=True):
        if capture_input.strip():
            with st.spinner("Capturing..."):
                try:
                    source_type, content = extract_content(capture_input.strip())
                    content_hash = get_sha256(content)
                    
                    if is_duplicate(content_hash):
                        st.error("Duplicate detected! Already captured.")
                    else:
                        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                        capture_id = f"{date_str}_{uuid.uuid4()}"
                        timestamp = datetime.now(timezone.utc).isoformat()
                        
                        metadata = {
                            "id": capture_id,
                            "timestamp": timestamp,
                            "source": "UI_Capture",
                            "source_type": source_type,
                            "content_hash": content_hash
                        }
                        
                        save_raw_capture(capture_id, content, metadata)
                        add_hash(content_hash)
                        st.success(f"Captured! ({capture_id})")
                except Exception as e:
                    st.error(f"Failed: {e}")
        else:
            st.warning("Input is empty.")

    st.markdown("---")
    st.markdown("## ⚙️ Processing")
    st.write("Run the pipeline to organize new captures (Classify → Link → Graph).")
    
    if st.button("Process Pipeline", use_container_width=True):
        with st.spinner("Organizing your brain... This may take a moment."):
            success = pipeline.run_pipeline()
            if success:
                # Clear the cache so the new graph loads
                load_graph_data.clear()
                st.success("Pipeline complete!")
                st.rerun()
            else:
                st.error("Pipeline failed. Check terminal for details.")
                
    st.markdown("---")
    st.markdown("## 📊 Stats")
    
    if graph_data and "metadata" in graph_data:
        meta = graph_data["metadata"]
        
        # Display as cards
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Nodes (Notes)</div>
            <div class="metric-value">{meta.get('node_count', 0)}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Edges (Connections)</div>
            <div class="metric-value">{meta.get('edge_count', 0)}</div>
        </div>
        <div style="font-size: 0.8rem; color: #718096; margin-top: 10px;">
            Last Updated: {meta.get('generated_at', 'Unknown')}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No stats available. Run pipeline.")

# --- MAIN CONTENT ---
st.title("SecondSelf")
st.markdown("*Your intelligent, self-organizing knowledge base.*")

# Create two tabs for better organization
tab_search, tab_graph = st.tabs(["🔍 Ask Your Brain", "🕸️ Interactive Graph"])

# --- TAB 1: RAG SEARCH ---
with tab_search:
    st.markdown("### Ask a question about your notes")
    query = st.text_input("What do you want to know?", placeholder="e.g., What are my current projects?", label_visibility="collapsed")
    
    if query:
        with st.spinner("Consulting the Oracle..."):
            answer = ask(query)
            st.markdown(f"""
            <div class="answer-box">
                {answer}
            </div>
            """, unsafe_allow_html=True)

# --- TAB 2: INTERACTIVE GRAPH ---
with tab_graph:
    if graph_data and graph_data.get("nodes"):
        nodes = []
        edges = []
        
        # Build agraph Nodes
        for n in graph_data["nodes"]:
            # Set node sizes based on group
            size = 25
            if n.get("group") == "Projects":
                size = 35
            
            nodes.append(Node(
                id=n["id"],
                label=n["label"],
                title=n.get("title", ""),
                size=size,
                color=n.get("color", "#808080")
            ))
            
        # Build agraph Edges
        for e in graph_data.get("edges", []):
            edges.append(Edge(
                source=e["source"],
                target=e["target"],
                color="#718096"
            ))
            
        # Configure the graph visual physics
        config = Config(
            width="100%",
            height=600,
            directed=True,
            physics=True,
            hierarchical=False,
            nodeHighlightBehavior=True,
            highlightColor="#F7A072",
            collapsible=False
        )
        
        # Render the graph
        st.markdown("### Living Brain Map")
        agraph(nodes=nodes, edges=edges, config=config)
    else:
        st.info("Graph is empty. Please capture some notes and run the pipeline.")
