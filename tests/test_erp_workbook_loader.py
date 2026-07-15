from io import BytesIO
from pathlib import Path

import pytest
from openpyxl import Workbook

from modules.erp_schema_registry import REQUIRED_SHEETS
from modules.erp_workbook_loader import WorkbookLoadError, load_erp_workbook


SAMPLE_DIR = Path("data/erp_samples")


def _workbook_bytes(sheet_names=REQUIRED_SHEETS, *, headers=None, with_data=True):
    workbook = Workbook()
    workbook.remove(workbook.active)
    for sheet_name in sheet_names:
        sheet = workbook.create_sheet(sheet_name)
        sheet.append(headers or ["Column_A", "Column_B"])
        if with_data:
            sheet.append(["A", "B"])
    buffer = BytesIO()
    workbook.save(buffer)
    workbook.close()
    return buffer.getvalue()


@pytest.mark.parametrize(
    "filename",
    [
        "synthetic_sap_procurement_workbook.xlsx",
        "synthetic_oracle_procurement_workbook.xlsx",
    ],
)
def test_positive_sample_workbooks_load(filename):
    summary = load_erp_workbook(SAMPLE_DIR / filename)

    assert summary.filename == filename
    assert set(REQUIRED_SHEETS).issubset(summary.sheets)
    assert summary.file_size_bytes > 0
    for sheet_name in REQUIRED_SHEETS:
        sheet = summary.sheets[sheet_name]
        assert sheet.headers
        assert sheet.column_count == len(sheet.headers)
        assert sheet.row_count > 0
        assert not sheet.is_empty


def test_loader_accepts_binary_file_object_and_preserves_position():
    stream = BytesIO(_workbook_bytes())
    stream.name = "upload.xlsx"
    stream.seek(5)

    summary = load_erp_workbook(stream)

    assert summary.filename == "upload.xlsx"
    assert stream.tell() == 5


def test_loader_rejects_non_xlsx_extension():
    with pytest.raises(WorkbookLoadError, match="Only non-macro"):
        load_erp_workbook(b"not used", filename="upload.xlsm")


def test_loader_rejects_renamed_or_corrupt_file():
    with pytest.raises(WorkbookLoadError, match="not a valid XLSX"):
        load_erp_workbook(b"not an excel zip", filename="upload.xlsx")


def test_loader_rejects_empty_file():
    with pytest.raises(WorkbookLoadError, match="Workbook is empty"):
        load_erp_workbook(b"", filename="upload.xlsx")


def test_loader_enforces_size_limit():
    payload = _workbook_bytes()

    with pytest.raises(WorkbookLoadError, match="exceeds"):
        load_erp_workbook(
            payload,
            filename="upload.xlsx",
            max_file_size_bytes=len(payload) - 1,
        )


def test_loader_reports_headers_rows_columns_and_empty_sheet():
    payload = _workbook_bytes(
        sheet_names=("Supplier_Master",),
        headers=["Supplier_ID", "Supplier_Name", "Country_Code"],
        with_data=False,
    )

    summary = load_erp_workbook(payload, filename="single.xlsx")
    sheet = summary.sheets["Supplier_Master"]

    assert sheet.headers == ("Supplier_ID", "Supplier_Name", "Country_Code")
    assert sheet.column_count == 3
    assert sheet.row_count == 0
    assert sheet.is_empty


def test_loader_requires_filename_for_raw_bytes():
    with pytest.raises(WorkbookLoadError, match="filename is required"):
        load_erp_workbook(_workbook_bytes())
