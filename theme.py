import streamlit as st

def apply_theme():
    st.markdown("""
    <style>
        /* Base Backgrounds */
        [data-testid="stAppViewContainer"] { background-color: #0a0a0b; }
        [data-testid="stSidebar"] { background-color: #111113; border-right: 1px solid #232326; }
        
        /* Typography - Neutral */
        h1, h2, h3, h4, h5, h6 { color: #f5f3f7 !important; font-weight: 600; }
        [data-testid="stSidebar"] h2 { color: #f0eef2 !important; }
        p, div { color: #e6e4ea; }
        
        .meta-text { font-size: 0.8rem; color: #565459; margin-top: 10px; }
        .faint-text { color: #565459; font-size: 0.8rem; }
        .secondary-text { color: #8c8a91; }
        
        /* Input Fields */
        .stTextInput > div > div > input, .stTextArea > div > div > textarea {
            background-color: #18181b !important;
            border: 1px solid #2a2a2e !important;
            color: #e6e4ea !important;
            border-radius: 8px;
        }
        
        /* Buttons - Default Ghost */
        .stButton > button {
            background-color: #18181b !important;
            border: 1px solid #2a2a2e !important;
            color: #b8b6bd !important;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            border-color: #8c8a91 !important;
            color: #f0eef2 !important;
        }
        
        /* Base Card Styling */
        .base-card {
            background-color: #131315;
            border: 1px solid #232326;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        
        .metric-label { font-size: 0.9rem; color: #8c8a91; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 0.5px;}
        .metric-value { font-size: 2rem; font-weight: 700; }
        
        /* ---------------------------------------------------- */
        /* MULTI-COLOR ACCENT SYSTEM                            */
        /* ---------------------------------------------------- */
        
        /* Blue Accent - Navigation & Notes */
        [data-testid="stSidebarNav"] span { color: #8c8a91 !important; }
        [data-testid="stSidebarNav"] div[data-testid="stSidebarNavLink"] {
            border-radius: 8px;
            margin: 4px 8px;
            transition: background-color 0.2s;
        }
        [data-testid="stSidebarNav"] div[data-testid="stSidebarNavLink"][aria-current="page"] {
            background-color: #1e2a4d !important; /* Blue active nav background */
        }
        [data-testid="stSidebarNav"] div[data-testid="stSidebarNavLink"][aria-current="page"] span {
            color: #8FB4F5 !important; /* Blue text */
            font-weight: 600;
        }
        
        .card-notes { border-color: #1e2a4d !important; }
        .card-notes .metric-value { color: #8FB4F5 !important; }
        
        /* Green Accent - Connections & Recently Captured */
        .card-connections { border-color: #1e3d2c !important; }
        .card-connections .metric-value { color: #7FD9A4 !important; }
        .card-recent { border-color: #1e3d2c !important; }
        
        /* Amber Accent - Topics, Ask Box, Chips */
        .card-topics { border-color: #402c14 !important; }
        .card-topics .metric-value { color: #F0B96E !important; }
        
        .answer-box {
            background-color: #111112;
            border-left: 2px solid #F0A83A !important;
            border-radius: 12px;
            padding: 20px;
            padding-left: 12px;
            margin-top: 10px;
            line-height: 1.6;
            color: #e6e4ea;
        }
        
        .source-chip {
            background-color: #3a2c14;
            color: #F0C978;
            border-radius: 8px;
            padding: 6px 10px;
            font-size: 0.85em;
            display: inline-block;
            margin: 4px 4px 4px 0;
            white-space: nowrap;
            /* border: 1px solid #402c14; */
        }
        .source-chip::before {
            content: "📄 ";
        }
        
        /* Pink Accent - Last Updated & Knowledge Graph Summary */
        .card-updated { border-color: #3a1e3d !important; }
        .card-updated .metric-value { color: #E28FD0 !important; }
        .card-graph { border-color: #3a1e3d !important; }
        
        /* Pink Button Override */
        .stButton.button-pink > button {
            color: #E28FD0 !important;
            background-color: #18181b !important;
        }
        .stButton.button-pink > button:hover {
            border-color: #E28FD0 !important;
        }
        
        /* Suggested Questions Chips (Neutral) */
        .stButton.suggestion-chip > button {
            background-color: #131315 !important;
            border: 1px solid #2a2a2e !important;
            color: #b8b6bd !important;
            border-radius: 16px !important;
            padding: 2px 10px !important;
            font-size: 0.85rem !important;
            min-height: 32px !important;
        }
        .stButton.suggestion-chip > button:hover {
            border-color: #8c8a91 !important;
            color: #f0eef2 !important;
        }
        
        /* Primary Button - Green Accent (Capture) */
        [data-testid="baseButton-primary"] {
            background-color: #1e3d2c !important;
            border: 1px solid #1e3d2c !important;
            color: #7FD9A4 !important;
        }
        [data-testid="baseButton-primary"]:hover {
            border-color: #7FD9A4 !important;
            color: #ffffff !important;
        }
        
        /* Input Focus - Amber Accent */
        .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
            border-color: #F0A83A !important;
            box-shadow: none !important;
        }

        /* Sources Container */
        .sources-container {
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid #232326;
        }
        .sources-heading {
            font-size: 0.9rem;
            color: #8c8a91;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
    </style>
    """, unsafe_allow_html=True)
