# Raw Material Engine

## Current Status

Foundation Preview — Build 0.9.1

## Purpose

The Raw Material Engine will support commodity-aware sourcing decisions without reusing packaging-specific should-cost assumptions.

## Initial Commodity Library

- PET Resin
- Polyethylene
- Polypropylene
- Aluminium Foil
- Steel
- Copper

## Planned Cost Model

```text
Commodity Index
+ Conversion / Producer Premium
+ Freight
+ Duty
+ FX Impact
+ Inventory and Working Capital
+ Risk-Adjusted Continuity Premium
= Delivered Risk-Adjusted TCO
```

## Planned Risk Signals

- Commodity volatility
- Import dependency
- FX exposure
- Supply concentration
- Plant or mine disruption
- Grade qualification
- Substitute availability
- Trade restrictions
- Contract indexation exposure

## Build 0.9.1 Boundary

Build 0.9.1 activates:

- Category routing
- Commodity selection
- Cost-driver metadata
- Risk-signal metadata
- Transparent preview UI

It does not yet activate raw-material supplier scoring, should-cost calculation, or award recommendations. Those capabilities are planned for Build 0.9.4.
