# Architecture Decision Records

## Purpose

This directory records material architecture decisions for `pratikoperations/AI-Procurement-Copilot`. ADRs preserve accepted intent, decision drivers, trade-offs, consequences, controls and reverification triggers. They are concise governance records, not implementation specifications, activity logs or project-status reports.

## Naming Convention

Use:

`ADR-NNN-short-decision-title.md`

Numbers are sequential and never reused. Accepted ADR files are not deleted or rewritten to erase history.

## Status Values

- **Proposed** — under governed review.
- **Accepted for current portfolio architecture, subject to governed change control** — currently authoritative architectural intent.
- **Superseded** — replaced by a later accepted ADR; retain the original file and link both records.
- **Deprecated** — retained for history but no longer recommended.
- **Rejected** — considered and not adopted.

## Source-of-Truth Position

ADRs record accepted architectural intent but do not override:

1. immutable Git objects and current refs;
2. CI and validation evidence tied to exact SHAs;
3. executable contracts, code and tests.

`PROJECT_CONTROL.md` is the current operational index. `PROJECT_ARCHITECTURE.md` describes the broader architecture. ADRs explain why specific material choices were accepted. Where evidence conflicts, the higher-authority source prevails and the affected ADR must be reverified.

## Creation and Amendment

Create an ADR only for a material decision that affects boundaries, authority, interfaces, business-risk controls or long-term implementation direction. Use the standard sections:

- Title
- Status
- Context
- Decision
- Decision Drivers
- Considered Alternatives
- Consequences
- Risks and Controls
- Scope
- Non-Scope
- Evidence
- Reverification Triggers

Amend an accepted ADR only through an explicitly scoped, reviewed and CI-validated change. Minor factual corrections may update the existing ADR. A changed decision requires a new ADR that supersedes the prior record.

## Supersession

A superseding ADR must identify the earlier ADR, explain why the decision changed and state the effective scope. Do not delete accepted ADR history.

## Relationship to Other Governance

- `PROJECT_CONTROL.md`: current verified state and active/deferred scope.
- `DEFINITION_OF_DONE.md`: completion and merge evidence requirements.
- `SIMPLICITY_GATE.md`: approval, simplification, deferral and rejection tests.
- `VERIFICATION_POLICY.md`: change-triggered reverification and evidence reuse.
- `PROJECT_ARCHITECTURE.md`: broader component and integration structure.
- Executable code and tests: authoritative implemented behaviour.

## Reverification

Reverify an ADR when its relevant code, contract, architecture, workflow, dependency, interface, business rule, evidence source, production classification or governance constraint changes. Record exact Git and CI evidence in the governed review rather than attempting to embed moving SHAs in every ADR.

## Concise Maintenance Rule

State the decision and its rationale once. Link evidence instead of copying formulas, detailed business rules, test-risk registers, component explainers, activity logs or status history. Do not document speculative or unimplemented production architecture as accepted.