# Recovery R1 Deployment Evidence

Date: 2026-07-15

## CI Runtime
- Candidate Streamlit smoke: PASS
- Exact main SHA Streamlit smoke: PASS
- Command: `bash scripts/streamlit_smoke_test.sh`
- Classification: VERIFIED COMPLETE

## Authoritative Hosted Candidate
- URL: `https://ai-procurement-copilot-pr9.streamlit.app/`
- Repository: `ai-procurement-copilot`
- Branch: `recovery/r1-v1.0.1-baseline-verification`
- Main module: `app.py`
- Python: 3.11.15
- Streamlit: 1.59.1
- Dependency installation: PASS
- Server startup: PASS (`Uvicorn server started on :::8501`)

## Hosted Acceptance
The project owner opened the hosted candidate and confirmed the application, all six supplier views, and USD/INR/Both modes looked correct. This is owner-observed manual acceptance and is recorded separately from CI smoke evidence.

- Hosted application response/startup: VERIFIED COMPLETE
- Fatal-error inspection: VERIFIED COMPLETE
- Hosted USD mode: VERIFIED COMPLETE
- Hosted INR mode: VERIFIED COMPLETE
- Hosted Both mode: VERIFIED COMPLETE
- Current hosted deployment health: VERIFIED COMPLETE

Historical deployment acceptance remains DOCUMENTED ONLY; the result above applies specifically to the Recovery R1 candidate URL and branch.
