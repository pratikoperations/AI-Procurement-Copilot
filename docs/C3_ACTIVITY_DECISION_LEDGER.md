# C3 Steel Sheets and Coils — Activity and Decision Ledger

## Governance baseline

- Repository: `pratikoperations/AI-Procurement-Copilot`
- Frozen base branch: `main`
- Frozen base SHA: `0b310b4e97e0c92112089929fca150d7f183ecc8`
- Feature branch: `agent/category-expansion-c3-steel`
- Category: Governed Steel Sheets and Coils Procurement
- Contract version: `C3.0-STEEL-v1`
- Current phase: C3.0 contract documentation and contract tests only

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

## Currency governance

- Supplier quotations normalize to USD/kg before decision logic.
- INR values derive deterministically from the shared USD/INR FX rate.
- Both mode uses separate numeric USD and INR fields.
- Display mode cannot alter eligibility, ranking, winner, allocation, scenario status, confidence or risk.
- Missing, non-numeric, zero or negative FX values fail closed.
- Unsupported quote currencies fail closed.
- The FX value is not represented as a live rate.

## Intended decision architecture

Future separately authorized phases may introduce:

- a dedicated Steel should-cost engine;
- controlled synthetic Steel supplier data;
- executable Steel validation and eligibility;
- Steel-specific risk;
- eligible-only recommendation;
- standard and optimized allocation;
- seven scenario calculations;
- Steel-specific UI and state controls;
- governed Excel and strict JSON production logic.

None of those executable features is authorized in C3.0.

## Seven frozen scenarios

1. Base Case
2. Steel Index +20%
3. Energy and Conversion Premium +15%
4. Import Duty and FX Stress
5. Demand +25%
6. Mill Allocation and Capacity Stress
7. Grade-Substitution Scenario

## Eligibility principles

The future executable gate must fail closed for unsupported or missing profile, grade family, thickness, width, coating, paint-line, surface, approval, certificate-availability, capacity, coil-weight or substitution evidence. Price cannot override technical ineligibility.

## Export intent

The intended Excel package includes Supplier Scores Report, Supplier Comparison, Should Cost, Allocation, Standard Allocation, Optimized Allocation, Scenarios, Audit Supplier Scores and C3 Governance.

The intended JSON package includes `steel_governance`, uses `allow_nan=False`, converts non-finite values to `null`, and stores USD and INR values in separate numeric fields.

## Claim boundaries

No metallurgical certification, engineering substitution approval, mill-test-certificate authentication, production-readiness claim, live commodity-index claim, live FX claim, autonomous award, ERP write-back or realized-savings claim is authorized.

## C3.0 readiness condition

C3.1 may be proposed only after:

- both C3.0 documents exist on the feature branch;
- contract tests pass;
- full regression passes;
- Python compilation passes;
- Streamlit smoke passes;
- the PR remains draft;
- `main` remains unchanged;
- no executable C3 production logic has been introduced.