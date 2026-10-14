# EAS-BIV Interview Evidence Pack

## Current positioning statement

AI Procurement Copilot is a governed procurement decision-support portfolio. The EAS-BIV programme added calculation explainability, assumption provenance, deterministic traces, reconciliation, internal evidence navigation and explicit human-review controls without replacing the existing business engines.

The current stabilized portfolio extends that foundation with:
- project-wide chat-style SourceMate;
- cross-category presentation hardening;
- public-demo safety controls;
- MRO / Industrial Supplies Foundation Preview.

## Current five-minute demonstration script

### 0:00–0:35 — Business problem

“Procurement decisions often sit across spreadsheets, category models and undocumented assumptions. A result may be numerically correct but still difficult to explain, reproduce or govern.”

### 0:35–1:15 — Authoritative Corrugated Board result

Open Governed Calculation Explorer and select Corrugated Board.

Explain:
- the result comes from the existing authoritative should-cost service;
- formula text is documentation only;
- the Explorer does not independently recalculate the answer;
- source module, source function, calculation ID and formula version remain visible.

### 1:15–2:00 — Assumption provenance

Open **Assumptions**.

Explain:
- supplied values originate from the current case;
- defaulted values come from governed defaults;
- inferred values are explicitly labelled;
- derived values are calculated outputs;
- unavailable evidence remains visible.

### 2:00–2:45 — Trace and reconciliation

Open **Calculation Trace** and **Reconciliation**.

Show:
- deterministic trace ID;
- `AIPC-CALC-TRACE-1.0`;
- input snapshot and authoritative raw output;
- retained configuration versions;
- exact matches, tolerated differences, mismatches and unavailable evidence;
- mandatory human review.

Say: “The trace supports review and repeatability. It does not create another calculation engine.”

### 2:45–3:35 — Current SourceMate

Open **SourceMate**.

Show:
- chat-style UX;
- page-aware governed context;
- source/evidence references;
- concise deterministic answers;
- browser-session conversation continuity.

Say: “SourceMate is a read-only internal evidence navigator. It does not browse, use an external LLM, use RAG, externally verify suppliers, recalculate authoritative results or execute procurement actions.”

Current SourceMate conversation contract: `AIPC-SOURCEMATE-PROJECT-WIDGET-BIV-1.0`.

### 3:35–4:20 — MRO Foundation Preview

Select **Indirect Procurement → MRO / Industrial Supplies → Industrial Bearings**.

Explain:
- manufacturer + manufacturer-part-number identity;
- OEM / Authorized Distributor / Approved Equivalent source status;
- technical/evidence contracts;
- fail-closed compatibility;
- explicit human approval for equivalent substitution.

Say: “This proves governed category extensibility without pretending MRO analytics are production-ready.”

### 4:20–5:00 — Limitation and governance close

Demonstrate a deferred evidence route such as Packaging TCO, or summarize the boundary:

- no fabricated trace/reconciliation;
- no autonomous award;
- no production allocation execution;
- no ERP write-back;
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
| Industrial Bearings | MRO category extensibility | Foundation Preview; fail-closed compatibility + human substitution approval |
| Packaging TCO | Honest limitation demonstration | `unsupported_deferred_coverage`; no fabricated trace |

The registry also retains adapter-backed coverage for generic scoring and recommendation eligibility, but they are not required in the five-minute demonstration.

## Strongest business-value messages

1. **Faster review:** reviewers can see result, assumptions, source and evidence in one governed view.
2. **Reduced ambiguity:** supplied, defaulted, inferred and derived values are not mixed together.
3. **Defensible decisions:** trace and reconciliation evidence explain how a supported route aligns with its authoritative service.
4. **Controlled limitation handling:** deferred coverage and unavailable evidence are disclosed rather than hidden.
5. **Human accountability:** the system supports procurement judgement but does not approve or award suppliers.
6. **Cross-category transferability:** the governance pattern works across packaging, raw-material, steel and MRO foundation examples.
7. **Scope discipline:** MRO-0 intentionally stops before unsupported analytical execution.

## Current portfolio evidence

- Current canonical main: `b7037fe21aa64aff799f38b911a6ed3e64d355c0`
- MRO-0 merged through PR #109
- Final documentation reconciliation merged through PR #110
- Current SourceMate contract: `AIPC-SOURCEMATE-PROJECT-WIDGET-BIV-1.0`
- Trace contract: `AIPC-CALC-TRACE-1.0`
- Explorer contract: `AIPC-GOVERNED-EXPLORER-1.0`

## Historical EAS-BIV Gate evidence

The following evidence remains intentionally preserved as historical Gate-5/earlier programme evidence:

- Gate 5 starting baseline / Gate 4 merged baseline: `834b34db145cc0156196579f7419e7db7b438106`
- Historical SourceMate Basic contract: `AIPC-SOURCEMATE-BASIC-1.0`
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
- separation of business results from human approval;
- MRO identity and equivalent-substitution governance.

## Governance evidence

- authoritative services remain primary;
- formula metadata is non-executable;
- unavailable evidence is not inferred;
- SourceMate does not claim external verification;
- deferred routes are not presented as reconciled;
- checklist statuses are evidence-derived;
- no approval persistence exists;
- MRO equivalent substitution requires human approval;
- human review remains mandatory.


## Procurement taxonomy

The public information architecture uses three top-level procurement categories:

1. **Packaging Materials**
2. **Raw Materials**
3. **Indirect Procurement**

MRO / Industrial Supplies and Logistics & Freight are subcategories of **Indirect Procurement**. Existing engine names are retained internally for backward compatibility; the hierarchy change does not alter calculation, scoring, scenario, negotiation or approval semantics.

## Logistics & Freight interview evidence

The Logistics & Freight extension is a governed **Foundation Preview** for Domestic Road Transportation — Full Truck Load (FTL). It demonstrates transfer of the procurement governance pattern into a service category without claiming production transport-management capability.

### What is implemented

- **LOGISTICS-0 — Category foundation:** explicit lane, service, vehicle, carrier-status, commercial-evidence and provenance contracts.
- **LOGISTICS-1 — Freight normalization:** deterministic INR normalization across Per Trip, Per Tonne and Per Tonne-Km bases using explicit payload, distance, fuel-surcharge, toll and accessorial inputs.
- **LOGISTICS-2 — Carrier performance & risk evaluation:** explicit buyer thresholds for capacity, transit time, OTIF, damage/claims and compliance; criterion-level PASS / FAIL / REVIEW; no hidden weights or composite carrier score.
- **LOGISTICS-3 — Carrier allocation & scenario analysis:** evaluates human-proposed carrier shares against explicit annual trip demand, capacity and evidence eligibility; demand stress recalculates volume, headroom and portfolio freight cost; no auto-selection or share optimization.
- **LOGISTICS-4 — Negotiation intelligence & decision presentation:** explicit buyer freight target, commercial ceiling, payment, detention and service positions; transparent commercial deltas; no invented targets or autonomous negotiation.
- **LOGISTICS-5 — SourceMate/evidence integration:** SourceMate can explain the Logistics architecture, governance boundaries and evidence sources without recalculating Logistics outputs.

### Defensible interviewer explanation

**Question:** “Does the Logistics module optimize freight awards?”

**Answer:** “No. The system deliberately separates evaluation from authority. It can normalize explicit freight quotations, test carrier evidence against buyer-defined thresholds, evaluate human-proposed allocation scenarios and quantify explicit negotiation positions. It does not rank carriers with hidden weights, optimize award shares, negotiate autonomously or execute an award. That boundary is intentional.”

**Question:** “Where do freight distance, fuel and toll values come from?”

**Answer:** “They must be explicit inputs. The portfolio does not infer route distance, live fuel price, tolls, telematics or market rates from external services.”

**Question:** “Are the savings shown realized savings?”

**Answer:** “No. LOGISTICS-4 shows target-versus-current commercial deltas under explicit buyer positions. Those are scenario values, not realized financial outcomes.”

### Logistics limitation language

Use these statements without dilution:

- “Logistics is a Foundation Preview, not a production TMS or carrier-management platform.”
- “Buyer thresholds and negotiation positions are explicit inputs; the system does not invent them.”
- “Carrier allocation scenarios are human-proposed; the system does not optimize award shares.”
- “No live market, route, fuel, toll, telematics or compliance feeds are used.”
- “Potential savings are scenario deltas, not realized-savings claims.”
- “No autonomous carrier award, production allocation or TMS/ERP writeback is performed.”
- “Human procurement approval remains mandatory.”


## Difficult interviewer objections and defensible answers

### “Is this just a dashboard over hardcoded examples?”

**Answer:** “The public demonstration uses controlled synthetic inputs, but the governance layer is connected to existing category services and governed contracts. Calculation identities, provenance, trace construction, reconciliation classifications and evidence boundaries are covered by automated tests. It still does not prove enterprise production adoption.”

### “Does the formula shown in the Explorer generate the result?”

**Answer:** “No. Formula text is non-executable metadata. The existing category service remains authoritative. This avoids creating two competing calculation engines.”

### “Can SourceMate verify supplier evidence from the internet?”

**Answer:** “No. SourceMate presents governed internal evidence and application context. It does not browse, use an external LLM, use RAG or claim external verification.”

### “Why are some routes marked deferred?”

**Answer:** “The project deliberately implements representative governed adapters rather than pretending every service has equivalent trace assurance. Deferred routes remain usable through their authoritative service, but they are labelled `unsupported_deferred_coverage` and are not represented as reconciled.”

### “Is MRO now fully implemented?”

**Answer:** “No. MRO-0 is intentionally a Foundation Preview. It establishes identity, source-status, technical/evidence contracts and fail-closed compatibility. It does not claim MRO should-cost, scoring, scenario, negotiation or allocation execution.”

### “Does the tool recommend or award a supplier?”

**Answer:** “It provides controlled decision support and may display recommendation-oriented analysis where validation allows it, but no autonomous award, production allocation or approval persistence exists. Human procurement approval remains mandatory.”

### “Do automated tests make it production-ready?”

**Answer:** “No. Strong automated regression and CI evidence support software quality, but production readiness would additionally require enterprise identity, security, privacy, monitoring, operational ownership, live-data validation and scale testing.”

### “Have you proven realized savings?”

**Answer:** “No. Demonstration values are illustrative and must not be presented as realized savings. The project proves workflow and governance capability, not organizational financial outcomes.”

## What the showcase proves

- procurement workflow and category understanding;
- ability to turn governance requirements into working software contracts;
- explainability without duplicate calculation logic;
- explicit provenance and evidence boundaries;
- deterministic trace and reconciliation controls;
- project-wide read-only evidence assistance;
- cross-category design transferability;
- governed MRO foundation design;
- automated testing and staged GitHub governance;
- ability to communicate limitations clearly.

## What the showcase does not prove

- production deployment readiness;
- live ERP integration or write-back;
- universal adapter coverage;
- production-ready MRO analytics;
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
- “SourceMate presents governed internal evidence and does not perform external verification.”
- “Deferred routes are not represented as adapter-reconciled.”
- “Illustrative outputs are not realized-savings claims.”
- “MRO-0 is a Foundation Preview and does not activate MRO analytical execution.”
- “No autonomous award or production allocation is performed.”
- “Human procurement approval remains mandatory.”
- “Automated and source-level validation do not constitute physical browser-device certification.”

## Demonstration discipline

- use synthetic or sanitized data;
- keep procurement value ahead of technical implementation detail;
- do not call internal evidence registration external verification;
- do not call a deferred route reconciled;
- do not call MRO-0 production-ready MRO analytics;
- do not claim production readiness or realized savings;
- do not conceal unavailable/deferred evidence;
- close with the human-review boundary.
