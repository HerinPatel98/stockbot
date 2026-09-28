import streamlit as st

THEMES = {
    "Cyberpunk Neon": {
        "primary": "#ff007f",
        "accent": "#00f0ff",
        "bg": "#0a0a12",
        "secondary_bg": "#161626",
        "text": "#f8f9fa",
        "border": "#ff007f"
    },
    "Terminal Amber": {
        "primary": "#f59e0b",
        "accent": "#fbbf24",
        "bg": "#0d0c00",
        "secondary_bg": "#1c1905",
        "text": "#fef08a",
        "border": "#b45309"
    },
    "Nordic Glacier": {
        "primary": "#0284c7",
        "accent": "#38bdf8",
        "bg": "#f0f9ff",
        "secondary_bg": "#ffffff",
        "text": "#0c4a6e",
        "border": "#bae6fd"
    },
    "Royal Amethyst": {
        "primary": "#a855f7",
        "accent": "#c084fc",
        "bg": "#13091f",
        "secondary_bg": "#231538",
        "text": "#faf5ff",
        "border": "#6b21a8"
    }
}

def apply_current_theme():
    """Injects high-contrast CSS based on the chosen theme in session_state."""
    if "current_theme" not in st.session_state:
        st.session_state.current_theme = "Cyberpunk Neon"

    if st.session_state.current_theme not in THEMES:
        st.session_state.current_theme = "Cyberpunk Neon"

    t = THEMES[st.session_state.current_theme]

    css = f"""
    <style>
    .stApp {{
        background-color: {t["bg"]} !important;
        color: {t["text"]} !important;
    }}
    
    section[data-testid="stSidebar"] {{
        background-color: {t["secondary_bg"]} !important;
        border-right: 2px solid {t["border"]} !important;
    }}
    
    h1, h2, h3, h4, h5, h6, p, label, span, .stMarkdown {{
        color: {t["text"]} !important;
    }}

    div[data-testid="stMetric"] {{
        background-color: {t["secondary_bg"]} !important;
        border: 1px solid {t["border"]} !important;
        border-radius: 10px;
        padding: 12px 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    }}
    div[data-testid="stMetricValue"] > div {{
        color: {t["primary"]} !important;
        font-weight: 700;
    }}
    div[data-testid="stMetricLabel"] p {{
        color: {t["text"]} !important;
        opacity: 0.85;
    }}

    .stButton > button {{
        background-color: {t["secondary_bg"]} !important;
        color: {t["text"]} !important;
        border: 1.5px solid {t["primary"]} !important;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.25s ease-in-out;
    }}
    .stButton > button:hover {{
        background-color: {t["primary"]} !important;
        color: #ffffff !important;
        border-color: {t["accent"]} !important;
        box-shadow: 0 0 12px {t["primary"]};
    }}

    .stTextInput > div > div > input, 
    .stSelectbox > div > div,
    .stChatInput textarea {{
        background-color: {t["secondary_bg"]} !important;
        color: {t["text"]} !important;
        border: 1.5px solid {t["border"]} !important;
        border-radius: 8px !important;
    }}
    .stChatInput textarea:focus {{
        border-color: {t["primary"]} !important;
        box-shadow: 0 0 8px {t["primary"]} !important;
    }}

    div[data-testid="stChatMessage"] {{
        background-color: {t["secondary_bg"]} !important;
        border: 1px solid {t["border"]} !important;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }}

    div[data-testid="stDataFrame"] {{
        border: 1.5px solid {t["border"]} !important;
        border-radius: 10px;
        overflow: hidden;
    }}

    .stProgress > div > div > div > div {{
        background-color: {t["primary"]} !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        border-bottom-color: {t["primary"]} !important;
        color: {t["primary"]} !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    