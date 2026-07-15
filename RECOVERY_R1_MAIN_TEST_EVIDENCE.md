# Recovery R1 Main Test Evidence

Date: 2026-07-15

## Exact Baseline
Canonical main SHA tested independently: `075fe16d889cdb82b126fe1e07b0c63dca369580`

The workflow explicitly checked out this exact SHA. The PR candidate code was not used for this run.

## Environment
- GitHub Actions Ubuntu 24.04 runner
- Python 3.11.15
- pip 26.1.2
- Workflow-supported Python: 3.11
- Dependencies installed successfully from pinned `requirements.txt`

## Commands
- `python -m compileall app.py modules tests`
- `python -m pytest`
- `bash scripts/streamlit_smoke_test.sh`

## Results
- Exact tested SHA: `075fe16d889cdb82b126fe1e07b0c63dca369580`
- Dependency installation: PASS
- Compile: PASS
- Pytest: `114 passed, 0 failed, 0 skipped, 1 warning in 1.89s`
- Streamlit startup smoke: PASS
- Classification: VERIFIED COMPLETE

## Warning
Existing pandas `FutureWarning` in `tests/test_adversarial_inputs.py::test_decimal_percentage_is_flagged`.

## Evidence
GitHub Actions run `29403967641`; artifact `recovery-r1-main-baseline-evidence`, digest `sha256:7f0463c8f7baa3c863925de3d7c42afc921fc954f90cafb9b71c50c47878f8d4`.

No modification was made to `main` to obtain this result. The temporary diagnostic workflow on the recovery branch was restored to the canonical workflow before finalization.
