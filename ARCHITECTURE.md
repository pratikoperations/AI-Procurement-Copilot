# Architecture

## Architecture Principle

AI Procurement Copilot is designed as a modular, category-aware procurement decision platform, not merely a Streamlit script.

## High-Level Layers

```text
AI Procurement Copilot
├── Presentation Layer
├── Category Engine Router
│   ├── Packaging Engine
│   └── Raw Material Engine
├── Commodity Library
├── Common Procurement Decision Engine
├── Business Rules Layer
├── AI Assistance Layer
├── Data Validation + Test Layer
├── Export + Handoff Layer
└── Documentation + Recovery Layer
```

## Presentation Layer

Current interface: Streamlit.

The interface exposes category, commodity, currency, scenario, and allocation controls while keeping engine maturity visible to the user.

## Category Engine Router

`modules/category_engine.py` is the entry point for category selection.

It:

- Registers supported categories.
- Routes requests to the correct category engine.
- Returns a common engine-profile contract.
- Distinguishes Active engines from Foundation Preview engines.
- Prevents unsupported categories from failing silently.

## Commodity Library

`modules/commodity_library.py` stores category-aware metadata:

- Commodity family
- Unit of measure
- Primary cost drivers
- Risk signals

The library is metadata-driven so new commodities can be added without rewriting the application shell.

## Common Procurement Decision Engine

Shared logic across production-ready categories:

- RFQ validation and normalization
- Supplier comparison
- Advanced TCO
- Risk scoring
- ESG scoring
- Supplier performance scoring
- Decision weighting
- Allocation recommendation
- Scenario simulation
- Executive recommendation
- Export package generation

## Packaging Engine

**Status:** Active

Current category-specific logic includes:

- Substrate / paper
- Resin / film / foil
- Ink / coating
- Adhesive / solvent
- Printing
- Conversion
- Lamination / slitting
- Tooling / plate amortization
- Scrap / wastage
- Packaging freight buffer
- EPR / recyclability / PCR logic

Initial commodity profiles:

- Corrugated Board
- Flexible Laminates
- PET Bottles
- Labels

## Raw Material Engine

**Status:** Foundation Preview in Build 0.9.1

Architecture and metadata are active for:

- PET Resin
- Polyethylene
- Polypropylene
- Aluminium Foil
- Steel
- Copper

Planned category-specific logic:

- Commodity index
- Conversion / producer premium
- Freight and duties
- FX exposure
- Additives or processing
- Supplier margin
- Volatility risk
- Contract indexation
- Substitute availability
- Supply concentration

The application intentionally stops before supplier scoring when Raw Material Procurement is selected until the production engine is implemented.

## AI Assistance Layer

AI supports:

- Explanation
- Summarization
- Email drafting
- Negotiation playbooks
- Executive memo drafting
- RFQ interpretation

AI does not replace transparent procurement decision logic.

## Data Layer

Current data sources:

- Synthetic demo data
- CSV RFQ upload
- Excel RFQ upload

Future sources:

- Supplier master
- ERP export
- Spend cube
- Commodity indices

## Design Priorities

1. Explainability
2. Procurement credibility
3. Category separation
4. Modular code
5. Interview readiness
6. GitHub recoverability
7. Future category extensibility
