# C3 Steel Sheets and Coils — Governed Contract

## Governance baseline

- Repository: `pratikoperations/AI-Procurement-Copilot`
- Frozen base branch: `main`
- Frozen base SHA: `0b310b4e97e0c92112089929fca150d7f183ecc8`
- Feature branch: `agent/category-expansion-c3-steel`
- Category: Raw Material Procurement — Steel Sheets and Coils
- Contract version: `C3.0-STEEL-v1`
- Phase: C3.0 documentation and contract tests only

This contract does not authorize an executable Steel cost engine, supplier data, validation, risk, scoring, recommendation, allocation, scenarios, UI controls, export production logic, deployment, tag, release or merge.

## Controlled profiles

Exactly three initial profiles are permitted.

| Profile ID | Display name | Thickness | Width band | Zinc coating | Paint coating |
|---|---|---:|---|---|---|
| `CR_COIL_COMMERCIAL` | Cold-Rolled Steel Coil | 0.80 mm | 1,000–1,250 mm | Not applicable | Not applicable |
| `GI_COIL_Z120` | Galvanized Steel Coil | 0.60 mm | 1,000–1,250 mm | 120 g/m² total | Not applicable |
| `PPGI_COIL_Z120` | Pre-Painted Galvanized Steel Coil | 0.50 mm | 1,000–1,250 mm | 120 g/m² total | Topcoat 20 μm; back coat 5 μm |

The selected profile is a controlled demonstration specification. It is not a metallurgical standard, engineering approval or technical certification.

## Commercial and currency contract

- Annual-volume input: kg.
- Optional reporting conversion: metric tonnes.
- Internal governed calculation currency: USD.
- Normalized comparison basis: USD/kg.
- User-selectable display modes: `USD`, `INR`, `Both`.
- Accepted supplier quotation currencies: `USD`, `INR`.
- One positive user-controlled USD/INR exchange-rate assumption is mandatory.
- The FX rate is a synthetic demonstration assumption, not live market data.
- All quotations must normalize to USD/kg before scoring, recommendation, allocation, scenario comparison or winner selection.
- INR values must be deterministic conversions from the single USD calculation path.
- `Both` mode must use separate numeric USD and INR columns.

Display mode must not change eligibility, supplier ranking, winner, allocation, scenario status, confidence or risk outcome.

## Fail-closed currency rules

Reject:

- missing FX rate;
- non-numeric FX rate;
- zero FX rate;
- negative FX rate;
- unsupported quote currency;
- mixed or combined text values in governed numeric export fields.

## Should-cost component contract

The intended dedicated Steel should-cost path contains:

1. base steel;
2. profile or grade premium;
3. rolling/conversion premium;
4. zinc coating where applicable;
5. paint or surface treatment where applicable;
6. energy surcharge;
7. yield-loss effect;
8. slitting/cutting;
9. packing;
10. freight;
11. duty;
12. supplier margin.

CR must reject zinc and paint components. GI must require the governed zinc coating and reject paint. PPGI must require both governed zinc and paint profiles.

## Fail-closed technical eligibility contract

Technical eligibility must be evaluated before recommendation. Mandatory controls cover:

- exact selected profile;
- controlled grade family;
- thickness capability;
- width capability;
- zinc coating capability where applicable;
- paint-line capability where applicable;
- surface requirement;
- mill or supplier approval;
- application approval;
- test-certificate availability;
- supplier capacity;
- coil-weight compatibility;
- substitution approval.

Missing, unsupported, contradictory, pending, unavailable or unapproved mandatory evidence results in technical ineligibility. A technically ineligible supplier cannot become the governed winner because of price.

## Governed scenarios

Exactly seven scenarios are permitted:

1. Base Case
2. Steel Index +20%
3. Energy and Conversion Premium +15%
4. Import Duty and FX Stress
5. Demand +25%
6. Mill Allocation and Capacity Stress
7. Grade-Substitution Scenario

Scenario outputs must disclose applicability, status, reason, winner or no-winner state, assumption version and confidence governance.

## Intended export contract

### Excel worksheets

1. Supplier Scores Report
2. Supplier Comparison
3. Should Cost
4. Allocation
5. Standard Allocation
6. Optimized Allocation
7. Scenarios
8. Audit Supplier Scores
9. C3 Governance

### Strict JSON

- Top-level block: `steel_governance`.
- Serialization: `allow_nan=False`.
- Non-finite values normalize to `null`.
- USD and INR values remain separate numeric fields.
- Required commercial metadata includes calculation currency, comparison unit, display mode, quote currency, USD/INR FX rate, FX source label, normalized USD/kg, equivalent INR/kg, annual USD value and annual INR value.

## Claim boundaries and exclusions

This controlled demonstration does not provide:

- metallurgical certification;
- engineering substitution approval;
- mill-test-certificate authentication;
- production-readiness assurance;
- live commodity or FX data;
- realized-savings evidence;
- autonomous supplier approval or award;
- ERP write-back;
- production authentication or enterprise RBAC.

Excluded product families include stainless steel, structural steel, bars, rods, pipes, tubes, castings, forgings, electrical steel, tool steel and advanced automotive grades.

C1 Kraft Paper and C2 Flexible Laminates remain frozen and must not be rewritten by C3.