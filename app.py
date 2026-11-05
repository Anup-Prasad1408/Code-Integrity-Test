"""Streamlit entry point for Code Integrity Auditor (Day 1 foundation)."""

from __future__ import annotations

import streamlit as st

from config.settings import get_gemini_api_key, get_gemini_model
from services.gemini_service import (
    GeminiConfigurationError,
    test_gemini_connection,
)


st.set_page_config(
    page_title="Code Integrity Auditor",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)


APP_CSS = """
<style>
    .block-container { padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1180px; }
    .cia-eyebrow {
        display: inline-block; padding: .3rem .65rem; border-radius: 999px;
        background: rgba(20, 184, 166, .12); color: #0f9f91;
        font-size: .75rem; font-weight: 700; letter-spacing: .08em;
        text-transform: uppercase;
    }
    .cia-subtitle { color: #8b95a5; font-size: 1.02rem; margin-top: -.35rem; }
    .cia-panel {
        border: 1px solid rgba(128, 128, 128, .24); border-radius: 14px;
        padding: 1rem 1.1rem; height: 100%;
    }
    .cia-panel h3 { margin-top: .2rem; }
    .cia-muted { color: #8b95a5; font-size: .9rem; }
    div.stButton > button[kind="primary"] { border-radius: 9px; }
</style>
"""
st.markdown(APP_CSS, unsafe_allow_html=True)


def render_sidebar() -> None:
    """Render project navigation and local configuration status."""
    with st.sidebar:
        st.title("🔍 CIA")
        st.caption("Code Integrity Auditor")
        st.divider()
        st.markdown("**Day 1 · Project Foundation**")
        st.markdown("- Project initialized\n- Streamlit interface ready\n- Gemini integration scaffolded")
        st.divider()
        if get_gemini_api_key():
            st.success("Gemini API key detected")
        else:
            st.warning("Gemini API key not configured")
        st.caption("Your API key is read locally from the .env file.")


def main() -> None:
    render_sidebar()

    st.markdown('<span class="cia-eyebrow">Day 1 · Initialization</span>', unsafe_allow_html=True)
    st.title("Code Integrity Auditor")
    st.markdown(
        '<p class="cia-subtitle">An intelligent, multi-layer platform for structural '
        'and statistical source-code analysis.</p>',
        unsafe_allow_html=True,
    )

    st.success("Project foundation initialized. The Streamlit application is running.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Project stage", "Day 1")
    with col2:
        st.metric("Analysis engines", "0 / 3", help="Engines will be implemented in upcoming days.")
    with col3:
        st.metric("Gemini model", get_gemini_model())

    st.divider()
    st.subheader("System components")
    cards = st.columns(3)
    components = [
        ("01", "AST Structural Parsing", "Parse source code into syntax structures and inspect programming constructs."),
        ("02", "Statistical AI Stylometry", "Measure entropy, token distributions, and coding-style indicators."),
        ("03", "Gemini-Assisted Insights", "Add an LLM layer for contextual explanations and structured feedback."),
    ]
    for column, (number, title, description) in zip(cards, components):
        with column:
            st.markdown(
                f'<div class="cia-panel"><span class="cia-muted">ENGINE {number}</span>'
                f'<h3>{title}</h3><p class="cia-muted">{description}</p></div>',
                unsafe_allow_html=True,
            )

    st.divider()
    left, right = st.columns([1.25, 1])
    with left:
        st.subheader("Gemini API configuration")
        if get_gemini_api_key():
            st.write("A Gemini API key was found in your local environment configuration.")
        else:
            st.write("Add your Gemini API key to `.env` to enable the connection test.")
            st.code("GEMINI_API_KEY=your_actual_api_key_here\nGEMINI_MODEL=gemini-3.8-flash", language="bash")
        st.caption("The connection test sends only a short test prompt to Gemini.")
        if st.button("Test Gemini API connection", type="primary", use_container_width=True):
            try:
                with st.spinner("Contacting Gemini API..."):
                    reply = test_gemini_connection()
                st.success("Gemini API connection successful.")
                st.write("**Model response:**", reply)
            except GeminiConfigurationError as exc:
                st.warning(str(exc))
            except Exception as exc:  # Surface a concise error without printing credentials.
                st.error(f"Gemini connection failed: {exc}")

    with right:
        st.subheader("Day 1 completion criteria")
        st.markdown(
            "- [ ] Python virtual environment created\n"
            "- [ ] Project dependencies installed\n"
            "- [ ] `.env` configured locally\n"
            "- [ ] Streamlit app launches successfully\n"
            "- [ ] Gemini connection test passes (when API key is configured)\n"
            "- [ ] Initial project pushed to GitHub"
        )

    st.divider()
    st.caption("Code Integrity Auditor · Academic Software Engineering Project · In Development")


if __name__ == "__main__":
    main()
