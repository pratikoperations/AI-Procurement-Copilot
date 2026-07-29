# AI Procurement Copilot v1.3 — Field Dictionary

Requirement classes: **Mandatory**, **Conditional**, **Optional**, and **Required in governed internal use**. Blank optional values mean unknown, not zero.

## RFQ_QUOTES

| Field | Type | Requirement | Definition |
|---|---|---|---|
| `SOURCING_EVENT_ID` | string | Mandatory | Unique governed sourcing-event identifier. |
| `RFQ_NUMBER` | string | Mandatory | SAP RFQ or equivalent sourcing document number; preserve leading zeros. |
| `RFQ_ITEM` | string | Mandatory | RFQ item identifier; preserve leading zeros. |
| `QUOTATION_VERSION` | integer | Mandatory | Positive amendment/version number; earlier versions remain auditable. |
| `SUPPLIER_ID` | string | Mandatory | Supplier identifier; preserve leading zeros. |
| `SUPPLIER_NAME` | string | Mandatory | Supplier display name. |
| `MATERIAL_ID` | string | Conditional | Required unless approved free-text or non-material RFQ. |
| `MATERIAL_DESCRIPTION` | string | Mandatory | Quoted item or service description. |
| `MATERIAL_GROUP` | string | Mandatory | Governed material/category grouping. |
| `PURCHASING_ORG` | string | Mandatory | Purchasing organization. |
| `REQUESTED_QUANTITY` | decimal | Mandatory | Requested quantity; must be greater than zero. |
| `QUOTED_QUANTITY` | decimal | Mandatory | Quoted quantity; must be greater than zero. |
| `QUOTATION_UOM` | string | Mandatory | Original quotation unit of measure. |
| `COMPARISON_UOM` | string | Mandatory | Approved comparison unit of measure. |
| `UOM_CONVERSION_FACTOR` | decimal | Conditional | Required when quotation and comparison UOM differ. |
| `BASE_UNIT_PRICE` | decimal | Mandatory | Original quoted base price before approved additions/deductions. |
| `PRICE_UNIT` | decimal | Mandatory | Price basis quantity; must be greater than zero. |
| `CURRENCY` | string | Mandatory | ISO currency code. |
| `EXCHANGE_RATE` | decimal | Conditional | Required when quote currency differs from approved comparison currency. |
| `EXCHANGE_RATE_DATE` | date | Conditional | Required with EXCHANGE_RATE. |
| `QUOTATION_DATE` | date | Mandatory | Quotation date. |
| `VALIDITY_END_DATE` | date | Mandatory | Quotation validity end date. |
| `QUOTATION_STATUS` | string | Mandatory | Current quotation status. |
| `SOURCE_TRANSACTION` | string | Mandatory | ME49, ME80AN, Fiori report, or approved equivalent. |
| `SOURCE_FILE_NAME` | string | Mandatory | Original export filename. |
| `SOURCE_EXTRACTED_AT` | datetime | Mandatory | Source extraction timestamp. |
| `SOURCE_ROW_ID` | string | Mandatory | Stable source-row identifier. |
| `COLLECTIVE_NUMBER` | string | Optional | Collective RFQ/event number. |
| `PLANT` | string | Optional | Plant/site. |
| `PURCHASING_GROUP` | string | Optional | Purchasing group. |
| `FREIGHT_AMOUNT` | decimal | Optional | Freight amount; blank means unknown, never zero. |
| `PACKING_AMOUNT` | decimal | Optional | Packing amount. |
| `INSURANCE_AMOUNT` | decimal | Optional | Insurance amount. |
| `DUTY_AMOUNT` | decimal | Optional | Duty amount. |
| `TAX_AMOUNT` | decimal | Optional | Tax amount; treatment governed separately. |
| `TOOLING_AMOUNT` | decimal | Optional | Tooling amount. |
| `OTHER_CHARGES_AMOUNT` | decimal | Optional | Other approved charges. |
| `DISCOUNT_AMOUNT` | decimal | Optional | Absolute discount amount. |
| `DISCOUNT_PERCENT` | decimal | Optional | Discount percentage. |
| `INCOTERMS_CODE` | string | Optional | Incoterms code. |
| `INCOTERMS_LOCATION` | string | Optional | Incoterms location. |
| `PAYMENT_TERMS_CODE` | string | Optional | Payment-terms code. |
| `PAYMENT_DAYS` | integer | Optional | Normalized payment days. |
| `LEAD_TIME_DAYS` | integer | Optional | Lead time in days. |
| `PROMISED_DELIVERY_DATE` | date | Optional | Promised delivery date. |
| `MINIMUM_ORDER_QUANTITY` | decimal | Optional | Minimum order quantity. |
| `ORDER_MULTIPLE` | decimal | Optional | Order multiple. |
| `FULL_QUANTITY_AVAILABLE` | boolean | Optional | Whether full requested quantity is available. |
| `TECHNICALLY_APPROVED` | boolean | Optional | Explicit technical approval indicator. |
| `QUALITY_SCORE` | decimal | Optional | Approved quality score. |
| `DELIVERY_SCORE` | decimal | Optional | Approved delivery score. |
| `RISK_SCORE` | decimal | Optional | Approved risk score. |
| `ESG_SCORE` | decimal | Optional | Approved ESG score. |
| `REJECTION_REASON` | string | Optional | Reason for rejection/withdrawal/technical failure. |

## PO_HISTORY

| Field | Type | Requirement | Definition |
|---|---|---|---|
| `PO_NUMBER` | string | Mandatory | Purchase-order number; preserve leading zeros. |
| `PO_ITEM` | string | Mandatory | PO item; preserve leading zeros. |
| `PO_DATE` | date | Mandatory | PO document date. |
| `SUPPLIER_ID` | string | Mandatory | Supplier identifier. |
| `SUPPLIER_NAME` | string | Mandatory | Supplier display name. |
| `MATERIAL_ID` | string | Conditional | Required unless approved free-text/non-material history. |
| `MATERIAL_DESCRIPTION` | string | Mandatory | Historical item description. |
| `MATERIAL_GROUP` | string | Mandatory | Governed category/material group. |
| `PURCHASING_ORG` | string | Mandatory | Purchasing organization. |
| `ORDER_QUANTITY` | decimal | Mandatory | Ordered quantity. |
| `ORDER_UOM` | string | Mandatory | Historical order UOM. |
| `COMPARISON_UOM` | string | Mandatory | Approved comparison UOM. |
| `UOM_CONVERSION_FACTOR` | decimal | Conditional | Required when ORDER_UOM and COMPARISON_UOM differ. |
| `NET_PRICE` | decimal | Mandatory | Historical net price. |
| `PRICE_UNIT` | decimal | Mandatory | Historical price basis quantity. |
| `CURRENCY` | string | Mandatory | ISO currency code. |
| `EXCHANGE_RATE` | decimal | Conditional | Required when history currency differs from comparison currency. |
| `NET_ORDER_VALUE` | decimal | Mandatory | Historical PO line value. |
| `PO_STATUS` | string | Mandatory | PO item status. |
| `DELETION_FLAG` | boolean | Mandatory | Deletion/cancellation indicator retained. |
| `SOURCE_TRANSACTION` | string | Mandatory | ME80FN or approved equivalent. |
| `SOURCE_FILE_NAME` | string | Mandatory | Source filename. |
| `SOURCE_EXTRACTED_AT` | datetime | Mandatory | Extraction timestamp. |
| `SOURCE_ROW_ID` | string | Mandatory | Stable source-row identifier. |
| `PLANT` | string | Optional | Plant/site. |
| `PURCHASING_GROUP` | string | Optional | Purchasing group. |
| `PAYMENT_TERMS_CODE` | string | Optional | Payment terms. |
| `PAYMENT_DAYS` | integer | Optional | Normalized payment days. |
| `INCOTERMS_CODE` | string | Optional | Incoterms code. |
| `CONTRACT_NUMBER` | string | Optional | Contract reference. |
| `INFO_RECORD_NUMBER` | string | Optional | Purchasing info-record reference. |
| `REQUESTED_DELIVERY_DATE` | date | Optional | Requested delivery date. |
| `ACTUAL_RECEIPT_DATE` | date | Optional | Actual receipt date. |
| `DELIVERED_QUANTITY` | decimal | Optional | Delivered quantity. |
| `ON_TIME_FLAG` | boolean | Optional | On-time indicator. |
| `IN_FULL_FLAG` | boolean | Optional | In-full indicator. |
| `DELIVERY_DELAY_DAYS` | integer | Optional | Delivery delay in days. |
| `QUALITY_REJECTED_QUANTITY` | decimal | Optional | Rejected quantity. |
| `INVOICE_VARIANCE_AMOUNT` | decimal | Optional | Invoice variance amount. |

## UPLOAD_METADATA

| Field | Type | Requirement | Definition |
|---|---|---|---|
| `UPLOAD_ID` | string | Required in governed internal use | Unique upload identifier. |
| `SCHEMA_VERSION` | string | Required in governed internal use | Contract version, initially 1.3.0. |
| `UPLOAD_MODE` | string | Required in governed internal use | QUICK_RFQ or FULL_SOURCING_REVIEW. |
| `SOURCE_SYSTEM` | string | Required in governed internal use | Source system family. |
| `SAP_SYSTEM_ID` | string | Optional | SAP system identifier. |
| `SAP_RELEASE` | string | Optional | SAP release reported by organization. |
| `COMPANY_CODE` | string | Optional | Company code. |
| `PURCHASING_ORG` | string | Required in governed internal use | Purchasing organization. |
| `BASE_CURRENCY` | string | Required in governed internal use | Approved comparison currency. |
| `EXTRACTED_BY` | string | Optional | Extractor identity; avoid personal data in public demo. |
| `EXTRACTED_AT` | datetime | Required in governed internal use | Extraction timestamp. |
| `UPLOAD_CREATED_AT` | datetime | Required in governed internal use | Workbook creation timestamp. |
| `HISTORY_START_DATE` | date | Conditional | Required when PO_HISTORY is used. |
| `HISTORY_END_DATE` | date | Conditional | Required when PO_HISTORY is used. |
| `RFQ_SOURCE_TRANSACTION` | string | Required in governed internal use | ME49, ME80AN, or equivalent. |
| `HISTORY_SOURCE_TRANSACTION` | string | Conditional | ME80FN or equivalent when history is used. |
| `RFQ_VARIANT_NAME` | string | Optional | Saved variant name. |
| `HISTORY_VARIANT_NAME` | string | Optional | Saved history variant name. |
| `DATA_CLASSIFICATION` | string | Required in governed internal use | Approved classification. |
| `ANONYMIZATION_STATUS` | string | Required in governed internal use | SYNTHETIC, SANITIZED, or APPROVED_PRIVATE. |
| `SOURCE_FILE_HASH_SHA256` | string | Required in governed internal use | SHA-256 of the original SAP/Fiori/company export before canonical preparation; not the canonical workbook containing this field. |
| `NOTES` | string | Optional | Governed notes. |

## Hash handling

- `SOURCE_FILE_HASH_SHA256` is the SHA-256 of the original SAP/Fiori/company export before canonical workbook preparation. It may be stored in `UPLOAD_METADATA`.
- `UPLOAD_FILE_HASH_SHA256` is computed during ingestion for the completed canonical workbook and stored in the external event/audit record. It is not a workbook column, preventing self-referential hashing.
