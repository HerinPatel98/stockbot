import streamlit as st
from theme_manager import THEMES, apply_current_theme

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

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

if selected_theme != st.session_state.current_theme:
    st.session_state.current_theme = selected_theme
    apply_current_theme()
    st.rerun()

st.divider()
st.markdown("#### Theme Palette Showcase")

cols = st.columns(len(THEMES))
for col, (name, palette) in zip(cols, THEMES.items()):
    with col:
        is_active = (name == st.session_state.current_theme)
        st.markdown(
            f"""
            <div style="
                border: 2px solid {palette['primary'] if is_active else palette['border']};
                border-radius: 10px;
                padding: 14px;
                background-color: {palette['secondary_bg']};
                text-align: center;
                box-shadow: {'0 0 15px ' + palette['primary'] if is_active else 'none'};
                margin-bottom: 10px;
            ">
                <span style="color: {palette['text']}; font-weight: bold; font-size: 14px;">
                    {'👉 ' if is_active else ''}{name}
                </span>
                <div style="display: flex; gap: 8px; justify-content: center; margin-top: 10px;">
                    <div title="Canvas" style="width: 22px; height: 22px; border-radius: 50%; background: {palette['bg']}; border: 1px solid #666;"></div>
                    <div title="Surface" style="width: 22px; height: 22px; border-radius: 50%; background: {palette['secondary_bg']}; border: 1px solid #666;"></div>
                    <div title="Primary Accent" style="width: 22px; height: 22px; border-radius: 50%; background: {palette['primary']};"></div>
                    <div title="Highlight" style="width: 22px; height: 22px; border-radius: 50%; background: {palette['accent']};"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.divider()
st.markdown("### ℹ️ Architecture Specs")
st.text("Frontend: Streamlit Multi-Page Framework")
st.text("Orchestration: Groq Cloud LPU (Function Calling Engine)")
st.text("Persistence: SQLite Structured Local Storage")