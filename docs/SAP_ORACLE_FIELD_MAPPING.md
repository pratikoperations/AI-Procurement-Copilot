# SAP and Oracle Field Mapping

## Status

Version 1.1 planning only. ERP field names vary by product version, configuration, report, data warehouse, and organization. The mappings below are canonical examples and must be confirmed against the user's actual extracts.

## Mapping Principles

- Map business meaning, not only column labels.
- Preserve source columns in audit metadata.
- Prefer stable identifiers over descriptions.
- Never infer currency, unit, supplier, or material identity from free text when an authoritative code exists.
- Treat SAP ECC, SAP S/4HANA, Oracle EBS, and Oracle Fusion as separate mapping profiles where needed.

## 1. Supplier_Master

| Standard column | SAP equivalent | Oracle equivalent | Description | Req. | Type | Example | Validation | Copilot module |
|---|---|---|---|---|---|---|---|---|
| Supplier_ID | LIFNR / Business Partner ID | VENDOR_ID / SUPPLIER_ID | Stable supplier identifier | Yes | Text | 100045 | Unique, nonblank | All supplier modules |
| Supplier_Name | NAME1 / BP Name | VENDOR_NAME / SUPPLIER_NAME | Supplier display name | Yes | Text | Apex Packaging Corp | Nonblank | RFQ, Supplier 360 |
| Legal_Entity_Name | NAME1/NAME2 | LEGAL_BUSINESS_NAME | Registered entity | No | Text | Apex Packaging Pvt Ltd | Optional | Risk, compliance |
| Country_Code | LAND1 | COUNTRY_CODE | ISO country | Yes | Text | IN | ISO-2/3 | Risk, logistics |
| Supplier_Status | SPERR / deletion/block indicators | ENABLED_FLAG / STATUS | Active or blocked state | Yes | Text | Active | Controlled values | Eligibility |
| Parent_Supplier_ID | Parent BP / group field | PARENT_VENDOR_ID | Parent relationship | No | Text | 100001 | Must reference supplier | Supplier 360 |
| Tax_ID | STCD1/STCD2 | TAXPAYER_ID | Legal tax identifier | No | Text | 27ABCDE1234F1Z5 | Format by country | Matching, compliance |
| Default_Currency | WAERS | INVOICE_CURRENCY_CODE | Default transactional currency | No | Text | INR | ISO currency | Currency governance |
| Payment_Terms | ZTERM | TERMS_NAME / TERM_ID | Standard payment terms | No | Text | NET45 | Valid term | TCO, working capital |
| Incoterms | INCO1/INCO2 | FOB_LOOKUP_CODE / FREIGHT_TERMS | Delivery terms | No | Text | DDP | Controlled values | TCO, risk |
| Approved_Categories | Classification / custom field | Category assignment / DFF | Approved category coverage | No | Text | Corrugated Packaging | Delimited or mapped | Supplier 360, SRM |
| Source_System | Constant | Constant | ERP source | Yes | Text | SAP_S4 | Controlled | Audit |

## 2. RFQ_Quotes

| Standard column | SAP equivalent | Oracle equivalent | Description | Req. | Type | Example | Validation | Copilot module |
|---|---|---|---|---|---|---|---|---|
| RFQ_ID | EBELN / RFQ number | NEGOTIATION_NUMBER / RFQ_NUM | RFQ event | Yes | Text | RFQ-2026-0042 | Nonblank | RFQ analysis |
| Quote_Line_ID | EBELP | LINE_NUMBER | Quote line | Yes | Text | 10 | Unique within RFQ/supplier | RFQ analysis |
| Supplier_ID | LIFNR | SUPPLIER_ID | Supplier | Yes | Text | 100045 | Must match master | All |
| Material_ID | MATNR | ITEM_ID / ITEM_NUMBER | Material or item | Yes | Text | PET-RESIN-01 | Must match material master | Category routing |
| RFQ_Date | BEDAT / ERDAT | CREATION_DATE | RFQ creation date | Yes | Date | 2026-06-01 | Valid date | Time analytics |
| Quote_Effective_Date | ANGDT / custom | QUOTE_START_DATE | Quote start | No | Date | 2026-07-01 | Valid date | Price validity |
| Quote_Expiry_Date | EINDT / custom | QUOTE_END_DATE | Quote expiry | No | Date | 2026-09-30 | >= effective date | Governance |
| Quoted_Quantity | KTMNG / MENGE | QUANTITY | Quoted quantity | Yes | Number | 500000 | >0 | RFQ, allocation |
| Original_Unit_Price | NETPR | PRICE / UNIT_PRICE | Supplier quote | Yes | Decimal | 0.45 | >0 | RFQ, TCO |
| Original_Currency | WAERS | CURRENCY_CODE | Quote currency | Yes | Text | USD | ISO currency | Currency governance |
| Original_Unit | MEINS | UOM_CODE | Quote unit | Yes | Text | EA | Governed unit | Unit governance |
| MOQ | BSTMI / custom | MIN_ORDER_QUANTITY | Minimum order | No | Number | 50000 | >=0 | Allocation, risk |
| Lead_Time_Days | PLIFZ / custom | LEAD_TIME | Quoted lead time | No | Integer | 21 | >=0 | Risk, inventory |
| Payment_Terms | ZTERM | PAYMENT_TERMS | Quote terms | No | Text | NET60 | Valid term | TCO |
| Incoterms | INCO1/INCO2 | FOB_LOOKUP_CODE | Delivery basis | No | Text | DDP | Controlled | Freight logic |
| Freight_Amount | FRA1 / condition value | FREIGHT_AMOUNT | Explicit freight | No | Decimal | 0.02 | >=0 | TCO, scenarios |
| Source_Record_ID | RFQ+item+vendor | Header/line ID | Source uniqueness | Yes | Text | 6001-10-100045 | Unique | Audit |

## 3. Purchase_Orders

| Standard column | SAP equivalent | Oracle equivalent | Description | Req. | Type | Example | Validation | Copilot module |
|---|---|---|---|---|---|---|---|---|
| PO_Number | EBELN | PO_HEADER_ID / SEGMENT1 | Purchase order | Yes | Text | 4500012345 | Nonblank | Spend, compliance |
| PO_Line_Number | EBELP | PO_LINE_ID / LINE_NUM | PO line | Yes | Text | 10 | Unique within PO | Spend |
| Supplier_ID | LIFNR | VENDOR_ID | Supplier | Yes | Text | 100045 | Match master | Supplier 360 |
| Material_ID | MATNR | ITEM_ID | Item | Yes | Text | PET-RESIN-01 | Match master | Category analytics |
| PO_Date | BEDAT | CREATION_DATE | PO date | Yes | Date | 2026-05-10 | Valid | Time analytics |
| Ordered_Quantity | MENGE | QUANTITY | Ordered quantity | Yes | Number | 100000 | >0 | Spend, volume |
| Unit_Price | NETPR | UNIT_PRICE | PO price | Yes | Decimal | 1.28 | >0 | Price history |
| Currency | WAERS | CURRENCY_CODE | PO currency | Yes | Text | USD | ISO | Currency governance |
| Unit_Of_Measure | MEINS | UOM_CODE | PO unit | Yes | Text | KG | Governed | Unit governance |
| Plant_Or_Business_Unit | WERKS | ORG_ID / BUSINESS_UNIT | Buying location | No | Text | 1100 | Controlled | Segmentation |
| Contract_ID | KONNR | FROM_HEADER_ID / AGREEMENT_NUM | Linked agreement | No | Text | CTR-1022 | Valid reference | Contract compliance |
| Release_Status | FRGKE / status | AUTHORIZATION_STATUS | Approval status | No | Text | Released | Controlled | Compliance |

## 4. Receipts

| Standard column | SAP equivalent | Oracle equivalent | Description | Req. | Type | Example | Validation | Copilot module |
|---|---|---|---|---|---|---|---|---|
| Receipt_Number | MBLNR | RECEIPT_NUM / SHIPMENT_HEADER_ID | Receipt | Yes | Text | 5000123456 | Nonblank | Delivery analytics |
| Receipt_Line_Number | ZEILE | SHIPMENT_LINE_ID | Receipt line | Yes | Text | 1 | Unique | Delivery analytics |
| PO_Number | EBELN | PO_HEADER_ID / PO_NUM | Related PO | Yes | Text | 4500012345 | Must match PO | OTIF |
| PO_Line_Number | EBELP | PO_LINE_ID | Related line | Yes | Text | 10 | Must match PO line | OTIF |
| Supplier_ID | LIFNR | VENDOR_ID | Supplier | Yes | Text | 100045 | Match master | Performance |
| Material_ID | MATNR | ITEM_ID | Item | Yes | Text | PET-RESIN-01 | Match material | Performance |
| Promised_Date | EINDT | NEED_BY_DATE / PROMISED_DATE | Expected delivery | Yes | Date | 2026-05-30 | Valid | OTIF |
| Receipt_Date | BUDAT / CPUDT | RECEIPT_DATE | Actual receipt | Yes | Date | 2026-06-02 | Valid | OTIF |
| Received_Quantity | MENGE | QUANTITY_RECEIVED | Quantity received | Yes | Number | 98000 | >=0 | Delivery reliability |
| Accepted_Quantity | custom / inspection lot | QUANTITY_ACCEPTED | Accepted quantity | No | Number | 97000 | <= received | Quality |
| Rejected_Quantity | custom / inspection lot | QUANTITY_REJECTED | Rejected quantity | No | Number | 1000 | <= received | Quality |

## 5. Invoices

| Standard column | SAP equivalent | Oracle equivalent | Description | Req. | Type | Example | Validation | Copilot module |
|---|---|---|---|---|---|---|---|---|
| Invoice_Number | BELNR / XBLNR | INVOICE_NUM | Invoice | Yes | Text | INV-77841 | Nonblank | Invoice analytics |
| Invoice_Line_Number | BUZEI | INVOICE_LINE_NUMBER | Invoice line | Yes | Text | 1 | Unique | Invoice analytics |
| Supplier_ID | LIFNR | VENDOR_ID | Supplier | Yes | Text | 100045 | Match master | Supplier 360 |
| PO_Number | EBELN | PO_HEADER_ID / PO_NUM | Related PO | No | Text | 4500012345 | Valid if present | Compliance |
| Invoice_Date | BLDAT | INVOICE_DATE | Invoice date | Yes | Date | 2026-06-05 | Valid | Time analytics |
| Invoice_Quantity | MENGE | QUANTITY_INVOICED | Quantity | No | Number | 98000 | >=0 | Variance |
| Invoice_Unit_Price | WRBTR/MENGE or condition | UNIT_PRICE | Invoiced price | Yes | Decimal | 1.30 | >=0 | PPV |
| Invoice_Currency | WAERS | INVOICE_CURRENCY_CODE | Currency | Yes | Text | USD | ISO | Currency governance |
| Freight_Amount | condition / charge line | FREIGHT_AMOUNT | Freight charge | No | Decimal | 2000 | >=0 | TCO |
| Tax_Amount | MWSKZ / tax value | TAX_AMOUNT | Tax | No | Decimal | 18000 | >=0 | TCO |
| Payment_Date | AUGDT | PAYMENT_DATE | Payment date | No | Date | 2026-07-15 | >= invoice date | Working capital |
| Payment_Status | AUGBL/open item status | PAYMENT_STATUS_FLAG | Paid/open status | No | Text | Paid | Controlled | Compliance |

## 6. Quality_Performance

| Standard column | SAP equivalent | Oracle equivalent | Description | Req. | Type | Example | Validation | Copilot module |
|---|---|---|---|---|---|---|---|---|
| Quality_Record_ID | Inspection lot / notification | QUALITY_RESULT_ID | Quality event | Yes | Text | QN-10072 | Unique | Quality |
| Supplier_ID | LIFNR | SUPPLIER_ID | Supplier | Yes | Text | 100045 | Match master | Supplier 360 |
| Material_ID | MATNR | ITEM_ID | Item | No | Text | PET-RESIN-01 | Match if present | Category quality |
| Inspection_Date | PRUEFLOS dates | INSPECTION_DATE | Event date | Yes | Date | 2026-06-03 | Valid | Time analytics |
| Inspected_Quantity | LOSMENGE | INSPECTED_QTY | Quantity inspected | No | Number | 98000 | >=0 | Quality score |
| Rejected_Quantity | defect/rejection qty | REJECTED_QTY | Rejected quantity | No | Number | 1000 | <= inspected | Quality score |
| Defect_Count | QDEF / notification count | DEFECT_COUNT | Defects | No | Integer | 12 | >=0 | PPM |
| PPM | Derived/custom | PPM | Parts per million | No | Decimal | 122.4 | >=0 | Quality score |
| NCR_Status | QM notification status | NCR_STATUS | Corrective action status | No | Text | Open | Controlled | Risk, development |
| Corrective_Action_Due_Date | QM task date | CAPA_DUE_DATE | Due date | No | Date | 2026-06-30 | Valid | SRM |

## 7. Supplier_Performance

| Standard column | SAP equivalent | Oracle equivalent | Description | Req. | Type | Example | Validation | Copilot module |
|---|---|---|---|---|---|---|---|---|
| Supplier_ID | LIFNR | SUPPLIER_ID | Supplier | Yes | Text | 100045 | Match master | Supplier 360 |
| Period_Start | Evaluation period/custom | PERIOD_START_DATE | Period start | Yes | Date | 2026-04-01 | Valid | Time analytics |
| Period_End | Evaluation period/custom | PERIOD_END_DATE | Period end | Yes | Date | 2026-06-30 | >= start | Time analytics |
| OTIF_Percent | Vendor evaluation/custom | OTIF_PERCENT | On-time in-full | No | Decimal | 94.5 | 0-100 | Performance |
| Quality_Score | LFA1 evaluation/custom | QUALITY_SCORE | Quality rating | No | Decimal | 88.0 | 0-100 | Supplier 360 |
| Service_Score | Vendor evaluation | SERVICE_SCORE | Service rating | No | Decimal | 82.0 | 0-100 | SRM |
| Responsiveness_Score | Custom | RESPONSIVENESS_SCORE | Response rating | No | Decimal | 85.0 | 0-100 | SRM |
| Contract_Compliance_Percent | Derived | CONTRACT_COMPLIANCE | Compliance | No | Decimal | 96.0 | 0-100 | Contracts |
| Supplier_Evaluation_Score | Vendor evaluation total | OVERALL_SCORE | Overall evaluation | No | Decimal | 87.0 | 0-100 | Supplier 360 |

## 8. Contracts

| Standard column | SAP equivalent | Oracle equivalent | Description | Req. | Type | Example | Validation | Copilot module |
|---|---|---|---|---|---|---|---|---|
| Contract_ID | KONNR / outline agreement | PO_HEADER_ID / AGREEMENT_NUM | Contract | Yes | Text | CTR-1022 | Unique | Contract management |
| Supplier_ID | LIFNR | VENDOR_ID | Supplier | Yes | Text | 100045 | Match master | SRM |
| Material_ID | MATNR | ITEM_ID | Item | No | Text | PET-RESIN-01 | Match if present | Category compliance |
| Contract_Start_Date | KDATB | START_DATE | Start | Yes | Date | 2026-01-01 | Valid | Expiry analytics |
| Contract_End_Date | KDATE | END_DATE | End | Yes | Date | 2026-12-31 | >= start | Expiry analytics |
| Contract_Currency | WAERS | CURRENCY_CODE | Currency | Yes | Text | USD | ISO | Currency governance |
| Contract_Unit_Price | NETPR | UNIT_PRICE | Contracted price | No | Decimal | 1.27 | >=0 | Leakage |
| Contract_Quantity | KTMNG | AGREED_QUANTITY | Contract quantity | No | Number | 1000000 | >=0 | Utilization |
| Payment_Terms | ZTERM | TERMS_NAME | Contract payment terms | No | Text | NET60 | Valid | TCO |
| Incoterms | INCO1/INCO2 | FOB_LOOKUP_CODE | Contract delivery basis | No | Text | DDP | Controlled | TCO |
| Auto_Renewal_Flag | Custom | AUTO_RENEW_FLAG | Renewal | No | Boolean | No | Boolean | Risk |
| Termination_Notice_Days | Custom | NOTICE_DAYS | Notice period | No | Integer | 90 | >=0 | Contract risk |

## 9. Material_Master

| Standard column | SAP equivalent | Oracle equivalent | Description | Req. | Type | Example | Validation | Copilot module |
|---|---|---|---|---|---|---|---|---|
| Material_ID | MATNR | INVENTORY_ITEM_ID / ITEM_NUMBER | Item identifier | Yes | Text | PET-RESIN-01 | Unique | Category routing |
| Material_Description | MAKTX | DESCRIPTION | Description | Yes | Text | PET Resin Bottle Grade | Nonblank | UI |
| Category | MATKL / product hierarchy | CATEGORY_NAME | Procurement category | Yes | Text | Raw Material Procurement | Controlled | Router |
| Commodity | Commodity code/custom | COMMODITY | Commodity | Yes | Text | PET Resin | Controlled | Should-cost |
| Base_Unit | MEINS | PRIMARY_UOM_CODE | Base unit | Yes | Text | KG | Governed | Unit normalization |
| Material_Grade | CLASS / characteristic | ATTRIBUTE / DFF | Grade/specification | No | Text | IV 0.80 | Optional | Cost model |
| Specification_ID | Classification/spec | SPECIFICATION_ID | Spec link | No | Text | SPEC-PET-080 | Optional | Quality, risk |
| Standard_Cost | STPRS | ITEM_COST | ERP standard cost | No | Decimal | 1.22 | >=0 | Benchmarking |
| Standard_Cost_Currency | WAERS | CURRENCY_CODE | Cost currency | No | Text | USD | ISO | Currency governance |

## 10. Cost_Drivers

ERP systems usually hold only part of this data. External and manual fields are explicitly identified.

| Standard column | SAP equivalent | Oracle equivalent | Description | Req. | Type | Example | Validation | Copilot module |
|---|---|---|---|---|---|---|---|---|
| Cost_Driver_ID | Custom / material cost component | Custom / cost element | Driver ID | Yes | Text | PET-INDEX | Unique by effective date | Should-cost |
| Category | MATKL/custom | CATEGORY_NAME | Category | Yes | Text | Raw Material Procurement | Controlled | Router |
| Commodity | Material group/custom | COMMODITY | Commodity | Yes | Text | PET Resin | Controlled | Should-cost |
| Driver_Type | Cost component | COST_ELEMENT_TYPE | Index, labour, freight, energy | Yes | Text | Commodity Index | Controlled | Should-cost |
| Driver_Value | Standard cost component/custom | COST_ELEMENT_VALUE | Driver value | Yes | Decimal | 950 | Numeric | Should-cost |
| Currency | WAERS | CURRENCY_CODE | Currency | Yes | Text | USD | ISO | Currency governance |
| Unit | MEINS | UOM_CODE | Unit | Yes | Text | MT | Governed | Unit governance |
| Effective_Date | Costing date | EFFECTIVE_DATE | Effective date | Yes | Date | 2026-07-01 | Valid | Time analytics |
| Source_Type | Constant | Constant | ERP, Manual, External | Yes | Text | External | Controlled | Data confidence |
| Source_Name | Custom | Custom | Index/provider/source | Yes | Text | Market Index A | Nonblank | Audit |
| Confidence_Level | Custom | Custom | Evidence confidence | No | Text | High | Controlled | Governance |

## Mapping Profile Governance

Each organization-specific profile must record:

- ERP product and version
- Report or extract name
- Source sheet
- Source field
- Canonical field
- Transformation
- Unit conversion
- Currency rule
- Date format
- Required-field override
- Data owner
- Approval date
- Version number

## Final Rule

These mappings are design references, not universal SAP or Oracle truths. Before implementation, test against at least one real SAP extract and one real Oracle extract and document every deviation.