import streamlit as st
import pandas as pd
from database import fetch_products_dataframe, fetch_recent_transactions_dataframe
from theme_manager import apply_current_theme
apply_current_theme()

st.set_page_config(page_title="Inventory Dashboard", page_icon="📊", layout="wide")

st.title("📊 Inventory Analytics & Ledger")
st.caption("Live overview of warehouse assets and chronological transaction history.")

# Fetch live data
df_products = fetch_products_dataframe()
df_tx = fetch_recent_transactions_dataframe(limit=25)

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
    st.metric("Low Stock Alerts (<10)", low_stock_count, delta=-low_stock_count if low_stock_count > 0 else 0, delta_color="inverse")

st.divider()

# ----------------- Data Tables Section -----------------
tab1, tab2 = st.tabs(["📦 Current Stock Items", "📝 Audit Activity Ledger"])

with tab1:
    st.subheader("Warehouse Catalog")
    
    # Quick search filter
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
            "Stock": st.column_config.ProgressColumn("Stock Level", format="%d", min_value=0, max_value=max(100, int(df_products["Stock"].max() or 100))),
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
                "Time": st.column_config.DatetimeColumn("Timestamp", format="YYYY-MM-DD HH:mm:ss")
            }
        )