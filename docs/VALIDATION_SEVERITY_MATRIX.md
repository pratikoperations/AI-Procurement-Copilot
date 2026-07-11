# Validation Severity Matrix

## Status
Planning only. No application code or Version 1.0 changes.

## Purpose
Standardize how ERP-upload defects are classified, displayed, and allowed to affect downstream procurement analysis.

## Severity Levels

| Severity | Meaning | Processing | User action |
|---|---|---|---|
| PASS | Rule satisfied | Continue | None |
| INFO | Informational condition | Continue | Optional review |
| WARNING | Noncritical quality issue | Continue with reduced confidence | Review recommended |
| REVIEW REQUIRED | Ambiguous or material issue | Continue only after explicit human decision | Mandatory review |
| BLOCKING | Unsafe or unusable condition | Stop workbook, row, or module | Correct data or mapping |

## Scope Levels
- Workbook
- Sheet
- Column
- Row
- Cross-sheet
- Module

A finding must include both severity and scope.

## Structural Rules

| Rule | Severity | Scope | Outcome |
|---|---|---|---|
| Unsupported file type | BLOCKING | Workbook | Reject file |
| Macro-enabled workbook | BLOCKING | Workbook | Reject file |
| Corrupt workbook | BLOCKING | Workbook | Reject file |
| Missing required sheet | BLOCKING | Workbook/module | Block dependent modules |
| Empty required sheet | BLOCKING | Sheet/module | Block dependent modules |
| Extra unknown sheet | INFO | Workbook | Ignore and log |
| Duplicate headers | BLOCKING | Sheet | Reject sheet |
| Blank header | BLOCKING | Sheet | Reject sheet |
| Hidden column | WARNING | Sheet | Disclose and inspect |
| Formula in critical field | BLOCKING | Cell/row | Quarantine row |

## Identifier Rules

| Rule | Severity | Scope | Outcome |
|---|---|---|---|
| Missing Supplier_ID | BLOCKING | Row/module | Quarantine row |
| Missing Material_ID | BLOCKING where material required | Row/module | Quarantine row |
| Unknown supplier reference | REVIEW REQUIRED | Row | Resolve match |
| Unknown material reference | REVIEW REQUIRED | Row | Resolve match |
| Ambiguous fuzzy supplier match | REVIEW REQUIRED | Row | Human approval |
| Duplicate supplier ID with conflicting legal entity | BLOCKING | Supplier | Quarantine supplier records |
| Leading zeros altered but recoverable | WARNING | Column | Correct with audit |

## Currency Rules

| Rule | Severity | Scope | Outcome |
|---|---|---|---|
| Missing quote currency | BLOCKING | Row/RFQ | Exclude row |
| Invalid currency code | BLOCKING | Row/module | Exclude row |
| Missing FX rate for cross-currency comparison | BLOCKING | Module | Block comparison |
| FX date missing for historical normalization | REVIEW REQUIRED | Module | Approve source or block |
| Original currency not preserved | BLOCKING | Module | Block output |
| Rounding difference within tolerance | INFO | Row | Continue |
| Normalized amount inconsistent with FX | BLOCKING | Row | Quarantine |

## Unit Rules

| Rule | Severity | Scope | Outcome |
|---|---|---|---|
| Missing UOM | BLOCKING | Row/module | Exclude row |
| Unknown UOM | REVIEW REQUIRED | Row | Map or reject |
| Incompatible UOMs | BLOCKING | Comparison | Block comparison |
| Zero or negative conversion factor | BLOCKING | Mapping | Reject mapping |
| Piece-to-weight conversion without basis | BLOCKING | Comparison | Block comparison |
| Approved equivalent alias | INFO | Mapping | Continue |

## Date Rules

| Rule | Severity | Scope | Outcome |
|---|---|---|---|
| Invalid date | BLOCKING | Row if governing date | Quarantine row |
| Missing governing date | WARNING or BLOCKING by module | Row/module | Exclude from trends |
| End date before start date | BLOCKING | Row | Quarantine |
| Quote expired | WARNING | RFQ row | Mark ineligible/current comparison warning |
| Receipt before PO date | REVIEW REQUIRED | Cross-sheet | Investigate |
| Future extraction date | BLOCKING | Workbook | Reject metadata |
| Partial comparison period | WARNING | Module | Display prominently |

## Numeric Rules

| Rule | Severity | Scope | Outcome |
|---|---|---|---|
| Negative price | BLOCKING | Row | Quarantine |
| Zero quoted quantity | BLOCKING | Row | Quarantine |
| Percentage outside 0–100 | BLOCKING | Row | Quarantine |
| Rejected quantity above received | BLOCKING | Row | Quarantine |
| Extreme price outlier | REVIEW REQUIRED | Row | Human validation |
| Missing optional lead time | WARNING | Row/module | Reduce confidence |

## Duplicate Rules

| Rule | Severity | Scope | Outcome |
|---|---|---|---|
| Exact duplicate | WARNING | Row set | Collapse with audit count |
| Conflicting duplicate business key | BLOCKING | Row set | Quarantine conflicts |
| Duplicate source record ID | BLOCKING | Sheet | Quarantine duplicates |
| Multiple identical latest timestamps | REVIEW REQUIRED | Record set | Human selection |

## Business Rules

| Rule | Severity | Scope | Outcome |
|---|---|---|---|
| Blocked supplier included in active RFQ | REVIEW REQUIRED | RFQ | Exclude unless approved |
| Inactive material in current transaction | REVIEW REQUIRED | Row | Investigate |
| Missing payment terms | WARNING | TCO | Use visible assumption only |
| Missing freight basis | WARNING | TCO | Provisional result |
| Missing cost-driver source | BLOCKING | Should-cost | Exclude driver |
| Missing performance period | BLOCKING | Performance | Exclude from trend |
| Unsupported category | BLOCKING | Module | Block routing |

## Module Status Rules

| Highest unresolved finding | Module status |
|---|---|
| PASS/INFO | Eligible |
| WARNING | Eligible With Warnings |
| REVIEW REQUIRED | Human Review Required |
| BLOCKING | Blocked |

## Finding Record Standard
Every finding must contain:
- Rule ID
- Severity
- Scope
- Sheet
- Row or key
- Source field
- Canonical field
- Original value
- Explanation
- Required remediation
- Affected module
- Resolved status
- Resolver and timestamp where applicable

## Acceptance Criteria
- Every validation rule has a severity.
- Blocking rules cannot be bypassed silently.
- Review-required rules need explicit human action.
- Warnings reduce confidence where material.
- Module eligibility is derived from unresolved findings.
- Findings are exportable and auditable.
