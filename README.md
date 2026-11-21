# Code Integrity Auditor

**A professional, multi-language source-code workspace built with Streamlit.**

Code Integrity Auditor is an academic software project designed to prepare Python, C++ and Java source files for future structural, statistical and AI-assisted integrity analysis. This release focuses on a premium dashboard experience, reliable multi-file ingestion, descriptive workspace analytics and exportable file inventories.

> **Important scope note:** The dashboard, Dark/Light theme, upload validation, session workspace, descriptive metrics and inventory exports are implemented. AST analysis, code stylometry, similarity detection, risk scoring and Gemini-assisted review are still marked **Coming Soon**. The application does not claim to identify an author, prove plagiarism or determine AI authorship.

---

## What is included

### Dashboard experience

- Reference-inspired dark dashboard with a graphite/teal visual system.
- Light appearance available through the **Dark appearance** switch in the sidebar.
- Sidebar navigation for Overview, Upload Workspace, Analytics, Reports & Exports, Development Roadmap and Settings & About.
- Responsive layout with KPI cards, language distribution, largest-file chart, recent source files and development-status panels.
- Workspace search by filename or detected language.

### Source upload and validation

- Upload multiple `.py`, `.cpp` and `.java` files in one batch.
- Validate each file independently; an invalid file does not block other valid files.
- Validate filename, extension, file size, empty content and encoding.
- Decode UTF-8, UTF-8 with BOM and BOM-marked UTF-16.
- Reject undecodable or binary source instead of silently corrupting it.
- Detect language from the file extension.
- Generate SHA-256 fingerprints and source line counts.
- Preview, download or remove individual files.
- Download the full validated workspace as a ZIP.

### Analytics and exports

- Calculate workspace file count, source lines, language count, total size and average file size.
- Display language mix and largest files using Plotly charts.
- Export the validated inventory as CSV or JSON.
- Export source files as ZIP.
- JSON and CSV exports include metadata only; the JSON manifest does not embed source-code contents.

## Project structure

```text
Code-Integrity-Auditor/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── pyproject.toml
├── run_windows.bat
├── .streamlit/
│   └── config.toml
├── analyzers/
│   ├── __init__.py
│   ├── complexity.py
│   ├── risk_engine.py
│   └── similarity.py
├── datasets/
│   └── README.md
├── engines/
│   ├── __init__.py
│   ├── ast_engine.py
│   ├── llm_engine.py
│   └── stylometry_engine.py
├── models/
│   ├── __init__.py
│   └── analysis_result.py
├── parsers/
│   ├── __init__.py
│   ├── cpp_parser.py
│   ├── java_parser.py
│   └── python_parser.py
├── tests/
│   ├── __init__.py
│   ├── test_dashboard_metrics.py
│   ├── test_file_handler.py
│   ├── test_language_detector.py
│   └── test_reporting.py
└── utils/
    ├── __init__.py
    ├── dashboard_metrics.py
    ├── file_handler.py
    ├── language_detector.py
    └── reporting.py
```

## Requirements

- Python 3.10 or newer
- pip
- A modern web browser

The currently active dashboard uses Streamlit and Plotly. Gemini and Tree-sitter dependencies are intentionally not required yet because those analysis phases are not implemented in this release.

## Run locally (Windows)

1. Extract the ZIP archive.
2. Open the extracted `Code-Integrity-Auditor` folder in a terminal.
3. Create and activate a virtual environment:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

4. Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

5. Start the app:

```powershell
streamlit run app.py
```

Streamlit prints a local URL, usually `http://localhost:8501`.

You can also run `run_windows.bat` after Python and dependencies are installed.

## Use the application

1. Open **Upload Workspace** from the sidebar.
2. Select one or more `.py`, `.cpp` or `.java` source files.
3. Click **Validate & add to workspace**.
4. Review accepted files and rejected-file reasons.
5. Select a validated file to preview its source code.
6. Use **Analytics** to inspect workspace metrics.
7. Use **Reports & Exports** to download the source ZIP, CSV inventory or JSON manifest.
8. Switch between Dark and Light appearance using the sidebar toggle.

### Upload limits

| Rule | Limit |
|---|---|
| Supported extensions | `.py`, `.cpp`, `.java` |
| Maximum file size | 5 MiB per file |
| Maximum batch size | 20 files |
| Accepted encodings | UTF-8, UTF-8 BOM, BOM-marked UTF-16 |
| Empty/whitespace-only source | Rejected |
| Binary/NUL content | Rejected |
| Storage | Current Streamlit session only |

The browser's file-picker extension filter is only a convenience. The Python validation layer checks files again.

## Run tests

```powershell
pytest -q
```

The included test suite covers file validation, language detection, workspace metric calculations and CSV/JSON export generation.

## Deploy to Streamlit Community Cloud

1. Create a GitHub repository and upload the contents of this project folder while preserving the structure.
2. Open Streamlit Community Cloud and connect your GitHub account.
3. Select the repository and branch.
4. Set **Main file path** to `app.py`.
5. Deploy.

No API key is required for the features implemented in this version. When Gemini integration is implemented in a future phase, store the actual key in Streamlit Cloud **App settings → Secrets**, not in GitHub. `.env.example` contains only a placeholder.

## Current implementation status

| Module | Status | Description |
|---|---|---|
| `app.py` | Implemented | Dashboard, navigation, theme switch, workspace UI and charts |
| `utils/file_handler.py` | Implemented | Multi-file validation, decoding, metadata and ZIP creation |
| `utils/language_detector.py` | Implemented | Python, C++ and Java extension detection |
| `utils/dashboard_metrics.py` | Implemented | Descriptive workspace metrics |
| `utils/reporting.py` | Implemented | CSV inventory and JSON manifest exports |
| `tests/` | Implemented | 30 unit tests in the packaged release |
| `engines/ast_engine.py` | Coming Soon | Structural parsing |
| `engines/stylometry_engine.py` | Coming Soon | Statistical code-style signals |
| `engines/llm_engine.py` | Coming Soon | Gemini-assisted review |
| `analyzers/` | Coming Soon | Complexity, similarity and risk analysis |
| `parsers/` | Coming Soon | Python, C++ and Java parsing |

## Privacy, safety and limitations

- Uploaded files are held in Streamlit session memory; this release does not configure permanent file storage or a database.
- The active upload workflow does not send source code to an external AI provider.
- Do not upload confidential or third-party source code unless you have permission.
- Source-style metrics cannot establish who wrote a file. Similarity and AI-assisted analysis, when implemented, must be treated as probabilistic signals with evidence and uncertainty—not as conclusive proof.

---

**Code Integrity Auditor** · Source Code Intelligence Workspace
