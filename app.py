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

# Custom Styling (JetBrains Mono terminal-inspired dark design)
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Hide Streamlit header, footer, and default chrome */
    #MainMenu, header[data-testid="stHeader"], footer, .stAppDeployButton {visibility: hidden;}

    /* Global styling */
    .stApp {
        background-color: #131313;
        color: #e5e2e1;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    /* Main container constraint */
    .main .block-container {
        max-width: 880px;
        padding-top: 2.25rem;
        padding-bottom: 3rem;
        padding-left: 2rem;
        padding-right: 2rem;
        margin: 0 auto;
    }

    /* ===== Cockpit Header ===== */
    .era-header {
        background-color: #0e0e0e;
        border: 1px solid #2a2a2a;
        border-radius: 2px;
        padding: 24px;
        margin-bottom: 24px;
    }
    .era-header-row {
        display: flex;
        flex-wrap: wrap;
        align-items: flex-start;
        justify-content: space-between;
        gap: 16px;
    }
    .era-brand {
        display: flex;
        align-items: baseline;
        gap: 12px;
    }
    .era-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 32px;
        font-weight: 600;
        letter-spacing: 0.12em;
        color: #e5e2e1;
        line-height: 1;
    }
    .era-engine {
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #c9a96e;
    }
    .era-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 12px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #6b6560;
        margin-top: 6px;
    }
    .era-meta {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        text-align: right;
        line-height: 1.7;
    }
    .era-meta-primary { color: #c9a96e; letter-spacing: 0.06em; }
    .era-meta-muted { color: #6b6560; }
    .era-header-divider {
        height: 1px;
        background-color: #c9a96e;
        opacity: 0.8;
        margin: 18px 0;
    }

    /* ===== Search row ===== */
    div[data-testid="stTextInput"] > div > div > input {
        background-color: #1c1b1b !important;
        border: 1px solid #2a2a2a !important;
        color: #e5e2e1 !important;
        border-radius: 2px !important;
        padding: 12px 14px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 13px !important;
    }
    div[data-testid="stTextInput"] > div > div > input:focus {
        border-color: #c9a96e !important;
        box-shadow: none !important;
    }

    /* Buttons */
    div.stButton > button {
        border-radius: 2px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        letter-spacing: 0.06em !important;
        transition: all 0.15s ease;
    }

    /* ===== Progress & Status ===== */
    .progress-track {
        height: 4px;
        background-color: #2a2a2a;
        border-radius: 1px;
        position: relative;
    }
    .progress-fill {
        height: 4px;
        background-color: #c9a96e;
        border-radius: 1px;
    }
    .status-text {
        font-family: 'JetBrains Mono', monospace;
        color: #c9a96e;
        font-size: 12px;
        letter-spacing: 0.06em;
        margin-top: 8px;
        margin-bottom: 24px;
    }

    /* ===== Search History expandable drawer ===== */
    div[data-testid="stExpander"] {
        background-color: #0e0e0e !important;
        border: 1px solid #2a2a2a !important;
        border-radius: 2px !important;
        margin-bottom: 24px !important;
        overflow: hidden;
    }
    div[data-testid="stExpander"] summary {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 12px !important;
        letter-spacing: 0.04em !important;
        color: #e5e2e1 !important;
        padding: 14px 16px !important;
    }
    div[data-testid="stExpander"] summary:hover { background-color: #1c1b1b !important; }
    div[data-testid="stExpander"] summary p {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 12px !important;
        letter-spacing: 0.04em !important;
        color: #e5e2e1 !important;
    }
    div[data-testid="stExpander"] div[data-testid="stButton"] > button {
        background: transparent !important;
        border: none !important;
        border-left: 2px solid transparent !important;
        border-radius: 0 !important;
        color: #e5e2e1 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 12px !important;
        text-align: left !important;
        padding: 8px 10px !important;
        width: 100% !important;
    }
    div[data-testid="stExpander"] div[data-testid="stButton"] > button:hover {
        background-color: #201f1f !important;
        border-left-color: #c9a96e !important;
    }
    .era-history-ts {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 11px !important;
        color: #6b6560 !important;
        text-align: right !important;
        white-space: nowrap;
        padding-top: 9px !important;
    }
    .era-history-clear {
        margin-top: 8px;
        border-top: 1px solid #2a2a2a;
        padding-top: 8px;
    }

    /* ===== Recommendation Callout ===== */
    .recommendation-card {
        background-color: #1c1b1b;
        border: 1px solid #2a2a2a;
        border-left: 3px solid #c9a96e;
        border-radius: 2px;
        padding: 24px;
        margin-top: 24px;
        margin-bottom: 32px;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
    }
    .recommendation-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #c9a96e;
        margin-bottom: 12px;
    }
    .recommendation-body {
        font-family: 'Inter', sans-serif;
        font-size: 13px;
        color: #e5e2e1;
        line-height: 1.6;
    }
    .spark-icon {
        color: #c9a96e;
        font-size: 20px;
        margin-left: 24px;
        flex-shrink: 0;
    }

    /* ===== Company entries section ===== */
    .era-company-section {
        background-color: #0e0e0e;
        border: 1px solid #2a2a2a;
        border-radius: 2px;
        margin-bottom: 32px;
        overflow: hidden;
    }
    .era-company-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
        padding: 14px 24px;
        background-color: #1c1b1b;
        border-bottom: 1px solid #2a2a2a;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: #e5e2e1;
    }
    .era-company-criteria {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        font-weight: 400;
        letter-spacing: 0.03em;
        text-transform: none;
        color: #6b6560;
    }
    .company-entry {
        display: flex;
        flex-direction: column;
        gap: 24px;
        padding: 24px;
        border-bottom: 1px solid #2a2a2a;
    }
    .company-entry:last-child { border-bottom: none; }
    @media (min-width: 900px) {
        .company-entry { flex-direction: row; }
    }
    .company-left { flex: 1 1 auto; }
    .company-name {
        font-family: 'JetBrains Mono', monospace;
        font-size: 22px;
        font-weight: 600;
        letter-spacing: -0.01em;
        color: #c9a96e;
        display: inline-block;
        margin-right: 12px;
    }
    .company-url {
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        color: #6b6560;
        text-decoration: none;
        vertical-align: middle;
    }
    .company-url:hover { color: #c9a96e; }
    .company-desc {
        color: #cdc5bf;
        font-size: 13px;
        line-height: 1.6;
        margin: 10px 0 16px;
    }
    .pill-group { display: flex; flex-wrap: wrap; gap: 8px; }
    .pill-chip {
        display: inline-flex;
        align-items: center;
        border: 1px solid rgba(201, 169, 110, 0.6);
        background-color: #1c1b1b;
        color: #e5e2e1;
        border-radius: 2px;
        padding: 3px 10px;
        font-size: 11px;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.02em;
    }
    .company-right {
        flex: 0 0 320px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        line-height: 1.7;
        border-left: 1px solid #2a2a2a;
        padding-left: 24px;
    }
    @media (max-width: 899px) {
        .company-right {
            flex-basis: auto;
            border-left: none;
            border-top: 1px solid #2a2a2a;
            padding-left: 0;
            padding-top: 16px;
        }
    }
    .meta-row { margin-bottom: 16px; }
    .meta-label {
        display: block;
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #6b6560;
        margin-bottom: 4px;
    }
    .meta-value { color: #e5e2e1; }

    /* ===== Footer ===== */
    .era-footer-text {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: #6b6560;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .era-footer-dot { color: #c9a96e; }
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

# App Header
st.markdown("""
<div class="era-header">
    <div class="era-header-row">
        <div>
            <div class="era-brand">
                <span class="era-title">ERA</span>
                <span class="era-engine">[ DEV_SYNTHESIS_ENGINE ]</span>
            </div>
            <div class="era-subtitle">AI Research Assistant for Developers</div>
        </div>
        <div class="era-meta">
            <div class="era-meta-primary">[ CLI.V2.4 // NODE_01 // ONLINE ]</div>
            <div class="era-meta-muted">BUFFER: FLUSHED // LATENCY: LOW</div>
        </div>
    </div>
    <div class="era-header-divider"></div>
</div>
""", unsafe_allow_html=True)

# Search Bar and Research Button
col_search, col_btn = st.columns([5.2, 1], gap="small")
with col_search:
    query = st.text_input(
        "Search Query",
        placeholder="Enter research prompt or stack analysis query...",
        label_visibility="collapsed"
    )

with col_btn:
    st.markdown("""
    <style>
    div[data-testid="stColumn"]:nth-child(2) button {
        background-color: #c9a96e !important;
        color: #131313 !important;
        border: none !important;
        height: 46px !important;
        width: 100% !important;
        letter-spacing: 0.1em !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 600 !important;
        font-size: 12px !important;
        border-radius: 2px !important;
    }
    div[data-testid="stColumn"]:nth-child(2) button:hover {
        background-color: #e6c487 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    research_clicked = st.button("RESEARCH", use_container_width=True)

# Search History
if st.session_state.search_history:
    with st.expander(f"[ SEARCH HISTORY // {len(st.session_state.search_history):02d} CACHED RUNS ]"):
        for idx, entry in enumerate(st.session_state.search_history):
            col1, col2 = st.columns([5, 1])
            with col1:
                if st.button("▸  " + entry["query"], key=f"history_{idx}", use_container_width=True):
                    loaded_companies = []
                    for c in entry.get("companies", []):
                        try:
                            loaded_companies.append(CompanyInfo(**c))
                        except Exception:
                            continue
                    st.session_state.current_query = entry.get("query", "")
                    st.session_state.results = loaded_companies
                    st.session_state.recommendation = entry["recommendation"]
                    st.rerun()
            with col2:
                st.markdown(
                    f'<div class="era-history-ts">{entry.get("timestamp", "")}</div>',
                    unsafe_allow_html=True,
                )
        st.markdown('<div class="era-history-clear"></div>', unsafe_allow_html=True)
        if st.button("[ CLEAR HISTORY ]", key="btn_clear_history"):
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
if companies:
    entries_html = ""
    for c in companies:
        tag_html = "".join([f'<span class="pill-chip">{t}</span>' for t in c["tags"]])
        entries_html += f"""
        <div class="company-entry">
            <div class="company-left">
                <div>
                    <span class="company-name">{c["name"]}</span>
                    <a class="company-url" href="{c["url"]}" target="_blank">{c["url"]}</a>
                </div>
                <div class="company-desc">{c["desc"] if c["desc"] not in ("Failed", "None") else ""}</div>
                <div class="pill-group">{tag_html}</div>
            </div>
            <div class="company-right">
                <div class="meta-row"><span class="meta-label">Tech Stack</span><span class="meta-value">{c["tech_stack"]}</span></div>
                <div class="meta-row"><span class="meta-label">Languages</span><span class="meta-value">{c["languages"]}</span></div>
                <div class="meta-row"><span class="meta-label">Integrations</span><span class="meta-value">{c["integrations"]}</span></div>
            </div>
        </div>
        """
    section_html = f"""
    <div class="era-company-section">
        <div class="era-company-header">
            <span>[ {len(companies):02d} DISCOVERED ENTITIES // PARALLEL AUDIT ]</span>
            <span class="era-company-criteria">CRITERIA: RELIABILITY, DX, PRICING, TECH STACK</span>
        </div>
        {entries_html}
    </div>
    """
    st.markdown(section_html, unsafe_allow_html=True)

# Recommendation Section
if recommendation_text:
    st.markdown(f"""
    <div class="recommendation-card">
        <div>
            <div class="recommendation-title">// Synthesis &amp; Architectural Recommendation</div>
            <div class="recommendation-body">{recommendation_text}</div>
        </div>
        <div class="spark-icon">✦</div>
    </div>
    """, unsafe_allow_html=True)

# Export Markdown
col_empty, col_export = st.columns([3.2, 1])
with col_empty:
    st.markdown(
        '<div class="era-footer-text"><span class="era-footer-dot">●</span>&nbsp;&nbsp;'
        f'ERA Research Agent — {len(companies)} entities indexed // source verified</div>',
        unsafe_allow_html=True,
    )
with col_export:
    st.markdown("""
    <style>
    div[data-testid="stColumn"]:nth-child(2) div[data-testid="stButton"] button,
    div[data-testid="stColumn"]:nth-child(2) div[data-testid="stDownloadButton"] button {
        background-color: #1c1b1b !important;
        color: #999 !important;
        border: 1px solid #2d2d2d !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 12px !important;
        letter-spacing: 0.06em !important;
        padding: 12px 16px !important;
        border-radius: 2px !important;
        width: 100% !important;
    }
    div[data-testid="stColumn"]:nth-child(2) div[data-testid="stButton"] button:hover,
    div[data-testid="stColumn"]:nth-child(2) div[data-testid="stDownloadButton"] button:hover {
        color: #e5e2e1 !important;
        border-color: #c9a96e !important;
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
            "[ EXPORT.MD ]",
            md,
            file_name="era_report.md",
            mime="text/markdown",
            use_container_width=True,
            key="btn_export"
        )
    else:
        st.button("[ EXPORT.MD ]", key="btn_export", use_container_width=True)