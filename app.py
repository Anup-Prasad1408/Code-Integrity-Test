"""Code Integrity Auditor — dashboard-only Day 1 starter application.

All analysis capabilities are intentionally placeholders in this release.
The dashboard uses clearly labelled zero-state data; it does not claim to
analyze, score, classify, or store source-code submissions yet.
"""

from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="Code Integrity Auditor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Theme and component styling
# ---------------------------------------------------------------------------
CUSTOM_CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');
:root {
  --cia-bg: #080d17;
  --cia-panel: #101827;
  --cia-panel-2: #131f30;
  --cia-border: rgba(148, 163, 184, .14);
  --cia-text: #eef4fb;
  --cia-muted: #91a1b5;
  --cia-accent: #4de0c1;
  --cia-blue: #7da9ff;
}
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: radial-gradient(ellipse at 78% -12%, rgba(38, 119, 130, .18), transparent 34%), var(--cia-bg); color: var(--cia-text); }
.block-container { max-width: 1500px; padding-top: 2.0rem; padding-bottom: 3rem; }
[data-testid="stHeader"] { background: rgba(8,13,23,.72); }
[data-testid="stSidebar"] { background: #0b1220; border-right: 1px solid var(--cia-border); }
[data-testid="stSidebar"] > div:first-child { padding-top: 1.2rem; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: var(--cia-muted); }
[data-testid="stSidebar"] [data-testid="stRadio"] label { border-radius: 10px; padding: 7px 10px; }
[data-testid="stSidebar"] [data-testid="stRadio"] label p { font-size: .92rem; font-weight: 600; }
.stButton > button { border: 1px solid rgba(77,224,193,.34); background: linear-gradient(135deg, rgba(77,224,193,.16), rgba(77,224,193,.07)); color: #dffff7; border-radius: 10px; min-height: 2.65rem; font-weight: 700; transition: .18s ease; }
.stButton > button:hover { border-color: var(--cia-accent); color: white; transform: translateY(-1px); }
[data-testid="stMetric"] { background: transparent; }
hr { border-color: var(--cia-border); }
.eyebrow { color: var(--cia-accent); font: 500 .72rem 'DM Mono', monospace; letter-spacing: .16em; text-transform: uppercase; margin-bottom: .55rem; }
.page-title { font: 700 clamp(2rem, 4vw, 3.05rem) 'Space Grotesk', sans-serif; letter-spacing: -.055em; line-height: 1.06; color: #f3f7fc; margin: 0; }
.page-subtitle { color: var(--cia-muted); font-size: .98rem; margin-top: .65rem; max-width: 760px; line-height: 1.6; }
.top-meta { display: flex; justify-content: flex-end; gap: 8px; align-items: center; padding-top: .6rem; flex-wrap: wrap; }
.pill { display: inline-flex; align-items: center; gap: 7px; border: 1px solid var(--cia-border); background: rgba(16,24,39,.75); border-radius: 999px; padding: 7px 11px; color: #c5d2e1; font: 500 .7rem 'DM Mono', monospace; letter-spacing: .04em; white-space: nowrap; }
.pill-dot { width: 7px; height: 7px; border-radius: 50%; background: #f2bb66; box-shadow: 0 0 10px rgba(242,187,102,.45); }
.hero { border: 1px solid rgba(77,224,193,.22); background: radial-gradient(circle at 90% 10%, rgba(77,224,193,.13), transparent 30%), linear-gradient(115deg, #142338, #101a2a 68%, #10232b); border-radius: 18px; padding: 25px 27px; position: relative; overflow: hidden; }
.hero-kicker { color: var(--cia-accent); font: 500 .68rem 'DM Mono', monospace; letter-spacing: .15em; text-transform: uppercase; }
.hero-title { color: #f4f8fc; font: 700 1.45rem 'Space Grotesk', sans-serif; margin: 9px 0 6px; }
.hero-copy { color: #a8b8c9; font-size: .9rem; max-width: 720px; line-height: 1.6; margin: 0; }
.hero-orb { position: absolute; right: 7%; top: 17%; width: 132px; height: 132px; border-radius: 50%; border: 1px solid rgba(77,224,193,.25); box-shadow: 0 0 0 18px rgba(77,224,193,.035), 0 0 0 38px rgba(77,224,193,.025); display:flex; align-items:center; justify-content:center; color: var(--cia-accent); font-size: 2.7rem; opacity: .8; }
.section-head { display:flex; justify-content:space-between; align-items:end; gap: 12px; margin: 1.65rem 0 .8rem; }
.section-title { color:#eaf1f8; font: 600 1.12rem 'Space Grotesk', sans-serif; margin:0; }
.section-note { color:var(--cia-muted); font-size:.77rem; }
.metric-card { background: linear-gradient(145deg, rgba(19,31,48,.98), rgba(13,22,36,.98)); border: 1px solid var(--cia-border); border-radius: 15px; padding: 17px 18px 16px; min-height: 132px; }
.metric-label { color: #9bacc0; font-size: .78rem; font-weight: 600; }
.metric-value { color: #f1f6fc; font: 700 2rem 'Space Grotesk', sans-serif; margin: 8px 0 5px; letter-spacing: -.04em; }
.metric-foot { color: #74869b; font: 400 .68rem 'DM Mono', monospace; }
.metric-icon { float:right; font-size:1.12rem; color:var(--cia-accent); background:rgba(77,224,193,.09); width:32px;height:32px;border-radius:9px;display:flex;align-items:center;justify-content:center; }
.panel { background: rgba(16,24,39,.82); border: 1px solid var(--cia-border); border-radius: 15px; padding: 18px; height: 100%; }
.panel-title { color:#eaf1f8; font:600 .98rem 'Space Grotesk',sans-serif; margin-bottom:5px; }
.panel-sub { color:#8293a8; font-size:.75rem; line-height:1.5; }
.engine-row { display:flex; align-items:center; justify-content:space-between; padding: 12px 0; border-bottom: 1px solid rgba(148,163,184,.10); gap: 10px; }
.engine-row:last-child { border-bottom:0; padding-bottom:0; }
.engine-name { color:#dbe6f1; font-size:.83rem; font-weight:600; }
.engine-detail { color:#75879d; font-size:.7rem; margin-top:3px; }
.coming { color:#efc27a; border:1px solid rgba(239,194,122,.22); background:rgba(239,194,122,.07); border-radius:999px; padding:4px 8px; font:500 .62rem 'DM Mono',monospace; white-space:nowrap; }
.status-line { display:flex; align-items:center; gap:9px; color:#a9b8c9; font-size:.8rem; padding:8px 0; }
.status-check { width:7px;height:7px;border-radius:50%;background:#4de0c1; }
.status-pending { width:7px;height:7px;border-radius:50%;background:#d7a95e; }
.empty-state { border:1px dashed rgba(148,163,184,.22); border-radius:12px; padding:22px; text-align:center; color:#8192a7; background:rgba(8,13,23,.28); }
.empty-icon { font-size:1.55rem; margin-bottom:7px; }
.empty-title { color:#dce7f2; font-weight:700; font-size:.87rem; margin-bottom:4px; }
.empty-copy { color:#8192a7; font-size:.75rem; line-height:1.5; }
.module-card { border:1px solid var(--cia-border); background:linear-gradient(145deg,rgba(19,31,48,.88),rgba(12,20,33,.9)); border-radius:14px; padding:15px; min-height:145px; }
.module-icon { color:var(--cia-accent); font-size:1.15rem; margin-bottom:12px; }
.module-title { color:#e5edf6; font-weight:700; font-size:.85rem; margin-bottom:5px; }
.module-copy { color:#8293a8; font-size:.72rem; line-height:1.5; min-height:34px; }
.footer { color:#687b91; font:400 .66rem 'DM Mono',monospace; text-align:center; padding-top:24px; }
.coming-page { border:1px solid rgba(239,194,122,.2); background:linear-gradient(140deg,rgba(34,32,29,.7),rgba(16,24,39,.86)); border-radius:18px; padding:30px; margin-top:15px; }
.coming-hero { font:700 1.7rem 'Space Grotesk',sans-serif; color:#f0f4f8; margin:9px 0; }
code { color:#a5f2df !important; }
@media (max-width: 800px) { .hero-orb { display:none; } .top-meta { justify-content:flex-start; padding-top:0; margin-top:12px; } .block-container { padding-left:1rem; padding-right:1rem; } }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Reusable UI helpers
# ---------------------------------------------------------------------------
def section_heading(title: str, note: str = "") -> None:
    st.markdown(
        f'<div class="section-head"><div class="section-title">{title}</div>'
        f'<div class="section-note">{note}</div></div>',
        unsafe_allow_html=True,
    )


def metric_card(icon: str, label: str, value: str, foot: str) -> None:
    st.markdown(
        f'''<div class="metric-card">
          <div class="metric-icon">{icon}</div>
          <div class="metric-label">{label}</div>
          <div class="metric-value">{value}</div>
          <div class="metric-foot">{foot}</div>
        </div>''',
        unsafe_allow_html=True,
    )


def engine_row(name: str, detail: str) -> None:
    st.markdown(
        f'''<div class="engine-row"><div><div class="engine-name">{name}</div>
        <div class="engine-detail">{detail}</div></div><span class="coming">COMING SOON</span></div>''',
        unsafe_allow_html=True,
    )


def show_coming_soon(page_name: str, description: str, planned_step: str) -> None:
    st.markdown('<div class="eyebrow">MODULE ROADMAP</div>', unsafe_allow_html=True)
    st.markdown(f'<h1 class="page-title">{page_name}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="page-subtitle">{description}</p>', unsafe_allow_html=True)
    st.markdown(
        f'''<div class="coming-page">
          <div class="coming">COMING SOON</div>
          <div class="coming-hero">This module is not active yet.</div>
          <div class="page-subtitle" style="margin-top:0">We are building the platform in clear, testable stages. This section will become available when its implementation is ready.</div>
          <div style="height:16px"></div>
          <div class="hero-kicker">PLANNED NEXT STEP</div>
          <div style="color:#dbe6f1;font-weight:600;margin-top:7px">{planned_step}</div>
        </div>''',
        unsafe_allow_html=True,
    )
    st.info("Coming Soon — this feature is intentionally not implemented in the Day 1 dashboard.", icon="🚧")


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        '''<div style="display:flex;align-items:center;gap:11px;padding:4px 2px 18px">
          <div style="width:42px;height:42px;border-radius:13px;background:linear-gradient(145deg,#174d50,#132d3d);border:1px solid rgba(77,224,193,.35);display:flex;align-items:center;justify-content:center;font-size:21px">🛡️</div>
          <div><div style="font:700 1rem 'Space Grotesk',sans-serif;color:#eef5fb">CODE INTEGRITY</div>
          <div style="font:500 .62rem 'DM Mono',monospace;color:#7890a5;letter-spacing:.13em">AUDITOR / CIA</div></div>
        </div>''',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="eyebrow">WORKSPACE</div>', unsafe_allow_html=True)
    pages = [
        "◈  Overview",
        "⌁  Code Analysis",
        "⌘  Structural Engine",
        "∿  Stylometry",
        "⟷  Similarity",
        "⬡  Risk Assessment",
        "▤  Reports",
        "⚙  Settings",
    ]
    selected = st.radio("Navigation", pages, index=0, label_visibility="collapsed")
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '''<div style="border:1px solid rgba(148,163,184,.14);background:rgba(16,24,39,.65);border-radius:13px;padding:13px">
          <div class="eyebrow" style="margin-bottom:8px">BUILD STATUS</div>
          <div style="color:#e6eef7;font-size:.82rem;font-weight:700">Day 1 · Foundation</div>
          <div style="color:#8293a8;font-size:.7rem;margin-top:5px;line-height:1.5">Dashboard shell is ready. Analysis engines are planned for upcoming milestones.</div>
          <div style="height:8px"></div>
          <div style="height:4px;border-radius:99px;background:#273648"><div style="width:12%;height:4px;border-radius:99px;background:#4de0c1"></div></div>
          <div style="color:#73869b;font: .62rem 'DM Mono',monospace;margin-top:7px">FOUNDATION PHASE</div>
        </div>''',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="color:#5e7187;font: .61rem \'DM Mono\',monospace;padding:16px 3px 0">VERSION 0.1.0 · PREVIEW</div>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Main dashboard and placeholder sections
# ---------------------------------------------------------------------------
if selected == "◈  Overview":
    top_left, top_right = st.columns([3.2, 1.2])
    with top_left:
        st.markdown('<div class="eyebrow">CODE INTELLIGENCE / CONTROL CENTER</div>', unsafe_allow_html=True)
        st.markdown('<h1 class="page-title">Code Integrity Auditor</h1>', unsafe_allow_html=True)
        st.markdown(
            '<p class="page-subtitle">A unified workspace for exploring source-code structure, statistical patterns, and integrity signals — built one verified module at a time.</p>',
            unsafe_allow_html=True,
        )
    with top_right:
        st.markdown(
            '<div class="top-meta"><span class="pill"><span class="pill-dot"></span> FOUNDATION PHASE</span><span class="pill">v0.1.0</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:23px'></div>", unsafe_allow_html=True)
    st.markdown(
        '''<div class="hero">
          <div class="hero-kicker">YOUR ANALYSIS WORKSPACE</div>
          <div class="hero-title">A clear view of what is built — and what comes next.</div>
          <p class="hero-copy">The Day 1 release establishes the dashboard, project navigation, and module roadmap. Source-code parsing, scoring, AI interpretation, and reporting are deliberately marked as coming soon until each component is implemented and tested.</p>
          <div class="hero-orb">⌘</div>
        </div>''',
        unsafe_allow_html=True,
    )

    section_heading("Platform snapshot", "LIVE DATA WILL APPEAR AFTER ENGINE INTEGRATION")
    metric_cols = st.columns(4, gap="medium")
    with metric_cols[0]: metric_card("◉", "Audits completed", "0", "NO ANALYSIS RUN YET")
    with metric_cols[1]: metric_card("⌗", "Files analyzed", "0", "FILE PROCESSING · COMING SOON")
    with metric_cols[2]: metric_card("⚑", "Risk signals", "—", "RISK ENGINE · COMING SOON")
    with metric_cols[3]: metric_card("⌘", "Languages planned", "03", "PYTHON · C++ · JAVA")

    left, right = st.columns([1.25, 1], gap="large")
    with left:
        section_heading("Engine readiness", "IMPLEMENTATION ROADMAP")
        st.markdown('<div class="panel"><div class="panel-title">Analysis pipeline</div><div class="panel-sub">Each engine will be activated after its logic, tests, and integration are complete.</div>', unsafe_allow_html=True)
        engine_row("01 · AST Structural Engine", "Syntax trees, nodes, control-flow signals")
        engine_row("02 · Statistical Stylometry", "Entropy, token patterns, formatting ratios")
        engine_row("03 · Gemini Intelligence Layer", "Contextual explanation and structured insights")
        engine_row("04 · Similarity & Risk Analysis", "Comparative signals and risk aggregation")
        st.markdown('</div>', unsafe_allow_html=True)
    with right:
        section_heading("Workspace status", "DAY 1 OVERVIEW")
        st.markdown('<div class="panel"><div class="panel-title">System checks</div><div class="panel-sub">Dashboard shell status — not an analysis-engine health check.</div>', unsafe_allow_html=True)
        for label in ["Streamlit dashboard", "Project navigation", "Coming-soon module states"]:
            st.markdown(f'<div class="status-line"><span class="status-check"></span>{label}<span style="margin-left:auto;color:#70d9c1;font: .64rem \'DM Mono\',monospace">READY</span></div>', unsafe_allow_html=True)
        for label in ["Source-code processing", "Gemini API integration", "Analysis & scoring engines"]:
            st.markdown(f'<div class="status-line"><span class="status-pending"></span>{label}<span style="margin-left:auto;color:#d7b779;font: .64rem \'DM Mono\',monospace">PLANNED</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    section_heading("Explore the platform", "MODULES WILL OPEN AS THEY ARE IMPLEMENTED")
    module_cols = st.columns(4, gap="medium")
    modules = [
        ("⌘", "Structural analysis", "Inspect syntax trees, functions, branches, and code structure."),
        ("∿", "Statistical stylometry", "Measure entropy, token distributions, and style indicators."),
        ("⟷", "Similarity analysis", "Compare submissions using explainable similarity signals."),
        ("⬡", "Risk assessment", "Bring analysis signals together into a transparent report."),
    ]
    for col, (icon, title, copy) in zip(module_cols, modules):
        with col:
            st.markdown(
                f'''<div class="module-card"><div class="module-icon">{icon}</div>
                <div class="module-title">{title}</div><div class="module-copy">{copy}</div>
                <div style="margin-top:12px"><span class="coming">COMING SOON</span></div></div>''',
                unsafe_allow_html=True,
            )

    section_heading("Recent activity", "YOUR AUDIT HISTORY WILL APPEAR HERE")
    st.markdown(
        '''<div class="empty-state"><div class="empty-icon">◷</div>
        <div class="empty-title">No activity to display</div>
        <div class="empty-copy">No code has been analyzed yet. Audit history will appear here after the analysis workflow is implemented.</div></div>''',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="footer">CODE INTEGRITY AUDITOR · ENGINEERING THE FOUNDATION FIRST</div>', unsafe_allow_html=True)

else:
    page_content = {
        "⌁  Code Analysis": (
            "Code Analysis",
            "The future workspace for submitting source files and reviewing analysis results.",
            "Build secure file upload, validation, and the end-to-end analysis workflow.",
        ),
        "⌘  Structural Engine": (
            "Structural Engine",
            "The future workspace for AST parsing, syntax-tree traversal, and structural feature extraction.",
            "Implement Python AST analysis and Tree-sitter parsing for C++ and Java.",
        ),
        "∿  Stylometry": (
            "Statistical Stylometry",
            "The future workspace for entropy, token distributions, and measurable code-style indicators.",
            "Implement feature extraction, statistical calculations, and score calibration experiments.",
        ),
        "⟷  Similarity": (
            "Similarity Analysis",
            "The future workspace for comparing code submissions and inspecting similarity signals.",
            "Define comparison features and build a validated similarity methodology.",
        ),
        "⬡  Risk Assessment": (
            "Risk Assessment",
            "The future workspace for combining analytical signals into an interpretable assessment.",
            "Design transparent risk aggregation with documented limitations and explainable outputs.",
        ),
        "▤  Reports": (
            "Reports & Exports",
            "The future workspace for viewing, exporting, and reviewing completed analysis reports.",
            "Create report schemas and a presentation layer after the analysis pipeline is stable.",
        ),
        "⚙  Settings": (
            "Settings",
            "The future workspace for application preferences and secure service configuration.",
            "Add validated configuration handling and secure Gemini API integration when the LLM module is developed.",
        ),
    }
    title, description, step = page_content[selected]
    show_coming_soon(title, description, step)

