from modules.erp_schema_registry import (
    COMMON_METADATA_COLUMNS,
    REQUIRED_SHEETS,
    SHEET_SCHEMAS,
    get_sheet_schema,
    validate_registry,
)


def test_registry_contains_exactly_seven_approved_sheets():
    assert REQUIRED_SHEETS == (
        "Supplier_Master",
        "RFQ_Quotes",
        "Purchase_Orders",
        "Receipts",
        "Supplier_Performance",
        "Material_Master",
        "Cost_Drivers",
    )
    assert set(REQUIRED_SHEETS) == set(SHEET_SCHEMAS)


def test_every_sheet_has_required_columns_and_no_overlap():
    validate_registry()

    for schema in SHEET_SCHEMAS.values():
        assert schema.required_columns
        assert not schema.required_columns.intersection(schema.optional_columns)
        assert schema.known_columns == schema.required_columns | schema.optional_columns


def test_supplier_and_rfq_critical_columns_are_registered():
    supplier_schema = get_sheet_schema("Supplier_Master")
    rfq_schema = get_sheet_schema("RFQ_Quotes")

    assert {"Supplier_ID", "Supplier_Name"}.issubset(supplier_schema.required_columns)
    assert {
        "RFQ_ID",
        "Supplier_ID",
        "Material_ID",
        "Original_Unit_Price",
        "Original_Currency",
        "Original_Unit",
    }.issubset(rfq_schema.required_columns)


def test_common_metadata_columns_are_defined_separately():
    assert {
        "Source_System",
        "Source_Record_ID",
        "Data_Extraction_Date",
    }.issubset(COMMON_METADATA_COLUMNS)


def test_unknown_sheet_raises_clear_error():
    try:
        get_sheet_schema("Invoices")
    except KeyError as exc:
        assert "Unsupported ERP sheet: Invoices" in str(exc)
    else:
        raise AssertionError("Unknown ERP sheet should raise KeyError")
