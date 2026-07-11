# Category-Specific Cost and Risk Engines

## Build

Build 0.9.4

## Purpose

Build 0.9.4 activates production-grade category separation. Packaging and raw materials now use different should-cost, TCO, risk, and scoring logic.

## Packaging Engine

The packaging workflow continues to use:

- Substrate / paper
- Resin / film / foil
- Printing and conversion
- Tooling and plate amortization
- Scrap and wastage
- Packaging freight
- Supplier quality and service risk
- MOQ, payment, lead time, and incoterm exposure

## Raw Material Engine

The raw-material workflow now uses:

- Commodity index
- Conversion / producer premium
- Freight
- Duty / import cost
- FX exposure
- Grade / quality premium
- Supplier margin
- Inventory and working capital
- Commodity volatility buffer
- Risk-adjusted continuity premium

## Raw Material Risk Factors

- Commodity volatility
- Import dependency
- Supplier concentration
- Substitute availability
- Capacity buffer
- Quality PPM
- Currency exposure
- Logistics lead time
- Commercial terms
- Incoterms

## Category-Aware Scoring

Packaging and raw materials use different weights. Raw materials place more emphasis on risk and slightly less on MOQ and lead time because commodity exposure, continuity, and import dependency can dominate the decision.

## Governance

The application no longer presents packaging calculations as raw-material intelligence. Category selection controls demo data, should-cost, TCO, risk, and supplier scoring.
