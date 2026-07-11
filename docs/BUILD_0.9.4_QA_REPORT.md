# Build 0.9.4 QA Report

## Build

Build 0.9.4 — Category-Specific Cost and Risk Engines

## Quality Gates

| Gate | Result | Notes |
|---|---|---|
| Packaging engine preserved | Pass by regression design | Existing packaging test suite remains active |
| Raw-material engine active | Pass by test design | Engine status and production routing covered |
| Raw-material should-cost | Pass by test design | Commodity shock increases target cost |
| Raw-material risk | Pass by test design | High dependency and volatility reduce score |
| Raw-material TCO | Pass by test design | Duty, volatility, inventory, working capital, and risk included |
| Category-aware scoring | Pass by test design | Raw-material scoring route and weights covered |
| Category cost router | Pass by test design | Commodity should-cost components returned |
| App integration | Static pass | Category selection controls demo data and engines |
| CI | Pending | Await latest GitHub Actions result |
| Live multi-category review | Pending | Requires packaging and raw-material Streamlit validation |

## Provisional Quality Score

- Architecture: 9.4/10
- Code Quality: 9.1/10
- Procurement Logic: 9.4/10
- Category Separation: 9.6/10
- Explainability: 9.3/10
- Maintainability: 9.2/10

**Provisional Average:** 9.3/10

## Key Controls

- Packaging and raw materials use separate commercial logic.
- Raw-material decisions include volatility, import, concentration, substitution, duty, FX, and continuity exposure.
- Category selection controls the full calculation path.
- No black-box award logic is introduced.

## Remaining Validation

1. Confirm latest Quality Checks are green.
2. Open Packaging Procurement and verify all existing tabs.
3. Select Raw Material Procurement and verify demo data changes.
4. Change commodity and confirm should-cost changes.
5. Apply a raw-material shock and confirm cost and recommendation update.
6. Confirm downloads and Procurement Intelligence render for both categories.
