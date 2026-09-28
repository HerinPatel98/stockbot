import streamlit as st
import pandas as pd
from auth import require_auth
from database import get_connection, top_up_client_wallet, hash_password
from theme_manager import apply_current_theme

st.set_page_config(
    page_title="StockBot Admin Control Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_current_theme()

user = require_auth(allowed_roles=["admin"])

st.title("🛡️ StockBot Global Administration Portal")
st.caption("Central fleet telemetry, client billing management, and platform analytics.")

conn = get_connection()

clients_df = pd.read_sql("SELECT * FROM clients ORDER BY id ASC", conn)
telemetry_df = pd.read_sql("""
    SELECT t.id AS 'Log ID', c.company_name AS 'Client', u.username AS 'User',
           t.model_used AS 'Engine', t.total_tokens AS 'Tokens',
           t.cost_deducted AS 'Charged ($)', t.balance_after AS 'Post Balance ($)',
           t.timestamp AS 'Timestamp'
    FROM api_billing_telemetry t
    JOIN clients c ON t.client_id = c.id
    JOIN users u ON t.user_id = u.id
    ORDER BY t.id DESC
""", conn)

# ----------------- Macro Analytics Metrics -----------------
m1, m2, m3, m4 = st.columns(4)

total_revenue = telemetry_df["Charged ($)"].sum() if not telemetry_df.empty else 0.0
total_queries = len(telemetry_df)
total_tokens = telemetry_df["Tokens"].sum() if not telemetry_df.empty else 0
active_clients = len(clients_df[clients_df["status"] == "active"])

with m1:
    st.metric("Gross Billed Revenue", f"${total_revenue:.2f}")
with m2:
    st.metric("Total AI Queries Handled", total_queries)
with m3:
    st.metric("Fleet Token Consumption", f"{total_tokens:,}")
with m4:
    st.metric("Active Client Accounts", active_clients)

st.divider()

# ----------------- Tabs: Fleet Management, Global Telemetry, Provisioning -----------------
tab_fleet, tab_telemetry, tab_provision = st.tabs([
    "🏢 Client Fleet & Wallets",
    "📡 Zero-Knowledge Telemetry Stream",
    "➕ Provision New Client"
])

with tab_fleet:
    st.subheader("Client Organizations & Billing Configurations")
    
    st.dataframe(
        clients_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": st.column_config.NumberColumn("Tenant ID"),
            "company_name": st.column_config.TextColumn("Organization"),
            "contact_email": st.column_config.TextColumn("Contact"),
            "rate_per_query": st.column_config.NumberColumn("Rate / Query ($)", format="$%.2f"),
            "wallet_balance": st.column_config.NumberColumn("Wallet Balance ($)", format="$%.2f"),
            "status": st.column_config.TextColumn("Status"),
            "created_at": st.column_config.DatetimeColumn("Registered On")
        }
    )

    st.markdown("#### ⚡ Quick Actions: Top-Up or Adjust Rates")
    action_col1, action_col2 = st.columns(2)

    with action_col1:
        with st.form("admin_wallet_topup"):
            st.markdown("**Manual Balance Deposit**")
            target_client_id = st.selectbox(
                "Select Client Organization",
                options=clients_df["id"],
                format_func=lambda x: f"{clients_df[clients_df['id'] == x]['company_name'].values[0]} (ID: {x})"
            )
            deposit_amount = st.number_input("Deposit Amount ($)", min_value=1.0, value=25.0, step=5.0)
            deposit_ref = st.text_input("Deposit Reference", value="ADMIN_MANUAL_CREDIT")
            submit_deposit = st.form_submit_button("Credit Client Wallet", use_container_width=True)

            if submit_deposit:
                new_bal = top_up_client_wallet(target_client_id, deposit_amount, deposit_ref)
                st.success(f"Deposited ${deposit_amount:.2f}! New balance: ${new_bal:.2f}")
                st.rerun()

    with action_col2:
        with st.form("admin_rate_adjust"):
            st.markdown("**Adjust Pricing Rate ($ / query)**")
            rate_client_id = st.selectbox(
                "Select Client to Re-price",
                options=clients_df["id"],
                format_func=lambda x: f"{clients_df[clients_df['id'] == x]['company_name'].values[0]} (ID: {x})"
            )
            new_query_rate = st.number_input("New Per-Query Rate ($)", min_value=0.01, max_value=2.00, value=0.05, step=0.01)
            submit_rate = st.form_submit_button("Update Contract Rate", use_container_width=True)

            if submit_rate:
                cursor = conn.cursor()
                cursor.execute("UPDATE clients SET rate_per_query = ? WHERE id = ?", (new_query_rate, rate_client_id))
                conn.commit()
                st.success(f"Rate updated to ${new_query_rate:.2f} per query!")
                st.rerun()

with tab_telemetry:
    st.subheader("Global Zero-Knowledge Telemetry Audit")
    st.caption("Displays purely operational and financial telemetry. No inventory items or user prompts are ever transmitted or stored here.")

    client_filter = st.selectbox(
        "Filter by Organization:",
        options=["All Organizations"] + list(clients_df["company_name"].unique())
    )

    if client_filter != "All Organizations":
        filtered_logs = telemetry_df[telemetry_df["Client"] == client_filter]
    else:
        filtered_logs = telemetry_df

    st.dataframe(
        filtered_logs,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Log ID": st.column_config.NumberColumn("ID"),
            "Client": st.column_config.TextColumn("Tenant"),
            "User": st.column_config.TextColumn("Operator"),
            "Engine": st.column_config.TextColumn("Model"),
            "Tokens": st.column_config.NumberColumn("Total Tokens", format="%d"),
            "Charged ($)": st.column_config.NumberColumn("Charged ($)", format="$%.2f"),
            "Post Balance ($)": st.column_config.NumberColumn("Balance Post-Query", format="$%.2f"),
            "Timestamp": st.column_config.DatetimeColumn("Execution Time")
        }
    )

with tab_provision:
    st.subheader("Provision New Tenant Organization & Admin User")
    with st.form("provision_form"):
        p_c1, p_c2 = st.columns(2)
        with p_c1:
            new_org_name = st.text_input("Company Name (e.g. Nexus Electronics)")
            new_email = st.text_input("Contact Email", placeholder="ops@nexuselec.com")
            new_rate = st.number_input("Standard Rate per Query ($)", min_value=0.01, value=0.05, step=0.01)
            new_initial_balance = st.number_input("Starter Wallet Balance ($)", min_value=1.0, value=20.0, step=5.0)

        with p_c2:
            new_username = st.text_input("Initial Admin Username", placeholder="nexus_admin")
            new_password = st.text_input("Initial Admin Password", type="password")

        provision_submit = st.form_submit_button("🚀 Provision Client Instance", use_container_width=True)

        if provision_submit:
            if not new_org_name.strip() or not new_username.strip() or not new_password.strip():
                st.error("Please fill out all required organization and admin user fields.")
            else:
                cursor = conn.cursor()
                try:
                    cursor.execute("""
                        INSERT INTO clients (company_name, contact_email, rate_per_query, wallet_balance)
                        VALUES (?, ?, ?, ?)
                    """, (new_org_name.strip(), new_email.strip(), new_rate, new_initial_balance))
                    new_tenant_id = cursor.lastrowid

                    pwd_h = hash_password(new_password.strip())
                    cursor.execute("""
                        INSERT INTO users (client_id, username, password_hash, role)
                        VALUES (?, ?, ?, 'client_admin')
                    """, (new_tenant_id, new_username.strip(), pwd_h))

                    conn.commit()
                    st.success(f"Tenant '{new_org_name}' provisioned with ID #{new_tenant_id} and user '{new_username}'!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to provision tenant: {e}")

conn.close()