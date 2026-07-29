# Build Group D Acceptance Criteria

- Consumes Build Group C `AdapterResult` without modifying the adapter.
- Adds only the ten authorized Build Group D files.
- Evaluation-date precedence is deterministic and recorded.
- Comparison currency never defaults silently to USD.
- Currency and UOM normalization preserve source values and expose provenance.
- Missing FX/UOM evidence blocks normalization.
- Expired quotations are visible but ineligible.
- Full Review history metadata, window, and 60-day staleness are governed.
- Evidence weights total 100%; missing evidence receives zero and no partial credit.
- Item coverage uses the minimum valid supplier; event aggregation discloses its method.
- Eligibility language is analysis-only.
- Adapter findings are preserved.
- Focused tests, full regression tests, and Streamlit smoke test pass.
- No UI, scoring, TCO, recommendation, persistence, SAP, deployment, tag, release, or Build Group E change.
