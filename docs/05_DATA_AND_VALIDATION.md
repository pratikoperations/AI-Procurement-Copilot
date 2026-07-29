# AI Procurement Copilot v1.2 — Data and Validation

## Data principles

The application is designed around visible assumptions, preserved source evidence and deterministic validation. It distinguishes original quotation values from normalized comparison fields and keeps business-readable outputs separate from machine-readable audit data.

## Input sources

- Synthetic demonstration datasets
- Supported CSV and Excel RFQ uploads
- Separate XLSX-only ERP Upload Preview

Public demonstrations should use synthetic, sanitized or non-confidential data.

## Procurement-data controls

Implemented controls include:

- required-field checks;
- duplicate-supplier detection;
- invalid or negative-value checks;
- supported currency handling;
- visible FX-rate metadata;
- category and unit validation;
- annual-volume and capacity checks;
- data-confidence assessment;
- business-rule validation;
- recommendation eligibility and withholding controls.

## Comparison basis

The application preserves original currency and unit-price information and creates explicit normalized fields for comparison. Display-currency changes do not alter canonical procurement calculations or supplier rankings.

## Recommendation gates

The system can classify an evaluation as eligible, eligible with conditions or blocked. When evidence or validation is insufficient, final award-oriented language is withheld or qualified. This is a decision-control feature, not an autonomous approval mechanism.

## ERP workbook preview controls

The ERP Preview checks workbook-package and structural conditions such as unsupported macros, external links, connections, query tables, sheet structure, headers and dimensions. BLOCKED inputs suppress mapping preview and stop processing.

The ERP page does not:

- inspect or display full business rows;
- normalize procurement records;
- match supplier or material masters;
- connect to SAP or Oracle;
- send data to procurement engines;
- persist or write back data.

## Data limitations

Validation quality depends on available source data and configured rules. The application has not been validated against live organizational datasets or enterprise master-data environments. Production use would require customer-specific schemas, lineage, reconciliation, privacy, security and operational controls.