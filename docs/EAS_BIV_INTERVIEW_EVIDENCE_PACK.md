# EAS-BIV Interview Evidence Pack

## Positioning statement

AI Procurement Copilot is a governed procurement decision-support portfolio. The EAS-BIV programme adds calculation explainability, assumption provenance, deterministic traces, reconciliation, internal evidence navigation and explicit human-review controls without replacing the existing business engines.

## Five-minute demonstration script

### 0:00–0:35 — Business problem

“Procurement calculations often sit across spreadsheets, category models and undocumented assumptions. A result may be numerically correct but difficult to explain, reproduce or govern. This project makes the calculation source, assumptions, trace, reconciliation and evidence boundaries visible.”

### 0:35–1:15 — Authoritative Corrugated Board result

Open the Governed Calculation Explorer and select the Corrugated Board route.

Explain:

- the result comes from the existing authoritative should-cost service;
- formula text is documentation only;
- the Explorer does not independently recalculate the answer;
- the source module, source function, calculation ID and formula version remain visible.

### 1:15–2:00 — Assumption provenance

Open **Assumptions**.

Explain:

- supplied values originate from the current case;
- defaulted values come from governed defaults;
- inferred values are explicitly labelled rather than hidden;
- derived values are calculated outputs rather than source claims;
- uncatalogued or unavailable evidence remains visible.

### 2:00–2:50 — Trace and configuration identity

Open **Calculation Trace**.

Show:

- deterministic trace ID;
- `AIPC-CALC-TRACE-1.0`;
- calculation and formula identity;
- input snapshot and authoritative raw output;
- available intermediate steps;
- configuration versions;
- explicit unavailable-evidence disclosure where evidence is absent.

Say: “The trace supports review and repeatability. It does not create another calculation engine.”

### 2:50–3:35 — Reconciliation

Open **Reconciliation**.

Show:

- exact matches;
- tolerated differences;
- mismatches;
- unavailable evidence;
- blocking or review-required status;
- mandatory human review.

Say: “The system does not convert an unresolved mismatch into an approved result.”

### 3:35–4:20 — SourceMate Basic

Open **SourceMate**.

Show:

- source module and function;
- formula and catalogue references;
- assumption source references;
- registered Excel and JSON evidence locations;
- evidence classification and review-expiry warnings;
- runtime-presence and external-verification limitations.

Say: “SourceMate is an internal evidence navigator, not a web-research agent or external verification service.”

### 4:20–5:00 — Deferred coverage and governance close

Select Packaging TCO.

Explain:

- the existing authoritative service executes;
- a dedicated governed trace adapter remains deferred;
- no trace or reconciliation evidence is fabricated;
- the checklist records unavailable evidence honestly;
- no autonomous recommendation, award or production allocation occurs;
- human approval remains mandatory.

Close with:

“This demonstrates governed decision support: business results remain authoritative, evidence boundaries remain visible, and missing assurance is disclosed rather than invented.”

## Cross-category confirmations

| Route | Interview value | Governed evidence |
|---|---|---|
| Corrugated Board | Primary packaging should-cost story | Adapter-backed trace and reconciliation |
| PET Resin | Raw-material-style packaging input | Adapter-backed trace and reconciliation |
| Kraft Paper | Commodity packaging model | Adapter-backed trace and reconciliation |
| Flexible Laminates | Multi-component conversion complexity | Adapter-backed trace and reconciliation |
| Steel | Transferability beyond packaging | Adapter-backed trace and reconciliation |
| Packaging TCO | Honest limitation demonstration | `unsupported_deferred_coverage`; no fabricated trace |

The registry also retains adapter-backed coverage for generic scoring and recommendation eligibility, but they are not required in the five-minute hosted demonstration.

## Strongest business-value messages

1. **Faster review:** reviewers can see result, assumptions, source and evidence in one governed view.
2. **Reduced ambiguity:** supplied, defaulted, inferred and derived values are not mixed together.
3. **Defensible decisions:** trace and reconciliation evidence explain how a supported route aligns with its authoritative service.
4. **Controlled limitation handling:** deferred coverage and unavailable evidence are disclosed rather than hidden.
5. **Human accountability:** the system supports procurement judgement but does not approve or award suppliers.
6. **Cross-category transferability:** the same governance pattern works across packaging, raw-material and steel examples.

## Technical evidence

- Trace contract: `AIPC-CALC-TRACE-1.0`
- Explorer contract: `AIPC-GOVERNED-EXPLORER-1.0`
- SourceMate contract: `AIPC-SOURCEMATE-BASIC-1.0`
- Gate 4 merge commit: `834b34db145cc0156196579f7419e7db7b438106`
- Accepted CI: Quality Checks run `816`
- Run ID: `30706340753`
- Job ID: `91386012618`
- Python: `3.11.15`
- Tests: `1011 passed`, `0 failures`, `0 errors`
- Compilation: passed
- Streamlit smoke: passed
- Warning boundary: one pre-existing pandas `FutureWarning`; no new Gate 4 warning

## Adapter-backed coverage

- `REC-PET`
- `REC-KRF`
- `REC-COR`
- `REC-LAM`
- `REC-STL`
- `REC-SCORE-GEN`
- `REC-ELG`

All remaining non-export routes remain `unsupported_deferred_coverage`.

## Procurement evidence

The showcase demonstrates practical understanding of:

- category-specific should-cost review;
- assumption governance;
- sourcing evidence and auditability;
- total-cost and decision-quality boundaries;
- supplier-review controls;
- validation before recommendation language;
- separation of business results from human approval.

## Governance evidence

- authoritative services remain primary;
- formula metadata is non-executable;
- unavailable evidence is not inferred;
- SourceMate does not claim external verification;
- deferred routes are not presented as reconciled;
- checklist statuses are evidence-derived;
- no approval persistence exists;
- human review remains mandatory.

## Difficult interviewer objections and defensible answers

### “Is this just a dashboard over hardcoded examples?”

**Answer:** “The public demonstration uses controlled synthetic inputs, but the governance layer is connected to existing category services and governed contracts. The key evidence is not the visual layout alone: calculation identities, provenance, trace construction, reconciliation classifications and export evidence are covered by automated tests. It still does not prove enterprise production adoption.”

### “Does the formula shown in the Explorer generate the result?”

**Answer:** “No. Formula text is non-executable metadata. The existing category service remains authoritative. This avoids creating two competing calculation engines.”

### “Can SourceMate verify supplier evidence from the internet?”

**Answer:** “No. SourceMate Basic presents registered internal evidence references, classifications and limitations. It does not browse, use RAG, run OCR or claim external verification.”

### “Why are some routes marked deferred?”

**Answer:** “The BIV deliberately implements representative governed adapters rather than pretending every service has equivalent trace assurance. Deferred routes remain usable through their authoritative service, but they are labelled `unsupported_deferred_coverage` and are not represented as reconciled.”

### “Does the tool recommend or award a supplier?”

**Answer:** “It provides controlled decision support and may display recommendation-oriented analysis where validation allows it, but no autonomous award, production allocation or approval persistence exists. Human procurement approval remains mandatory.”

### “Does 1,011 tests mean production-ready?”

**Answer:** “No. It means the repository has strong automated regression, compilation and startup evidence. Production readiness would additionally require enterprise identity, security, privacy, monitoring, operational ownership, live-data validation and scale testing.”

### “Have you proven realized savings?”

**Answer:** “No. Demonstration values are illustrative and must not be presented as realized savings. The project proves workflow and governance capability, not organizational financial outcomes.”

### “Has mobile behavior been certified?”

**Answer:** “No formal device certification is claimed. Source and automated controls exist, but physical desktop and Android observations remain `not performed` unless separately evidenced.”

### “Why not add all remaining adapters before calling it complete?”

**Answer:** “The objective is a Basic Interview Version, not exhaustive production coverage. The representative routes prove the architecture, while the deferred registry demonstrates scope discipline and honest assurance boundaries.”

## What the showcase proves

- procurement workflow and category understanding;
- ability to turn governance requirements into working software contracts;
- explainability without duplicate calculation logic;
- explicit provenance and evidence boundaries;
- deterministic trace and reconciliation controls;
- cross-category design transferability;
- automated testing and staged GitHub governance;
- ability to communicate limitations clearly.

## What the showcase does not prove

- production deployment readiness;
- live ERP integration or write-back;
- universal adapter coverage;
- enterprise-scale performance or security;
- external evidence verification;
- supplier qualification, legal or audit completion;
- realized savings;
- autonomous sourcing, approval or award;
- formal browser/mobile or WCAG certification.

## Exact limitation language

Use these statements without dilution:

- “Formula metadata is documentation only; authoritative services produce business results.”
- “Unavailable evidence is disclosed and is not reconstructed.”
- “SourceMate Basic presents internal evidence references and does not perform external verification.”
- “Deferred routes are not represented as adapter-reconciled.”
- “Illustrative outputs are not realized-savings claims.”
- “No autonomous award or production allocation is performed.”
- “Human procurement approval remains mandatory.”
- “Automated and source-level validation do not constitute physical browser-device certification.”

## Demonstration discipline

- use synthetic or sanitized data;
- keep procurement value ahead of technical implementation detail;
- do not call internal evidence registration external verification;
- do not call a deferred route reconciled;
- do not claim production readiness or realized savings;
- do not conceal `not_available` checklist states;
- close with the human-review boundary.
