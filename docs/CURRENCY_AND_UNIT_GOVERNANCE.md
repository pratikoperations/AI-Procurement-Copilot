# Currency and Unit Governance

## Principles

1. Preserve the original supplier quotation currency and price.
2. Normalize comparative calculations to an explicit base currency.
3. Record the FX rate used.
4. Never place a non-USD amount in a USD-labelled field.
5. Block unsupported currency conversion.
6. Preserve the category unit of measure.
7. PET Resin uses kg in the current portfolio edition.

## Required fields

- Original Currency
- Original Unit Price
- Normalized Currency
- Normalized Unit Price
- FX Rate Used
- Unit of Measure
- Comparison Basis

## Current conversion support

- USD to USD: 1.0
- INR to USD: INR-per-USD rate supplied through application assumptions
- Other currencies: blocked until an approved conversion is available

## Governance warning

Normalization supports comparison only. It does not replace treasury approval, contractual FX clauses, tax review, customs review, or finance validation.
