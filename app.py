import streamlit as st
import json
import os
import uuid
import re
from datetime import datetime, timezone
from streamlit_agraph import agraph, Node, Edge, Config

# Import internal modules
from ask import ask
import pipeline
from lib.extract import extract_content, get_sha256
from lib.storage import is_duplicate, add_hash, save_raw_capture, load_json
from theme import apply_theme

# Set page config
st.set_page_config(
    page_title="SecondSelf",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()

# --- LOAD DATA ---
GRAPH_FILE = os.path.join("data", "graph.json").replace("\\", "/")

@st.cache_data(ttl=5)
def load_graph_data():
    # Use our centralized Supabase-enabled storage
    try:
        data = load_json(GRAPH_FILE, default_val=None)
        # If it returns empty dict by default from some edge cases, we want None for safety checks
        if data == {}: return None
        return data
    except Exception:
        return None

graph_data = load_graph_data()


# -------------------------------------------------------------------
# HELPER: Render RAG Results (Used in Dashboard & Ask)
# -------------------------------------------------------------------
def render_ask_results(query):
    with st.spinner("Consulting the Oracle..."):
        answer = ask(query)
        
        sources = set()
        
        # 1. Strip out the citations from the main answer text while collecting them
        def collect_and_strip(match):
            uuid_val = match.group(1)
            sources.add(uuid_val)
            return "" # Strip from prose
            
        clean_answer = re.sub(r'\[\[(.*?)\]\]', collect_and_strip, answer)
        
        # Display the clean prose
        st.markdown(f"""
        <div class="answer-box">
            {clean_answer.strip()}
        </div>
        """, unsafe_allow_html=True)
        
        # 2. Render the sources as chips in a dedicated section
        if sources:
            st.markdown('<div class="sources-container"><div class="sources-heading">Sources</div>', unsafe_allow_html=True)
            chips_html = ""
            for uuid_val in sources:
                title = uuid_val
                if graph_data and "nodes" in graph_data:
                    for n in graph_data["nodes"]:
                        if n.get("id") == uuid_val:
                            title = n.get("summary", n.get("label", uuid_val))
                            if len(title) > 60:
                                title = title[:57] + "..."
                            break
                chips_html += f'<span class="source-chip" title="{uuid_val}">{title}</span>'
                
            st.markdown(chips_html + '</div>', unsafe_allow_html=True)


# -------------------------------------------------------------------
# VIEW: DASHBOARD
# -------------------------------------------------------------------
def dashboard():
    st.markdown('<h1 style="color: #f5f3f7; padding-bottom: 0;">Good morning</h1>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 1.2rem; color: #8c8a91; margin-top:-10px;">Your second brain, at a glance</p>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    meta = {}
    if graph_data and "metadata" in graph_data:
        meta = graph_data["metadata"]
        
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="base-card card-notes"><div class="metric-label">Notes</div><div class="metric-value">{meta.get('node_count', 0)}</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="base-card card-connections"><div class="metric-label">Connections</div><div class="metric-value">{meta.get('edge_count', 0)}</div></div>""", unsafe_allow_html=True)
    with c3:
        topics_count = len([n for n in graph_data.get("nodes", []) if n.get("group") == "Areas"]) if graph_data else 0
        st.markdown(f"""<div class="base-card card-topics"><div class="metric-label">Topics</div><div class="metric-value">{topics_count}</div></div>""", unsafe_allow_html=True)
    with c4:
        date_str = meta.get('generated_at', 'Unknown')
        if date_str != 'Unknown' and 'T' in date_str:
            date_str = date_str.split('T')[0]
        st.markdown(f"""<div class="base-card card-updated"><div class="metric-label">Last updated</div><div class="metric-value" style="font-size:1.5rem;">{date_str}</div></div>""", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("### Ask your brain")
    st.markdown('<p class="secondary-text" style="margin-top:-10px;">Ask anything, I\'ll answer from what you\'ve captured</p>', unsafe_allow_html=True)

    if "dash_q" not in st.session_state:
        st.session_state.dash_q = ""
        
    def set_dash_query(q):
        st.session_state.dash_q = q
        
    # Suggested question chips
    col1, col2, _ = st.columns([1, 1, 3])
    with col1:
        st.button("What am I working on?", on_click=set_dash_query, args=("What am I working on?",), key="dash_btn_1", use_container_width=True)
    with col2:
        st.button("Show my AI notes", on_click=set_dash_query, args=("Show my AI notes",), key="dash_btn_2", use_container_width=True)

    # Input for query
    query = st.text_input("Ask your brain directly from the dashboard...", value=st.session_state.dash_q, placeholder="e.g. What are my current projects?", key="dash_q_input", label_visibility="collapsed")
    if query:
        render_ask_results(query)
        
    st.markdown("<br><hr style='border-color:#232326;'><br>", unsafe_allow_html=True)
    
    # Custom CSS block to style the specific buttons in this layout correctly
    st.markdown("""
    <style>
    /* Style suggestion buttons to look like chips */
    div[data-testid="column"]:nth-child(1) .stButton > button,
    div[data-testid="column"]:nth-child(2) .stButton > button {
        border-radius: 16px !important;
        padding: 2px 10px !important;
    }
    
    /* Style the Open full graph button pink */
    /* It is in the 2nd column of the bottom row (which is the last horizontal block) */
    div[data-testid="stHorizontalBlock"]:last-of-type > div[data-testid="column"]:nth-child(2) .stButton > button p {
        color: #E28FD0 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    c_recent, c_graph = st.columns(2)
    with c_recent:
        st.markdown('<div class="base-card card-recent" style="height: 100%;">', unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top: 0;'>Recently captured</h3>", unsafe_allow_html=True)
        if graph_data and "nodes" in graph_data:
            nodes = sorted(graph_data["nodes"], key=lambda x: x["id"], reverse=True)
            for n in nodes[:5]:
                st.markdown(f"- {n.get('summary', n.get('label', n['id']))}")
        else:
            st.info("No notes yet.")
        st.markdown('</div>', unsafe_allow_html=True)
            
    with c_graph:
        st.markdown('<div class="base-card card-graph" style="height: 100%;">', unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top: 0;'>Knowledge graph summary</h3>", unsafe_allow_html=True)
        st.markdown(f"**{meta.get('node_count', 0)} Nodes** and **{meta.get('edge_count', 0)} Connections** mapping your thoughts.")
        st.markdown('<br>', unsafe_allow_html=True)
        
        if st.button("Open full graph", key="open_graph_btn", use_container_width=True):
            # Use string name of the page instead of variable to avoid linter "undefined variable" error
            st.switch_page("Knowledge Graph")
            
        st.markdown('</div>', unsafe_allow_html=True)


# -------------------------------------------------------------------
# VIEW: CAPTURE
# -------------------------------------------------------------------
def capture_ui():
    st.markdown('<h1 style="color: #7FD9A4; padding-bottom: 0;">Capture</h1>', unsafe_allow_html=True)
    st.markdown('<p class="secondary-text">Save a new thought, URL, or filepath into your second brain.</p>', unsafe_allow_html=True)
    
    capture_input = st.text_area("Enter content:", height=200, label_visibility="collapsed", placeholder="Enter Text, URL, or Filepath to capture...")
    
    if st.button("Save to Brain", type="primary"):
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
    st.markdown("### Processing")
    st.write("Run the pipeline to organize new captures (Classify → Link → Graph).")
    
    if st.button("Process Pipeline", type="primary"):
        with st.spinner("Organizing your brain... This may take a moment."):
            success = pipeline.run_pipeline()
            if success:
                load_graph_data.clear() # type: ignore
                st.success("Pipeline complete!")
            else:
                st.error("Pipeline failed. Check terminal for details.")


# -------------------------------------------------------------------
# VIEW: ASK YOUR BRAIN
# -------------------------------------------------------------------
def ask_ui():
    st.markdown('<h1 style="color: #F0A83A; padding-bottom: 0;">Ask your brain</h1>', unsafe_allow_html=True)
    st.markdown('<p class="secondary-text" style="margin-top:-10px;">Ask anything, I\'ll answer from what you\'ve captured</p>', unsafe_allow_html=True)
    
    if "ask_query" not in st.session_state:
        st.session_state.ask_query = ""
        
    def set_query(q):
        st.session_state.ask_query = q
        
    c1, c2, _ = st.columns([1, 1, 3])
    with c1:
        st.button("What am I working on?", on_click=set_query, args=("What am I working on?",), key="ask_btn_1", use_container_width=True)
    with c2:
        st.button("Show my AI notes", on_click=set_query, args=("Show my AI notes",), key="ask_btn_2", use_container_width=True)
        
    st.markdown("""
    <style>
    /* Style suggestion buttons to look like chips */
    div[data-testid="column"]:nth-child(1) .stButton > button,
    div[data-testid="column"]:nth-child(2) .stButton > button {
        border-radius: 16px !important;
        padding: 2px 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)
        
    query = st.text_input("Question:", value=st.session_state.ask_query, placeholder="e.g. What am I working on?", label_visibility="collapsed")
    
    if query:
        render_ask_results(query)


# -------------------------------------------------------------------
# VIEW: KNOWLEDGE GRAPH
# -------------------------------------------------------------------
def graph_ui():
    st.markdown('<h1 style="color: #E28FD0; padding-bottom: 0;">Knowledge Graph</h1>', unsafe_allow_html=True)
    meta = {}
    if graph_data and "metadata" in graph_data:
        meta = graph_data["metadata"]
        
    st.markdown(f'<p class="secondary-text" style="margin-top:-10px;">Live View: <strong style="color: #8FB4F5;">{meta.get("node_count", 0)} Nodes</strong> • <strong style="color: #7FD9A4;">{meta.get("edge_count", 0)} Connections</strong></p>', unsafe_allow_html=True)
    
    if graph_data and graph_data.get("nodes"):
        nodes = []
        edges = []
        
        for n in graph_data["nodes"]:
            size = 25
            if n.get("group") == "Projects":
                size = 35
            
            color = n.get("color", "#8c8a91")
            
            nodes.append(Node(
                id=n["id"],
                label=n["label"],
                title=n.get("title", ""),
                size=size,
                color=color
            ))
            
        for e in graph_data.get("edges", []):
            edges.append(Edge(
                source=e["source"],
                target=e["target"],
                color="#2a2a2e"
            ))
            
        config = Config(
            width="100%",
            height=600,
            directed=True,
            physics=True,
            hierarchical=False,
            nodeHighlightBehavior=True,
            highlightColor="#f0eef2",
            collapsible=False
        )
        
        st.markdown('<div style="margin-top: 20px; background: #131315; padding: 10px; border-radius: 12px; border: 1px solid #232326;">', unsafe_allow_html=True)
        agraph(nodes=nodes, edges=edges, config=config)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Graph is empty. Please capture some notes and run the pipeline.")


# -------------------------------------------------------------------
# NAVIGATION (Multi-Page Setup)
# -------------------------------------------------------------------
dashboard_page = st.Page(dashboard, title="Dashboard", icon="📊", default=True)
capture_page = st.Page(capture_ui, title="Capture", icon="📥")
ask_page = st.Page(ask_ui, title="Ask Your Brain", icon="🔍")
graph_page = st.Page(graph_ui, title="Knowledge Graph", icon="🕸️")

pg = st.navigation([dashboard_page, capture_page, ask_page, graph_page])

with st.sidebar:
    st.markdown('<h2 style="color: #f0eef2;">SecondSelf</h2>', unsafe_allow_html=True)

pg.run()

# Pin last updated to bottom of sidebar
if graph_data and "metadata" in graph_data:
    date_str = graph_data["metadata"].get('generated_at', 'Unknown')
    if date_str != 'Unknown' and 'T' in date_str:
        date_str = date_str.split('T')[0]
    with st.sidebar:
        st.markdown("<br>"*10, unsafe_allow_html=True)
        st.markdown(f'<div class="meta-text" style="position: absolute; bottom: 20px;">Updated today ({date_str})</div>', unsafe_allow_html=True)
