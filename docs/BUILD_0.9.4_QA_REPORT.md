# Build 0.9.4 QA Report

## Build

Build 0.9.4 — Category-Specific Cost and Risk Engines

## Quality Gates

| Gate | Result | Notes |
|---|---|---|
| Packaging engine preserved | Pass by regression design | Existing packaging test suite remains active |
| Raw-material engine active | Pass by updated regression design | Engine status and production routing covered |
| Raw-material should-cost | Pass by test design | Commodity shock increases target cost |
| Raw-material risk | Pass by test design | High dependency and volatility reduce score |
| Raw-material TCO | Pass by test design | Duty, volatility, inventory, working capital, and risk included |
| Category-aware scoring | Pass by test design | Raw-material scoring route and weights covered |
| Category cost router | Pass by test design | Commodity should-cost components returned |
| App integration | Static pass | Category selection controls demo data and engines |
| CI | Pending latest rerun | Initial failure was caused by an outdated preview-only assertion |
| Live multi-category review | Pending | Requires packaging and raw-material Streamlit validation |

## Initial CI Failure

The first failing workflow occurred at commit #116 after Raw Material Procurement was promoted from `Foundation Preview` to `Active`.

The code change was correct, but `tests/test_category_engine.py` still asserted:

```python
assert profile["engine_status"] == "Foundation Preview"
assert is_production_ready("Raw Material Procurement") is False
```

This historical expectation no longer matched Build 0.9.4.

## Remediation

The regression test was updated to validate the new production state:

```python
assert profile["engine_status"] == "Active"
assert is_production_ready("Raw Material Procurement") is True
```

The updated test also verifies:

- PET Resin selection
- `kg` unit consistency
- Raw-material cost-model metadata
- Raw-material risk-model metadata

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

1. Confirm the latest post-fix Quality Checks run is green.
2. Open Packaging Procurement and verify all existing tabs.
3. Select Raw Material Procurement and verify demo data changes.
4. Change commodity and confirm should-cost changes.
5. Apply a raw-material shock and confirm cost and recommendation update.
6. Confirm downloads and Procurement Intelligence render for both categories.
