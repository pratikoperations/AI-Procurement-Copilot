# Build 1.0 RC1.2.3 — Final Manual Validation: Export Acceptance

## Validation status

**Status:** CONDITIONAL ACCEPTANCE — DIRECT ARTIFACT CONTENT REVIEW STILL REQUIRED  
**Release freeze:** Maintained  
**Application logic modified:** No  
**Version 1.0.0 tag created:** No

## Scope

This report consolidates the available validation evidence for:

1. Excel Analysis
2. Supplier Scores Report
3. Supplier Comparison Report
4. Allocation Report
5. Executive Memo
6. Supplier Narrative
7. Decision Machine-Readable Audit Data
8. Supplier 360 Machine-Readable Audit Data

The review used:

- Live Streamlit screenshots supplied during RC1.2.3 validation
- Repository inspection of `app.py`
- Repository inspection of `modules/exports.py`
- Existing export-integrity regression coverage
- User confirmation that the latest GitHub Quality Checks are green

The generated files themselves were not attached to this review session. Therefore, direct opening and row-by-row inspection of every downloaded artifact remains an explicit final release gate.

---

## Validation summary

| Validation area | Result | Severity | Evidence / conclusion |
|---|---|---:|---|
| Download controls render | PASS | — | All eight required download paths are visible in the live Streamlit interface. |
| Readable vs machine-readable separation | PASS | — | CSV/TXT/Excel business outputs are separated from JSON audit downloads in application code and UI labels. |
| Currency governance | PASS | — | Original and normalized currency fields are present in readable score/comparison export builders. Live PET Resin screens show USD comparison values consistently. |
| Unit governance | PASS | — | Live PET Resin screens use kg. Scenario headings use category-aware unit language. |
| Supplier Scores headings | PASS | — | Export builder differentiates RFQ and governed Supplier 360 scores with business-readable headings. |
| Supplier Comparison headings | PASS | — | Risk terminology is converted to `Risk Resilience Score`; validation context is appended. |
| Excel readable/audit sheet separation | PASS | — | Workbook builder creates readable sheets and a separate `Audit Supplier Scores` sheet. |
| Executive Memo governance | PASS | — | Memo generation is passed through eligibility-aware safety controls before download. |
| Supplier Narrative governance | PASS | — | Supplier narrative is passed through eligibility-aware safety controls before download. |
| Supplier Email governance | PASS | — | Category, commodity, unit, and eligibility are explicitly passed to the email generator. |
| Allocation export | PASS WITH LIMITATION | MINOR | Download path exists and exports the allocation dataframe directly. Direct file formatting inspection is still required. |
| Decision audit export | PASS | — | JSON output intentionally retains machine-readable structures and includes eligibility metadata. |
| Supplier 360 audit export | PASS | — | JSON profile output is download-only and not displayed as raw JSON in the business interface. |
| Scenario export integrity | PASS | — | RC1.2.3 resolves the governed annual-TCO column contract; live Multi-Scenario Stress Test renders successfully. |
| Mobile UI | PASS | — | Screenshots show functional mobile navigation, tables, charts, and download controls. Wide analytical tables require horizontal scrolling but remain usable. |
| Executive terminology | PASS | — | Visible labels use procurement language; no raw JSON is shown. |
| Direct opening of every generated artifact | NOT COMPLETED | MODERATE PROCESS GAP | The actual downloaded files were not supplied to this review session. Their final content cannot be independently confirmed from screenshots and source code alone. |

---

## Export verification by artifact

### 1. Excel Analysis

**Result:** PASS WITH FINAL DIRECT REVIEW REQUIRED

Verified from source:

- `Supplier Scores Report` sheet uses the readable score dataframe.
- `Supplier Comparison` sheet uses the readable comparison dataframe.
- `Should Cost`, `Allocation`, and `Scenarios` sheets are included.
- `Audit Supplier Scores` is separated as an audit-oriented sheet.
- The scenario dataframe now uses the governed annual-TCO schema.

Final manual checks still required:

- Open the `.xlsx` file.
- Confirm every sheet opens without repair warnings.
- Confirm column widths and numeric formatting are usable.
- Confirm PET Resin scenario values and headings match the live screen.
- Confirm no readable sheet exposes unintended snake_case fields.

### 2. Supplier Scores Report

**Result:** PASS WITH FINAL DIRECT REVIEW REQUIRED

Verified headings include:

- Supplier
- Original Currency
- Original Unit Price
- Normalized Currency
- Normalized Unit Price
- FX Rate Used
- Unit of Measure
- Comparison Basis
- Risk-Adjusted TCO (USD)
- Annual TCO (USD)
- Risk Resilience Score
- RFQ Performance Score
- RFQ ESG Score
- Supplier 360 Performance Score
- Governed Financial Indicator
- Governed ESG Maturity Score
- Governed Innovation Maturity Score
- Supplier 360 Score
- Overall Decision Score
- Data Confidence
- Eligibility Status
- Validation Warning
- Human Review Required

Regression coverage verifies that readable headings do not contain underscores.

### 3. Supplier Comparison Report

**Result:** PASS WITH FINAL DIRECT REVIEW REQUIRED

Verified:

- Risk terminology is presented as `Risk Resilience Score`.
- Data confidence, eligibility, validation warning, and human-review status are appended.
- Original and normalized currency/price fields are visible in the live Supplier Intelligence comparison screen.

### 4. Allocation Report

**Result:** PASS WITH MINOR LIMITATION

Verified:

- Download control exists.
- Live allocation tables and charts render.
- Allocation totals shown in the validated PET Resin workflow are coherent.

Limitation:

- The allocation CSV is exported directly from the dataframe. Direct inspection is required to confirm all headings remain fully business-readable and category-aware.

### 5. Executive Memo

**Result:** PASS WITH FINAL DIRECT REVIEW REQUIRED

Verified:

- Generated using validation-aware inputs.
- Routed through the eligibility safety layer.
- Downloaded as UTF-8 plain text.
- Final award language is governed by eligibility status.

### 6. Supplier Narrative

**Result:** PASS WITH FINAL DIRECT REVIEW REQUIRED

Verified:

- Generated from Supplier Intelligence.
- Routed through eligibility-aware safety controls.
- Downloaded as UTF-8 plain text.
- Live narrative presentation is executive-readable and provisional when appropriate.

### 7. Decision Machine-Readable Audit Data

**Result:** PASS

Verified payload sections:

- recommended_supplier
- value_metrics
- allocation
- scenarios
- negotiation
- eligibility

This output is intentionally technical and is correctly labelled as machine-readable audit data.

### 8. Supplier 360 Machine-Readable Audit Data

**Result:** PASS

Verified:

- Contains the Supplier 360 profile objects.
- Uses JSON only as a download.
- Does not expose raw JSON in the live executive interface.

---

## Screenshots reviewed

The following live areas were reviewed through user-provided screenshots:

- Build 1.0 RC1.2.3 application header/footer
- Raw Material Procurement — PET Resin
- Validation Assurance Gate
- Executive Dashboard
- Supplier RFQ Decision Snapshot
- Recommended Supplier Allocation
- Multi-Scenario Stress Test
- Negotiation Simulator and Playbook
- Raw Material Should-Cost Model
- Procurement Intelligence
- Optimized Allocation
- Negotiation Intelligence
- AI Explainability 2.0
- Supplier Intelligence
- Supplier Performance
- Financial evidence governance
- ESG and Innovation evidence governance
- SRM classification
- Download Decision Package

The previous scenario runtime `KeyError` is no longer present in the live screenshots.

---

## Findings by severity

### CRITICAL

None identified in the reviewed evidence.

### MAJOR

None identified in the reviewed evidence.

### MODERATE

**RC1-VAL-EVIDENCE-001 — Direct artifact content review incomplete**

The generated download files were not attached to the review session. Source-code and screenshot evidence strongly support export integrity, but final release approval requires opening the actual files and checking their content.

This is a validation-evidence gap, not a confirmed application defect.

### MINOR

**RC1-MINOR-001 — Allocation report direct-format review pending**

The allocation CSV is generated directly from the allocation dataframe. Confirm its final headings and numeric formatting in the downloaded file.

**RC1-MINOR-002 — Mobile analytical tables require horizontal scrolling**

This is acceptable for dense procurement tables and is not release-blocking.

**RC1-MINOR-003 — Numeric display precision varies by screen and output**

Standardization may be included in a post-v1.0 polish backlog. It does not invalidate the decision logic.

---

## Remaining known limitations

- Demo and uploaded data remain decision-support inputs, not verified ERP or supplier-master records.
- Financial, ESG, and innovation assessments remain evidence-dependent and are appropriately capped when evidence is weak.
- Human approval and procurement due diligence remain mandatory.
- Direct workbook formatting and CSV/TXT content must still be manually inspected.
- Time-aware analytics remains deferred to Version 1.1.

---

## Release recommendation

**Current recommendation: HOLD THE VERSION 1.0.0 TAG UNTIL DIRECT ARTIFACT INSPECTION IS COMPLETED.**

No Major or Critical product defect is visible in the reviewed evidence. However, the requested export-acceptance milestone cannot be honestly declared fully complete until the actual downloaded files are opened and reviewed.

### Acceptance condition

After the user supplies or manually confirms all eight downloaded artifacts open correctly and match the validated screen values, update this report to:

- **STATUS: Release Candidate Accepted**
- **Recommendation: Ready for Version 1.0.0 Tag**

Until then:

- Release freeze remains active.
- Do not tag `v1.0.0`.
- Do not begin Version 1.1.
