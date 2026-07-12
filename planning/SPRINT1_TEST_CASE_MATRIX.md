# Sprint 1 Test-Case Matrix

| ID | Area | Test case | Asset | Expected result | Severity |
|---|---|---|---|---|---|
| S1-001 | File | Valid SAP XLSX | SAP workbook | Opens, seven sheets detected | PASS |
| S1-002 | File | Valid Oracle XLSX | Oracle workbook | Opens, seven sheets detected | PASS |
| S1-003 | File | Macro-enabled workbook | Adversarial | Rejected | BLOCKING |
| S1-004 | File | Corrupt workbook | Adversarial | Rejected clearly | BLOCKING |
| S1-005 | Sheets | Missing required sheet | Adversarial | Dependent modules blocked | BLOCKING |
| S1-006 | Sheets | Extra sheet | Adversarial | Logged and ignored | INFO |
| S1-007 | Headers | Duplicate headers | Adversarial | Sheet rejected | BLOCKING |
| S1-008 | Headers | Blank header | Adversarial | Sheet rejected | BLOCKING |
| S1-009 | IDs | Leading-zero supplier IDs | SAP workbook | Preserved as text | PASS |
| S1-010 | IDs | Leading-zero material IDs | SAP workbook | Preserved as text | PASS |
| S1-011 | Mapping | SAP profile coverage | SAP profile | Required fields mapped | PASS |
| S1-012 | Mapping | Oracle profile coverage | Oracle profile | Required fields mapped | PASS |
| S1-013 | Mapping | Empty custom profile | Custom template | Requires user mapping | REVIEW REQUIRED |
| S1-014 | Security | Formula-like text | Adversarial | Not executed and flagged | BLOCKING |
| S1-015 | Summary | Row counts | SAP and Oracle | Correct per sheet | PASS |
| S1-016 | Regression | Existing v1.0 upload | Existing application | Unchanged | PASS |
