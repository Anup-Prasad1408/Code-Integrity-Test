from __future__ import annotations

import os
from itertools import combinations
from pathlib import Path

import streamlit as st
import plotly.graph_objects as go
from dotenv import load_dotenv

from utils.file_handler import (
    MAX_FILE_SIZE, MAX_FILES_PER_BATCH, process_multiple_files,
    create_source_archive, validate_and_process_file,
)
from engines.ast_engine import ASTEngine, compare_analyses
from engines.stylometry_engine import StylometryEngine
from engines.llm_engine import LLMEngine
from analyzers.complexity import analyze_complexity
from analyzers.risk_engine import calculate_risk
from utils.reporting import build_pdf_report

load_dotenv()

st.set_page_config(page_title="CodeAuditor · Student Code Integrity", page_icon="🛡️",
                   layout="wide", initial_sidebar_state="expanded")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root{--bg:#0b0c0e;--panel:#141619;--line:rgba(255,255,255,.075);--muted:#858b94;--text:#f4f5f6;--green:#39d98a;--red:#f05252;--amber:#f4bd50}
html,body,[class*="css"]{font-family:Inter,sans-serif}
.stApp{background:radial-gradient(ellipse at 85% 0%,rgba(110,115,122,.16),transparent 32%),radial-gradient(ellipse at 15% 12%,rgba(44,49,55,.24),transparent 35%),#0b0c0e;color:var(--text)}
[data-testid="stHeader"]{background:rgba(11,12,14,.65)}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#111316 0%,#0e1012 100%);border-right:1px solid var(--line)}
[data-testid="stSidebar"] *{color:#d7d9dc}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p{color:#9298a1}
[data-testid="stSidebar"] [data-testid="stRadio"] label{padding:.42rem .55rem;border-radius:9px}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover{background:#24272b}
.block-container{max-width:1680px;padding-top:1.15rem;padding-bottom:2.5rem}
.cia-brand{font-size:1.15rem;font-weight:800;letter-spacing:-.035em;color:#fff;margin:.35rem 0 .15rem}
.cia-brand-sub{font-size:.72rem;color:#858b94;margin-bottom:1rem}
.topline{display:flex;align-items:center;justify-content:space-between;gap:1rem;color:#8e949c;font-size:.78rem;margin:.15rem 0 1.15rem}
.crumb strong{color:#e8e9eb;font-weight:600}
.searchfake{background:rgba(255,255,255,.055);border:1px solid var(--line);border-radius:22px;padding:.55rem 1rem;min-width:250px;color:#8d939b}
.hero{padding:.3rem 0 1.1rem;margin-bottom:.5rem}
.hero-kicker{color:#9ba1a9;text-transform:uppercase;letter-spacing:.14em;font-size:.66rem;font-weight:700;margin-bottom:.45rem}
.hero h1{color:#fff;font-size:clamp(1.65rem,3vw,2.25rem);line-height:1.1;letter-spacing:-.045em;margin:0 0 .35rem;font-weight:800}
.hero p{color:#9298a1;font-size:.88rem;max-width:850px;margin:0;line-height:1.55}
.section-heading{color:#f0f1f2;font-size:1rem;font-weight:700;letter-spacing:-.02em;margin:.35rem 0 .25rem}
.section-caption{color:#858b94;font-size:.75rem;margin:0 0 .75rem}
.dash-card,.metric-card{border:1px solid var(--line);background:linear-gradient(145deg,rgba(28,31,35,.96),rgba(18,20,23,.96));border-radius:16px;padding:1rem 1.05rem;box-shadow:0 12px 30px rgba(0,0,0,.16)}
.metric-card{min-height:125px;position:relative;overflow:hidden}
.metric-label{color:#9298a1;font-size:.73rem}
.metric-value{color:#f5f6f7;font-size:1.65rem;line-height:1.2;font-weight:800;letter-spacing:-.045em;margin:.35rem 0 .2rem}
.metric-foot{color:#858b94;font-size:.69rem}
.metric-orb{position:absolute;right:-22px;top:-35px;width:110px;height:110px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.06),transparent 68%)}
.pill{display:inline-block;border:1px solid var(--line);border-radius:30px;padding:.23rem .55rem;font-size:.65rem;color:#c6c9cd;background:rgba(255,255,255,.045)}
.pill-green{color:#54dfa0;background:rgba(57,217,138,.09);border-color:rgba(57,217,138,.18)}
.pill-red{color:#ff7777;background:rgba(240,82,82,.09);border-color:rgba(240,82,82,.2)}
.pill-amber{color:#f4c86d;background:rgba(244,189,80,.09);border-color:rgba(244,189,80,.2)}
.small-muted{color:#858b94;font-size:.75rem}
.activity-row{display:flex;align-items:center;gap:.75rem;padding:.72rem 0;border-bottom:1px solid rgba(255,255,255,.055)}
.activity-row:last-child{border-bottom:0}
.activity-icon{width:34px;height:34px;border-radius:11px;display:flex;align-items:center;justify-content:center;background:#25292e;color:#e8eaed;flex-shrink:0}
.activity-title{color:#eceef0;font-size:.77rem;font-weight:600}
.activity-sub{color:#858b94;font-size:.66rem;margin-top:.15rem}
.activity-right{margin-left:auto;text-align:right;font-size:.7rem;white-space:nowrap}
.heatmap{display:grid;grid-template-columns:repeat(14,1fr);gap:4px;margin-top:.8rem}
.heat{aspect-ratio:1;border-radius:3px;background:#25292d}
.heat.l1{background:#454a50}.heat.l2{background:#777e85}.heat.l3{background:#b7bdc3}.heat.l4{background:#f1f3f4}
.flow-row{display:flex;align-items:center;justify-content:space-between;gap:.5rem;margin:.55rem 0}
.flow-node{background:#25292e;border:1px solid var(--line);border-radius:9px;padding:.5rem .6rem;color:#d8dadd;font-size:.68rem;text-align:center;flex:1}
.flow-arrow{color:#777e85;font-size:1.1rem}
div[data-testid="stMetric"]{background:#171a1e;border:1px solid var(--line);padding:.75rem .9rem;border-radius:13px}
div[data-testid="stMetric"] label{color:#9298a1!important}
div[data-testid="stMetric"] [data-testid="stMetricValue"]{color:#f5f6f7;font-weight:800}
div.stButton>button,div.stDownloadButton>button{border-radius:10px;font-weight:600;border:1px solid #343940;background:#202429;color:#eceef0;transition:all .18s ease}
div.stButton>button[kind="primary"]{background:#f04b18;border-color:#f04b18;color:white}
div.stButton>button:hover,div.stDownloadButton>button:hover{border-color:#737b84;color:#fff;transform:translateY(-1px)}
div.stButton>button[kind="primary"]:hover{background:#d93f12;border-color:#d93f12}
[data-testid="stFileUploader"]{background:#171a1e;border:1px dashed #454b53;padding:.7rem;border-radius:14px}
[data-baseweb="select"]>div,input,textarea{background:#191c20!important;color:#f2f3f4!important;border-color:#343940!important}
[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:12px;overflow:hidden}
hr{border-color:var(--line)}
.footer{color:#686f78;font-size:.68rem;text-align:center;padding-top:1.3rem}
@media(max-width:800px){.block-container{padding-left:1rem;padding-right:1rem}.searchfake{display:none}.metric-value{font-size:1.35rem}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

DEFAULTS = {"uploaded_files": [], "invalid_files": [], "analysis_results": {},
            "comparisons": [], "upload_version": 0, "notice": ""}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

LANGUAGES = ["Python", "JavaScript", "C"]

def add_record(record):
    existing = {item["id"]: item for item in st.session_state.uploaded_files}
    existing[record["id"]] = record
    st.session_state.uploaded_files = list(existing.values())
    st.session_state.analysis_results.pop(record["id"], None)

def get_secret(name, fallback=""):
    try:
        return st.secrets.get(name, fallback)
    except Exception:
        return os.getenv(name, fallback)

def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="cia-brand">✳ CodeAuditor</div><div class="cia-brand-sub">STUDENT CODE INTEGRITY</div>', unsafe_allow_html=True)
        st.markdown("**GENERAL**")
        page = st.radio("NAVIGATION", ["Overview", "Upload & Analyze", "Audit Results", "Development Roadmap", "About Project"], label_visibility="collapsed")
        st.divider()
        st.markdown("**TOOLS**")
        st.markdown("🛡️  Structural Plagiarism")
        st.markdown("✦  Code Stylometry")
        st.markdown("⌘  Assignment Evaluator")
        st.markdown("▣  Multi-file Vault")
        st.divider()
        st.markdown("**INSIGHTS**")
        st.markdown("◷  Flagged Activity")
        st.markdown("▥  Analytics")
        st.markdown("▤  Audit Reports")
        st.divider()
        st.markdown("**OTHER**")
        st.markdown("⚙️  Settings")
        st.markdown("☷  System Logs")
        st.markdown('<div class="dash-card" style="padding:.85rem;margin-top:1rem"><b>✦ Auditor Pro</b><div class="small-muted">Local-first analysis · Optional LLM review</div></div>', unsafe_allow_html=True)
        st.caption("Python · JavaScript · C")
        st.caption(f"{MAX_FILE_SIZE // (1024*1024)} MB per file · {MAX_FILES_PER_BATCH} per batch")
    return page

def topbar(current):
    st.markdown(f'<div class="topline"><div class="crumb">Dashboard&nbsp; / &nbsp;<strong>{current}</strong></div><div class="searchfake">⌕ &nbsp; Search or type command... &nbsp; <span style="float:right">⌘ K</span></div><div>▦ &nbsp; ◉ &nbsp; ? &nbsp; ◉</div></div>', unsafe_allow_html=True)

def hero(title, subtitle, kicker="STUDENT CODE INTEGRITY AUDITOR"):
    st.markdown(f'<section class="hero"><div class="hero-kicker">{kicker}</div><h1>{title}</h1><p>{subtitle}</p></section>', unsafe_allow_html=True)

def metric_card(label, value, foot, tag, tagclass):
    st.markdown(f'<div class="metric-card"><div class="metric-orb"></div><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-foot">{foot}</div><div style="margin-top:.65rem"><span class="pill {tagclass}">{tag}</span></div></div>', unsafe_allow_html=True)

def run_analysis():
    records = st.session_state.uploaded_files
    ast_engine, style_engine, llm_engine = ASTEngine(), StylometryEngine(), LLMEngine()
    results = {}
    for record in records:
        ast_result = ast_engine.analyze(record["content"], record["language"])
        style_result = style_engine.analyze(record["content"], record["language"])
        complexity = analyze_complexity(record["content"], record["language"])
        results[record["id"]] = {
            "ast": ast_result, "stylometry": style_result, "complexity": complexity,
            "llm": {"enabled": False, "status": "Not requested", "adherence_score": None,
                    "passed_constraints": [], "issues": [], "hints": [], "summary": ""},
            "risk": {}, "summary": "Static analysis completed.",
        }

    comparisons = []
    for a, b in combinations(records, 2):
        if a["language"] != b["language"]:
            continue
        comp = compare_analyses(results[a["id"]]["ast"], results[b["id"]]["ast"])
        if comp.get("comparable"):
            row = {"file_a": a["name"], "file_b": b["name"], **comp}
            comparisons.append(row)
            results[a["id"]].setdefault("similarity", []).append(row)
            results[b["id"]].setdefault("similarity", []).append(row)

    requirements = st.session_state.get("assignment_requirements", "").strip()
    enable_llm = st.session_state.get("enable_llm", False)
    if enable_llm:
        provider = get_secret("LLM_PROVIDER", "gemini").lower()
        api_key = get_secret("OPENAI_API_KEY" if provider == "openai" else "GEMINI_API_KEY", "")
        model = get_secret("OPENAI_MODEL" if provider == "openai" else "GEMINI_MODEL",
                           "gpt-4o-mini" if provider == "openai" else "gemini-2.5-flash")
        for record in records:
            results[record["id"]]["llm"] = llm_engine.analyze(
                record["content"], record["language"], requirements,
                api_key=api_key, model=model, provider=provider
            )

    for record in records:
        item = results[record["id"]]
        relevant = [c["similarity"] for c in comparisons if record["name"] in (c["file_a"], c["file_b"])]
        item["risk"] = calculate_risk({
            "max_similarity": max(relevant) if relevant else None,
            "stylometry_score": item["stylometry"]["stylometry_score"],
            "syntax_valid": item["ast"]["syntax_valid"],
        })
    st.session_state.analysis_results = results
    st.session_state.comparisons = comparisons

def render_overview():
    topbar("Overview")
    hero("Integrity Overview", "Monitor source submissions, inspect structural similarities and review transparent code-style signals from one workspace.")
    records = st.session_state.uploaded_files
    results = st.session_state.analysis_results
    n = len(records)
    analyzed = len(results)
    comparisons = st.session_state.comparisons
    flagged_pairs = sum(c["similarity"] >= 75 for c in comparisons)
    mean_style = round(sum(r["stylometry"]["stylometry_score"] for r in results.values()) / analyzed, 1) if analyzed else None
    syntax_issues = sum(not r["ast"]["syntax_valid"] for r in results.values())
    cols = st.columns(4)
    values = [
        ("Total submissions", f"{n:,}", f"{analyzed} analyzed · {sum(x['line_count'] for x in records):,} lines", "LIVE", "pill-green"),
        ("High similarity pairs", f"{flagged_pairs:,}", f"{len(comparisons)} same-language comparisons", "ENGINE 1", "pill-red"),
        ("Stylometry average", f"{mean_style:.1f}" if mean_style is not None else "—", "Heuristic style-anomaly indicator", "ENGINE 2", "pill-amber"),
        ("Syntax issues", f"{syntax_issues:,}", "Parser errors / incomplete parses", "PARSER", "pill-green" if syntax_issues == 0 else "pill-amber"),
    ]
    for col, args in zip(cols, values):
        with col: metric_card(*args)
    st.write("")
    c1,c2,c3 = st.columns([1,1,1.8])
    with c1:
        if st.button("＋ Add submissions", type="primary", use_container_width=True):
            st.session_state["goto_upload"] = True
            st.rerun()
    with c2:
        if st.button("↻ Re-run engines", use_container_width=True, disabled=not bool(records)):
            run_analysis()
            st.success("Analysis refreshed from current workspace.")
    with c3:
        st.markdown('<div class="small-muted" style="padding:.55rem 0">Metrics are computed from the current workspace. No demo counts are mixed into live results.</div>', unsafe_allow_html=True)

    left,right = st.columns([1.55,1])
    with left:
        st.markdown('<div class="dash-card">',unsafe_allow_html=True)
        st.markdown('<div class="section-heading">Structural similarity by comparison</div><div class="section-caption">Engine 1 · same-language submissions only</div>',unsafe_allow_html=True)
        if comparisons:
            fig=go.Figure()
            labels=[f'{c["file_a"][:16]} ↔ {c["file_b"][:16]}' for c in comparisons[:12]]
            vals=[c["similarity"] for c in comparisons[:12]]
            fig.add_trace(go.Scatter(x=list(range(len(vals))),y=vals,mode="lines+markers",name="Similarity",
                                     line=dict(color="#39d98a",width=2.5,shape="spline"),
                                     marker=dict(size=7,color=["#f05252" if v>=75 else "#39d98a" for v in vals])))
            fig.update_layout(height=250,margin=dict(l=5,r=5,t=12,b=35),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#8c929a",size=9),xaxis=dict(tickmode="array",tickvals=list(range(len(labels))),ticktext=labels,showgrid=False),
                yaxis=dict(range=[0,100],showgrid=True,gridcolor="rgba(255,255,255,.06)",ticksuffix="%"),showlegend=False)
            st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False},key="overview_similarity")
        else:
            st.markdown('<div class="small-muted" style="padding:3rem 1rem;text-align:center">Add at least two submissions in the same language to populate structural comparisons.</div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with right:
        st.markdown('<div class="dash-card">',unsafe_allow_html=True)
        st.markdown('<div class="section-heading">Engine activity</div><div class="section-caption">Current workspace coverage</div>',unsafe_allow_html=True)
        engine_data=[("AST structural parser", analyzed, n),("Stylometry scanner",analyzed,n),
                     ("LLM evaluator",sum(1 for r in results.values() if r["llm"].get("status")=="Completed"),n)]
        for label,count,total in engine_data:
            pct=100*count/max(1,total)
            st.markdown(f'<div style="display:flex;justify-content:space-between;font-size:.75rem;margin:.8rem 0 .25rem"><span>{label}</span><span>{count}/{total}</span></div>',unsafe_allow_html=True)
            st.progress(pct/100)
        st.markdown('<div class="small-muted">LLM engine requires an API key and assignment requirements.</div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

    st.write("")
    left,middle,right=st.columns([1.2,1.05,.9])
    with left:
        st.markdown('<div class="dash-card">',unsafe_allow_html=True)
        st.markdown('<div class="section-heading">Recent analysis activity</div><div class="section-caption">Latest workspace submissions</div>',unsafe_allow_html=True)
        for rec in records[-5:][::-1]:
            res=results.get(rec["id"],{})
            status="Analyzed" if res else "Awaiting analysis"
            cls="pill-green" if res else "pill-amber"
            st.markdown(f'<div class="activity-row"><div class="activity-icon">⌘</div><div style="flex:1;min-width:0"><div class="activity-title">{rec["name"]}</div><div class="activity-sub">{rec["language"]} · {rec["line_count"]} lines</div></div><div class="activity-right"><span class="pill {cls}">{status}</span></div></div>',unsafe_allow_html=True)
        if not records: st.markdown('<div class="small-muted">No submissions yet. Add code to begin.</div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with middle:
        st.markdown('<div class="dash-card">',unsafe_allow_html=True)
        st.markdown('<div class="section-heading">Similarity review flow</div><div class="section-caption">Top structural matches</div>',unsafe_allow_html=True)
        for c in sorted(comparisons,key=lambda x:x["similarity"],reverse=True)[:3]:
            col="negative" if c["similarity"]>=75 else "positive"
            st.markdown(f'<div class="flow-row"><div class="flow-node">{c["file_a"][:12]}</div><div class="flow-arrow">↔</div><div class="flow-node">{c["file_b"][:12]}<br><span class="{col}">{c["similarity"]:.1f}%</span></div></div>',unsafe_allow_html=True)
        if not comparisons: st.markdown('<div class="small-muted" style="padding:1.2rem 0">Pairwise flows appear when multiple same-language files have been analyzed.</div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with right:
        st.markdown('<div class="dash-card">',unsafe_allow_html=True)
        st.markdown('<div class="section-heading">Code activity</div><div class="section-caption">Lines per submission</div>',unsafe_allow_html=True)
        vals=[r["line_count"] for r in records[-10:]]
        heat_html=''.join(f'<div class="heat {"l"+str(min(4,1+v//25)) if v else ""}'+'></div>' for v in vals)
        st.markdown(f'<div class="heatmap">{heat_html or "".join(["<div class=heat></div>" for _ in range(28)])}</div><div class="small-muted" style="margin-top:.7rem">{sum(vals):,} lines across recent files</div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="small-muted">ENGINE OUTPUTS · LIVE</div>',unsafe_allow_html=True)
    a,b,c,d=st.columns(4)
    a.metric("Files analyzed",analyzed)
    b.metric("Pair comparisons",len(comparisons))
    c.metric("Avg. stylometry",f"{mean_style:.1f}/100" if mean_style is not None else "—")
    d.metric("LLM reviews",sum(1 for r in results.values() if r["llm"].get("status")=="Completed"))

def render_upload():
    topbar("Upload & Analyze")
    hero("Upload & Analyze", "Paste source code or add a batch of files. All selected submissions are analyzed locally; the optional LLM layer runs only when configured.", "SUBMISSION WORKSPACE")
    st.markdown('<div class="section-heading">Add code by pasting</div><div class="section-caption">Useful for a quick single submission. Choose the language explicitly.</div>',unsafe_allow_html=True)
    with st.form("paste_form",clear_on_submit=True):
        p1,p2=st.columns([1,2])
        with p1:
            paste_lang=st.selectbox("Programming language",LANGUAGES,key="paste_lang")
            paste_name=st.text_input("Submission name",value="pasted_submission")
        with p2:
            pasted=st.text_area("Paste code here",height=170,placeholder="Paste Python, JavaScript or C source code...")
        submit_paste=st.form_submit_button("＋ Add pasted submission",type="primary",use_container_width=True)
        if submit_paste:
            if pasted.strip():
                from hashlib import sha256
                name=paste_name.strip() or "pasted_submission"
                ext={"Python":".py","JavaScript":".js","C":".c"}[paste_lang]
                if not name.lower().endswith(ext): name+=ext
                raw=pasted.encode("utf-8")
                from utils.file_handler import _make_record
                rec=_make_record(name,raw,pasted,"Pasted UTF-8",paste_lang)
                add_record(rec)
                st.success(f"Added {name}.")
            else:
                st.error("Paste some source code before adding.")

    st.divider()
    st.markdown('<div class="section-heading">Upload files</div><div class="section-caption">Supported: .py, .js, .c, .txt and text-based .pdf · up to 20 files per batch.</div>',unsafe_allow_html=True)
    generic_lang=st.selectbox("Language for .txt and .pdf files",LANGUAGES,key="generic_upload_language")
    uploads=st.file_uploader("Choose multiple submissions",type=["py","js","c","txt","pdf"],accept_multiple_files=True,key=f"uploads_{st.session_state.upload_version}")
    if st.button("Validate & add files",type="primary",disabled=not bool(uploads),use_container_width=False):
        valid,invalid=process_multiple_files(uploads,generic_lang)
        for item in valid: add_record(item)
        st.session_state.invalid_files=invalid
        st.success(f"Added {len(valid)} file(s); rejected {len(invalid)}.")
        st.rerun()
    if st.session_state.invalid_files:
        with st.expander(f"Rejected files ({len(st.session_state.invalid_files)})",expanded=True):
            for item in st.session_state.invalid_files:
                st.error(f'{item["name"]}: {item["error"]}')
    records=st.session_state.uploaded_files
    st.write("")
    m1,m2,m3,m4=st.columns(4)
    m1.metric("Workspace files",len(records))
    m2.metric("Source lines",f'{sum(r["line_count"] for r in records):,}')
    m3.metric("Languages",len({r["language"] for r in records}))
    m4.metric("Workspace size",f'{sum(r["size"] for r in records)/(1024*1024):.2f} MB')
    if records:
        with st.expander("Review workspace files",expanded=False):
            st.dataframe([{"File":r["name"],"Language":r["language"],"Lines":r["line_count"],"Size KB":round(r["size"]/1024,1),"Analyzed":r["id"] in st.session_state.analysis_results} for r in records],use_container_width=True,hide_index=True)
            sel=st.selectbox("Preview source",options=[r["id"] for r in records],format_func=lambda x:next(r["name"] for r in records if r["id"]==x))
            item=next(r for r in records if r["id"]==sel)
            st.code(item["content"],language={"Python":"python","JavaScript":"javascript","C":"c"}[item["language"]],line_numbers=True)
            d1,d2=st.columns(2)
            d1.download_button("Download selected file",item["content"],file_name=item["name"],mime="text/plain",use_container_width=True)
            d2.download_button("Download source ZIP",create_source_archive(records),file_name="code-auditor-submissions.zip",mime="application/zip",use_container_width=True)
        st.divider()
        st.markdown('<div class="section-heading">Engine 3 · Assignment requirements</div><div class="section-caption">Optional. Gemini evaluates whether code appears to meet the supplied requirements and gives learning-oriented hints. It does not assess authorship.</div>',unsafe_allow_html=True)
        st.text_area("Paste assignment prompt / rubric",height=110,key="assignment_requirements",placeholder="Example: Write a function that sorts an array without using built-in sort...")
        selected_provider=get_secret("LLM_PROVIDER","gemini").lower()
        api_available=bool(get_secret("OPENAI_API_KEY" if selected_provider=="openai" else "GEMINI_API_KEY",""))
        st.checkbox("Run optional Gemini requirement review for each submission",key="enable_llm",help="Requires GEMINI_API_KEY in .env or Streamlit secrets.")
        st.caption(f"{selected_provider.upper()} key status: " + ("Configured" if api_available else "Not configured — local Engines 1 and 2 still work."))
        if st.button("▶ Run all available engines",type="primary",use_container_width=True):
            with st.spinner("Parsing structures, calculating stylometry and running configured reviews..."):
                run_analysis()
            st.success("Analysis completed. Open Audit Results or Overview to inspect live metrics.")
            st.rerun()
        if st.button("Clear all submissions and results"):
            st.session_state.uploaded_files=[]
            st.session_state.analysis_results={}
            st.session_state.comparisons=[]
            st.session_state.invalid_files=[]
            st.session_state.upload_version+=1
            st.rerun()
    else:
        st.info("Workspace is empty. Paste a code sample or upload one or more files.")

def render_results():
    topbar("Audit Results")
    hero("Audit Results", "Inspect per-file structural parsing, code-style statistics, pairwise similarity and optional assignment feedback.", "ANALYSIS REPORT")
    records=st.session_state.uploaded_files
    results=st.session_state.analysis_results
    if not records:
        st.info("Add submissions in Upload & Analyze first.")
        return
    if not results:
        st.warning("Files are in the workspace but engines have not been run yet.")
        if st.button("Run all available engines",type="primary"):
            run_analysis()
            st.rerun()
        return
    st.markdown('<div class="section-heading">Submission results</div>',unsafe_allow_html=True)
    summary=[]
    for rec in records:
        res=results.get(rec["id"])
        if not res: continue
        summary.append({"File":rec["name"],"Language":rec["language"],"Parser":res["ast"]["parse_status"],
                        "Syntax": "Valid" if res["ast"]["syntax_valid"] else "Issue",
                        "Functions":res["ast"]["functions"],"Loops":res["ast"]["loops"],
                        "Stylometry":res["stylometry"]["stylometry_score"],
                        "Review priority":res["risk"]["review_score"]})
    st.dataframe(summary,use_container_width=True,hide_index=True)
    selected=st.selectbox("Select submission",options=[r["id"] for r in records if r["id"] in results],
                          format_func=lambda x:next(r["name"] for r in records if r["id"]==x))
    rec=next(r for r in records if r["id"]==selected)
    res=results[selected]
    st.divider()
    x1,x2,x3,x4=st.columns(4)
    x1.metric("Structural nodes",res["ast"]["node_count"])
    x2.metric("Functions",res["ast"]["functions"])
    x3.metric("Stylometry signal",f'{res["stylometry"]["stylometry_score"]}/100')
    x4.metric("Review priority",f'{res["risk"]["review_score"]}/100' if res["risk"]["review_score"] is not None else "—")
    left,right=st.columns([1.1,1])
    with left:
        st.markdown('<div class="dash-card">',unsafe_allow_html=True)
        st.markdown('<div class="section-heading">Engine 1 · AST structural analysis</div>',unsafe_allow_html=True)
        st.write("Parser:",res["ast"]["parse_status"])
        st.write("Syntax:", "Valid" if res["ast"]["syntax_valid"] else "Issue detected")
        st.write("Fingerprint:",res["ast"]["structural_fingerprint"][:24]+"…")
        st.write("Structure counts:",f'{res["ast"]["functions"]} functions · {res["ast"]["classes"]} classes · {res["ast"]["branches"]} branches · {res["ast"]["loops"]} loops')
        if res["ast"].get("parse_error"): st.warning(res["ast"]["parse_error"])
        st.markdown('</div>',unsafe_allow_html=True)
    with right:
        st.markdown('<div class="dash-card">',unsafe_allow_html=True)
        st.markdown('<div class="section-heading">Engine 2 · Stylometry</div>',unsafe_allow_html=True)
        st.metric("Style-anomaly indicator",f'{res["stylometry"]["stylometry_score"]}/100',res["stylometry"]["band"])
        st.write(res["stylometry"]["interpretation"])
        for signal in res["stylometry"]["signals"]: st.markdown("• "+signal)
        st.markdown('</div>',unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="dash-card">',unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Stylometric feature profile</div>',unsafe_allow_html=True)
    feat=res["stylometry"]["features"]
    st.dataframe([{"Feature":k.replace("_"," ").title(),"Value":v} for k,v in feat.items()],use_container_width=True,hide_index=True)
    st.markdown('</div>',unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="dash-card">',unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Engine 3 · Assignment evaluator</div>',unsafe_allow_html=True)
    llm=res["llm"]
    st.write("Status:",llm.get("status","Not run"))
    if llm.get("adherence_score") is not None: st.metric("Requirement adherence",f'{llm["adherence_score"]}/100')
    if llm.get("summary"): st.write(llm["summary"])
    if llm.get("passed_constraints"):
        st.markdown("**Requirements apparently met**")
        for x in llm["passed_constraints"]: st.markdown("• "+str(x))
    if llm.get("issues"):
        st.markdown("**Potential gaps**")
        for x in llm["issues"]: st.warning(str(x))
    if llm.get("hints"):
        st.markdown("**Learning hints**")
        for x in llm["hints"]: st.info(str(x))
    st.markdown('</div>',unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="dash-card">',unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Pairwise similarity evidence</div>',unsafe_allow_html=True)
    related=[c for c in st.session_state.comparisons if rec["name"] in (c["file_a"],c["file_b"])]
    if related:
        st.dataframe([{"Other submission":c["file_b"] if c["file_a"]==rec["name"] else c["file_a"],
                       "Similarity %":c["similarity"],"AST sequence %":c["structure_similarity"],
                       "Token sequence %":c["normalized_token_similarity"],"Interpretation":c["interpretation"]} for c in related],
                     use_container_width=True,hide_index=True)
    else:
        st.caption("No same-language comparison is available. Add another submission in the same language.")
    st.markdown('</div>',unsafe_allow_html=True)
    with st.expander("View submitted source"):
        st.code(rec["content"],language={"Python":"python","JavaScript":"javascript","C":"c"}[rec["language"]],line_numbers=True)
    st.warning("Review-priority and stylometry scores are indicators only. They are not proof of plagiarism or AI authorship.")

    st.divider()
    st.markdown('<div class="section-heading">Export faculty report</div>',unsafe_allow_html=True)
    try:
        pdf=build_pdf_report(records,results,st.session_state.comparisons)
        st.download_button("⇩ Download PDF audit report",data=pdf,file_name="student-code-integrity-audit.pdf",mime="application/pdf",type="primary")
    except Exception as exc:
        st.error(f"Could not generate PDF report: {exc}")

def render_roadmap():
    topbar("Development Roadmap")
    hero("Engineering Roadmap","The core analysis workflow is implemented in this release. Further tuning will follow measured evaluation, not assumed accuracy.","PROJECT DELIVERY")
    items=[
        ("Engine 1","AST structural parser","Python native AST; Tree-sitter JS/C; normalized pairwise comparison","Implemented"),
        ("Engine 2","Statistical stylometry","Shannon entropy, token diversity, comment density, indentation and formatting features","Implemented"),
        ("Engine 3","LLM requirement evaluator","Optional Gemini JSON review, requirement adherence and educational hints","Implemented · optional key"),
        ("Interface","Submission dashboard","Paste, multi-file upload, text PDF extraction, live metrics and PDF report","Implemented"),
        ("Next","Calibration and dataset evaluation","Human-labelled benchmark set, false-positive analysis, threshold tuning","Next phase"),
    ]
    for tag,title,detail,status in items:
        with st.container(border=True):
            a,b,c=st.columns([1,4,1.7])
            a.markdown(f"**{tag}**")
            b.markdown(f"**{title}**")
            b.caption(detail)
            c.success(status) if status.startswith("Implemented") else c.info(status)

def render_about():
    topbar("About Project")
    hero("A student-focused code integrity toolkit","A local-first academic review assistant that combines compiler structure, statistical code-style features and optional LLM requirement feedback.","ABOUT CODEAUDITOR")
    st.markdown("### Three-engine architecture")
    cols=st.columns(3)
    cards=[
        ("01 · AST Structural Parser","Native Python AST plus Tree-sitter grammar parsing for JavaScript and C. Identifiers and literals are normalized for structural comparison."),
        ("02 · Statistical Stylometry","Measures Shannon entropy, token diversity, comment ratio, indentation consistency and formatting signals. It is not a trained AI detector."),
        ("03 · Smart Logic Evaluator","Optional Gemini-powered assignment requirement review with strict JSON output, issue summaries and student-friendly hints."),
    ]
    for col,(title,body) in zip(cols,cards):
        with col:
            st.markdown(f'<div class="dash-card"><div class="section-heading">{title}</div><div class="small-muted">{body}</div></div>',unsafe_allow_html=True)
    st.write("")
    st.info("The capstone presentation describes a five-step flow: script ingestion, AST normalization, stylometric scan, LLM prompt check and faculty report. This release implements those stages with an optional LLM provider and transparent offline fallbacks.")
    st.warning("Neither similarity nor code style can conclusively establish misconduct. Results are designed to support an instructor's review and a fair conversation with the student.")

page=render_sidebar()
if st.session_state.pop("goto_upload",False):
    page="Upload & Analyze"
if page=="Overview": render_overview()
elif page=="Upload & Analyze": render_upload()
elif page=="Audit Results": render_results()
elif page=="Development Roadmap": render_roadmap()
else: render_about()
st.markdown('<div class="footer">CODEAUDITOR · STUDENT CODE INTEGRITY · LOCAL-FIRST STATIC ANALYSIS</div>',unsafe_allow_html=True)
