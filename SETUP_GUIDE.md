# Setup Guide

## Prerequisites

- Git
- Python 3.11 recommended
- Access to this GitHub repository

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
python -m pytest
```

Run the application:

```bash
streamlit run app.py
```

## Environment Variables

The stable v1.0.0 runtime does not require ChatGPT access. For future external integrations, copy `.env.example` to a local `.env` or configure Streamlit secrets. Never commit real values.

## Verification Checklist

- Application starts without import errors.
- Demo data loads.
- Packaging and Raw Material workflows render.
- Tests pass.
- Currency, unit, eligibility, and export controls remain visible.

## Cross-LLM Handoff

A new assistant should receive the repository or relevant files and be instructed to read `AI_HANDOFF_GUIDE.md` before proposing changes. Chat history is not required to run the app.
