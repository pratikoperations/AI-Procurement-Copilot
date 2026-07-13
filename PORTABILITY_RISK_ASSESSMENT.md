# Portability Risk Assessment

**Repository:** `pratikoperations/AI-Procurement-Copilot`  
**Baseline:** Portfolio Edition v1.0.0 (Stable)  
**Scope:** Documentation, environment governance, and handoff controls only. No business logic changes.

## Executive Assessment

The application is operationally portable because its Python, Streamlit, data-processing logic, tests, and dependency manifest are stored in GitHub. The main remaining risk is knowledge portability: a new LLM or developer may not understand calculation ownership, protected rules, data contracts, validation gates, and deployment assumptions without structured documentation.

## Risk Register

| Risk | Current level | Impact | Required control |
|---|---|---|---|
| Critical decisions exist only in chat history | High | Rework or inconsistent changes | Store architecture, rules, data definitions, and decisions in GitHub |
| New assistant changes formulas without context | High | Incorrect recommendations | Protected business-rule register and mandatory tests |
| Environment cannot be reproduced | Medium | Setup failures | Pinned dependencies, setup guide, environment template |
| Secrets are committed or copied into prompts | Medium | Security exposure | `.env.example`, secret-handling rules, deployment guide |
| Data fields are interpreted inconsistently | Medium | Wrong calculations or labels | Data dictionary and missing-data rules |
| Stable release is modified directly | Medium | Regression risk | Branch + pull-request workflow |
| One LLM provider becomes unavailable | Low | Development interruption | Provider-neutral handoff process; current runtime is not LLM-dependent |

## Portability Rating

- **Code ownership:** Strong
- **Runtime independence from ChatGPT:** Strong
- **Environment reproducibility:** Good
- **Business-rule discoverability:** Needs improvement
- **Cross-LLM handoff:** Needs improvement
- **Overall current portability:** Medium-High
- **Target after this change:** High

## Non-Negotiable Controls

1. GitHub remains the canonical source of truth.
2. Stable business logic is not changed during portability work.
3. Every future logic change must include tests and documented rationale.
4. Real credentials must never be committed.
5. A new assistant must read the handoff, architecture, business-rules, and data-dictionary documents before editing code.
6. Human procurement approval and due diligence remain mandatory.
