# ERP Upload Template Specification

## Status

Version 1.1 planning only. No application implementation is authorized by this document.

## Purpose

Define a single Excel workbook that can be populated from SAP or Oracle exports and uploaded to AI Procurement Copilot after future implementation.

## File Standard

- Format: `.xlsx`
- Maximum first-release size target: 50 MB
- Sheet names must match exactly.
- First row contains canonical column headers.
- No merged cells.
- No formulas required from the user.
- No hidden rows or columns in the standard template.
- Dates use `YYYY-MM-DD`.
- Percentages use numeric values from 0 to 100.
- Currency uses ISO 4217 codes.
- Units use governed codes such as `EA`, `KG`, `MT`, `L`, `M`, or `M2`.
- Every sheet includes source and extraction metadata.

## Required Sheets

### 1. Supplier_Master

Required columns:

- `Supplier_ID`
- `Supplier_Name`
- `Country_Code`
- `Supplier_Status`
- `Source_System`
- `Source_Record_ID`
- `Data_Extraction_Date`

Recommended optional columns:

- `Legal_Entity_Name`
- `Parent_Supplier_ID`
- `Tax_ID`
- `Default_Currency`
- `Payment_Terms`
- `Incoterms`
- `Approved_Categories`
- `Commodity_Coverage`
- `Risk_Flag`
- `Compliance_Status`
- `Record_Created_Date`
- `Record_Updated_Date`

Primary use:

- Supplier identity
- Supplier 360
- SRM
- Risk and eligibility

### 2. RFQ_Quotes

Required columns:

- `RFQ_ID`
- `Quote_Line_ID`
- `Supplier_ID`
- `Material_ID`
- `RFQ_Date`
- `Quoted_Quantity`
- `Original_Unit_Price`
- `Original_Currency`
- `Original_Unit`
- `Source_System`
- `Source_Record_ID`
- `Data_Extraction_Date`

Recommended optional columns:

- `Quote_Effective_Date`
- `Quote_Expiry_Date`
- `MOQ`
- `Lead_Time_Days`
- `Payment_Terms`
- `Incoterms`
- `Freight_Amount`
- `Tax_Amount`
- `Capacity_Available`
- `Technical_Compliance_Status`
- `Commercial_Compliance_Status`

Primary use:

- RFQ comparison
- Best-value decision
- TCO
- Negotiation
- Allocation

### 3. Purchase_Orders

Required columns:

- `PO_Number`
- `PO_Line_Number`
- `Supplier_ID`
- `Material_ID`
- `PO_Date`
- `Ordered_Quantity`
- `Unit_Price`
- `Currency`
- `Unit_Of_Measure`
- `Source_System`
- `Source_Record_ID`
- `Data_Extraction_Date`

Recommended optional columns:

- `Plant_Or_Business_Unit`
- `Contract_ID`
- `Buyer_ID`
- `Release_Status`
- `Delivery_Date`
- `Freight_Amount`
- `Tax_Amount`
- `PO_Status`

Primary use:

- Spend history
- Volume and price trend
- Contract compliance
- Supplier concentration
- TCO

### 4. Receipts

Required columns:

- `Receipt_Number`
- `Receipt_Line_Number`
- `PO_Number`
- `PO_Line_Number`
- `Supplier_ID`
- `Material_ID`
- `Promised_Date`
- `Receipt_Date`
- `Received_Quantity`
- `Source_System`
- `Source_Record_ID`
- `Data_Extraction_Date`

Recommended optional columns:

- `Accepted_Quantity`
- `Rejected_Quantity`
- `Receipt_Status`
- `Plant_Or_Business_Unit`

Primary use:

- OTIF
- Delivery reliability
- Lead-time variance
- Quantity fulfilment

### 5. Invoices

Required columns:

- `Invoice_Number`
- `Invoice_Line_Number`
- `Supplier_ID`
- `Invoice_Date`
- `Invoice_Unit_Price`
- `Invoice_Currency`
- `Source_System`
- `Source_Record_ID`
- `Data_Extraction_Date`

Recommended optional columns:

- `PO_Number`
- `PO_Line_Number`
- `Invoice_Quantity`
- `Freight_Amount`
- `Tax_Amount`
- `Payment_Date`
- `Payment_Status`
- `Invoice_Status`

Primary use:

- Invoice-price variance
- Payment analysis
- Freight and tax visibility
- Commercial leakage

### 6. Quality_Performance

Required columns:

- `Quality_Record_ID`
- `Supplier_ID`
- `Inspection_Date`
- `Source_System`
- `Source_Record_ID`
- `Data_Extraction_Date`

Recommended optional columns:

- `Material_ID`
- `Inspected_Quantity`
- `Accepted_Quantity`
- `Rejected_Quantity`
- `Defect_Count`
- `PPM`
- `NCR_Status`
- `Corrective_Action_Due_Date`
- `Corrective_Action_Close_Date`
- `Severity`

Primary use:

- Supplier quality
- PPM and rejection trends
- Corrective-action governance
- Supplier development

### 7. Supplier_Performance

Required columns:

- `Supplier_ID`
- `Period_Start`
- `Period_End`
- `Source_System`
- `Source_Record_ID`
- `Data_Extraction_Date`

Recommended optional columns:

- `OTIF_Percent`
- `Quality_Score`
- `Service_Score`
- `Responsiveness_Score`
- `Contract_Compliance_Percent`
- `Supplier_Evaluation_Score`
- `Risk_Score`
- `ESG_Score`
- `Innovation_Score`
- `Review_Status`
- `Reviewed_By`

Primary use:

- Supplier scorecards
- Supplier 360
- SRM classification
- Time-aware trend analytics

### 8. Contracts

Required columns:

- `Contract_ID`
- `Supplier_ID`
- `Contract_Start_Date`
- `Contract_End_Date`
- `Contract_Currency`
- `Source_System`
- `Source_Record_ID`
- `Data_Extraction_Date`

Recommended optional columns:

- `Material_ID`
- `Contract_Unit_Price`
- `Contract_Quantity`
- `Payment_Terms`
- `Incoterms`
- `Auto_Renewal_Flag`
- `Termination_Notice_Days`
- `Contract_Status`
- `Owner`
- `Compliance_Percent`

Primary use:

- Contract expiry
- Compliance
- Leakage
- Renewal risk

### 9. Material_Master

Required columns:

- `Material_ID`
- `Material_Description`
- `Category`
- `Commodity`
- `Base_Unit`
- `Source_System`
- `Source_Record_ID`
- `Data_Extraction_Date`

Recommended optional columns:

- `Material_Grade`
- `Specification_ID`
- `Standard_Cost`
- `Standard_Cost_Currency`
- `Standard_Pack_Size`
- `Weight_Per_Piece`
- `Conversion_Factor`
- `Active_Status`

Primary use:

- Category routing
- Unit normalization
- Specification matching
- Should-cost inputs

### 10. Cost_Drivers

Required columns:

- `Cost_Driver_ID`
- `Category`
- `Commodity`
- `Driver_Type`
- `Driver_Value`
- `Currency`
- `Unit`
- `Effective_Date`
- `Source_Type`
- `Source_Name`
- `Source_System`
- `Source_Record_ID`
- `Data_Extraction_Date`

Recommended optional columns:

- `Confidence_Level`
- `Geography`
- `Supplier_ID`
- `Material_ID`
- `Index_Name`
- `Reference_URL_Or_Document`
- `Notes`

Primary use:

- Should-cost
- Commodity and freight scenarios
- Negotiation benchmarks

## Validation Rules

### Workbook-Level

- All ten sheets must exist, even if an optional sheet has zero rows.
- Duplicate sheet names are invalid.
- Unknown sheets may be retained but ignored unless mapped.
- A validation summary must list rows accepted, warned, quarantined, and rejected.

### Identifier Rules

- `Supplier_ID` and `Material_ID` are text, not numeric, to preserve leading zeros.
- IDs must not be trimmed or reformatted.
- Blank IDs in transaction sheets are blocking errors.

### Currency Rules

- Use ISO currency codes.
- Original and normalized values must remain separate.
- Missing FX rates block cross-currency comparisons.

### Unit Rules

- Use controlled units.
- Unknown units require mapping.
- No price comparison is allowed across incompatible units.

### Date Rules

- Dates must be parseable.
- End dates must not precede start dates.
- Missing governing dates exclude records from time-based analysis and lower confidence.

### Numeric Rules

- Quantities and prices must be numeric and nonnegative.
- Percentages must be between 0 and 100.
- Rejected quantity must not exceed inspected or received quantity.

### Referential Integrity

- Every transaction supplier must exist in `Supplier_Master`.
- Every transaction material must exist in `Material_Master`, unless explicitly marked nonmaterial.
- Receipt and invoice PO references must resolve where supplied.
- Contract references must resolve where supplied.

## User Experience for Future Upload

The future upload screen should show:

1. File selected
2. ERP profile selected or detected
3. Sheet recognition status
4. Column mapping status
5. Data-quality summary
6. Supplier and material match summary
7. Currency and unit warnings
8. Historical coverage
9. Recommendation eligibility impact
10. Confirm and process action

## Output of Ingestion

After successful ingestion, the application should produce:

- Canonical supplier table
- Canonical material table
- Canonical RFQ table
- Canonical transaction tables
- Mapping audit
- Data-quality report
- Match exceptions
- Missing-field summary
- Historical-period coverage
- Module-eligibility matrix

## Template Versioning

Every workbook should include a hidden or visible `Template_Metadata` section in a later implementation containing:

- `Template_Version`
- `Generated_Date`
- `ERP_Profile`
- `Organization_Name`
- `Prepared_By`
- `Reporting_Period_Start`
- `Reporting_Period_End`

Recommended first template version:

`ERP_UPLOAD_TEMPLATE_V1`

## Acceptance Criteria

- A user can export SAP or Oracle reports and copy or map them into the workbook without changing Copilot logic.
- Validation identifies missing, invalid, duplicate, and unmatched records before analysis.
- All raw source fields remain auditable.
- The workbook supports RFQ, SRM, Supplier 360, TCO, should-cost, contract, quality, and performance analysis.
