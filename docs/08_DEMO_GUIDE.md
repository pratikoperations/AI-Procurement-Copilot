# AI Procurement Copilot — Demonstration Guide

> Presentation aid for the project owner. This content is intentionally outside the public application navigation.

## Recommended current five-minute sequence

### 0:00–0:35 — Business problem

Explain that supplier decisions often sit across spreadsheets and fragmented assumptions. Lowest price alone can obscure total cost, risk, evidence quality and decision confidence.

### 0:35–1:20 — Governed sourcing workflow

Show an active analytical category and briefly demonstrate:
- category/commodity context;
- visible assumptions;
- quotation validation;
- supplier comparison;
- recommendation gating.

State: “Validation and eligibility come before recommendation language.”

### 1:20–2:20 — Calculation explainability

Open **Governed Calculation Explorer** on a supported route such as Corrugated Board.

Show:
- calculation ID and business name;
- formula/version identity;
- authoritative source module/function;
- assumptions and provenance;
- deterministic trace;
- reconciliation status.

State: “Formula metadata is documentation only. The existing business service produces the result.”

### 2:20–3:15 — SourceMate

Open **SourceMate** and demonstrate its chat-style, project-wide, read-only evidence experience.

Show:
- page-aware governed context;
- source references;
- evidence classifications;
- concise governed answers;
- browser-session conversation continuity.

State: “SourceMate helps navigate internal governed evidence. It does not browse the web, externally verify suppliers, call an external LLM, use RAG, recalculate authoritative results or execute procurement actions.”

### 3:15–4:00 — MRO / Industrial Supplies Foundation Preview

Select **Indirect Procurement → MRO / Industrial Supplies → Industrial Bearings**.

Explain:
- manufacturer + manufacturer-part-number identity;
- OEM / Authorized Distributor / Approved Equivalent status;
- technical/evidence requirements;
- fail-closed compatibility;
- human approval for equivalent substitution.

State: “This is a Foundation Preview, not a production MRO analytics engine.”

Explicitly note that MRO should-cost, scoring, scenarios, negotiation and allocation execution are intentionally disabled.

### 4:00–4:35 — Logistics & Freight decision support

Select **Indirect Procurement → Logistics & Freight → Domestic Road Transportation — FTL**.

Explain the four governed layers:
- freight-rate normalization from explicit commercial inputs;
- buyer-threshold carrier performance evaluation;
- human-proposed allocation and demand-stress scenarios;
- explicit buyer negotiation positions and commercial deltas.

State: “The Logistics workflow evaluates evidence and explicit scenarios. It does not rank carriers with hidden weights, optimize award shares, infer live route/fuel data, negotiate autonomously or execute an award.”

### 4:35–4:50 — Honest limitation handling

Show either:
- a deferred adapter route such as Packaging TCO; or
- an unavailable evidence state.

Explain:
- unavailable/deferred evidence remains visible;
- no trace or reconciliation is fabricated;
- human review remains mandatory.

### 4:50–5:00 — Close

State that the project proves:
- procurement workflow understanding;
- governed decision-support design;
- explainability and evidence discipline;
- cross-category extensibility;
- automated testing and GitHub governance.

It does **not** prove production adoption, realized savings, autonomous procurement or live ERP execution.

## Optional deeper EAS-BIV sequence

For technical interviewers, use the earlier explainability-focused path:

1. Corrugated Board authoritative result.
2. Assumption provenance.
3. Deterministic calculation trace.
4. Reconciliation.
5. SourceMate evidence navigation.
6. Deferred adapter coverage.

Historical EAS-BIV evidence remains preserved in the Interview Evidence Pack and Final Closure documents.

## Cross-category confirmation

Use short confirmations only:
- PET Resin — raw-material-style transferability;
- Kraft Paper — commodity packaging should-cost;
- Flexible Laminates — conversion complexity;
- Steel — non-packaging transferability;
- Industrial Bearings — governed MRO foundation;
- Domestic Road Transportation — FTL — governed freight normalization, carrier policy checks, human-proposed allocation scenarios and negotiation deltas;
- Packaging TCO — honest deferred-coverage boundary.

## Strong phrases

- Governed decision support, not autonomous procurement.
- Lowest price is an input; best value is the decision context.
- Validation and eligibility come before recommendation language.
- Formula metadata is documentation only; authoritative services produce results.
- Unavailable evidence is disclosed and is not reconstructed.
- SourceMate presents governed internal evidence; it does not externally verify it.
- Deferred routes are not represented as adapter-reconciled.
- MRO equivalent substitution requires human approval.
- Logistics allocation scenarios are human-proposed; the system does not optimize carrier awards.
- Logistics negotiation targets are explicit buyer inputs; potential savings are scenario deltas, not realized savings.
- Human procurement review remains mandatory.

## Demonstration discipline

- Use synthetic or sanitized data.
- Do not present illustrative values as realized savings.
- Do not call draft mapping profiles integrations.
- Do not call registered evidence external verification.
- Do not call a deferred route reconciled.
- Do not describe MRO-0 as a production-ready MRO analytics engine.
- Keep technical detail subordinate to procurement value.
- Do not claim physical browser/mobile certification unless actual evidence is recorded.
- Hosted acceptance remains separate from CI evidence.

See also:
- [EAS-BIV Final Closure](EAS_BIV_FINAL_CLOSURE.md)
- [EAS-BIV Interview Evidence Pack](EAS_BIV_INTERVIEW_EVIDENCE_PACK.md)
