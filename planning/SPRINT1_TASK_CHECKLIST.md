# Sprint 1 Task Checklist

## Planning and Branch Safety
- [ ] Confirm branch is `v1.1-development`
- [ ] Confirm `main` and `release/v1.0.0` remain unchanged
- [ ] Confirm ERP upload remains feature-isolated

## Workbook Intake
- [ ] Define `.xlsx` file-size limit
- [ ] Reject `.xlsm`, `.xls`, CSV-renamed files, and corrupt workbooks
- [ ] Detect seven required sheets
- [ ] Log unsupported sheets
- [ ] Count rows and columns
- [ ] Detect empty sheets, blank headers, and duplicate headers

## Schema and Profiles
- [ ] Load canonical schema registry
- [ ] Load SAP mapping profile
- [ ] Load Oracle mapping profile
- [ ] Load Custom template
- [ ] Show mapping coverage
- [ ] Preserve source headers

## Validation UX
- [ ] Show workbook-level status
- [ ] Show sheet-level status
- [ ] Show PASS, INFO, WARNING, REVIEW REQUIRED, BLOCKING
- [ ] Disable analysis during Sprint 1
- [ ] Provide validation summary export

## Test Assets
- [ ] Validate synthetic SAP workbook
- [ ] Validate synthetic Oracle workbook
- [ ] Safely reject adversarial workbook cases
- [ ] Confirm leading-zero IDs remain text
- [ ] Confirm no formulas or macros execute

## Definition of Done
- [ ] Existing Version 1.0 workflows remain green
- [ ] No data persists by default
- [ ] No scoring, TCO, Supplier 360, or recommendation runs from ERP upload
- [ ] Documentation and release checklist updated
