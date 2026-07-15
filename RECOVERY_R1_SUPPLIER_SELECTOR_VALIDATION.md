# Recovery R1 Supplier Selector Validation

Date: 2026-07-15

## Capability Evidence
Stable code contains `st.selectbox("Select Supplier 360 Profile", ...)` and maps the selected supplier name to the corresponding profile. The maintenance wrapper delegates to the original Supplier Intelligence renderer and does not create a duplicate selector.

## Automated Evidence
- Supplier Intelligence UI contract tests: PASS
- Selector-preservation source assertion: PASS
- Complete candidate regression: PASS
- Streamlit startup smoke: PASS
- Supplier-selector capability: VERIFIED COMPLETE
- Automated preservation and startup evidence: VERIFIED COMPLETE

## Available Synthetic Suppliers
### Packaging demo
| Supplier | Hosted selection attempted | Matching Supplier 360 confirmed | Stale/wrong/empty view check | Classification |
|---|---|---|---|---|
| Apex Packaging Corp | No | Not directly observed | Not directly observed | NOT STARTED |
| Vertex Global Print | No | Not directly observed | Not directly observed | NOT STARTED |
| Matrix Logistics & Pack | No | Not directly observed | Not directly observed | NOT STARTED |

### Raw-material demo
| Supplier | Hosted selection attempted | Matching Supplier 360 confirmed | Stale/wrong/empty view check | Classification |
|---|---|---|---|---|
| Indus Materials Ltd | No | Not directly observed | Not directly observed | NOT STARTED |
| Global Commodity Corp | No | Not directly observed | Not directly observed | NOT STARTED |
| Bharat Advanced Polymers | No | Not directly observed | Not directly observed | NOT STARTED |

## Validation Boundary
Repository evidence does not contain an authoritative hosted Streamlit URL, and the connected GitHub environment does not provide browser interaction. Therefore all-supplier hosted interactive acceptance remains NOT STARTED.

No stale-state, duplicate-selector, wrong-profile or empty-view defect was found in code or automated tests, but absence of such evidence is not a substitute for hosted interaction.
