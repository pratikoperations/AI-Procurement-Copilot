# AI Procurement Copilot v1.3 — Field Dictionary

## Interpretation

- **Mandatory:** required whenever the sheet is present.
- **Conditional:** required when the documented condition applies.
- **Optional:** may be blank; blank means unknown, not zero.
- **Required in governed internal use:** optional in portfolio demonstration but required before approved internal record retention.

| Sheet | Canonical field | Type | Requirement | Definition |
|---|---|---|---|---|
| RFQ_QUOTES | `SOURCING_EVENT_ID` | string | Mandatory | Unique governed sourcing-event identifier. |
| RFQ_QUOTES | `RFQ_NUMBER` | string | Mandatory | SAP RFQ or equivalent sourcing document number; preserve leading zeros. |
| RFQ_QUOTES | `RFQ_ITEM` | string | Mandatory | RFQ item identifier; preserve leading zeros. |
| RFQ_QUOTES | `QUOTATION_VERSION` | integer | Mandatory | Positive amendment/version number; earlier versions remain auditable. |
| RFQ_QUOTES | `SUPPLIER_ID` | string | Mandatory | Supplier identifier; preserve leading zeros. |
| RFQ_QUOTES | `SUPPLIER_NAME` | string | Mandatory | Supplier display name. |
| RFQ_QUOTES | `MATERIAL_ID` | string | Conditional | Required unless approved free-text or non-material RFQ. |
| RFQ_QUOTES | `MATERIAL_DESCRIPTION` | string | Mandatory | Quoted item or service description. |
| RFQ_QUOTES | `MATERIAL_GROUP` | string | Mandatory | Governed material/category grouping. |
| RFQ_QUOTES | `PURCHASING_ORG` | string | Mandatory | Purchasing organization. |
| RFQ_QUOTES | `REQUESTED_QUANTITY` | decimal | Mandatory | Requested quantity; must be greater than zero. |
| RFQ_QUOTES | `QUOTED_QUANTITY` | decimal | Mandatory | Quoted quantity; must be greater than zero. |
| RFQ_QUOTES | `QUOTATION_UOM` | string | Mandatory | Original quotation unit of measure. |
| RFQ_QUOTES | `COMPARISON_UOM` | string | Mandatory | Approved comparison unit of measure. |
| RFQ_QUOTES | `UOM_CONVERSION_FACTOR` | decimal | Conditional | Required when quotation and comparison UOM differ. |
| RFQ_QUOTES | `BASE_UNIT_PRICE` | decimal | Mandatory | Original quoted base price before approved additions/deductions. |
| RFQ_QUOTES | `PRICE_UNIT` | decimal | Mandatory | Price basis quantity; must be greater than zero. |
| RFQ_QUOTES | `CURRENCY` | string | Mandatory | ISO currency code. |
| RFQ_QUOTES | `EXCHANGE_RATE` | decimal | Conditional | Required when quote currency differs from approved comparison currency. |
| RFQ_QUOTES | `EXCHANGE_RATE_DATE` | date | Conditional | Required with EXCHANGE_RATE. |
| RFQ_QUOTES | `QUOTATION_DATE` | date | Mandatory | Quotation date. |
| RFQ_QUOTES | `VALIDITY_END_DATE` | date | Mandatory | Quotation validity end date. |
| RFQ_QUOTES | `QUOTATION_STATUS` | string | Mandatory | Current quotation status. |
| RFQ_QUOTES | `SOURCE_TRANSACTION` | string | Mandatory | ME49, ME80AN, Fiori report, or approved equivalent. |
| RFQ_QUOTES | `SOURCE_FILE_NAME` | string | Mandatory | Original export filename. |
| RFQ_QUOTES | `SOURCE_EXTRACTED_AT` | datetime | Mandatory | Source extraction timestamp. |
| RFQ_QUOTES | `SOURCE_ROW_ID` | string | Mandatory | Stable source-row identifier. |
| RFQ_QUOTES | `COLLECTIVE_NUMBER` | string | Optional | Collective RFQ/event number. |
| RFQ_QUOTES | `PLANT` | string | Optional | Plant/site. |
| RFQ_QUOTES | `PURCHASING_GROUP` | string | Optional | Purchasing group. |
| RFQ_QUOTES | `FREIGHT_AMOUNT` | decimal | Optional | Freight amount; blank means unknown, never zero. |
| RFQ_QUOTES | `PACKING_AMOUNT` | decimal | Optional | Packing amount. |
| RFQ_QUOTES | `INSURANCE_AMOUNT` | decimal | Optional | Insurance amount. |
| RFQ_QUOTES | `DUTY_AMOUNT` | decimal | Optional | Duty amount. |
| RFQ_QUOTES | `TAX_AMOUNT` | decimal | Optional | Tax amount; treatment governed separately. |
| RFQ_QUOTES | `TOOLING_AMOUNT` | decimal | Optional | Tooling amount. |
| RFQ_QUOTES | `OTHER_CHARGES_AMOUNT` | decimal | Optional | Other approved charges. |
| RFQ_QUOTES | `DISCOUNT_AMOUNT` | decimal | Optional | Absolute discount amount. |
| RFQ_QUOTES | `DISCOUNT_PERCENT` | decimal | Optional | Discount percentage. |
| RFQ_QUOTES | `INCOTERMS_CODE` | string | Optional | Incoterms code. |
| RFQ_QUOTES | `INCOTERMS_LOCATION` | string | Optional | Incoterms location. |
| RFQ_QUOTES | `PAYMENT_TERMS_CODE` | string | Optional | Payment-terms code. |
| RFQ_QUOTES | `PAYMENT_DAYS` | integer | Optional | Normalized payment days. |
| RFQ_QUOTES | `LEAD_TIME_DAYS` | integer | Optional | Lead time in days. |
| RFQ_QUOTES | `PROMISED_DELIVERY_DATE` | date | Optional | Promised delivery date. |
| RFQ_QUOTES | `MINIMUM_ORDER_QUANTITY` | decimal | Optional | Minimum order quantity. |
| RFQ_QUOTES | `ORDER_MULTIPLE` | decimal | Optional | Order multiple. |
| RFQ_QUOTES | `FULL_QUANTITY_AVAILABLE` | boolean | Optional | Whether full requested quantity is available. |
| RFQ_QUOTES | `TECHNICALLY_APPROVED` | boolean | Optional | Explicit technical approval indicator. |
| RFQ_QUOTES | `QUALITY_SCORE` | decimal | Optional | Approved quality score. |
| RFQ_QUOTES | `DELIVERY_SCORE` | decimal | Optional | Approved delivery score. |
| RFQ_QUOTES | `RISK_SCORE` | decimal | Optional | Approved risk score. |
| RFQ_QUOTES | `ESG_SCORE` | decimal | Optional | Approved ESG score. |
| RFQ_QUOTES | `REJECTION_REASON` | string | Optional | Reason for rejection/withdrawal/technical failure. |
| PO_HISTORY | `PO_NUMBER` | string | Mandatory | Purchase-order number; preserve leading zeros. |
| PO_HISTORY | `PO_ITEM` | string | Mandatory | PO item; preserve leading zeros. |
| PO_HISTORY | `PO_DATE` | date | Mandatory | PO document date. |
| PO_HISTORY | `SUPPLIER_ID` | string | Mandatory | Supplier identifier. |
| PO_HISTORY | `SUPPLIER_NAME` | string | Mandatory | Supplier display name. |
| PO_HISTORY | `MATERIAL_ID` | string | Conditional | Required unless approved free-text/non-material history. |
| PO_HISTORY | `MATERIAL_DESCRIPTION` | string | Mandatory | Historical item description. |
| PO_HISTORY | `MATERIAL_GROUP` | string | Mandatory | Governed category/material group. |
| PO_HISTORY | `PURCHASING_ORG` | string | Mandatory | Purchasing organization. |
| PO_HISTORY | `ORDER_QUANTITY` | decimal | Mandatory | Ordered quantity. |
| PO_HISTORY | `ORDER_UOM` | string | Mandatory | Historical order UOM. |
| PO_HISTORY | `COMPARISON_UOM` | string | Mandatory | Approved comparison UOM. |
| PO_HISTORY | `UOM_CONVERSION_FACTOR` | decimal | Conditional | Required when ORDER_UOM and COMPARISON_UOM differ. |
| PO_HISTORY | `NET_PRICE` | decimal | Mandatory | Historical net price. |
| PO_HISTORY | `PRICE_UNIT` | decimal | Mandatory | Historical price basis quantity. |
| PO_HISTORY | `CURRENCY` | string | Mandatory | ISO currency code. |
| PO_HISTORY | `EXCHANGE_RATE` | decimal | Conditional | Required when history currency differs from comparison currency. |
| PO_HISTORY | `NET_ORDER_VALUE` | decimal | Mandatory | Historical PO line value. |
| PO_HISTORY | `PO_STATUS` | string | Mandatory | PO item status. |
| PO_HISTORY | `DELETION_FLAG` | boolean | Mandatory | Deletion/cancellation indicator retained. |
| PO_HISTORY | `SOURCE_TRANSACTION` | string | Mandatory | ME80FN or approved equivalent. |
| PO_HISTORY | `SOURCE_FILE_NAME` | string | Mandatory | Source filename. |
| PO_HISTORY | `SOURCE_EXTRACTED_AT` | datetime | Mandatory | Extraction timestamp. |
| PO_HISTORY | `SOURCE_ROW_ID` | string | Mandatory | Stable source-row identifier. |
| PO_HISTORY | `PLANT` | string | Optional | Plant/site. |
| PO_HISTORY | `PURCHASING_GROUP` | string | Optional | Purchasing group. |
| PO_HISTORY | `PAYMENT_TERMS_CODE` | string | Optional | Payment terms. |
| PO_HISTORY | `PAYMENT_DAYS` | integer | Optional | Normalized payment days. |
| PO_HISTORY | `INCOTERMS_CODE` | string | Optional | Incoterms code. |
| PO_HISTORY | `CONTRACT_NUMBER` | string | Optional | Contract reference. |
| PO_HISTORY | `INFO_RECORD_NUMBER` | string | Optional | Purchasing info-record reference. |
| PO_HISTORY | `REQUESTED_DELIVERY_DATE` | date | Optional | Requested delivery date. |
| PO_HISTORY | `ACTUAL_RECEIPT_DATE` | date | Optional | Actual receipt date. |
| PO_HISTORY | `DELIVERED_QUANTITY` | decimal | Optional | Delivered quantity. |
| PO_HISTORY | `ON_TIME_FLAG` | boolean | Optional | On-time indicator. |
| PO_HISTORY | `IN_FULL_FLAG` | boolean | Optional | In-full indicator. |
| PO_HISTORY | `DELIVERY_DELAY_DAYS` | integer | Optional | Delivery delay in days. |
| PO_HISTORY | `QUALITY_REJECTED_QUANTITY` | decimal | Optional | Rejected quantity. |
| PO_HISTORY | `INVOICE_VARIANCE_AMOUNT` | decimal | Optional | Invoice variance amount. |
| UPLOAD_METADATA | `UPLOAD_ID` | string | Required in governed internal use | Unique upload identifier. |
| UPLOAD_METADATA | `SCHEMA_VERSION` | string | Required in governed internal use | Contract version, initially 1.3.0. |
| UPLOAD_METADATA | `UPLOAD_MODE` | string | Required in governed internal use | QUICK_RFQ or FULL_SOURCING_REVIEW. |
| UPLOAD_METADATA | `SOURCE_SYSTEM` | string | Required in governed internal use | Source system family. |
| UPLOAD_METADATA | `SAP_SYSTEM_ID` | string | Optional | SAP system identifier. |
| UPLOAD_METADATA | `SAP_RELEASE` | string | Optional | SAP release reported by organization. |
| UPLOAD_METADATA | `COMPANY_CODE` | string | Optional | Company code. |
| UPLOAD_METADATA | `PURCHASING_ORG` | string | Required in governed internal use | Purchasing organization. |
| UPLOAD_METADATA | `BASE_CURRENCY` | string | Required in governed internal use | Approved comparison currency. |
| UPLOAD_METADATA | `EXTRACTED_BY` | string | Optional | Extractor identity; avoid personal data in public demo. |
| UPLOAD_METADATA | `EXTRACTED_AT` | datetime | Required in governed internal use | Extraction timestamp. |
| UPLOAD_METADATA | `UPLOAD_CREATED_AT` | datetime | Required in governed internal use | Workbook creation timestamp. |
| UPLOAD_METADATA | `HISTORY_START_DATE` | date | Conditional | Required when PO_HISTORY is used. |
| UPLOAD_METADATA | `HISTORY_END_DATE` | date | Conditional | Required when PO_HISTORY is used. |
| UPLOAD_METADATA | `RFQ_SOURCE_TRANSACTION` | string | Required in governed internal use | ME49, ME80AN, or equivalent. |
| UPLOAD_METADATA | `HISTORY_SOURCE_TRANSACTION` | string | Conditional | ME80FN or equivalent when history is used. |
| UPLOAD_METADATA | `RFQ_VARIANT_NAME` | string | Optional | Saved variant name. |
| UPLOAD_METADATA | `HISTORY_VARIANT_NAME` | string | Optional | Saved history variant name. |
| UPLOAD_METADATA | `DATA_CLASSIFICATION` | string | Required in governed internal use | Approved classification. |
| UPLOAD_METADATA | `ANONYMIZATION_STATUS` | string | Required in governed internal use | SYNTHETIC, SANITIZED, or APPROVED_PRIVATE. |
| UPLOAD_METADATA | `FILE_HASH_SHA256` | string | Required in governed internal use | SHA-256 of approved source workbook or package. |
| UPLOAD_METADATA | `NOTES` | string | Optional | Governed notes. |
