"""Canonical structural schema registry for Version 1.1 ERP uploads.

This module is independent of Streamlit and Version 1.0 business logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class SheetSchema:
    """Structural metadata for one approved ERP workbook sheet."""

    name: str
    required_columns: frozenset[str]
    optional_columns: frozenset[str]

    @property
    def known_columns(self) -> frozenset[str]:
        return self.required_columns | self.optional_columns


SHEET_SCHEMAS: Mapping[str, SheetSchema] = {
    "Supplier_Master": SheetSchema(
        "Supplier_Master",
        frozenset({"Supplier_ID", "Supplier_Name", "Country_Code", "Supplier_Status"}),
        frozenset({"Legal_Entity_Name", "Parent_Supplier_ID", "Tax_ID", "Default_Currency", "Payment_Terms", "Incoterms", "Approved_Categories", "Commodity_Coverage"}),
    ),
    "RFQ_Quotes": SheetSchema(
        "RFQ_Quotes",
        frozenset({"RFQ_ID", "Quote_Line_ID", "Supplier_ID", "Material_ID", "RFQ_Date", "Quoted_Quantity", "Original_Unit_Price", "Original_Currency", "Original_Unit"}),
        frozenset({"Quote_Effective_Date", "Quote_Expiry_Date", "MOQ", "Lead_Time_Days", "Payment_Terms", "Incoterms", "Freight_Amount"}),
    ),
    "Purchase_Orders": SheetSchema(
        "Purchase_Orders",
        frozenset({"PO_Number", "PO_Line_Number", "Supplier_ID", "Material_ID", "PO_Date", "Ordered_Quantity", "Unit_Price", "Currency", "Unit_Of_Measure"}),
        frozenset({"Plant_Or_Business_Unit", "Contract_ID", "Release_Status"}),
    ),
    "Receipts": SheetSchema(
        "Receipts",
        frozenset({"Receipt_Number", "Receipt_Line_Number", "PO_Number", "PO_Line_Number", "Supplier_ID", "Material_ID", "Promised_Date", "Receipt_Date", "Received_Quantity"}),
        frozenset({"Accepted_Quantity", "Rejected_Quantity"}),
    ),
    "Supplier_Performance": SheetSchema(
        "Supplier_Performance",
        frozenset({"Supplier_ID", "Period_Start", "Period_End"}),
        frozenset({"OTIF_Percent", "Quality_Score", "Service_Score", "Responsiveness_Score", "Contract_Compliance_Percent", "Supplier_Evaluation_Score"}),
    ),
    "Material_Master": SheetSchema(
        "Material_Master",
        frozenset({"Material_ID", "Material_Description", "Category", "Commodity", "Base_Unit"}),
        frozenset({"Material_Grade", "Specification_ID", "Standard_Cost", "Standard_Cost_Currency", "Active_Status"}),
    ),
    "Cost_Drivers": SheetSchema(
        "Cost_Drivers",
        frozenset({"Cost_Driver_ID", "Category", "Commodity", "Driver_Type", "Driver_Value", "Currency", "Unit", "Effective_Date", "Source_Type", "Source_Name"}),
        frozenset({"Confidence_Level"}),
    ),
}

REQUIRED_SHEETS: tuple[str, ...] = tuple(SHEET_SCHEMAS)
COMMON_METADATA_COLUMNS: frozenset[str] = frozenset({
    "Source_System", "Source_Record_ID", "Record_Created_Date",
    "Record_Updated_Date", "Data_Extraction_Date",
})


def get_sheet_schema(sheet_name: str) -> SheetSchema:
    """Return the schema for an approved sheet or raise a clear error."""
    try:
        return SHEET_SCHEMAS[sheet_name]
    except KeyError as exc:
        raise KeyError(f"Unsupported ERP sheet: {sheet_name}") from exc


def validate_registry() -> None:
    """Fail fast if the static registry contains structural defects."""
    if len(REQUIRED_SHEETS) != 7:
        raise ValueError("ERP MVP must define exactly seven required sheets.")
    for name, schema in SHEET_SCHEMAS.items():
        if schema.name != name:
            raise ValueError(f"Schema name mismatch for {name}.")
        overlap = schema.required_columns & schema.optional_columns
        if overlap:
            raise ValueError(f"Columns cannot be both required and optional in {name}: {sorted(overlap)}")
        if not schema.required_columns:
            raise ValueError(f"{name} must define at least one required column.")


validate_registry()
