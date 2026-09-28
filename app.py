import streamlit as st
from database import init_db
from theme_manager import apply_current_theme
from auth import require_auth

init_db()

st.set_page_config(
    page_title="StockBot Enterprise",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_current_theme()

# Gate access for clients
user = require_auth(allowed_roles=["client_admin", "client_staff"])

st.title(f"📦 Welcome, {user['company_name']}")
st.markdown("### Autonomous Inventory Management System")

st.write(
    """
    Your warehouse instance is isolated and protected with zero-knowledge billing telemetry.
    
    Use the navigation menu on the left to get started:
    - **📊 Dashboard:** Real-time stock levels, catalog valuations, and audit logs.
    - **💬 AI Assistant:** Conversational agent to restock, sell, and query items via natural speech.
    - **⚙️ Settings:** Personalize visual design themes.
    - **💳 Usage & Billing:** Check your dummy dollar balance and top up prepaid queries.
    """
)

st.divider()
c1, c2, c3 = st.columns(3)
with c1:
    st.info(f"**🏢 Tenant Account**\n\n{user['company_name']} (ID: {user['client_id']})")
with c2:
    st.success(f"**💰 Active Wallet**\n\n${user['wallet_balance']:.2f} Dummy USD")
with c3:
    st.warning("**🔒 Security Status**\n\nZero-Knowledge Telemetry Active")
    