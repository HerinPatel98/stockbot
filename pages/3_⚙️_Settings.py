import streamlit as st
from auth import require_auth
from theme_manager import THEMES, apply_current_theme

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")
apply_current_theme()

user = require_auth(allowed_roles=["client_admin", "client_staff"])

st.title("⚙️ Visual Theme & Preferences")
st.caption("Customize your visual workspace display profile.")

theme_names = list(THEMES.keys())
current_idx = theme_names.index(st.session_state.current_theme) if st.session_state.current_theme in theme_names else 0

selected_theme = st.selectbox(
    "Select Color Palette",
    options=theme_names,
    index=current_idx
)

if selected_theme != st.session_state.current_theme:
    st.session_state.current_theme = selected_theme
    st.rerun()

st.divider()

st.subheader("Palette Color Samples")
t = THEMES[selected_theme]

c1, c2, c3, c4 = st.columns(4)
samples = (
    ("Primary Color", t["primary"]),
    ("Accent Color", t["accent"]),
    ("Background Canvas", t["bg"]),
    ("Card Background", t["secondary_bg"]),
)

for column, (label, color) in zip((c1, c2, c3, c4), samples):
    with column:
        st.markdown(
            f"""
            <div style="font-weight: 600; margin-bottom: 8px;">{label}</div>
            <div style="height: 72px; background-color: {color}; border: 2px solid {t['text']};
                        outline: 1px solid {t['border']}; outline-offset: 2px; border-radius: 8px;
                        margin: 4px 2px 10px;"></div>
            <code>{color}</code>
            """,
            unsafe_allow_html=True,
        )