import os
from string import Template

import streamlit as st

DEFAULT_THEME = "Cyberpunk Neon"

THEMES = {
    "Cyberpunk Neon": {
        "mode": "dark",
        "primary": "#ff007f",
        "accent": "#00f0ff",
        "bg": "#0a0a12",
        "secondary_bg": "#161626",
        "text": "#f8f9fa",
        "muted": "#9a9ab5",
        "border": "#ff007f",
    },
    "Terminal Amber": {
        "mode": "dark",
        "primary": "#f59e0b",
        "accent": "#fbbf24",
        "bg": "#0d0c00",
        "secondary_bg": "#1c1905",
        "text": "#fef08a",
        "muted": "#a3893a",
        "border": "#b45309",
    },
    "Nordic Glacier": {
        "mode": "light",
        "primary": "#0284c7",
        "accent": "#0369a1",
        "bg": "#e6edf5",
        "secondary_bg": "#ffffff",
        "text": "#0f172a",
        "muted": "#475569",
        "border": "#cbd5e1",
    },
    "Dark Nordic Glacier": {
        "mode": "dark",
        "primary": "#38bdf8",
        "accent": "#2dd4bf",
        "bg": "#070d18",
        "secondary_bg": "#0f1c30",
        "text": "#f1f5f9",
        "muted": "#94a3b8",
        "border": "#1e3a5f",
    },
    "Royal Amethyst": {
        "mode": "dark",
        "primary": "#a855f7",
        "accent": "#c084fc",
        "bg": "#13091f",
        "secondary_bg": "#231538",
        "text": "#faf5ff",
        "muted": "#a78bcb",
        "border": "#6b21a8",
    },
    "Forest Emerald": {
        "mode": "dark",
        "primary": "#10b981",
        "accent": "#34d399",
        "bg": "#06120d",
        "secondary_bg": "#0d211a",
        "text": "#ecfdf5",
        "muted": "#86b7a3",
        "border": "#14503b",
    },
    "Crimson Ember": {
        "mode": "dark",
        "primary": "#ef4444",
        "accent": "#f97316",
        "bg": "#120707",
        "secondary_bg": "#221010",
        "text": "#fef2f2",
        "muted": "#c49a9a",
        "border": "#7f1d1d",
    },
    "Synthwave Sunset": {
        "mode": "dark",
        "primary": "#f472b6",
        "accent": "#fb923c",
        "bg": "#1a1033",
        "secondary_bg": "#2a1a4d",
        "text": "#fdf4ff",
        "muted": "#b9a3d9",
        "border": "#5b3a9a",
    },
    "Dracula": {
        "mode": "dark",
        "primary": "#bd93f9",
        "accent": "#50fa7b",
        "bg": "#282a36",
        "secondary_bg": "#343746",
        "text": "#f8f8f2",
        "muted": "#9aa0c0",
        "border": "#6272a4",
    },
    "Slate Mono": {
        "mode": "dark",
        "primary": "#e2e8f0",
        "accent": "#94a3b8",
        "bg": "#0b0b0c",
        "secondary_bg": "#18181b",
        "text": "#fafafa",
        "muted": "#a1a1aa",
        "border": "#3f3f46",
    },
    "Solarized Light": {
        "mode": "light",
        "primary": "#268bd2",
        "accent": "#2aa198",
        "bg": "#fdf6e3",
        "secondary_bg": "#eee8d5",
        "text": "#073642",
        "muted": "#586e75",
        "border": "#d3cbb7",
    },
    "Rose Quartz": {
        "mode": "light",
        "primary": "#db2777",
        "accent": "#9333ea",
        "bg": "#fdf2f8",
        "secondary_bg": "#ffffff",
        "text": "#3b0a24",
        "muted": "#9d5c7c",
        "border": "#fbcfe8",
    },
}

CSS_TEMPLATE = Template("""
<style>
html, :root, body {
    color-scheme: $mode !important;
    background-color: $bg !important;
}

.stApp, [data-testid="stApp"], [data-testid="stAppViewContainer"],
[data-testid="stMain"], [data-testid="stMainBlockContainer"], .main, .block-container {
    background-color: $bg !important;
    color: $text !important;
}
header[data-testid="stHeader"], [data-testid="stHeader"] {
    background-color: $bg !important;
}
[data-testid="stToolbar"] *, [data-testid="stMainMenu"] *, [data-testid="stHeader"] button,
[data-testid="stHeader"] a {
    color: $text !important;
}
[data-testid="stHeader"] svg, [data-testid="stToolbar"] svg,
[data-testid="stSidebarCollapseButton"] svg, [data-testid="stExpandSidebarButton"] svg,
[data-testid="stSidebarCollapsedControl"] svg {
    fill: $text !important;
    color: $text !important;
}
[data-testid="stBottom"], [data-testid="stBottom"] > div,
[data-testid="stBottomBlockContainer"], [data-testid="stBottom"] [data-testid="stVerticalBlock"] {
    background-color: $bg !important;
}
[data-testid="stDecoration"] {
    background-image: linear-gradient(90deg, $primary, $accent) !important;
}

section[data-testid="stSidebar"], section[data-testid="stSidebar"] > div,
[data-testid="stSidebarContent"], [data-testid="stSidebarHeader"],
[data-testid="stSidebarUserContent"] {
    background-color: $secondary_bg !important;
}
section[data-testid="stSidebar"] {
    border-right: 2px solid $border !important;
}

h1, h2, h3, h4, h5, h6, p, li, label, td, th, strong, em,
[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] *:not(code):not(pre),
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] *,
[data-testid="stHeadingWithActionElements"] *,
[data-testid="stCheckbox"] label *, [data-testid="stRadio"] label *,
[data-testid="stToggle"] label *, [data-testid="stSlider"] label *,
[data-testid="stChatMessageContent"] p, [data-testid="stChatMessageContent"] li {
    color: $text !important;
}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] *,
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] *,
small, .stCaption {
    color: $muted !important;
}
.stApp a, .stApp a * { color: $accent !important; }
.stApp a:hover, .stApp a:hover * { color: $primary !important; }
hr { border-color: $border !important; background-color: $border !important; }
::selection { background: $primary; color: $on_primary; }
blockquote { border-left: 4px solid $primary !important; }
blockquote, blockquote * { color: $muted !important; }

::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: $bg; }
::-webkit-scrollbar-thumb { background: $border; border-radius: 8px; }
::-webkit-scrollbar-thumb:hover { background: $primary; }

div[data-testid="stMetric"] {
    background-color: $secondary_bg !important;
    border: 1px solid $border !important;
    border-radius: 10px;
    padding: 12px 16px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.18);
}
div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] * {
    color: $primary !important;
    font-weight: 700;
}

.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button,
.stLinkButton > a, button[data-testid^="stBaseButton-secondary"] {
    background-color: $secondary_bg !important;
    border: 1.5px solid $primary !important;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.25s ease-in-out;
}
.stButton > button *, .stDownloadButton > button *, .stFormSubmitButton > button *,
.stLinkButton > a *, button[data-testid^="stBaseButton-secondary"] * {
    color: $text !important;
}
.stButton > button:hover, .stDownloadButton > button:hover,
.stFormSubmitButton > button:hover, .stLinkButton > a:hover,
button[data-testid^="stBaseButton-secondary"]:hover {
    background-color: $primary !important;
    border-color: $accent !important;
    box-shadow: 0 0 12px $primary;
}
.stButton > button:hover *, .stDownloadButton > button:hover *,
.stFormSubmitButton > button:hover *, .stLinkButton > a:hover *,
button[data-testid^="stBaseButton-secondary"]:hover * {
    color: $on_primary !important;
}
button[data-testid="stBaseButton-primary"], button[kind="primary"] {
    background-color: $primary !important;
    border: 1.5px solid $primary !important;
}
button[data-testid="stBaseButton-primary"] *, button[kind="primary"] * {
    color: $on_primary !important;
}
button:focus-visible { outline: 2px solid $accent !important; }
button:disabled { opacity: 0.45 !important; }

div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="textarea"],
div[data-baseweb="select"] > div, div[data-baseweb="datepicker"] div[data-baseweb="input"],
div[data-testid="stTextArea"] textarea {
    background-color: $secondary_bg !important;
    border: 1.5px solid $border !important;
    border-radius: 8px !important;
}
section[data-testid="stSidebar"] div[data-baseweb="input"],
section[data-testid="stSidebar"] div[data-baseweb="base-input"],
section[data-testid="stSidebar"] div[data-baseweb="textarea"],
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background-color: $bg !important;
}
div[data-baseweb="input"]:focus-within, div[data-baseweb="base-input"]:focus-within,
div[data-baseweb="textarea"]:focus-within, div[data-baseweb="select"]:focus-within > div {
    border-color: $primary !important;
    box-shadow: 0 0 8px $primary !important;
}
div[data-baseweb="input"] > div, div[data-baseweb="base-input"] > div,
div[data-baseweb="textarea"] > div {
    background-color: transparent !important;
}
input, textarea, select {
    background-color: transparent !important;
    color: $text !important;
    -webkit-text-fill-color: $text !important;
    caret-color: $primary !important;
}
input::placeholder, textarea::placeholder, select::placeholder {
    color: $muted !important;
    -webkit-text-fill-color: $muted !important;
    opacity: 1 !important;
}
input::-webkit-input-placeholder, textarea::-webkit-input-placeholder {
    color: $muted !important;
    -webkit-text-fill-color: $muted !important;
    opacity: 1 !important;
}
input:disabled, textarea:disabled {
    -webkit-text-fill-color: $muted !important;
    opacity: 0.6 !important;
}
input:-webkit-autofill {
    -webkit-box-shadow: 0 0 0 1000px $secondary_bg inset !important;
    -webkit-text-fill-color: $text !important;
}
div[data-baseweb="select"] *, div[data-baseweb="select"] input {
    color: $text !important;
    -webkit-text-fill-color: $text !important;
}
div[data-baseweb="select"] [aria-hidden="true"] {
    color: $muted !important;
}
div[data-baseweb="select"] svg, div[data-baseweb="input"] svg, div[data-baseweb="textarea"] svg {
    fill: $muted !important;
    color: $muted !important;
}
[data-testid="stNumberInput"] button {
    background-color: $secondary_bg !important;
    border-color: $border !important;
}
[data-testid="stNumberInput"] button svg { fill: $text !important; }
[data-testid="stNumberInput"] button:hover { background-color: $primary !important; }
[data-testid="stNumberInput"] button:hover svg { fill: $on_primary !important; }
div[data-baseweb="input"] button { background-color: transparent !important; }

[data-testid="stChatInput"] {
    background-color: $secondary_bg !important;
    border: 1.5px solid $border !important;
    border-radius: 12px !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: $primary !important;
    box-shadow: 0 0 8px $primary !important;
}
[data-testid="stChatInput"] > div, [data-testid="stChatInput"] div,
[data-testid="stChatInput"] div[data-baseweb="textarea"],
[data-testid="stChatInput"] div[data-baseweb="base-input"] {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
[data-testid="stChatInput"] textarea, [data-testid="stChatInputTextArea"] {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: $text !important;
    -webkit-text-fill-color: $text !important;
    caret-color: $primary !important;
}
[data-testid="stChatInput"] textarea::placeholder,
[data-testid="stChatInputTextArea"]::placeholder {
    color: $muted !important;
    -webkit-text-fill-color: $muted !important;
    opacity: 1 !important;
}
[data-testid="stChatInput"] button, [data-testid="stChatInputSubmitButton"] {
    background-color: $primary !important;
    border: none !important;
    border-radius: 8px !important;
    opacity: 1 !important;
}
[data-testid="stChatInput"] button svg, [data-testid="stChatInputSubmitButton"] svg {
    fill: $on_primary !important;
    color: $on_primary !important;
}
[data-testid="stChatInput"] button:disabled,
[data-testid="stChatInputSubmitButton"]:disabled {
    background-color: $border !important;
    opacity: 0.7 !important;
}
[data-testid="stChatInput"] button:disabled svg { fill: $muted !important; }

div[data-testid="stChatMessage"] {
    background-color: $secondary_bg !important;
    border: 1px solid $border !important;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
}
div[data-testid="stChatMessage"] [data-testid^="stChatMessageAvatar"] {
    background-color: $primary !important;
}
div[data-testid="stChatMessage"] [data-testid^="stChatMessageAvatar"] * {
    color: $on_primary !important;
    fill: $on_primary !important;
}

div[data-baseweb="popover"], div[data-baseweb="popover"] > div,
div[data-baseweb="popover"] div, div[data-baseweb="popover"] ul,
div[data-baseweb="popover"] li, ul[data-baseweb="menu"], ul[role="listbox"],
[data-testid="stSelectboxVirtualDropdown"], [data-testid="stSelectboxVirtualDropdown"] * {
    background-color: $secondary_bg !important;
}
div[data-baseweb="popover"] > div, ul[role="listbox"] {
    border: 1px solid $border !important;
    border-radius: 8px;
}
div[data-baseweb="popover"] *:not(svg):not(path), ul[role="listbox"] *,
[data-testid="stSelectboxVirtualDropdown"] * {
    color: $text !important;
    -webkit-text-fill-color: $text !important;
}
div[data-baseweb="popover"] svg { fill: $text !important; }
div[data-baseweb="popover"] li:hover, div[data-baseweb="popover"] li:hover *,
div[data-baseweb="popover"] li[aria-selected="true"], div[data-baseweb="popover"] li[aria-selected="true"] *,
div[data-baseweb="popover"] li[data-highlighted="true"], div[data-baseweb="popover"] li[data-highlighted="true"] *,
ul[role="listbox"] li:hover, ul[role="listbox"] li:hover *,
ul[role="listbox"] li[aria-selected="true"], ul[role="listbox"] li[aria-selected="true"] *,
[data-testid="stSelectboxVirtualDropdown"] li:hover, [data-testid="stSelectboxVirtualDropdown"] li:hover *,
[data-testid="stSelectboxVirtualDropdown"] li[aria-selected="true"],
[data-testid="stSelectboxVirtualDropdown"] li[aria-selected="true"] * {
    background-color: $primary !important;
    color: $on_primary !important;
    -webkit-text-fill-color: $on_primary !important;
}
div[data-baseweb="calendar"], div[data-baseweb="calendar"] * {
    background-color: $secondary_bg !important;
    color: $text !important;
}
div[data-baseweb="calendar"] [aria-selected="true"],
div[data-baseweb="calendar"] [aria-selected="true"] * {
    background-color: $primary !important;
    color: $on_primary !important;
}
div[data-baseweb="tooltip"], div[data-baseweb="tooltip"] *, [data-testid="stTooltipContent"] {
    background-color: $secondary_bg !important;
    color: $text !important;
}

span[data-baseweb="tag"] {
    background-color: $primary !important;
    border-radius: 6px;
}
span[data-baseweb="tag"], span[data-baseweb="tag"] * {
    color: $on_primary !important;
    -webkit-text-fill-color: $on_primary !important;
}
span[data-baseweb="tag"] svg { fill: $on_primary !important; }

label[data-baseweb="checkbox"] > span:first-child,
label[data-baseweb="radio"] > div:first-child {
    border-color: $primary !important;
    background-color: $secondary_bg !important;
}
label[data-baseweb="checkbox"] input:checked + div,
label[data-baseweb="checkbox"] [aria-checked="true"],
label[data-baseweb="radio"] input:checked + div,
div[data-testid="stToggle"] [role="checkbox"][aria-checked="true"] {
    background-color: $primary !important;
    border-color: $primary !important;
}
div[data-testid="stToggle"] [role="checkbox"][aria-checked="false"] {
    background-color: $border !important;
}

div[data-testid="stSlider"] div[role="slider"] {
    background-color: $primary !important;
    border-color: $primary !important;
    box-shadow: 0 0 8px $primary;
}
div[data-testid="stSlider"] [data-testid="stThumbValue"],
div[data-testid="stSlider"] [data-testid="stTickBarMin"],
div[data-testid="stSlider"] [data-testid="stTickBarMax"] {
    color: $text !important;
    background-color: transparent !important;
}
div[data-testid="stSlider"] div[data-baseweb="slider"] > div > div:first-child {
    background: $border !important;
}

.stProgress > div > div > div { background-color: $border !important; }
.stProgress > div > div > div > div { background-color: $primary !important; }
[data-testid="stSpinner"] * { color: $text !important; }

button[data-baseweb="tab"] {
    background-color: transparent !important;
}
button[data-baseweb="tab"], button[data-baseweb="tab"] * { color: $muted !important; }
button[data-baseweb="tab"]:hover, button[data-baseweb="tab"]:hover * { color: $accent !important; }
button[data-baseweb="tab"][aria-selected="true"],
button[data-baseweb="tab"][aria-selected="true"] * {
    color: $primary !important;
}
div[data-baseweb="tab-highlight"] { background-color: $primary !important; }
div[data-baseweb="tab-border"] { background-color: $border !important; }
div[data-baseweb="tab-list"], div[data-baseweb="tab-panel"] { background-color: transparent !important; }

div[data-testid="stExpander"], div[data-testid="stExpander"] details {
    background-color: $secondary_bg !important;
    border: 1px solid $border !important;
    border-radius: 10px;
}
div[data-testid="stExpander"] summary, div[data-testid="stExpander"] summary * {
    background-color: transparent !important;
    color: $text !important;
}
div[data-testid="stExpander"] summary:hover, div[data-testid="stExpander"] summary:hover * {
    color: $primary !important;
}
div[data-testid="stExpander"] svg { fill: $text !important; }

div[data-testid="stDataFrame"], div[data-testid="stTable"], div[data-testid="stDataFrameResizable"] {
    border: 1.5px solid $border !important;
    border-radius: 10px;
    overflow: hidden;
}
div[data-testid="stTable"] table, div[data-testid="stTable"] th, div[data-testid="stTable"] td {
    background-color: $secondary_bg !important;
    color: $text !important;
    border-color: $border !important;
}
div[data-testid="stTable"] th { color: $primary !important; }

div[data-testid="stAlert"] {
    background-color: $secondary_bg !important;
    border: 1px solid $border !important;
    border-left: 4px solid $accent !important;
    border-radius: 8px;
}
div[data-testid="stAlert"] * { color: $text !important; }

div[data-testid="stCode"], div[data-testid="stCode"] pre, [data-testid="stCodeBlock"],
[data-testid="stCodeBlock"] pre, .stCodeBlock, pre {
    background-color: $secondary_bg !important;
    border-radius: 8px;
}
pre, pre code { color: $text !important; }
.stApp :not(pre) > code {
    background-color: $secondary_bg !important;
    color: $accent !important;
    border: 1px solid $border;
    border-radius: 6px;
    padding: 1px 6px;
}
[data-testid="stJson"], [data-testid="stJson"] * {
    background-color: $secondary_bg !important;
    color: $text !important;
}

section[data-testid="stFileUploaderDropzone"], [data-testid="stFileUploaderDropzone"] {
    background-color: $secondary_bg !important;
    border: 1.5px dashed $border !important;
    border-radius: 10px;
}
[data-testid="stFileUploaderDropzone"] *, [data-testid="stFileUploaderFile"] * {
    color: $muted !important;
}
[data-testid="stFileUploaderDropzone"] button {
    background-color: $secondary_bg !important;
    border: 1.5px solid $primary !important;
}
[data-testid="stFileUploaderDropzone"] button * { color: $text !important; }
[data-testid="stFileUploaderDropzone"]:hover { border-color: $primary !important; }

div[data-testid="stForm"], div[data-testid="stVerticalBlockBorderWrapper"]:has(> div > div[data-testid="stForm"]) {
    background-color: $secondary_bg !important;
    border: 1px solid $border !important;
    border-radius: 10px;
}
div[data-testid="stVerticalBlockBorderWrapper"] { border-color: $border !important; }

div[role="dialog"], [data-testid="stDialog"] > div, [data-testid="stModal"] > div {
    background-color: $secondary_bg !important;
    color: $text !important;
    border: 1px solid $border !important;
}
div[role="dialog"] *:not(svg):not(path):not(button):not(button *) { color: $text !important; }
[data-testid="stToast"], [data-testid="stToast"] * {
    background-color: $secondary_bg !important;
    color: $text !important;
}
[data-testid="stStatus"], [data-testid="stStatusWidget"] {
    background-color: $secondary_bg !important;
    border: 1px solid $border !important;
    border-radius: 10px;
}
[data-testid="stStatus"] *, [data-testid="stStatusWidget"] * { color: $text !important; }

html body .stApp [data-testid="stTextInputRootElement"],
html body .stApp [data-testid="stNumberInputContainer"],
html body .stApp [data-testid="stTextArea"] > div,
html body .stApp div[data-baseweb="input"],
html body .stApp div[data-baseweb="base-input"],
html body .stApp div[data-baseweb="textarea"],
html body .stApp div[data-baseweb="select"] > div {
    background-color: $secondary_bg !important;
    background-image: none !important;
    box-shadow: none !important;
}
html body .stApp div[data-baseweb="input"],
html body .stApp div[data-baseweb="textarea"],
html body .stApp div[data-baseweb="select"] > div {
    border: 1.5px solid $border !important;
    border-radius: 8px !important;
}
html body .stApp div[data-baseweb="base-input"] { border: none !important; }
html body .stApp div[data-baseweb="input"]:focus-within,
html body .stApp div[data-baseweb="textarea"]:focus-within,
html body .stApp div[data-baseweb="select"]:focus-within > div {
    border-color: $primary !important;
    box-shadow: 0 0 8px $primary !important;
}
html body .stApp input:not([type="checkbox"]):not([type="radio"]):not([type="range"]),
html body .stApp textarea, html body .stApp select {
    background-color: $secondary_bg !important;
    color: $text !important;
    -webkit-text-fill-color: $text !important;
}
html body .stApp input::placeholder, html body .stApp textarea::placeholder {
    color: $muted !important;
    -webkit-text-fill-color: $muted !important;
    opacity: 1 !important;
}
html body .stApp section[data-testid="stSidebar"] div[data-baseweb="input"],
html body .stApp section[data-testid="stSidebar"] div[data-baseweb="base-input"],
html body .stApp section[data-testid="stSidebar"] div[data-baseweb="textarea"],
html body .stApp section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background-color: $bg !important;
}
html body .stApp section[data-testid="stSidebar"] input:not([type="checkbox"]):not([type="radio"]):not([type="range"]),
html body .stApp section[data-testid="stSidebar"] textarea,
html body .stApp section[data-testid="stSidebar"] select {
    background-color: $bg !important;
}
</style>
""")


def _on_color(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#0b0b0b" if (0.299 * r + 0.587 * g + 0.114 * b) / 255 > 0.58 else "#ffffff"


def _ensure_theme() -> str:
    if st.session_state.get("current_theme") not in THEMES:
        st.session_state.current_theme = DEFAULT_THEME
    return st.session_state.current_theme


def get_theme() -> dict:
    return THEMES[_ensure_theme()]


def apply_current_theme():
    """Injects theme CSS based on the theme stored in session_state."""
    t = get_theme()
    css = CSS_TEMPLATE.substitute(**t, on_primary=_on_color(t["primary"]))
    st.markdown(css, unsafe_allow_html=True)


def theme_selector(container=None, label: str = "Theme"):
    """Renders a theme picker (sidebar by default) and applies the choice."""
    target = container if container is not None else st.sidebar
    names = list(THEMES)
    current = _ensure_theme()
    choice = target.selectbox(label, names, index=names.index(current), key="_theme_selector")
    if choice != current:
        st.session_state.current_theme = choice
        st.rerun()


def config_toml(name: str = None) -> str:
    """Returns .streamlit/config.toml text for a theme (styles canvas widgets like st.dataframe)."""
    t = THEMES[name or DEFAULT_THEME]
    return (
        "[theme]\n"
        f'base = "{t["mode"]}"\n'
        f'primaryColor = "{t["primary"]}"\n'
        f'backgroundColor = "{t["bg"]}"\n'
        f'secondaryBackgroundColor = "{t["secondary_bg"]}"\n'
        f'textColor = "{t["text"]}"\n'
    )


def write_streamlit_config(name: str = None, path: str = ".streamlit/config.toml"):
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(config_toml(name))

