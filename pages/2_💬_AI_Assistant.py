import streamlit as st
from auth import require_auth
from ai_service import InventoryAgent
from theme_manager import apply_current_theme

st.set_page_config(page_title="AI Stock Assistant", page_icon="💬", layout="wide")
apply_current_theme()

user = require_auth(allowed_roles=["client_admin", "client_staff"])
client_id = user["client_id"]
user_id = user["user_id"]

st.title("💬 Autonomous Stock Assistant")
st.caption(f"Natural language warehouse controller for {user['company_name']}.")

if "agent" not in st.session_state:
    st.session_state.agent = InventoryAgent()

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": f"Hello! I am your warehouse assistant for {user['company_name']}. You can ask me to restock, log sales, or inspect current inventory."
        }
    ]

with st.sidebar:
    st.subheader("⚡ Quick Prompts")
    if st.button("📋 Check All Stock"):
        st.session_state.incoming_prompt = "Show me the complete inventory list."
    if st.button("📦 Add 10 USB-C Docks"):
        st.session_state.incoming_prompt = "Add 10 USB-C Docks to inventory at $49.99 each."
    if st.button("🏷️ Log Sale of 2 Units"):
        st.session_state.incoming_prompt = "Sold 2 Ergonomic Desks to a customer."
    
    st.divider()
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Chat history cleared. How can I help you today?"}
        ]
        st.rerun()

for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "meta" in msg:
            st.caption(msg["meta"])

prompt_to_send = None
if "incoming_prompt" in st.session_state and st.session_state.incoming_prompt:
    prompt_to_send = st.session_state.incoming_prompt
    st.session_state.incoming_prompt = None
else:
    prompt_to_send = st.chat_input("Enter stock action (e.g. 'Received 15 Wireless Mice at $20 each')...")

if prompt_to_send:
    st.session_state.chat_messages.append({"role": "user", "content": prompt_to_send})
    with st.chat_message("user"):
        st.write(prompt_to_send)

    with st.chat_message("assistant"):
        with st.status("🤖 Processing tool call & logging telemetry...", expanded=True) as status:
            try:
                res = st.session_state.agent.send_user_message(
                    user_text=prompt_to_send,
                    client_id=client_id,
                    user_id=user_id
                )
                status.update(label="✅ Completed & Billed", state="complete", expanded=False)
                reply = res["reply"]
                meta_str = f"⚡ {res['tokens']} tokens | Billed: ${res['cost_charged']:.2f} | Balance: ${res['new_balance']:.2f}"
            except Exception as err:
                status.update(label="❌ Action Failed", state="error", expanded=False)
                reply = f"Error: {err}"
                meta_str = None

        st.write(reply)
        if meta_str:
            st.caption(meta_str)

        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": reply,
            "meta": meta_str
        })
    st.rerun()