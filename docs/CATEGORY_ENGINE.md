# Category Engine

## Purpose

The Category Engine separates shared procurement decision logic from category-specific commercial logic.

## Active Registry

- Packaging Procurement — Active production engine
- Raw Material Procurement — Active production engine
- MRO / Industrial Supplies — Foundation Preview (MRO-0)
- Logistics & Freight — Foundation Preview (LOGISTICS-0)

## Architecture

```text
Category Engine Router
├── Packaging Engine
│   └── Packaging commodity metadata
├── Raw Material Engine
│   └── Raw-material commodity metadata
├── MRO / Industrial Supplies Engine
│   └── Industrial Bearings foundation contracts and synthetic metadata
└── Logistics & Freight Engine
    └── Domestic Road Transportation — FTL lane, carrier, evidence, and service contracts
```

## Common Category Contract

Each category engine returns:

- Category name
- Engine status
- Selected commodity
- Supported commodities
- Cost-model description
- Risk-model description
- Unit of measure
- Primary cost drivers
- Category risk signals
- Implementation note

## Governance Rule

The application must not reuse packaging cost logic for raw materials and present it as category-specific intelligence. Until the raw-material engine is fully implemented, the UI clearly labels it as a foundation preview and stops before supplier scoring.

## Extension Pattern

A new category should:

1. Define its engine module.
2. Implement the common category profile contract.
3. Register itself in `modules/category_engine.py`.
4. Add commodity metadata.
5. Add regression tests.
6. Add category-specific cost, risk, scoring, and scenario logic before being marked Active.


## MRO-0 Foundation Governance

MRO-0 introduces a dedicated MRO / Industrial Supplies engine with Industrial Bearings as the first representative commodity.

- Manufacturer and manufacturer-part-number identity are explicit contract fields.
- Source status is explicit: OEM, Authorized Distributor, or Approved Equivalent.
- Technical compatibility is fail-closed when required evidence is missing or conflicting.
- Approved-equivalent substitution requires explicit human approval.
- Supplier selection remains a human procurement decision.
- MRO risk dimensions are qualitative in MRO-0; no unsupported numerical weights are introduced.
- No MRO should-cost, supplier scoring, scenario, negotiation, or percentage-allocation engine is active.
- Synthetic demonstration evidence is isolated and must not be represented as manufacturer certification or live supplier verification.


## LOGISTICS-0 Foundation Governance

LOGISTICS-0 introduces a dedicated Logistics & Freight engine with Domestic Road Transportation — Full Truck Load (FTL) as the first representative service.

- Lane identity is explicit: origin, destination, transport mode, and service type.
- Vehicle type and minimum payload capacity are explicit service-compatibility fields.
- Carrier status is explicit: Contracted Carrier, Approved Carrier, or Spot / Unverified Carrier.
- Lane/service compatibility is fail-closed when required evidence is missing or conflicting.
- Spot / unverified carrier use requires explicit human approval before the offer can be treated as compatible for human review.
- Commercial evidence captures base freight rate, rate basis, fuel-surcharge treatment, toll treatment, detention, loading/unloading, payment terms, and quote validity without calculating a normalized freight cost.
- Performance evidence can record capacity status, transit time, OTIF, and damage/claim rate without applying score weights or thresholds.
- Logistics risk dimensions remain qualitative in LOGISTICS-0; no unsupported numerical weights are introduced.
- No freight-cost engine, carrier scoring, scenario, allocation, route optimization, negotiation, live fuel/route data, telematics, TMS integration, or autonomous carrier award is active.
- Synthetic demonstration evidence must not be represented as live carrier certification, live route data, fuel-market data, or external verification.
