# Build Group C2 — Integration Architecture

## Boundary
C2 extends `rfq_workbook_adapter.py` and adds isolated ranking contract, model, semantic, and matching modules. Build D and Build E interfaces remain unchanged. No analytical DataFrame or engine call is permitted.

## Pipeline
1. Secure workbook load.
2. Preliminary `UPLOAD_METADATA` version read.
3. Select frozen v1.3.0 or additive v1.3.1 contract bundle.
4. Register `urn:aipc:minimum-workbook:1.3.0` locally; network resolution is prohibited.
5. Parse frozen quotation/history/metadata rows using the frozen schema.
6. Parse `SUPPLIER_RANKING_INPUTS` for v1.3.1 only.
7. Require bound confirmation for every non-canonical ranking alias.
8. Retain per-field `VALUE_ORIGINS` and optional source status.
9. Derive per-field canonical evidence results.
10. Apply cross-row findings, four-level scope matching, and per-supplier/item mode eligibility.
11. Return extended `AdapterResult` for review only.

## Compatibility
v1.3.0 keeps the existing three-sheet behavior. v1.3.1 adds ranking evidence alongside the unchanged quotation and PO structures. `GOVERNED_RANKING_INPUTS_NOT_CANONICAL` remains active until E2.
