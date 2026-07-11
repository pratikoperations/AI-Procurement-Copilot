# Category Engine

## Purpose

The Category Engine separates shared procurement decision logic from category-specific commercial logic.

## Active Registry

- Packaging Procurement — Active production engine
- Raw Material Procurement — Foundation preview

## Architecture

```text
Category Engine Router
├── Packaging Engine
│   └── Packaging commodity metadata
└── Raw Material Engine
    └── Raw-material commodity metadata
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
