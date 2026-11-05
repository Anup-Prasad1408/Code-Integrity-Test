# Code Integrity Auditor

### An Intelligent Multi-Layer Source Code Analysis Platform

> **Analyze. Compare. Detect. Understand Code Integrity.**

Code Integrity Auditor (CIA) is an academic software-engineering project intended to explore source-code structure, statistical stylometry, similarity analysis, risk assessment, and AI-assisted interpretation.

## Day 1 release: Dashboard foundation

This release intentionally delivers **the dashboard shell only**. It establishes the visual workspace, navigation, project status, and implementation roadmap. The analysis engines and integrations are placeholders and are not active yet.

- Professional Streamlit dashboard with overview metrics and module roadmap.
- Sidebar navigation with explicit **Coming Soon** pages.
- Clear distinction between dashboard readiness and analysis-engine readiness.
- Starter package structure for incremental development.
- No source code is uploaded, analyzed, scored, stored, or sent to an AI service in this release.

## Dashboard preview

Run the application locally or deploy it to Streamlit Community Cloud to view the dashboard.

## Technology

- Python
- Streamlit
- Pytest (starter test framework)

Gemini integration is planned for a later milestone. `google-genai` is deliberately not included in Day 1 because no Gemini request is made by this dashboard.

## Project structure

```text
Code-Integrity-Auditor/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── engines/
│   ├── ast_engine.py
│   ├── stylometry_engine.py
│   └── llm_engine.py
├── analyzers/
│   ├── complexity.py
│   ├── similarity.py
│   └── risk_engine.py
├── parsers/
│   ├── python_parser.py
│   ├── cpp_parser.py
│   └── java_parser.py
├── models/
│   └── analysis_result.py
├── utils/
│   ├── file_handler.py
│   └── language_detector.py
├── datasets/
│   └── README.md
└── tests/
    └── test_project_structure.py
```

## Run locally

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
```

**Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

Install dependencies and launch:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy directly from GitHub

1. Create a GitHub repository named `Code-Integrity-Auditor`.
2. Extract this ZIP archive on your computer.
3. On the repository page, choose **Add file → Upload files**.
4. Upload the contents of the extracted `Code-Integrity-Auditor` folder (the files and directories inside it, not an extra nested project folder).
5. Commit the files to the `main` branch.
6. Open [Streamlit Community Cloud](https://share.streamlit.io/), connect GitHub, and create an app.
7. Select your repository, branch `main`, and main file path `app.py`, then deploy.

Do not upload a real `.env` file or API key. The Day 1 dashboard does not need a Gemini key. When Gemini integration is implemented, add the key through Streamlit app settings → **Secrets**, not in source code.

## Development status

| Module | Day 1 status |
|---|---|
| Dashboard and navigation | Ready |
| AST structural engine | Coming soon |
| Statistical stylometry | Coming soon |
| Gemini / LLM integration | Coming soon |
| Complexity analysis | Coming soon |
| Similarity analysis | Coming soon |
| Risk engine | Coming soon |
| Python / C++ / Java parsers | Coming soon |
| File handling and language detection | Coming soon |
| Reports and exports | Coming soon |

## Responsible interpretation

When analysis capabilities are introduced, outputs should be treated as analytical indicators rather than definitive proof of code authorship or AI generation. Evaluation methods, limitations, and false-positive risks must be documented.

## Testing

Run the starter project checks with:

```bash
pytest -q
```

## License

No license has been selected for this academic project yet. Add a `LICENSE` file before granting permissions for public reuse or redistribution.

---

<p align="center"><strong>CODE INTEGRITY AUDITOR</strong><br/>Engineering the foundation first.</p>
