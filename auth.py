import streamlit as st
import hashlib
from database import verify_user, get_connection

def require_auth(allowed_roles=None):
    """
    Guarantees page protection.
    Persists session across browser reloads via st.query_params.
    """
    if "auth_user" not in st.session_state:
        st.session_state.auth_user = None

    # Check query_params if session_state is empty (e.g. on F5 or rerun)
    if st.session_state.auth_user is None:
        token_user = st.query_params.get("session_user")
        token_role = st.query_params.get("session_role")
        token_client = st.query_params.get("session_client")
        token_uid = st.query_params.get("session_uid")

        if token_user and token_role:
            # Validate against database
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, client_id, username, role FROM users WHERE username = ? AND role = ?", (token_user, token_role))
            u_row = cursor.fetchone()
            
            if u_row:
                c_name = "Platform Administrator"
                bal = 0.0
                rate = 0.0
                if u_row[1]:
                    cursor.execute("SELECT company_name, wallet_balance, rate_per_query FROM clients WHERE id = ?", (u_row[1],))
                    c_row = cursor.fetchone()
                    if c_row:
                        c_name, bal, rate = c_row

                st.session_state.auth_user = {
                    "user_id": u_row[0],
                    "client_id": u_row[1],
                    "username": u_row[2],
                    "role": u_row[3],
                    "company_name": c_name,
                    "wallet_balance": bal,
                    "rate_per_query": rate
                }
            conn.close()

    # Still unauthenticated: Hide nav & show login card
    if st.session_state.auth_user is None:
        st.markdown("""
            <style>
            [data-testid="stSidebarNav"] { display: none !important; }
            section[data-testid="stSidebar"] { display: none !important; }
            </style>
        """, unsafe_allow_html=True)
        render_login_form(allowed_roles)
        st.stop()

    user = st.session_state.auth_user
    if allowed_roles and user.get("role") not in allowed_roles:
        st.error(f"⛔ Access Denied: Role '{user.get('role')}' is not authorized to view this page.")
        if st.sidebar.button("🚪 Sign Out"):
            logout()
        st.stop()

    render_user_badge()
    return user

def render_login_form(allowed_roles=None):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 StockBot Portal Login")
        st.caption("Sign in with your enterprise credentials to access your inventory.")

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="e.g. acme_admin or admin")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submit_btn = st.form_submit_button("Sign In", use_container_width=True)

            if submit_btn:
                if not username.strip() or not password.strip():
                    st.warning("Please provide both username and password.")
                    return

                user_data = verify_user(username.strip(), password.strip())

                if not user_data:
                    st.error("❌ Invalid credentials. Please try again.")
                    return

                if allowed_roles and user_data["role"] not in allowed_roles:
                    st.error(f"⛔ Unauthorized role: '{user_data['role']}'. Access restricted.")
                    return

                # Persist in session_state and query_params
                st.session_state.auth_user = user_data
                st.query_params["session_user"] = user_data["username"]
                st.query_params["session_role"] = user_data["role"]
                st.query_params["session_uid"] = str(user_data["user_id"])
                if user_data.get("client_id"):
                    st.query_params["session_client"] = str(user_data["client_id"])

                st.success("✅ Signed in successfully!")
                st.rerun()

        with st.expander("ℹ️ Demo Credentials (Click to view)"):
            st.markdown("""
            - **Acme Corp:** `acme_admin` / `pass123`
            - **Stark Logistics:** `stark_admin` / `pass123`
            - **Platform Admin:** `admin` / `admin123`
            """)

def render_user_badge():
    user = st.session_state.auth_user
    if not user:
        return

    if user.get("client_id"):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT wallet_balance FROM clients WHERE id = ?", (user["client_id"],))
            row = cursor.fetchone()
            if row:
                user["wallet_balance"] = row[0]
            conn.close()
        except Exception:
            pass

    with st.sidebar:
        st.markdown(f"👤 **Operator:** `{user['username']}`")
        st.caption(f"🏢 **Tenant:** {user['company_name']}")
        if user.get("client_id"):
            st.caption(f"💰 **Wallet:** `${user['wallet_balance']:.2f}`")
        
        if st.button("🚪 Sign Out", use_container_width=True):
            logout()
        st.divider()

def logout():
    st.session_state.auth_user = None
    for key in ["session_user", "session_role", "session_client", "session_uid"]:
        if key in st.query_params:
            del st.query_params[key]
    if "chat_messages" in st.session_state:
        st.session_state.chat_messages = []
    st.rerun()
    