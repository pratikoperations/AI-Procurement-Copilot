# Setup Guide

## Prerequisites

- Git
- Python 3.11
- Access to this GitHub repository

Python 3.11 is the repository's verified CI version. `.github/workflows/quality-checks.yml` configures `actions/setup-python@v5` with `python-version: "3.11"`, then compiles `app.py`, `modules`, and `tests`, runs the full pytest suite, and executes the Streamlit smoke test. Other Python versions are not claimed as validated unless separately tested and documented.

## Local Setup

```bash
git clone https://github.com/pratikoperations/AI-Procurement-Copilot.git
cd AI-Procurement-Copilot
python -m venv .venv
```

Activate the environment:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

Install dependencies and run tests:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m compileall app.py modules tests
python -m pytest
```

Run the application:

```bash
streamlit run app.py
```

## Environment Variables

Stable Portfolio Edition v1.0.0 does not require ChatGPT, Claude, Gemini, a database connection, or any external LLM API key to run. `.env.example` contains optional placeholders only for possible future integrations. Do not create or populate them unless a separately approved integration requires them. Never commit real values.

## Verification Checklist

- `python --version` reports Python 3.11.x for parity with CI.
- Application starts without import errors.
- Demo data loads.
- Packaging and Raw Material workflows render.
- Full tests pass.
- Currency, unit, eligibility and export controls remain visible.
- Streamlit smoke test succeeds where the script environment is available.

## Cross-LLM Handoff

A new assistant should receive the repository or relevant files and be instructed to read `AI_HANDOFF_GUIDE.md`, `FORMULA_TRACEABILITY_REGISTER.md`, `PROJECT_ARCHITECTURE.md`, `BUSINESS_RULES.md`, and `DATA_DICTIONARY.md` before proposing changes. Chat history is not required to run the app.