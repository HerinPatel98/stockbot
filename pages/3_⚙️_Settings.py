import streamlit as st
from theme_manager import THEMES, apply_current_theme

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

# Ensure theme persists on load
apply_current_theme()

st.title("⚙️ System Settings")
st.caption("Customize appearance, UI preferences, and system parameters.")

st.markdown("### 🎨 Visual Theme")

theme_names = list(THEMES.keys())
current_idx = theme_names.index(st.session_state.current_theme)

selected_theme = st.selectbox(
    "Choose Theme Palette",
    options=theme_names,
    index=current_idx,
    help="Select a color palette. The UI updates instantly."
)

# If changed, store and rerun immediately
if selected_theme != st.session_state.current_theme:
    st.session_state.current_theme = selected_theme
    apply_current_theme()
    st.rerun()

# Theme Preview Cards
st.divider()
st.markdown("#### Theme Preview")

cols = st.columns(len(THEMES))
for col, (name, palette) in zip(cols, THEMES.items()):
    with col:
        is_active = (name == st.session_state.current_theme)
        st.markdown(
            f"""
            <div style="
                border: 2px solid {palette['primary'] if is_active else palette['border']};
                border-radius: 8px;
                padding: 12px;
                background-color: {palette['secondary_bg']};
                text-align: center;
                margin-bottom: 8px;
            ">
                <span style="color: {palette['text']}; font-weight: {'bold' if is_active else 'normal'}; font-size: 14px;">
                    {'👉 ' if is_active else ''}{name}
                </span>
                <div style="display: flex; gap: 6px; justify-content: center; margin-top: 8px;">
                    <div style="width: 20px; height: 20px; border-radius: 50%; background: {palette['bg']}; border: 1px solid #777;"></div>
                    <div style="width: 20px; height: 20px; border-radius: 50%; background: {palette['secondary_bg']}; border: 1px solid #777;"></div>
                    <div style="width: 20px; height: 20px; border-radius: 50%; background: {palette['primary']};"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.divider()
st.markdown("### ℹ️ Application Info")
st.text("Project: Conversational AI Inventory Manager (StockBot)")
st.text("Engine: Groq Function Calling with SQLite Local Ledger")