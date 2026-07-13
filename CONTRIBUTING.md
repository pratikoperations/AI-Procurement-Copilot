# Contributing

## Workflow

1. Create a focused branch from the intended base.
2. Read the handoff, architecture, business-rules, and data-dictionary documents.
3. Define acceptance criteria before editing.
4. Make the smallest coherent change.
5. Add or update tests.
6. Run `python -m pytest` and a Streamlit smoke test where relevant.
7. Open a pull request with risks, assumptions, evidence, and rollback steps.

## Branch Names

- `docs/<topic>`
- `fix/<defect>`
- `feature/<capability>`
- `test/<coverage>`

## Pull-Request Requirements

- Problem and intended outcome
- Files and workflows affected
- Business-rule or schema impact
- Tests executed and results
- Screenshots/artifacts for visible or export changes
- Security and privacy considerations
- Rollback method

## Rules for AI-Generated Changes

- Never paste secrets or confidential supplier data into an assistant.
- Do not accept code without reviewing the diff.
- Do not allow an assistant to invent formulas, FX rates, defaults, or thresholds.
- Require targeted tests for calculations and governance.
- Keep unrelated formatting or refactoring out of focused changes.
- Treat GitHub, not chat history, as the authoritative project record.

## Stable Release Policy

Portfolio Edition v1.0.0 is stable. Maintenance must preserve documented behaviour. New capabilities belong in an explicitly planned future-release branch.
