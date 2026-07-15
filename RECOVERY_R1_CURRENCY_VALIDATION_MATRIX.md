# Recovery R1 Currency Validation Matrix

Date: 2026-07-15

| Surface / output | USD | INR | Both | Evidence | Classification |
|---|---|---|---|---|---|
| Dashboard tables and charts | Covered | Covered | Covered where supported | Automated currency/dashboard tests | VERIFIED COMPLETE |
| Supplier Intelligence comparison | Covered | Covered | Covered | Focused Supplier Intelligence tests | VERIFIED COMPLETE |
| Supplier 360 / selector path | Code path preserved | Wrapper passes currency/FX | Same governed path | Contract tests and smoke | VERIFIED COMPLETE |
| Business-readable exports | Covered | Covered | Covered | Export tests | VERIFIED COMPLETE |
| Machine-readable audit outputs | Canonical fields preserved | Canonical fields preserved | Canonical fields preserved | Export/currency tests | VERIFIED COMPLETE |
| Mobile-priority columns | Prioritized | Prioritized | Both sets prioritized | Focused tests | VERIFIED COMPLETE |
| Hosted visual interface | Not directly observed | Not directly observed | Not directly observed | No authoritative hosted URL | NOT STARTED |

## Automated Confirmations
- Display labels match generated business-facing values in covered tests.
- Canonical normalized unit price, original currency, FX rate and comparison basis remain unchanged.
- No double conversion occurs in precomputed-column scenarios.
- Supplier rankings and procurement formulas were not redesigned.
- Source-preservation correction affects display reconstruction only, not the FX formula.

## Hosted Acceptance Boundary
Hosted label/value alignment, mobile readability and ranking stability could not be directly observed because no authoritative hosted URL was found. Automated coverage is VERIFIED COMPLETE; hosted visual acceptance remains NOT STARTED.
