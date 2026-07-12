# Sprint 1 Asset Manifest

## Status

Pre-implementation assets generated. Application modules remain unimplemented.

## Excel Workbooks

| File | SAP/Oracle role | Sheets | Historical coverage | SHA-256 |
|---|---|---:|---|---|
| `synthetic_sap_procurement_workbook.xlsx` | SAP S/4HANA-style positive dataset | 7 | 18+ months | `a45ed3df8c24b282936b27b2afdf5ae386c1a04814a65334e9bed601548f59e4` |
| `synthetic_oracle_procurement_workbook.xlsx` | Oracle Fusion-style positive dataset | 7 | 18+ months | `b42536c70b5dfb52008cf1895c8aad38851c7e59524f3e03ae16805145591823` |
| `erp_adversarial_procurement_workbook.xlsx` | Negative and unsafe-data dataset | 7 | Mixed deliberately invalid records | `27d9091fe9a48c4a9d98604a266b051f9585f5b08ae309785389e1bb543e7de2` |

## Positive Workbook Row Counts

| Sheet | SAP rows | Oracle rows |
|---|---:|---:|
| Supplier_Master | 25 | 25 |
| RFQ_Quotes | 180 | 180 |
| Purchase_Orders | 360 | 360 |
| Receipts | 360 | 360 |
| Supplier_Performance | 100 | 100 |
| Material_Master | 40 | 40 |
| Cost_Drivers | 72 | 72 |

## Mapping Assets

- `config/mappings/sap_s4hana_mapping_profile.json`
- `config/mappings/oracle_fusion_mapping_profile.json`
- `config/mappings/custom_mapping_profile_template.json`

## Sprint Controls

- `planning/SPRINT1_TASK_CHECKLIST.md`
- `planning/SPRINT1_TEST_CASE_MATRIX.md`

## Important Note

The Excel binaries were generated and verified locally. The current connector supports text-file commits but does not provide a direct repository-content operation for uploading local binary files through the normal contents workflow. The workbooks must therefore be uploaded manually to the branch under `data/erp_samples/` while preserving the filenames and SHA-256 values above.

No Version 1.0 file was modified.