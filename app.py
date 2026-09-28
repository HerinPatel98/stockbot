import streamlit as st
from database import init_db
from theme_manager import apply_current_theme
apply_current_theme()

# Ensure database tables exist
init_db()

st.set_page_config(
    page_title="Autonomous Inventory System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📦 Autonomous Inventory Management System")
st.markdown("### Powered by LLM Tool Calling & Deterministic Ledger")

st.write(
    """
    Welcome to the Autonomous Inventory Management System. This project bridges human natural language 
    with a deterministic SQL database through structured AI tool calling.
    
    Use the sidebar on the left to navigate:
    - **📊 Dashboard:** Real-time stock levels, portfolio valuation, stock status alerts, and audit logs.
    - **💬 AI Assistant:** Conversational chat interface to restock, sell, and query items via natural speech.
    """
)

st.divider()

col1, col2 = st.columns(2)
with col1:
    st.info("### 📊 Want to view reports?\nNavigate to the **Dashboard** page to analyze current stock and ledger records.")
with col2:
    st.success("### 💬 Need to record transactions?\nOpen the **AI Assistant** page to interact with the LLM bot.")