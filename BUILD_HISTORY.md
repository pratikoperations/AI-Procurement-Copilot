# Build History

## Build 0.8.1 — Deployment Stabilization

**Status:** Completed — Cloud Redeployment Validation Pending  
**Objective:** Resolve Streamlit Community Cloud instability and make deployment reproducible.

### Completed

- Added `runtime.txt` with Python 3.11.
- Pinned Streamlit, Pandas, NumPy, Plotly, OpenPyXL, Pydantic, and Pytest versions.
- Replaced deprecated `use_container_width` usage with `width="stretch"`.
- Aligned deployment expectations with the Python 3.11 GitHub Actions environment.
- Updated project status, changelog, and application configuration.

### Incident Summary

Streamlit Community Cloud installed the app on Python 3.14.6 and later terminated the process with a native segmentation fault. Dependency installation and application startup completed before the crash, and no Python traceback indicated a procurement-engine error.

### QA Result

- Root-cause classification: Environment/runtime compatibility issue
- Code-level procurement defect: Not identified
- New GitHub Actions run: Pending confirmation
- Streamlit Cloud reboot/redeployment: Pending

### Outcome

Build 0.8.1 creates a controlled Python 3.11 deployment environment and removes deprecated Streamlit calls that were generating repeated runtime warnings.

### Next

Validate green CI and successful Streamlit Community Cloud deployment, then complete the Portfolio Edition v1.0 release freeze.

---

## Build 0.8 — Portfolio Edition v1.0 Release Candidate

**Status:** Completed — CI Validated  
**Objective:** Add final automated validation, prepare portfolio assets, and promote the project to release-candidate status.

### Completed

- Added export regression tests and Streamlit health smoke testing.
- Added portfolio, demo, and screenshot guidance.
- Promoted application to release-candidate status.

### Outcome

Build 0.8 closed automated-test coverage gaps and achieved green CI before cloud deployment testing.

---

## Build 0.7 — Downloadable Outputs and Release-Candidate Preparation

**Status:** Completed — CI Validated

### Completed

- Added Excel, CSV, TXT, and JSON exports.
- Added six-step interview workflow.
- Remediated pytest import-path defect.

---

## Build 0.6 — UX, Validation, Testing, and Documentation

**Status:** Completed

### Completed

- Added RFQ/output validation, regression tests, GitHub Actions, user guide, and tabbed workflow.

---

## Build 0.5 — Executive Communication Layer

**Status:** Completed

### Completed

- Added executive memo, supplier email, explainability, interview outputs, and QA protocol.

---

## Build 0.4 — Decision Intelligence

**Status:** Completed

### Completed

- Added best-value logic, allocation, scenarios, negotiation, confidence, and executive value.

---

## Build 0.3 — Packaging Procurement Engines

**Status:** Completed

### Completed

- Added should-cost, TCO, risk, ESG, performance, and supplier scoring engines.

---

## Build 0.2 — Modular Streamlit Framework

**Status:** Completed

### Completed

- Added modular app structure, sidebar, dashboard, loaders, utilities, and sample RFQ.

---

## Build 0.1 — Repository Foundation

**Status:** Completed

### Completed

- Created repository governance, recovery, architecture, build plan, documentation, and initial app skeleton.
