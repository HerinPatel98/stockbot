import streamlit as st
import pandas as pd
from auth import require_auth
from database import fetch_client_telemetry, top_up_client_wallet, get_connection
from theme_manager import apply_current_theme

st.set_page_config(page_title="Usage & Billing", page_icon="💳", layout="wide")
apply_current_theme()

user = require_auth(allowed_roles=["client_admin", "client_staff"])
client_id = user["client_id"]

st.title("💳 My Usage & Billing Portal")
st.caption(f"Account metering, dummy dollar balance, and audit telemetry for {user['company_name']}.")

conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT wallet_balance, rate_per_query, low_balance_threshold FROM clients WHERE id = ?", (client_id,))
wallet_bal, rate_per_q, low_thresh = cursor.fetchone()
conn.close()

telemetry_df = fetch_client_telemetry(client_id)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Wallet Balance", f"${wallet_bal:.2f}", delta=None)
with c2:
    st.metric("Rate Per Query", f"${rate_per_q:.2f}")
with c3:
    total_spent = telemetry_df["Cost ($)"].sum() if not telemetry_df.empty else 0.0
    st.metric("Total Spent", f"${total_spent:.2f}")
with c4:
    queries_run = len(telemetry_df)
    st.metric("AI Queries Run", queries_run)

if wallet_bal <= low_thresh:
    st.warning(f"⚠️ **Low Balance Alert:** Your wallet has ${wallet_bal:.2f} remaining. Top up to ensure continuous AI query processing.")

st.divider()

col_recharge, col_logs = st.columns([1, 2])

with col_recharge:
    st.subheader("💵 Dummy Dollar Top-Up")
    st.caption("Simulate adding prepaid funds to your account.")

    with st.form("wallet_topup_form"):
        topup_tier = st.radio(
            "Select Recharge Tier",
            options=[10.0, 25.0, 50.0, 100.0],
            format_func=lambda x: f"+${x:.2f} Dummy USD",
            index=1
        )
        card_dummy = st.text_input("Simulated Payment Method", value="TEST_VISA_•••• 4242", disabled=True)
        recharge_btn = st.form_submit_button("💳 Deposit Funds Now", use_container_width=True)

        if recharge_btn:
            new_bal = top_up_client_wallet(
                client_id=client_id,
                amount=topup_tier,
                reference=f"SANDBOX_{card_dummy}"
            )
            st.success(f"✅ Successfully deposited ${topup_tier:.2f}! New Balance: ${new_bal:.2f}")
            st.rerun()

    st.info("ℹ️ **Billing Policy:** Every conversational query deducts a fixed rate. Data models and catalog entries remain completely private to your instance.")

with col_logs:
    st.subheader("📊 Metered Query Ledger")
    if telemetry_df.empty:
        st.info("No AI queries processed yet. Your transactions will appear here.")
    else:
        st.dataframe(
            telemetry_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Log ID": st.column_config.NumberColumn("ID"),
                "Engine": st.column_config.TextColumn("Model Engine"),
                "Total Tokens": st.column_config.NumberColumn("Tokens", format="%d"),
                "Cost ($)": st.column_config.NumberColumn("Fee Charged", format="$%.2f"),
                "Balance After ($)": st.column_config.NumberColumn("Balance Remaining", format="$%.2f"),
                "Timestamp": st.column_config.DatetimeColumn("Execution Time")
            }
        )
        