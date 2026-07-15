# Recovery R1 Maintenance Test Evidence

Date: 2026-07-15

## Candidate
- Reconstructed from canonical main `075fe16d889cdb82b126fe1e07b0c63dca369580`
- Maintenance source HEAD: `ba49af44d8c1ff36d9d5d612e0909f5698d1d433`
- Corrected candidate commit: `acda17383cb1bed09787f69345ea60e359b94b06`

## Environment
- Ubuntu 24.04 GitHub Actions runner
- Python 3.11.15
- pip 26.1.2
- Pinned dependencies installed successfully

## Initial result
- Compile: PASS
- Complete pytest: FAIL
- Smoke: skipped by canonical workflow
- Isolated failure: `tests/test_supplier_intelligence_currency.py`

## Root cause and correction
The maintenance wrapper dropped `Risk-Adjusted TCO (USD)` before reusing it as the canonical USD source. The correction preserves that source in a temporary display-only column before rebuilding USD/INR/Both outputs. No FX formula, ranking, threshold, schema or audit field was changed.

## Final reproducible result
- Focused annual-volume tests: PASS
- Focused currency-display tests: PASS
- Focused export tests: PASS
- Focused Supplier Intelligence currency tests: PASS
- Focused Supplier Intelligence UI tests: PASS
- `python -m compileall app.py modules tests`: PASS
- `python -m pytest`: **162 passed, 0 failed, 0 skipped, 1 warning in 2.09s**
- `bash scripts/streamlit_smoke_test.sh`: **PASS**

Warning: existing pandas FutureWarning in `tests/test_adversarial_inputs.py::test_decimal_percentage_is_flagged`.

Classification: VERIFIED COMPLETE for CI compile/regression/smoke evidence.
