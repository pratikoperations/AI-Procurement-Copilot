# Test Structure

The existing pytest suite is the primary regression control for Portfolio Edition v1.0.0.

## Required Coverage Areas

- Input and external-file validation
- Header recognition and missing-data behaviour
- Currency and unit normalization
- Should-cost and TCO calculations
- Risk Resilience and supplier scoring
- Eligibility and human-review controls
- Supplier-role conflict prevention
- Scenario and freight-stress behaviour
- Allocation and negotiation outputs
- Category-aware communications
- Readable export and machine-readable audit separation
- Streamlit smoke behaviour

## Running Tests

```bash
python -m pytest
```

For any formula, threshold, schema, or governance change, add a targeted regression test before merging. Tests must use synthetic or de-identified data.
