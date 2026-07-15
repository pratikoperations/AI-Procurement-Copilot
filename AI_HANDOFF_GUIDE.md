# AI Handoff Guide

## Purpose
This file is the mandatory starting point for every AI, developer and reviewer working on this repository. GitHub is the canonical source of truth; chat history is non-authoritative unless supported by repository evidence.

## Mandatory Startup Sequence
Before modifying any repository file:

1. Read `PROJECT_RECOVERY_MANIFEST.md`.
2. Read `PROJECT_STATUS.md`.
3. Read `PROJECT_BUILD_PLAN.md`.
4. Read `PENDING_WORK_REGISTER.md`.
5. Read `PROJECT_ARCHITECTURE.md`.
6. Verify the current branch and exact HEAD SHA.
7. Run the applicable full tests and Streamlit smoke test.
8. Confirm the authorized work, acceptance criteria and excluded scope.
9. Only then modify the repository.

If the correct baseline cannot be established, stop before implementation and record the discrepancy.

## Additional Required Reading
- `BUSINESS_RULES.md`
- `DATA_DICTIONARY.md`
- `SETUP_GUIDE.md`
- `CONTRIBUTING.md`
- `DECISION_LOG.md`
- `VERSION_MANIFEST.md`
- `BUILD_HISTORY.md`
- Relevant tests and validation records

## Project Position
AI Procurement Copilot is a Streamlit-based procurement decision-support portfolio application. Portfolio Edition v1.0.0 is stable and frozen. It supports packaging and raw-material procurement, supplier comparison, should-cost, TCO, risk, Supplier 360, allocation, scenarios, negotiation, communication and executive reporting.

The application is transparent, rule-guided, auditable and human-controlled. It must never be represented as an autonomous supplier-award system.

## Source-of-Truth Order
1. Executable code and tests in GitHub
2. Current recovery, status and release-control documents
3. Stable validation evidence
4. Business rules, data definitions and architecture
5. Accepted PRs and recorded decisions
6. Chat history only as non-authoritative background

## Branch Rules
- `main` is the frozen v1.0.0 stable line.
- Maintenance changes belong on the approved maintenance branch and must be limited to documented defects, security fixes or deployment fixes.
- Feature work belongs on a separate development branch based on an approved baseline.
- Undocumented work must not be promoted merely because it exists on a branch.
- Do not merge feature work directly into stable v1.0.0.

## Change Protocol
Before changing code:
- State the requested outcome and observable acceptance criteria.
- Confirm branch, HEAD, baseline and authorized scope.
- Identify affected files, calculations, schemas, fields, exports and tests.
- Separate presentation changes from business-logic changes.
- Flag ambiguity instead of inventing a rule.
- Preserve backward compatibility unless explicitly authorized.
- Do not modify unrelated files.

After changing code:
- Run focused tests.
- Run `python -m pytest`.
- Run the Streamlit smoke test where applicable.
- Perform direct functional validation for user-visible changes.
- Explain formula, threshold, schema and visible behavior changes.
- Provide rollback instructions.
- Update `PROJECT_STATUS.md`.
- Update `PROJECT_ACTIVITY_LOG.md`.
- Update `PENDING_WORK_REGISTER.md`.
- Update `PROJECT_RECOVERY_MANIFEST.md`.
- Update changelog, architecture, data dictionary or business rules where behavior changed.

A substantive build is not complete until the four mandatory project-memory files above are updated.

## Protected Areas
Do not change without explicit approval and regression coverage:
- Currency normalization and comparison basis
- Original quotation preservation
- Unit governance
- Risk Resilience terminology
- Recommendation eligibility and award-language withholding
- Evidence caps for Financial, ESG and Innovation conclusions
- Supplier-role conflict controls
- Freight-stress behavior
- Readable versus machine-readable export separation
- Human review and due-diligence requirements
- ERP intake blocking boundary before analysis

## Secrets and Data
Never commit API keys, passwords, tokens, private supplier data or production credentials. Use environment variables or Streamlit secrets and retain placeholders only in `.env.example`. Synthetic data must remain clearly identified.

## Standard Task Prompt
```text
Read PROJECT_RECOVERY_MANIFEST.md, PROJECT_STATUS.md, PROJECT_BUILD_PLAN.md, PENDING_WORK_REGISTER.md, PROJECT_ARCHITECTURE.md, BUSINESS_RULES.md, DATA_DICTIONARY.md and the relevant tests.

Verify repository, branch and HEAD. Run the required baseline tests.

Task: [describe authorized change]
Acceptance criteria: [observable outcomes]
Excluded scope: [explicit exclusions]

Do not change unrelated files or protected business rules. Record affected files, assumptions, tests, validation results, rollback steps and updates to all mandatory project-memory documents.
```