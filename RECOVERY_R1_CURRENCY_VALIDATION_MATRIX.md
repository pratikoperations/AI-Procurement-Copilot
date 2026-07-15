# Recovery R1 Currency Validation Matrix

Date: 2026-07-15

| Surface / output | USD | INR | Both | Evidence | Result |
|---|---|---|---|---|---|
| Dashboard tables and charts | Selected labels and USD values | INR conversion through governed FX path | Separate business-facing columns where supported | Currency-display and dashboard regression coverage | PASS |
| Supplier Intelligence comparison | Quoted price and risk TCO in USD | Single conversion to INR | Separate USD and INR columns | `tests/test_supplier_intelligence_currency.py` | PASS |
| Supplier 360 / selector path | Existing profile path preserved | Wrapper passes selected currency and FX | Same governed path | UI contract tests and smoke | PASS WITH INTERACTIVE ACCEPTANCE PENDING |
| Business-readable exports | USD labels/values | INR labels/values | Separate readable outputs | `tests/test_exports.py` | PASS |
| Machine-readable audit outputs | Canonical normalized fields unchanged | Canonical fields unchanged | Canonical fields unchanged | Export and currency tests | PASS |
| Mobile-priority comparison columns | USD business columns prioritized | INR business columns prioritized | Both currency sets prioritized | Focused Supplier Intelligence tests | PASS |

## Confirmations
- Display labels match generated business-facing values in covered tests.
- Canonical normalized unit price, original currency, FX rate and comparison basis remain unchanged.
- No double conversion occurs in precomputed-column scenarios.
- Supplier rankings and procurement formulas were not redesigned.
- The defect discovered during Recovery R1 concerned source preservation in the display wrapper, not the FX formula.

Classification: VERIFIED COMPLETE for automated currency and export coverage; VERIFIED PARTIAL for manual hosted visual acceptance.
