# C3 Steel Sheets and Coils — Activity and Decision Ledger

## Governance baseline

- Repository: `pratikoperations/AI-Procurement-Copilot`
- Frozen base branch: `main`
- Frozen base SHA: `0b310b4e97e0c92112089929fca150d7f183ecc8`
- Feature branch: `agent/category-expansion-c3-steel`
- Category: Governed Steel Sheets and Coils Procurement
- Contract version: `C3.0-STEEL-v1`

## Historical C3.0 record

C3.0 authorized contract documentation and contract tests only. Its original statements that executable Steel features were future work are retained as historical phase evidence and do not describe the current C3.7 implementation state.

## Frozen decisions

| Decision | Governed outcome |
|---|---|
| Category family | Raw Material Procurement |
| Commercial quantity | kg |
| Optional reporting volume | metric tonnes |
| Internal calculation currency | USD |
| Normalized comparison | USD/kg |
| Display modes | USD; INR; Both |
| Accepted quote currencies | USD; INR |
| FX | One positive user-controlled USD/INR demonstration assumption |
| Profiles | CR_COIL_COMMERCIAL; GI_COIL_Z120; PPGI_COIL_Z120 |
| Recommendation | Technically eligible suppliers only; human approval mandatory |
| Allocation | Standard and optimized outputs remain separate |
| Scenarios | Exactly seven governed scenarios |
| JSON governance block | steel_governance |
| Historical evidence | S1, C1 and C2 remain preserved |

## Controlled profiles

1. `CR_COIL_COMMERCIAL` — Cold-Rolled Steel Coil; 0.80 mm; 1,000–1,250 mm; no zinc; no paint.
2. `GI_COIL_Z120` — Galvanized Steel Coil; 0.60 mm; 1,000–1,250 mm; 120 g/m² total zinc; no paint.
3. `PPGI_COIL_Z120` — Pre-Painted Galvanized Steel Coil; 0.50 mm; 1,000–1,250 mm; 120 g/m² total zinc; 20 μm topcoat; 5 μm back coat.

## Phase implementation ledger

| Phase | Implemented outcome |
|---|---|
| C3.0 | Contract, frozen profiles, scenario and export intent, claim boundaries |
| C3.1 | Category and supplier-data registration |
| C3.2 | Dedicated Steel should-cost and currency path |
| C3.3 | Fail-closed technical eligibility |
| C3.4 | Separate Steel risk, eligible-only scoring and governed recommendation |
| C3.5 | Exactly seven scenarios and separate standard/optimized allocation |
| C3.6 | Dependent-state UX, display invariance and visible governance outputs |
| C3.7 | Isolated Steel application route, nine-sheet Excel, strict JSON and closure evidence |

## Current executable architecture

Supplier quotations normalize to USD/kg before technical eligibility, separate generic and Steel risk, eligible-only scoring, recommendation, scenarios and allocation. Display mode cannot alter decision outputs. The Steel route stops before generic downstream recommendation, allocation, scenario, negotiation, intelligence or download sections.

## Export production

The Excel package contains exactly:

1. Supplier Scores Report
2. Supplier Comparison
3. Should Cost
4. Allocation
5. Standard Allocation
6. Optimized Allocation
7. Scenarios
8. Audit Supplier Scores
9. C3 Governance

The strict JSON package uses top-level `steel_governance`, `allow_nan=False`, converts non-finite values to `null`, preserves separate USD and INR numeric fields and records the selected profile, scenario, eligibility, separate risks, score, rank, winner/no-winner, allocations, unallocated volume and governance boundaries.

## Claim boundaries

No metallurgical certification, engineering substitution approval, mill-test-certificate authentication, production-readiness assurance, live commodity or FX claim, autonomous award, ERP write-back or realised-savings evidence is provided.

## Current readiness condition

C3 implementation is ready for final review only after final CI, deterministic application-route verification and direct confirmation that PR #33 remains draft, unmerged and based on the frozen main SHA. Ready-for-review and merge remain separately governed actions.
