# Validation Data — Expected Results

All files are synthetic and contain no confidential supplier information.

| File | Expected mapping / warnings | Eligibility expectation | Confidence expectation | Recommendation behavior |
|---|---|---|---|---|
| packaging_standard.csv | Canonical headers; complete commercial and service data | Eligible or Eligible With Conditions | High / Acceptable | Recommendation permitted with human approval |
| packaging_alternate_headers.csv | Vendor, rate, MOQ, delivery, payment, incoterm and UOM aliases mapped | Eligible With Conditions | Acceptable | Recommendation permitted after mapping review |
| packaging_missing_optional.csv | Required fields present; optional scoring fields missing | Human Review Required or Eligible With Conditions | Limited / Acceptable | Provisional only |
| packaging_invalid_values.csv | Negative price, negative lead time, invalid percentages and capacity | Blocked | Insufficient | Block calculation |
| resin_standard.csv | Raw-material canonical data including risk drivers | Eligible or Eligible With Conditions | High / Acceptable | Recommendation permitted with human approval |
| metal_alternate_headers.csv | Alternate raw-material headers mapped; unit normalized to kg | Eligible With Conditions | Acceptable | Recommendation permitted after mapping review |
| raw_material_mixed_currency.csv | Mixed USD and INR detected | Blocked | Acceptable | No award recommendation until FX normalization |
| raw_material_missing_fields.csv | Missing payment terms, incoterms, currency and unit | Blocked / Insufficient Data | Insufficient | No recommendation |
| duplicate_suppliers.csv | Duplicate supplier warning | Eligible With Conditions / Human Review | Acceptable | Consolidate or distinguish sites |
| percentage_formats.csv | Decimal percentage warning | Human Review Required | Acceptable | Confirm percentage convention |
| negative_values.csv | Negative price, MOQ, lead time, PPM, complaint and capacity | Blocked | Insufficient | Block calculation |
| capacity_shortfall.csv | Total capacity below test demand | Blocked | Acceptable | No feasible award allocation |
| single_supplier.csv | Comparative-sourcing warning | Eligible With Conditions | Acceptable | Single-source recommendation only with mitigation |
| large_50_supplier_file.csv | 50 rows load without loss | Eligible With Conditions | High / Acceptable | Recommendation permitted after review |
