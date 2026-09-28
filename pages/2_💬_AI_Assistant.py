import streamlit as st
from ai_service import InventoryAgent
from theme_manager import apply_current_theme
apply_current_theme()

st.set_page_config(page_title="AI Inventory Assistant", page_icon="💬", layout="wide")

st.title("💬 Autonomous Stock Assistant")
st.caption("Perform inventory actions through everyday conversational language.")

# Initialize the AI Agent in session state
if "agent" not in st.session_state:
    try:
        st.session_state.agent = InventoryAgent()
    except Exception as e:
        st.error(f"Failed to initialize AI Agent: {e}")
        st.stop()

# Initialize message history
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "Hello! I manage your warehouse database. Ask me to restock, log sales, or inspect current items."}
    ]

# Sidebar actions & prompt shortcuts
with st.sidebar:
    st.subheader("⚡ Quick Prompts")
    if st.button("📋 Check All Stock"):
        st.session_state.incoming_prompt = "Show me the complete inventory list."
    if st.button("📦 Restock 20 Laptop Stands"):
        st.session_state.incoming_prompt = "Add 20 Laptop Stands to inventory at $25 each."
    if st.button("🏷️ Record Sale of 5 Units"):
        st.session_state.incoming_prompt = "Sold 5 Laptop Stands to a customer."
    
    st.divider()
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Chat history cleared. How can I help you?"}
        ]
        st.rerun()

# Display chat history
for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Check for quick prompt trigger from sidebar
prompt_to_send = None
if "incoming_prompt" in st.session_state and st.session_state.incoming_prompt:
    prompt_to_send = st.session_state.incoming_prompt
    st.session_state.incoming_prompt = None
else:
    prompt_to_send = st.chat_input("Enter action (e.g., 'Received 30 Gaming Mice at $15 each')...")

if prompt_to_send:
    # 1. Render user message
    st.session_state.chat_messages.append({"role": "user", "content": prompt_to_send})
    with st.chat_message("user"):
        st.write(prompt_to_send)

    # 2. Get AI Response with animated status indicator
    with st.chat_message("assistant"):
        with st.status("🤖 Agent thinking & querying database...", expanded=True) as status:
            st.write("🧠 Interpreting natural language...")
            try:
                reply = st.session_state.agent.send_user_message(prompt_to_send)
                if not reply or not reply.strip():
                    reply = "Action logged successfully."
                
                st.write("⚡ Executing database operations...")
                status.update(label="✅ Completed!", state="complete", expanded=False)
            except Exception as err:
                status.update(label="❌ Execution failed", state="error", expanded=False)
                reply = f"Error processing request: {err}"

        # Write final output below the completed status pill
        st.write(reply)
        st.session_state.chat_messages.append({"role": "assistant", "content": reply})

    st.rerun()