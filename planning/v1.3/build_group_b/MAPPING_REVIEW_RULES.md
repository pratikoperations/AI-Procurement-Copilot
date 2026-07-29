# Header Mapping Review Rules

## Principles

1. Canonical fields are stable; source headers are variable.
2. Alias matching occurs outside procurement-engine logic.
3. Mapping output is versioned and auditable.
4. A source column maps to at most one canonical target.
5. A canonical target receives at most one active source column.
6. Unmapped source columns are retained in diagnostics but ignored by calculations.
7. Mandatory canonical fields must be resolved before analysis.
8. High-risk fields require exact alias evidence or explicit user confirmation.

## Confidence classes

| Class | Rule | Automatic acceptance |
|---|---|---|
| EXACT_APPROVED | Exact case-insensitive approved alias | Yes, except organization policy may require review |
| NORMALIZED_APPROVED | Approved alias after spacing/punctuation normalization | Yes with visible mapping |
| FUZZY_SUGGESTION | Similarity-based candidate | No |
| AMBIGUOUS | Multiple plausible targets or duplicate target | No |
| UNMAPPED | No acceptable candidate | No |

## High-risk fields

Identity, quantity, price, currency, UOM, exchange-rate and quotation-version fields may not be silently accepted from fuzzy suggestions.

## Review output

The review must show:

- source header;
- proposed canonical field;
- confidence class;
- alias-registry version;
- reviewer action;
- unresolved reason;
- final mapping;
- timestamp and analysis version.
