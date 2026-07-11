# Build 1.0 RC1.2.3 — Scenario Engine Column Alignment Critical Hotfix

## Purpose

Resolve the runtime `KeyError` in the Multi-Scenario Stress Test without changing scoring, recommendation logic, or scenario business rules.

## Root cause

Build 1.0 RC1.2.2 standardized the scenario dataframe to executive-readable headings such as:

- `Annual TCO (USD)`
- `Risk Resilience Score`
- `Risk-Adjusted TCO per kg (USD)`

The dashboard renderer still referenced the legacy heading:

- `Annual TCO USD`

This schema mismatch caused the Streamlit runtime failure in `render_scenario_table()`.

## Resolution

- Added a reusable scenario-column resolver.
- Made the renderer prefer the governed schema.
- Preserved backward compatibility with legacy column names.
- Updated chart and INR conversion logic to use the resolved annual-TCO column.
- Preserved category-aware TCO labels from the scenario engine.
- Added regression coverage for Raw Material and Packaging scenario contracts.

## Files changed

- `modules/dashboard.py`
- `modules/config.py`
- `tests/test_scenario_dashboard_schema.py`

## Validation coverage

Tests verify:

- Governed `Annual TCO (USD)` is resolved correctly.
- Legacy `Annual TCO USD` remains supported.
- Missing required schema raises a clear controlled error.
- Packaging and Raw Material scenarios share the renderer contract.
- Base Case, Freight +50%, Demand -25%, and Combined Stress remain present.
- Risk Resilience Score remains available.

## Release boundary

- No scoring change
- No recommendation change
- No allocation change
- No scenario formula change
- No new feature
- Release freeze remains active

GitHub Actions, Streamlit smoke testing, and live scenario retest remain mandatory before release approval.
