@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Creating local Python environment...
    py -3 -m venv .venv
    if errorlevel 1 (
        echo Could not create environment. Install Python 3.11+ from python.org and retry.
        pause
        exit /b 1
    )
)
echo Installing or updating project dependencies...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo Dependency installation failed. Check internet access and Python version.
    pause
    exit /b 1
)
echo Starting CodeAuditor locally...
".venv\Scripts\python.exe" -m streamlit run app.py
pause
