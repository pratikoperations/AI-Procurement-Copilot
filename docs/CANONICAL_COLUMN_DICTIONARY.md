# Canonical Column Dictionary

## Status
Planning only. This is the schema source of truth for the ERP Upload MVP.

## General Standards
- Identifiers are text.
- Dates use ISO `YYYY-MM-DD`.
- Currency uses ISO codes.
- Percentages use 0–100.
- Original and normalized values remain separate.
- Required fields may vary by module, but critical identifiers are never defaulted.

## Common Metadata Fields

| Field | Type | Req. | Meaning | Validation | Used by |
|---|---|---:|---|---|---|
| Source_System | Text | Yes | SAP, Oracle, or Custom source | Controlled values | Audit |
| Source_Record_ID | Text | Yes | Unique source-row identifier | Unique within sheet/profile | Audit, duplicates |
| Record_Created_Date | Date | No | Source creation date | Valid date | Lineage |
| Record_Updated_Date | Date | No | Source update date | >= created date | Deduplication |
| Data_Extraction_Date | Date | Yes | Export date | Valid, not unreasonably future | Coverage |

## Supplier_Master

| Field | Type | Req. | Meaning | Example | Validation | Used by |
|---|---|---:|---|---|---|---|
| Supplier_ID | Text | Yes | Stable supplier key | 00010045 | Nonblank, unique | All supplier modules |
| Supplier_Name | Text | Yes | Display name | Apex Packaging Corp | Nonblank | UI, matching |
| Legal_Entity_Name | Text | No | Registered name | Apex Packaging Pvt Ltd | Optional | Risk, compliance |
| Country_Code | Text | Yes | Supplier country | IN | ISO code | Risk, logistics |
| Supplier_Status | Text | Yes | Active/Inactive/Blocked | Active | Controlled | Eligibility |
| Parent_Supplier_ID | Text | No | Group parent | 00010001 | Must reference master | Supplier 360 |
| Tax_ID | Text | No | Legal identifier | 27ABCDE1234F1Z5 | Country format | Matching |
| Default_Currency | Text | No | Default supplier currency | INR | ISO code | Currency |
| Payment_Terms | Text | No | Standard terms | NET45 | Controlled/free text | TCO |
| Incoterms | Text | No | Delivery terms | DDP | Controlled | TCO |
| Approved_Categories | Text | No | Category coverage | Corrugated Packaging | Delimited/map | Supplier 360 |
| Commodity_Coverage | Text | No | Commodity coverage | PET Resin | Delimited/map | SRM |

## Material_Master

| Field | Type | Req. | Meaning | Example | Validation | Used by |
|---|---|---:|---|---|---|---|
| Material_ID | Text | Yes | Stable material key | 000000PET01 | Nonblank, unique | All material modules |
| Material_Description | Text | Yes | Item description | PET Resin Bottle Grade | Nonblank | UI |
| Category | Text | Yes | Procurement category | Raw Material Procurement | Controlled | Category router |
| Commodity | Text | Yes | Commodity | PET Resin | Controlled | Should-cost |
| Base_Unit | Text | Yes | Governed base UOM | KG | Supported unit | Unit governance |
| Material_Grade | Text | No | Grade/specification | IV 0.80 | Optional | Cost model |
| Specification_ID | Text | No | Specification key | SPEC-PET-080 | Optional | Quality |
| Standard_Cost | Decimal | No | ERP reference cost | 1.22 | >=0 | Benchmarking |
| Standard_Cost_Currency | Text | Conditional | Cost currency | USD | Required if cost supplied | Currency |
| Active_Status | Text | No | Active/obsolete | Active | Controlled | Eligibility |

## RFQ_Quotes

| Field | Type | Req. | Meaning | Example | Validation | Used by |
|---|---|---:|---|---|---|---|
| RFQ_ID | Text | Yes | RFQ event | RFQ-2026-0042 | Nonblank | RFQ |
| Quote_Line_ID | Text | Yes | Quote line | 10 | Unique in RFQ/supplier | RFQ |
| Supplier_ID | Text | Yes | Supplier key | 00010045 | Match master | All |
| Material_ID | Text | Yes | Material key | 000000PET01 | Match master | Router |
| RFQ_Date | Date | Yes | RFQ date | 2026-06-01 | Valid | Historical analytics |
| Quote_Effective_Date | Date | No | Start validity | 2026-07-01 | Valid | Governance |
| Quote_Expiry_Date | Date | No | End validity | 2026-09-30 | >= effective date | Governance |
| Quoted_Quantity | Decimal | Yes | Quote quantity | 500000 | >0 | RFQ, allocation |
| Original_Unit_Price | Decimal | Yes | Source quote price | 0.45 | >0 | RFQ, TCO |
| Original_Currency | Text | Yes | Source currency | USD | ISO code | Currency |
| Original_Unit | Text | Yes | Source UOM | EA | Supported/mapped | Unit |
| MOQ | Decimal | No | Minimum order | 50000 | >=0 | Allocation |
| Lead_Time_Days | Integer | No | Lead time | 21 | >=0 | Risk |
| Payment_Terms | Text | No | Quote payment terms | NET60 | Valid | TCO |
| Incoterms | Text | No | Delivery basis | DDP | Controlled | Freight |
| Freight_Amount | Decimal | No | Explicit freight | 0.02 | >=0 | TCO |

## Purchase_Orders

| Field | Type | Req. | Meaning | Example | Validation | Used by |
|---|---|---:|---|---|---|---|
| PO_Number | Text | Yes | PO number | 4500012345 | Nonblank | Spend |
| PO_Line_Number | Text | Yes | PO line | 10 | Unique within PO | Spend |
| Supplier_ID | Text | Yes | Supplier | 00010045 | Match master | Supplier 360 |
| Material_ID | Text | Yes | Material | 000000PET01 | Match master | Category analytics |
| PO_Date | Date | Yes | PO date | 2026-05-10 | Valid | Historical analytics |
| Ordered_Quantity | Decimal | Yes | Ordered quantity | 100000 | >0 | Spend |
| Unit_Price | Decimal | Yes | PO price | 1.28 | >0 | Price history |
| Currency | Text | Yes | PO currency | USD | ISO code | Currency |
| Unit_Of_Measure | Text | Yes | PO UOM | KG | Supported/mapped | Unit |
| Plant_Or_Business_Unit | Text | No | Buying location | 1100 | Optional | Segmentation |
| Contract_ID | Text | No | Agreement reference | CTR-1022 | Optional | Compliance |
| Release_Status | Text | No | Approval status | Released | Controlled | Compliance |

## Receipts

| Field | Type | Req. | Meaning | Example | Validation | Used by |
|---|---|---:|---|---|---|---|
| Receipt_Number | Text | Yes | Receipt | 5000123456 | Nonblank | Delivery |
| Receipt_Line_Number | Text | Yes | Receipt line | 1 | Unique | Delivery |
| PO_Number | Text | Yes | Related PO | 4500012345 | Match PO | OTIF |
| PO_Line_Number | Text | Yes | Related PO line | 10 | Match PO line | OTIF |
| Supplier_ID | Text | Yes | Supplier | 00010045 | Match master | Performance |
| Material_ID | Text | Yes | Material | 000000PET01 | Match master | Performance |
| Promised_Date | Date | Yes | Expected date | 2026-05-30 | Valid | OTIF |
| Receipt_Date | Date | Yes | Actual date | 2026-06-02 | Valid | OTIF |
| Received_Quantity | Decimal | Yes | Received quantity | 98000 | >=0 | Delivery |
| Accepted_Quantity | Decimal | No | Accepted quantity | 97000 | <= received | Quality |
| Rejected_Quantity | Decimal | No | Rejected quantity | 1000 | <= received | Quality |

## Supplier_Performance

| Field | Type | Req. | Meaning | Example | Validation | Used by |
|---|---|---:|---|---|---|---|
| Supplier_ID | Text | Yes | Supplier | 00010045 | Match master | Supplier 360 |
| Period_Start | Date | Yes | Period start | 2026-04-01 | Valid | Trends |
| Period_End | Date | Yes | Period end | 2026-06-30 | >= start | Trends |
| OTIF_Percent | Decimal | No | OTIF | 94.5 | 0–100 | Performance |
| Quality_Score | Decimal | No | Quality score | 88.0 | 0–100 | Supplier 360 |
| Service_Score | Decimal | No | Service score | 82.0 | 0–100 | SRM |
| Responsiveness_Score | Decimal | No | Responsiveness | 85.0 | 0–100 | SRM |
| Contract_Compliance_Percent | Decimal | No | Compliance | 96.0 | 0–100 | Contracts |
| Supplier_Evaluation_Score | Decimal | No | Overall score | 87.0 | 0–100 | Supplier 360 |

## Cost_Drivers

| Field | Type | Req. | Meaning | Example | Validation | Used by |
|---|---|---:|---|---|---|---|
| Cost_Driver_ID | Text | Yes | Driver key | PET-INDEX | Unique by date/category | Should-cost |
| Category | Text | Yes | Category | Raw Material Procurement | Controlled | Router |
| Commodity | Text | Yes | Commodity | PET Resin | Controlled | Should-cost |
| Driver_Type | Text | Yes | Driver class | Commodity Index | Controlled | Should-cost |
| Driver_Value | Decimal | Yes | Driver value | 950 | Numeric | Should-cost |
| Currency | Text | Yes | Currency | USD | ISO code | Currency |
| Unit | Text | Yes | UOM | MT | Supported/mapped | Unit |
| Effective_Date | Date | Yes | Effective date | 2026-07-01 | Valid | Historical analytics |
| Source_Type | Text | Yes | ERP/Manual/External | External | Controlled | Confidence |
| Source_Name | Text | Yes | Source name | Market Index A | Nonblank | Audit |
| Confidence_Level | Text | No | Evidence confidence | High | Controlled | Governance |

## Display and Audit Rules
- Canonical fields may receive business-readable display labels.
- Audit exports preserve canonical and source field names.
- No field may be silently redefined by an ERP profile.
- Dictionary changes require versioning and approval.
