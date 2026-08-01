#!/usr/bin/env bash
# Sets up a virtual environment and installs dependencies.
set -e

cd "$(dirname "$0")"

echo "Creating virtual environment (.venv) ..."
python3 -m venv .venv

echo "Activating and installing dependencies ..."
source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo ""
echo "Done. To use the tool:"
echo "  1. source .venv/bin/activate"
echo "  2. export ANTHROPIC_API_KEY=\"sk-ant-...\""
echo "  3. python test_smoke.py          # sanity check"
echo "  4. python main.py --file your_brd.docx --output stories.json"
echo ""
echo "See README.md for Jira push setup."
