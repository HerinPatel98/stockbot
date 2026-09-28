import streamlit as st
from auth import require_auth
from ai_service import InventoryAgent
from database import fetch_client_products
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

# ----------------- Guided Operations Bar (Inventory-Aware & Guardrailed) -----------------
with st.expander("⚡ Guided Stock Operations (Guaranteed SKU Match)", expanded=False):
    st.caption("Use this form to restock, sell, or delete items without typos, duplicate SKUs, or overselling.")
    
    products_df = fetch_client_products(client_id)
    
    # Build dictionary of product -> available stock and unit price
    stock_lookup = {}
    if not products_df.empty:
        for _, row in products_df.iterrows():
            stock_lookup[row["Product"]] = {
                "stock": int(row["Stock"]),
                "price": float(row["Price"])
            }
    
    existing_items = list(stock_lookup.keys())
    
    col_act, col_item, col_qty, col_price = st.columns([1.2, 2, 1, 1])
    
    with col_act:
        # HERE: Updated action selector with Delete SKU
        action_mode = st.selectbox(
            "Action", 
            ["Restock (+)", "Record Sale (-)", "➕ Create New SKU", "🗑️ Delete SKU"]
        )
    
    with col_item:
        if action_mode == "➕ Create New SKU":
            chosen_product = st.text_input("New Product Name", placeholder="e.g. 4K Webcam")
            available_stock = 0
            default_price = 25.0
        else:
            if existing_items:
                chosen_product = st.selectbox("Select Existing Item", options=existing_items)
                available_stock = stock_lookup[chosen_product]["stock"]
                default_price = stock_lookup[chosen_product]["price"]
            else:
                chosen_product = st.text_input("Product Name", placeholder="No items yet. Type new product.")
                action_mode = "➕ Create New SKU"
                available_stock = 0
                default_price = 25.0

    with col_qty:
        if action_mode == "Record Sale (-)":
            if available_stock > 0:
                chosen_qty = st.number_input(
                    f"Units (Max: {available_stock})",
                    min_value=1,
                    max_value=available_stock,
                    value=1,
                    step=1
                )
            else:
                st.number_input("Units", min_value=0, max_value=0, value=0, disabled=True)
                chosen_qty = 0
        elif action_mode == "🗑️ Delete SKU":
            st.number_input("Purge Units", value=available_stock, disabled=True)
            chosen_qty = available_stock
        else:
            chosen_qty = st.number_input("Units", min_value=1, value=5, step=1)

    with col_price:
        if action_mode in ["Record Sale (-)", "🗑️ Delete SKU"]:
            st.number_input("Unit Price ($)", value=default_price, disabled=True)
            chosen_price = default_price
        elif action_mode == "Restock (+)":
            chosen_price = st.number_input("Unit Price ($)", min_value=0.0, value=default_price, step=5.0)
        else:
            chosen_price = st.number_input("Unit Price ($)", min_value=0.0, value=25.0, step=5.0)

    # Disable sale if out of stock
    is_sale_disabled = (action_mode == "Record Sale (-)" and available_stock == 0)

    if is_sale_disabled:
        st.error(f"⚠️ '{chosen_product}' is currently completely out of stock (0 units). Cannot record sale.")

    # Destruction warning banner when Delete SKU is picked
    if action_mode == "🗑️ Delete SKU" and chosen_product:
        total_loss = available_stock * default_price
        st.warning(f"⚠️ **Warning:** Deleting '{chosen_product}' will permanently purge {available_stock} units (${total_loss:,.2f} valuation) from your catalog.")

    # Execution button
    button_label = "🚨 Confirm & Delete Product" if action_mode == "🗑️ Delete SKU" else "🚀 Execute Guided Action"
    button_type = "primary" if action_mode == "🗑️ Delete SKU" else "secondary"

    if st.button(button_label, use_container_width=True, disabled=is_sale_disabled, type=button_type):
        if not chosen_product or not chosen_product.strip():
            st.warning("Please specify a product name.")
        elif action_mode == "Record Sale (-)" and chosen_qty > available_stock:
            st.error(f"Cannot sell {chosen_qty} units. Only {available_stock} units available.")
        else:
            # HERE: The execution command builder
            if action_mode == "Restock (+)":
                cmd = f"Add {chosen_qty} units of '{chosen_product}' at ${chosen_price:.2f} each."
            elif action_mode == "Record Sale (-)":
                cmd = f"Sold {chosen_qty} units of '{chosen_product}'."
            elif action_mode == "➕ Create New SKU":
                cmd = f"Add new SKU '{chosen_product}' with {chosen_qty} units at ${chosen_price:.2f} each."
            elif action_mode == "🗑️ Delete SKU":
                cmd = f"Confirm delete product '{chosen_product}'"
            
            st.session_state.incoming_prompt = cmd
            st.rerun()
            
st.divider()

# Sidebar actions
with st.sidebar:
    st.subheader("⚡ Quick Prompts")
    if st.button("📋 Check All Stock"):
        st.session_state.incoming_prompt = "Show me the complete inventory list."
    
    st.divider()
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Chat history cleared. How can I help you today?"}
        ]
        st.rerun()

# Render chat history
for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "meta" in msg:
            st.caption(msg["meta"])

# Prompt handling
prompt_to_send = None
if "incoming_prompt" in st.session_state and st.session_state.incoming_prompt:
    prompt_to_send = st.session_state.incoming_prompt
    st.session_state.incoming_prompt = None
else:
    prompt_to_send = st.chat_input("Enter stock action (e.g. 'Sold 2 USB-C Docks')...")

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
    