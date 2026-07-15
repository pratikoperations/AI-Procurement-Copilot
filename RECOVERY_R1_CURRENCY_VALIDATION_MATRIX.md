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
| Hosted visual interface | Confirmed correct | Confirmed correct | Confirmed correct | Owner-observed acceptance at PR #9 hosted candidate | VERIFIED COMPLETE |

## Confirmations
- Display labels match generated business-facing values in automated coverage.
- Canonical normalized unit price, original currency, FX rate and comparison basis remain unchanged.
- No double conversion occurs in precomputed-column scenarios.
- Supplier rankings and procurement formulas were not redesigned.
- Source-preservation correction affects display reconstruction only, not the FX formula.
- The project owner manually checked USD, INR and Both modes on `https://ai-procurement-copilot-pr9.streamlit.app/` and reported that all looked correct.

## Evidence Boundary
Hosted visual acceptance is owner-observed rather than independently reproduced through the connected GitHub tool. Automated and owner acceptance evidence together are classified VERIFIED COMPLETE for Recovery R1.
