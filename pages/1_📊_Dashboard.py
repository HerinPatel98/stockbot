import streamlit as st
import pandas as pd
from auth import require_auth
from database import fetch_client_products, fetch_client_transactions
from theme_manager import apply_current_theme
from services import delete_stock

st.set_page_config(page_title="Inventory Dashboard", page_icon="📊", layout="wide")
apply_current_theme()

user = require_auth(allowed_roles=["client_admin", "client_staff"])
client_id = user["client_id"]

st.title("📊 Inventory Analytics & Ledger")
st.caption(f"Live warehouse assets and chronological transaction history for {user['company_name']}.")

df_products = fetch_client_products(client_id)
df_tx = fetch_client_transactions(client_id, limit=25)

# ----------------- Top KPI Metric Cards -----------------
col1, col2, col3, col4 = st.columns(4)

total_skus = len(df_products)
total_units = int(df_products["Stock"].sum()) if not df_products.empty else 0
total_value = float((df_products["Stock"] * df_products["Price"]).sum()) if not df_products.empty else 0.0
low_stock_count = int((df_products["Stock"] < 10).sum()) if not df_products.empty else 0

with col1:
    st.metric("Total SKUs", total_skus)
with col2:
    st.metric("Total Units in Stock", total_units)
with col3:
    st.metric("Total Inventory Valuation", f"${total_value:,.2f}")
with col4:
    st.metric(
        "Low Stock Alerts (<10)",
        low_stock_count,
        delta=-low_stock_count if low_stock_count > 0 else 0,
        delta_color="inverse"
    )

st.divider()

# ----------------- Data Tables Section -----------------
tab1, tab2 = st.tabs(["📦 Current Stock Items", "📝 Audit Activity Ledger"])

with tab1:
    st.subheader("Warehouse Catalog")
    
    search_query = st.text_input("🔍 Search product name...", "")
    if search_query and not df_products.empty:
        filtered_df = df_products[df_products["Product"].str.contains(search_query, case=False, na=False)]
    else:
        filtered_df = df_products

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Product": st.column_config.TextColumn("Product Name"),
            "Stock": st.column_config.ProgressColumn(
                "Stock Level",
                format="%d",
                min_value=0,
                max_value=max(100, int(df_products["Stock"].max() or 100))
            ),
            "Price": st.column_config.NumberColumn("Unit Price ($)", format="$%.2f")
        }
    )

with tab2:
    st.subheader("Transaction History (Audit Trail)")
    if df_tx.empty:
        st.info("No transaction logs recorded yet.")
    else:
        st.dataframe(
            df_tx,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Product": st.column_config.TextColumn("Item"),
                "Change": st.column_config.NumberColumn("Quantity Shift"),
                "Type": st.column_config.TextColumn("Action Type"),
                "Time": st.column_config.DatetimeColumn("Timestamp")
            }
        )
        
st.divider()

# ----------------- Catalog SKU Decommissioning Section -----------------
with st.expander("🗑️ Decommission / Delete Product SKU", expanded=False):
    st.caption("Permanently remove a discontinued SKU from catalog. This logs an audit trace and liquidates listed stock.")
    
    if not df_products.empty:
        sku_to_delete = st.selectbox("Select Product to Decommission", options=df_products["Product"].values)
        
        # Pull metadata for warning card
        selected_row = df_products[df_products["Product"] == sku_to_delete].iloc[0]
        cur_units = int(selected_row["Stock"])
        cur_unit_price = float(selected_row["Price"])
        cur_loss = cur_units * cur_unit_price

        st.warning(
            f"⚠️ **Destructive Action Notice:**\n\n"
            f"- Product: **{sku_to_delete}**\n"
            f"- Units being removed: **{cur_units}**\n"
            f"- Asset Valuation to write off: **${cur_loss:,.2f}**\n\n"
            f"This operation cannot be undone and will record a `DECOMMISSION` audit event."
        )

        confirm_check = st.checkbox(f"I understand the consequences and confirm removal of '{sku_to_delete}'.")
        
        if st.button("🚨 Permanently Delete Product", type="primary", disabled=not confirm_check):
            from services import delete_stock
            result_msg = delete_stock(sku_to_delete, client_id=client_id, confirm=True)
            st.success(result_msg)
            st.rerun()
    else:
        st.info("No items in catalog to delete.")
        