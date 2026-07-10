# Architecture

## Architecture Principle

AI Procurement Copilot is designed as a modular procurement decision platform, not merely a Streamlit script.

## High-Level Layers

```text
AI Procurement Copilot
├── Presentation Layer
├── Procurement Decision Engine
├── Category Engine Layer
├── Business Rules Layer
├── AI Assistance Layer
├── Data Layer
└── Documentation + Recovery Layer
```

## Presentation Layer

Initial interface: Streamlit.

Future interfaces may include:

- React
- Power BI
- Microsoft Teams
- Internal procurement portal
- API-driven interface

## Procurement Decision Engine

Shared logic across categories:

- RFQ normalization
- Supplier comparison
- Advanced TCO
- Risk scoring
- ESG scoring
- Supplier performance scoring
- Decision weighting
- Allocation recommendation
- Scenario simulation
- Executive recommendation

## Category Engine Layer

### v1.0 Packaging Engine

Category-specific logic:

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

### v1.1 Raw Material Engine

Future logic:

- Commodity index
- Conversion premium
- Freight and duties
- Additives or processing
- Supplier margin
- Volatility risk
- Contract indexation

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

Initial data sources:

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
3. Modular code
4. Interview readiness
5. GitHub recoverability
6. Future category extensibility
