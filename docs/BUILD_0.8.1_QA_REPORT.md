# Build 0.8.1 QA Report

## Build

Build 0.8.1 — Deployment Stabilization

## Deployment Incident

Streamlit Community Cloud installed the application using Python 3.14.6 and a very recent dependency set. The application cloned, installed, launched, and rendered before the process terminated with a native segmentation fault.

No Python traceback identified an application or procurement-engine error.

## Remediation

- Added `runtime.txt` with `python-3.11`.
- Pinned exact dependency versions in `requirements.txt`.
- Added an explicit NumPy version to avoid uncontrolled binary upgrades.
- Kept GitHub Actions on Python 3.11 to align CI with deployment.
- Replaced deprecated Streamlit `use_container_width=True` arguments with `width="stretch"`.

## Quality Gates

| Gate | Result | Notes |
|---|---|---|
| Runtime reproducibility | Pass | Python and direct dependencies are pinned |
| CI/deployment alignment | Pass by configuration | Both target Python 3.11 |
| Deprecation cleanup | Pass | Known width warnings removed from dashboard rendering |
| Procurement logic changes | None | No commercial model logic changed |
| Post-change CI | Pending | Await latest Quality Checks result |
| Cloud deployment | Pending | App must reboot or redeploy using the new runtime |
| Manual visual review | Pending | Required after deployment succeeds |

## Risk Assessment

The segmentation fault is classified as a deployment environment compatibility incident. The controlled Python 3.11 baseline substantially reduces the likelihood of the same native crash recurring.

## Release Decision

Do not freeze Portfolio Edition v1.0 until:

1. Post-stabilization Quality Checks are green.
2. Streamlit Cloud logs confirm Python 3.11.
3. The application remains open without a segmentation fault.
4. All six tabs, sample upload, and download buttons are manually reviewed.
