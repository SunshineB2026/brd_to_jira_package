@echo off
REM Sets up a virtual environment and installs dependencies.
cd /d "%~dp0"

echo Creating virtual environment (.venv) ...
python -m venv .venv

echo Activating and installing dependencies ...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q

echo.
echo Done. To use the tool:
echo   1. .venv\Scripts\activate.bat
echo   2. set ANTHROPIC_API_KEY=sk-ant-...
echo   3. python test_smoke.py          ^& sanity check
echo   4. python main.py --file your_brd.docx --output stories.json
echo.
echo See README.md for Jira push setup.
