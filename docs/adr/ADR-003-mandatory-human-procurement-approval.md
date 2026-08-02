# ADR-003 — Mandatory Human Procurement Approval

## Status

Accepted for current portfolio architecture, subject to governed change control.

## Context

The application generates procurement recommendations, comparisons, scenarios and allocation outputs. These outputs can inform commercial decisions but do not constitute delegated authority, contractual approval or ERP authorization.

## Decision

Every recommendation requires explicit human procurement review and approval.

The system must not autonomously award business, approve suppliers, write back to ERP, persist formal approvals or claim realized savings without organizational evidence. AI-generated narrative, summaries and explanations are advisory and must never be treated as procurement authorization.

## Decision Drivers

- Preserve accountable commercial decision-making.
- Prevent unsupported commitments and approvals.
- Separate analysis from delegated authority.
- Maintain auditability and interview credibility.
- Control legal, financial, supplier and compliance risk.

## Considered Alternatives

- **Autonomous award within predefined limits:** rejected for the current portfolio scope.
- **Treat an AI narrative as approval evidence:** rejected because narrative is not delegated authority.
- **Persist approvals without enterprise controls:** rejected due to identity, audit and authorization gaps.

## Consequences

UI and exports must visibly state that outputs are recommendations. Future workflow integration must preserve named human approvers, evidence and organizational authorization. Automation may prepare evidence but cannot replace the accountable decision owner.

## Risks and Controls

- **Risk:** users interpret ranking as award approval. **Control:** mandatory approval language and non-authoritative status.
- **Risk:** future ERP integration bypasses governance. **Control:** separate production authorization and approval controls.
- **Risk:** claimed savings exceed verified outcomes. **Control:** distinguish estimated opportunity from realized savings.

## Scope

Supplier recommendations, allocation outputs, negotiation scenarios, risk assessments, explanations, exports and future workflow integration.

## Non-Scope

The design of a production approval workflow, enterprise identity model or ERP transaction process.

## Evidence

- `PROJECT_CONTROL.md`
- `BUSINESS_RULES.md`
- `docs/07_GOVERNANCE_AND_LIMITATIONS.md`
- `modules/allocation_contract.py`
- `modules/multi_supplier_allocation.py`
- `modules/multi_supplier_allocation_adapter.py`
- Relevant tests
- Merged PRs #45, #46 and #47

## Reverification Triggers

Changes to approval workflow, ERP integration, persistence, identity, authorization, autonomous action, supplier award, savings classification or output status language.