# CodeAuditor — Student Code Integrity Auditor

A local-first Streamlit application that helps educators and reviewers examine student programming submissions using structural code analysis, stylometric features, and an optional AI-powered assignment-requirement evaluator.

> **Important:** CodeAuditor is a review-assistance tool. Similarity scores are not proof of plagiarism, and stylometric indicators are not proof that code was written by AI. Results should always be reviewed by a human.

## Features

- Upload multiple source files or paste code directly.
- Supports Python, JavaScript, and C source-code analysis.
- Structural parsing and pairwise similarity comparisons:
  - Python: native Python `ast`
  - JavaScript: Esprima
  - C: `pycparser`
- Stylometric signals such as token entropy, token diversity, comment density, indentation consistency, line length, and identifier length.
- Optional LLM-based review of code against assignment requirements using Gemini or OpenAI.
- Dashboard for reviewing analysis results.
- Exportable PDF reports and source-file archives (where enabled in the app).
- Automated tests for core project functionality.

The parser libraries have language and syntax limitations. For example, Esprima 4 does not support every modern JavaScript feature, and `pycparser` expects C that it can parse (some compiler extensions and complex preprocessor usage may need preprocessing). When parsing fails, check the parser status shown by the application; do not assume a fallback result is equivalent to a full AST parse.

## Requirements

- Python 3.11 or newer (Python 3.12 is recommended for the current development setup).
- Git.
- Internet access for the initial dependency installation.
- An API key only if you want to use the optional LLM evaluator.

## Run locally

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
cd YOUR-REPOSITORY
```

Replace the URL with the actual GitHub repository URL.

### 2. Create a virtual environment

**Windows PowerShell:**

```powershell
py -3.12 -m venv .venv
```

**macOS / Linux:**

```bash
python3 -m venv .venv
```

### 3. Activate the environment (optional)

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation scripts, you can skip activation and run the environment's Python executable directly (commands below). Do not weaken your machine's security settings just to activate the environment.

**Windows — without activation:**

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**macOS / Linux:**

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Install dependencies

If you activated the environment:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If you did not activate it on Windows, use the `.venv\Scripts\python.exe` commands from the previous step.

Make sure `requirements.txt` includes the dependencies used by the current code. The parser implementation in this version uses `esprima` and `pycparser`; if they are not already listed, add:

```text
esprima
pycparser
```

### 5. Configure optional API access

CodeAuditor's core structural and stylometric analysis should work without an API key. The optional assignment-requirement evaluator needs a provider key.

1. Copy `.env.example` to `.env`.
2. Open `.env` and set the provider and the corresponding API key.

Example for Gemini:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_supported_gemini_model
```

Example for OpenAI:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=your_supported_openai_model
```

Use a model name currently supported by your provider and by the SDK version installed in the environment.

**Never commit `.env`, API keys, passwords, or private credentials to GitHub.** The repository should contain `.env.example` with empty placeholder values only. If a key is accidentally pushed, revoke/rotate it immediately.

### 6. Start the application

**Windows PowerShell:**

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

**macOS / Linux (with the environment activated):**

```bash
streamlit run app.py
```

Streamlit will print a local address, usually:

```text
http://localhost:8501
```

Open that address in your browser.

## Run tests

With the virtual environment activated:

```bash
python -m pytest -q
```

On Windows without activation:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Typical workflow

1. Open the application in your browser.
2. Go to the code upload/analysis area.
3. Upload source files or paste code.
4. Select the correct language for files whose language cannot be inferred.
5. Add assignment requirements if you want to use the optional LLM evaluator.
6. Run the available analysis engines.
7. Review parser status, similarity results, and stylometric signals.
8. Export a report if required.

## Project structure

The exact folders may evolve as the team develops the project. The main modules are organized by responsibility:

```text
Code-Integrity-Auditor/
├── app.py
├── analyzers/       # Analysis coordination and risk/complexity helpers
├── engines/         # AST similarity, stylometry, and optional LLM evaluator
├── parsers/         # Language-specific parsing helpers
├── models/          # Shared result/data models
├── utils/           # File handling, language detection, and report generation
├── tests/           # Automated tests
├── datasets/        # Dataset documentation or permitted test data
├── .streamlit/      # Streamlit configuration
├── .env.example     # Safe template for local environment variables
├── .gitignore
├── requirements.txt
└── README.md
```

## Working together on GitHub

To avoid overwriting each other's work, use branches rather than having everyone commit directly to `main`.

### First-time setup for each teammate

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
cd YOUR-REPOSITORY
git switch -c feature/your-task
```

### Before starting work each day

```bash
git switch main
git pull origin main
git switch feature/your-task
git merge main
```

### Save and push your work

```bash
git add .
git commit -m "Describe the change"
git push -u origin feature/your-task
```

Then open a Pull Request on GitHub, review the changes, resolve any conflicts, and merge into `main` when ready.

### Team rules

- Do not commit `.venv`, `venv`, `__pycache__`, `.pytest_cache`, `.env`, or Streamlit secrets.
- Do not commit API keys or personal credentials.
- Do not edit the same module simultaneously without coordinating.
- Keep `requirements.txt` updated when adding or changing dependencies.
- Run the tests before opening a Pull Request.
- Use clear branch names, such as `feature/ast-engine`, `feature/dashboard`, or `fix/file-upload`.
- Keep test submissions synthetic or otherwise approved for sharing.

## Privacy and responsible use

- Only upload code you are authorized to review.
- If the optional LLM evaluator is enabled, selected code and assignment requirements are sent to the configured AI provider. Do not send confidential submissions unless you have permission and have reviewed the provider's data-handling terms.
- Similarity can occur naturally in beginner assignments, standard algorithms, templates, and code written from the same instructions.
- Stylometry is heuristic and can be affected by formatting, comments, language, and individual coding habits.
- Do not use a single score or indicator as the basis for an academic misconduct decision.

## Troubleshooting

### `streamlit` is not recognized

Run Streamlit through the virtual environment's Python executable:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

### Missing module error

Make sure the virtual environment is active (or use its Python executable), then reinstall dependencies:

```bash
python -m pip install -r requirements.txt
```

### Parser status shows fallback or parsing error

Check that the parser dependency is installed in the same environment running Streamlit. Confirm that the source uses syntax supported by the parser. JavaScript syntax newer than Esprima 4 or C requiring complex preprocessing may not parse successfully.

### API evaluator is unavailable

Check the provider setting, API key, model name, internet connection, and provider quota. The core analysis features should remain usable without the optional LLM service.
