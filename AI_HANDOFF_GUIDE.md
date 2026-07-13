# AI Handoff Guide

## Purpose

This file is the mandatory starting point for ChatGPT, Claude, Gemini, coding agents, and human developers working on this repository.

## Read Before Editing

1. `README.md`
2. `PORTABILITY_RISK_ASSESSMENT.md`
3. `PROJECT_ARCHITECTURE.md`
4. `BUSINESS_RULES.md`
5. `DATA_DICTIONARY.md`
6. `SETUP_GUIDE.md`
7. `CONTRIBUTING.md`
8. Relevant tests and validation records

## Project Position

AI Procurement Copilot is a Streamlit-based procurement decision-support portfolio application. Portfolio Edition v1.0.0 is stable. It supports Packaging Procurement and Raw Material Procurement workflows, supplier comparison, should-cost, TCO, risk, Supplier 360, allocation, scenarios, negotiation, communication, and executive reporting.

The application is transparent, rule-guided, auditable, and human-controlled. It must not be represented as an autonomous supplier-award system.

## Source-of-Truth Order

1. Executable code and tests in GitHub
2. Stable release and validation documents
3. Business-rule and data-definition documents
4. Pull-request discussion and accepted decisions
5. Chat history only as non-authoritative background

## Change Protocol

Before changing code:

- State the requested outcome and acceptance criteria.
- Identify affected files, calculations, data fields, exports, and tests.
- Distinguish a presentation change from a business-logic change.
- Flag any ambiguity instead of silently inventing a rule.
- Preserve backward compatibility unless the task explicitly changes it.
- Never modify unrelated files.

After changing code:

- Run `python -m pytest`.
- Run a Streamlit smoke test where practical.
- Explain formula, threshold, schema, and user-visible changes.
- Update documentation and changelog when behaviour changes.
- Provide rollback instructions.

## Protected Areas

Do not change without explicit approval and regression coverage:

- Currency normalization and comparison basis
- Original quotation preservation
- Unit governance
- Risk Resilience terminology
- Recommendation eligibility and award-language withholding
- Evidence caps for Financial, ESG, and Innovation conclusions
- Supplier-role conflict controls
- Freight-stress behaviour
- Readable versus machine-readable export separation
- Human review and due-diligence requirements

## Secrets

Never commit API keys, passwords, tokens, private supplier data, or production credentials. Use environment variables or Streamlit secrets and keep only placeholders in `.env.example`.

## Standard Task Prompt

```text
Read AI_HANDOFF_GUIDE.md, PROJECT_ARCHITECTURE.md, BUSINESS_RULES.md, DATA_DICTIONARY.md, and the relevant tests before editing.

Task: [describe change]
Acceptance criteria: [list observable outcomes]

Do not change unrelated files or protected business rules. Show affected files, assumptions, tests, validation results, and rollback steps.
```
