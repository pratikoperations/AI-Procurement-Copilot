# Project Build Plan

## Product Objective
Deliver an auditable, human-controlled procurement decision-support application that improves supplier comparison, should-cost, TCO, risk, scenario, negotiation and executive decision quality without representing automated recommendations as supplier-award approval.

## Release Roadmap
| Release | Objective | Status |
|---|---|---|
| Portfolio Edition v1.0.0 | Stable interview-ready procurement decision support | Released and frozen |
| Maintenance v1.0.1 | Correct documented currency/display defects without adding features | Validation and reconciliation required |
| Version 1.1 Sprint 1 | Safe ERP workbook intake, mapping and validation foundation | Verified partial |
| Version 1.1 later sprints | Normalization, analysis handoff, reporting and governed UI | Deferred pending baseline approval |

## Build Phases
### Phase 0 — Recovery and Baseline Control
- Reconcile branch history, tests, deployment and documentation.
- Acceptance: exact branch SHAs recorded; full tests and smoke checks evidenced; discrepancies classified.
- Approval gate: project owner accepts the development baseline.

### Phase 1 — v1.0.1 Maintenance Closure
Work packages:
1. Reconcile maintenance branch with portability documentation on main.
2. Run full regression and Streamlit smoke tests.
3. Validate USD, INR and Both modes across dashboards, Supplier Intelligence and exports.
4. Validate supplier selector and per-supplier views.
5. Update release and validation records.

Acceptance criteria:
- No new features.
- Full regression passes.
- Selected currency is correct in labels, calculations and exported business-facing fields.
- Canonical audit currency fields remain unchanged.
- Supplier selector works for every available supplier profile.
- Deployment smoke test passes.

### Phase 2 — Version 1.1 Sprint 1 Recovery
Work packages:
1. Rebase or reconstruct from approved v1.0.1 baseline.
2. Preserve verified ERP schema registry, mapping profiles, workbook loader and structural validator.
3. Complete missing upload orchestration, validation reporting and UI only if separately authorized.
4. Mark checklist items only after evidence exists.

Dependencies:
- Approved v1.0.1 baseline.
- Canonical ERP workbook specification.
- Security rules for workbook handling.
- Test fixtures and acceptance matrix.

Acceptance criteria:
- Safe `.xlsx` intake with explicit rejection rules.
- Required sheets and headers validated.
- Mapping coverage shown and source headers preserved.
- No formulas or macros executed.
- No scoring, TCO, Supplier 360 or recommendation initiated from unapproved ERP data.
- Existing v1.0 workflows remain green.

## Test Gates
1. Static import/compile gate.
2. Focused unit tests for changed modules.
3. Complete `python -m pytest` regression gate.
4. Streamlit startup smoke gate.
5. Currency and supplier-selector functional gate.
6. ERP adversarial workbook gate where applicable.
7. Direct export inspection for readable and machine-readable outputs.

## Approval Gates
- Scope approval before branch creation.
- Architecture approval before schema/business-rule changes.
- Test evidence approval before merge.
- Manual procurement acceptance before release.
- Deployment approval before stable release tagging.

## Excluded Scope
- Autonomous supplier award.
- Production ERP write-back.
- Live supplier-master or contract-system integration.
- External AI-provider dependency without explicit architecture and security approval.
- Unnecessary analytics or UI features outside authorized acceptance criteria.

## Estimated Effort
| Work package | Estimate |
|---|---:|
| Recovery evidence completion and exact SHA capture | 2–4 hours |
| v1.0.1 branch reconciliation | 2–4 hours |
| Full regression, smoke and manual defect validation | 3–6 hours |
| Documentation and release-control closure | 2–3 hours |
| Version 1.1 branch reconstruction/rebase assessment | 3–5 hours |

## Next Authorized Build
**Recovery Build R1 — Baseline Verification and v1.0.1 Maintenance Closure.**

No Version 1.1 feature implementation is authorized in this recovery task. The next build must first establish an approved, tested maintenance baseline and record exact branch HEADs.