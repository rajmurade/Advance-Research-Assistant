import json
import os
from datetime import datetime
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
load_dotenv()
# pyrefly: ignore [missing-import]
import streamlit as st
# pyrefly: ignore [missing-import]
from src.models import CompanyInfo

# Configure page settings
st.set_page_config(
    page_title="ERA - Developer Tools Research Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling (Linear / Vercel / GitHub minimalist monochrome aesthetic)
CUSTOM_CSS = """
<style>
    /* Hide Streamlit header, footer, and default chrome */
    #MainMenu, header, footer {visibility: hidden;}
    
    /* Global styling */
    .stApp {
        background-color: #161616;
        color: #e5e5e5;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    /* Main container constraint */
    .main .block-container {
        max-width: 900px;
        padding-top: 3.5rem;
        padding-bottom: 4rem;
        padding-left: 2rem;
        padding-right: 2rem;
        margin: 0 auto;
    }

    /* Typography */
    .app-title {
        font-size: 32px;
        font-weight: 600;
        color: #FFFFFF;
        letter-spacing: -0.02em;
        margin-bottom: 4px;
        line-height: 1.1;
    }

    .app-subtitle {
        font-size: 15px;
        color: #888888;
        font-weight: 400;
        margin-bottom: 28px;
    }

    /* Search row customization */
    div[data-testid="stTextInput"] > div > div > input {
        background-color: #212121 !important;
        border: 1px solid #2e2e2e !important;
        color: #e5e5e5 !important;
        border-radius: 6px !important;
        padding: 10px 14px !important;
        font-size: 14px !important;
    }
    div[data-testid="stTextInput"] > div > div > input:focus {
        border-color: #444444 !important;
        box-shadow: none !important;
    }

    /* Search & Action button styling */
    div.stButton > button {
        border-radius: 6px !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        transition: opacity 0.15s ease;
    }

    /* Progress & Status */
    .progress-track {
        width: 100%;
        height: 2px;
        background-color: #242424;
        margin-top: 14px;
        margin-bottom: 10px;
        position: relative;
    }
    .progress-fill {
        height: 2px;
        background-color: #888888;
    }
    .status-text {
        color: #777777;
        font-size: 13px;
        font-family: monospace;
        margin-bottom: 36px;
    }

    /* Company entries */
    .company-entry {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        padding-bottom: 24px;
        margin-bottom: 24px;
        border-bottom: 1px solid #222222;
    }

    .company-left {
        flex: 1 1 55%;
        padding-right: 32px;
    }

    .company-name {
        font-size: 18px;
        font-weight: 600;
        color: #FFFFFF;
        display: inline-block;
        margin-right: 8px;
    }

    .company-url {
        font-size: 13px;
        color: #666666;
        font-family: monospace;
        vertical-align: middle;
        text-decoration: none;
    }

    .company-desc {
        color: #aaaaaa;
        font-size: 14px;
        margin-top: 6px;
        margin-bottom: 14px;
        line-height: 1.4;
    }

    .pill-group {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
    }

    .pill-chip {
        display: inline-flex;
        align-items: center;
        border: 1px solid #333333;
        border-radius: 100px;
        padding: 3px 12px;
        font-size: 12px;
        color: #cccccc;
        background-color: transparent;
        letter-spacing: 0.01em;
    }

    .company-right {
        flex: 1 1 45%;
        font-size: 13px;
        line-height: 1.8;
    }

    .meta-row {
        color: #888888;
    }
    .meta-label {
        font-weight: 600;
        color: #dddddd;
    }
    .meta-value {
        color: #999999;
    }

    /* Recommendation Callout */
    .recommendation-card {
        border-left: 2px solid #D8D0C0;
        padding: 8px 18px;
        margin-top: 24px;
        margin-bottom: 28px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .recommendation-title {
        font-size: 15px;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 6px;
    }

    .recommendation-body {
        font-size: 14px;
        color: #b0b0b0;
        line-height: 1.5;
    }

    .spark-icon {
        color: #555555;
        font-size: 26px;
        margin-left: 24px;
        flex-shrink: 0;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Search history helpers
HISTORY_FILE = os.path.join(os.path.dirname(__file__), "search_history.json")


def load_search_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(e)
    return []


def save_search_history(history):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(e)


# App Header
st.markdown('<div class="app-title">ERA</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">AI Research Assistant for Developers</div>', unsafe_allow_html=True)

# Search Bar and Research Button
col_search, col_btn = st.columns([5.2, 1], gap="small")
with col_search:
    query = st.text_input(
        "Search Query",
        placeholder="Compare authentication providers...",
        label_visibility="collapsed"
    )

with col_btn:
    st.markdown("""
    <style>
    div[data-testid="stColumn"]:nth-child(2) button {
        background-color: #ECE7DF !important;
        color: #161616 !important;
        border: none !important;
        height: 42px !important;
        width: 100% !important;
    }
    div[data-testid="stColumn"]:nth-child(2) button:hover {
        background-color: #dfdad1 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    research_clicked = st.button("Research", use_container_width=True)

# Initialize session state
if "results" not in st.session_state:
    st.session_state.results = None
if "recommendation" not in st.session_state:
    st.session_state.recommendation = None
if "running" not in st.session_state:
    st.session_state.running = False
if "current_query" not in st.session_state:
    st.session_state.current_query = ""
if "search_history" not in st.session_state:
    st.session_state.search_history = load_search_history()

# Search History Sidebar
with st.sidebar:
    st.markdown("### Search History")
    if st.session_state.search_history:
        for idx, entry in enumerate(st.session_state.search_history):
            label = entry.get("query", "Unknown")
            ts = entry.get("timestamp", "")
            if st.button(
                f"{label}  ·  {ts}",
                key=f"history_{idx}",
                use_container_width=True,
            ):
                loaded_companies = []
                for c in entry.get("companies", []):
                    try:
                        loaded_companies.append(CompanyInfo(**c))
                    except Exception:
                        continue
                st.session_state.current_query = entry.get("query", "")
                st.session_state.results = loaded_companies
                st.session_state.recommendation = entry.get("recommendation", "")
                st.rerun()
    else:
        st.caption("No searches yet.")

    if st.button("Clear History", key="btn_clear_history", use_container_width=True):
        st.session_state.search_history = []
        save_search_history([])
        st.rerun()

# Progress indicator placeholder
progress_placeholder = st.empty()

# Run agent when Research clicked
if research_clicked and query:
    st.session_state.running = True
    st.session_state.current_query = query

    steps = [
        (10, "— Finding articles..."),
        (40, "— Researching tools..."),
        (80, "— Analyzing APIs..."),
        (95, "— Generating recommendation..."),
    ]

    for pct, label in steps:
        progress_placeholder.markdown(f"""
        <div class="progress-track">
            <div class="progress-fill" style="width:{pct}%"></div>
        </div>
        <div class="status-text">{label}</div>
        """, unsafe_allow_html=True)

    try:
        # pyrefly: ignore [missing-import]
        from src.workflow import Workflow
        workflow = Workflow()
        result = workflow.run(query)
        st.session_state.results = result.companies
        st.session_state.recommendation = result.analysis
    except Exception as e:
        st.error(f"Error: {e}")

    if st.session_state.results:
        entry = {
            "query": st.session_state.current_query,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "companies": [c.model_dump() for c in st.session_state.results],
            "recommendation": st.session_state.recommendation,
        }
        st.session_state.search_history.insert(0, entry)
        st.session_state.search_history = st.session_state.search_history[:10]
        save_search_history(st.session_state.search_history)

    progress_placeholder.markdown(f"""
    <div class="progress-track">
        <div class="progress-fill" style="width:100%"></div>
    </div>
    <div class="status-text">— Done.</div>
    """, unsafe_allow_html=True)
    st.session_state.running = False

elif not st.session_state.results:
    progress_placeholder.markdown("""
    <div class="progress-track">
        <div class="progress-fill" style="width:0%"></div>
    </div>
    <div class="status-text">— Enter a query and click Research.</div>
    """, unsafe_allow_html=True)

# Build companies list from real data or empty
companies = []
if st.session_state.results:
    for c in st.session_state.results:
        tech = " • ".join(c.tech_stack) if isinstance(c.tech_stack, list) else c.tech_stack
        langs = " • ".join(c.language_support) if isinstance(c.language_support, list) else c.language_support
        integrations = " • ".join(c.integration_capabilities) if isinstance(c.integration_capabilities, list) else c.integration_capabilities
        companies.append({
            "name": c.name,
            "url": c.website,
            "desc": c.description,
            "tags": [
                c.pricing_model,
                "Open Source ✓" if c.is_open_source else "Open Source ✕",
                "API ✓" if c.api_available else "API ✗"
            ],
            "tech_stack": tech,
            "languages": langs,
            "integrations": integrations
        })

recommendation_text = st.session_state.recommendation or ""

# Render company entries
for c in companies:
    tag_html = "".join([f'<span class="pill-chip">{t}</span>' for t in c["tags"]])
    entry_html = f"""
    <div class="company-entry">
        <div class="company-left">
            <div>
                <span class="company-name">{c["name"]}</span>
                <span class="company-url">{c["url"]}</span>
            </div>
            <div class="company-desc">{c["desc"] if c["desc"] not in ("Failed", "None") else ""}</div>
            <div class="pill-group">{tag_html}</div>
        </div>
        <div class="company-right">
            <div class="meta-row"><span class="meta-label">Tech Stack:</span> <span class="meta-value">{c["tech_stack"]}</span></div>
            <div class="meta-row"><span class="meta-label">Languages:</span> <span class="meta-value">{c["languages"]}</span></div>
            <div class="meta-row"><span class="meta-label">Integrations:</span> <span class="meta-value">{c["integrations"]}</span></div>
        </div>
    </div>
    """
    st.markdown(entry_html, unsafe_allow_html=True)

# Recommendation Section
if recommendation_text:
    st.markdown(f"""
    <div class="recommendation-card">
        <div>
            <div class="recommendation-title">Recommendation</div>
            <div class="recommendation-body">{recommendation_text}</div>
        </div>
        <div class="spark-icon">✦</div>
    </div>
    """, unsafe_allow_html=True)

# Export Markdown
col_empty, col_export = st.columns([4.8, 1.2])
with col_export:
    st.markdown("""
    <style>
    div[data-testid="stColumn"]:nth-child(2) div[data-testid="stButton"] button {
        background-color: #1f1f1f !important;
        color: #999999 !important;
        border: 1px solid #2d2d2d !important;
        font-size: 13px !important;
    }
    div[data-testid="stColumn"]:nth-child(2) div[data-testid="stButton"] button:hover {
        color: #ffffff !important;
        border-color: #444444 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    if st.session_state.results and companies:
        md = f"# ERA Research Report\n\n**Query:** {st.session_state.current_query}\n\n"
        for c in companies:
            md += f"## {c['name']}\n"
            md += f"- **URL:** {c['url']}\n"
            md += f"- **Description:** {c['desc']}\n"
            md += f"- **Tech Stack:** {c['tech_stack']}\n"
            md += f"- **Languages:** {c['languages']}\n"
            md += f"- **Integrations:** {c['integrations']}\n\n"
        md += f"## Recommendation\n{recommendation_text}"
        st.download_button(
            "Export Markdown",
            md,
            file_name="era_report.md",
            mime="text/markdown",
            use_container_width=True,
            key="btn_export"
        )
    else:
        st.button("Export Markdown", key="btn_export", use_container_width=True)