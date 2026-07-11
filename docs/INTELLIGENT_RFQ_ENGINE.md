# Intelligent RFQ Engine

## Purpose

The Intelligent RFQ Engine accepts supplier files with different header names and converts them into the canonical schema required by the procurement decision engine.

## Capabilities

- Exact and fuzzy header recognition
- Canonical column mapping
- Unit-of-measure normalization
- Numeric conversion diagnostics
- Duplicate supplier detection
- Missing-data analysis
- Unmapped-column preservation
- RFQ upload quality score
- User-facing validation recommendations

## Canonical Required Fields

- Supplier
- Quoted Unit Price USD
- MOQ
- Lead Time Days
- Payment Terms
- Incoterms

## Example Header Recognition

| Source Header | Canonical Header |
|---|---|
| Vendor Name | Supplier |
| Unit Rate | Quoted Unit Price USD |
| Minimum Order Quantity | MOQ |
| Delivery Days | Lead Time Days |
| Credit Terms | Payment Terms |
| Delivery Terms | Incoterms |
| UOM | Unit |

## Unit Normalization

Common variants are normalized:

- kgs / kilogram → kg
- tonnes / ton → MT
- pcs / ea → piece
- ltr / litre → liter
- metre / meters → meter

Unknown units are preserved rather than silently changed.

## Quality Score

The RFQ quality score considers:

- Share of source columns successfully mapped
- Data completeness
- Duplicate supplier penalty
- Numeric conversion penalty

A score below 70/100 triggers a warning that the file should be reviewed before award use.

## Governance

The engine supports decision preparation; it does not make assumptions silently. Unmapped columns are preserved, conversion issues are reported, and missing required fields block scoring.
