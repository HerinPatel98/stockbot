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
c1.color_picker("Primary Color", t["primary"], disabled=True)
c2.color_picker("Accent Color", t["accent"], disabled=True)
c3.color_picker("Background Canvas", t["bg"], disabled=True)
c4.color_picker("Card Background", t["secondary_bg"], disabled=True)