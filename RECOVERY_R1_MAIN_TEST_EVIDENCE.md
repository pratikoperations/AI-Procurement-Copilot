# Recovery R1 Main Test Evidence

Date: 2026-07-15

## Baseline
Canonical main start SHA: `075fe16d889cdb82b126fe1e07b0c63dca369580`

## Environment
- GitHub Actions Ubuntu 24.04 runner
- Python 3.11.15
- pip 26.1.2
- Workflow-supported Python: 3.11
- Dependencies installed from pinned `requirements.txt` successfully

## Commands
- `python -m compileall app.py modules tests`
- `python -m pytest`
- `bash scripts/streamlit_smoke_test.sh`

## Result context
The canonical main release had historical acceptance records. Recovery R1 did not alter main directly. The reconstructed candidate, based on this exact main SHA, completed compile, full regression and smoke validation after the documented maintenance correction.

Historical main acceptance classification: DOCUMENTED ONLY.
Recovery candidate executable evidence is recorded in `RECOVERY_R1_MAINTENANCE_TEST_EVIDENCE.md`.
