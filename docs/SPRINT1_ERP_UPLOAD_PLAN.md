# Sprint 1 ERP Upload Plan

## Status
Planning only. No implementation is authorized by this document.

## Sprint Goal
Prove that AI Procurement Copilot can safely inspect an SAP- or Oracle-style Excel workbook, recognize the seven approved sheets, preview source columns, and produce a structural validation summary without running procurement analytics.

## Sprint Duration
Estimated: 12–18 hours

Recommended schedule:
- 2 focused days, or
- 1 week part-time

## In Scope
- `.xlsx` file acceptance
- File size and extension checks
- Required sheet detection
- Unknown sheet logging
- Header extraction
- Row-count summary
- Empty-sheet detection
- Duplicate-header detection
- Source-column preview
- ERP profile selection
- Mapping preview only
- Structural validation summary
- Downloadable validation report specification

## Out of Scope
- Supplier matching
- Material matching
- Currency conversion
- Unit conversion
- Date normalization beyond structural inspection
- RFQ scoring
- TCO
- Should-cost
- Supplier 360
- SRM
- Scenario analysis
- Negotiation
- Recommendations
- ERP API integration
- Persistence or database storage

## Planned Modules

### `modules/erp_workbook_loader.py`
Planned responsibilities:
- Validate `.xlsx`
- reject macro-enabled files
- enforce size limit
- open workbook safely
- list sheets
- extract headers and row counts
- return structured loader result

### `modules/erp_schema_registry.py`
Planned responsibilities:
- Define seven required sheets
- Define required and optional columns
- expose sheet metadata
- provide canonical column references

### `modules/erp_mapping_profiles.py`
Planned responsibilities:
- Load SAP, Oracle, and Custom profile definitions
- expose mapping metadata
- no transformation execution in Sprint 1

### `modules/erp_structural_validator.py`
Planned responsibilities:
- Missing sheet checks
- empty sheet checks
- duplicate header checks
- blank header checks
- unknown sheet reporting
- workbook-level status

### `modules/erp_upload_ui.py`
Planned responsibilities:
- Data-source selection
- file upload
- ERP profile selection
- workbook summary
- sheet status cards
- header preview
- validation result display

## Streamlit Flow

1. User selects `ERP Procurement Workbook`.
2. User uploads `.xlsx`.
3. System validates file type and size.
4. User selects SAP, Oracle, or Custom profile.
5. System displays detected sheets.
6. Each sheet shows row count, headers, and structural status.
7. System shows overall status:
   - PASS
   - PASS WITH WARNINGS
   - BLOCKED
8. No analysis button is enabled in Sprint 1.

## Deliverables
- Approved Sprint 1 technical design
- Loader contract
- schema registry contract
- structural validation contract
- Streamlit wireflow
- test-case inventory
- release checklist

## Test Inventory

### Positive
- Valid SAP-style workbook
- Valid Oracle-style workbook
- Workbook with extra harmless sheet
- Workbook with optional empty columns

### Negative
- CSV renamed as XLSX
- macro-enabled workbook
- corrupted workbook
- missing required sheet
- empty required sheet
- duplicate headers
- blank headers
- excessive file size
- formula in identifier header/data preview

## Acceptance Criteria
- Version 1.0 workflows are untouched.
- Only `v1.1-development` is used.
- Valid SAP and Oracle workbooks open successfully.
- Missing required sheets are identified.
- Corrupt and macro-enabled files are rejected.
- Sheet names, row counts, and headers are displayed.
- Unknown sheets are logged but do not automatically block.
- Structural findings use the approved severity matrix.
- No procurement analysis runs from ERP data.
- No uploaded data is persisted.
- A Sprint 1 validation summary can be exported or copied.

## Definition of Done
Sprint 1 is done only when:
- All planned structural checks pass.
- Adversarial structural cases fail safely.
- Existing Version 1.0 regression tests remain green.
- Mobile upload flow is usable.
- Documentation is updated.
- No scoring, normalization, or recommendation logic has been added prematurely.

## Rollback
If Sprint 1 causes regression:
- Disable the ERP upload option.
- Revert Sprint 1 commits.
- Preserve planning documents.
- Keep current demo and RFQ upload paths unchanged.

## Next Sprint Boundary
Sprint 2 may begin only after Sprint 1 acceptance and should cover:
- column mapping
- canonical field coverage
- mapping-profile persistence
- required-field validation

Supplier and material entity matching remains later unless separately approved.
