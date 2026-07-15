from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest
from openpyxl import Workbook

from modules.erp_schema_registry import REQUIRED_SHEETS
from modules.erp_workbook_loader import WorkbookLoadError, load_erp_workbook


SAMPLE_DIR = Path("data/erp_samples")
FIXTURE_FILENAMES = (
    "synthetic_sap_procurement_workbook.xlsx",
    "synthetic_oracle_procurement_workbook.xlsx",
    "erp_adversarial_procurement_workbook.xlsx",
)
FORBIDDEN_PACKAGE_PREFIXES = (
    "xl/externallinks/",
    "xl/querytables/",
    "xl/externaldata/",
    "xl/model/",
)
CREDENTIAL_MARKERS = (
    "password=",
    "pwd=",
    "user id=",
    "userid=",
    "uid=",
    "access_token",
    "access token",
    "client_secret",
    "client secret",
)


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


def _with_package_member(payload, member_name, member_content=b"<test/>"):
    output = BytesIO()
    with ZipFile(BytesIO(payload), "r") as source, ZipFile(
        output, "w", compression=ZIP_DEFLATED
    ) as target:
        for item in source.infolist():
            target.writestr(item, source.read(item.filename))
        target.writestr(member_name, member_content)
    return output.getvalue()


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


@pytest.mark.parametrize("filename", FIXTURE_FILENAMES)
def test_repository_fixture_package_contains_no_active_external_features(filename):
    path = SAMPLE_DIR / filename
    with ZipFile(path) as archive:
        lowered = {name.lower() for name in archive.namelist()}

    assert not any(name.endswith("vbaproject.bin") for name in lowered)
    assert "xl/connections.xml" not in lowered
    assert not any(
        name.startswith(prefix)
        for name in lowered
        for prefix in FORBIDDEN_PACKAGE_PREFIXES
    )


@pytest.mark.parametrize("filename", FIXTURE_FILENAMES)
def test_repository_fixture_package_contains_no_credential_like_connection_string(
    filename,
):
    path = SAMPLE_DIR / filename
    with ZipFile(path) as archive:
        searchable_text = []
        for name in archive.namelist():
            if name.lower().endswith((".xml", ".rels", ".txt")):
                searchable_text.append(
                    archive.read(name).decode("utf-8", errors="ignore").lower()
                )

    combined = "\n".join(searchable_text)
    assert not any(marker in combined for marker in CREDENTIAL_MARKERS)


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


@pytest.mark.parametrize(
    ("member_name", "expected_message"),
    [
        ("xl/vbaProject.bin", "Macro-enabled"),
        ("xl/externalLinks/externalLink1.xml", "external workbook links"),
        ("xl/connections.xml", "connection definitions"),
        ("xl/queryTables/queryTable1.xml", "query-table definitions"),
        ("xl/externalData/externalData1.xml", "external-data definitions"),
    ],
)
def test_loader_rejects_active_or_external_package_features(
    member_name,
    expected_message,
):
    payload = _with_package_member(_workbook_bytes(), member_name)

    with pytest.raises(WorkbookLoadError, match=expected_message):
        load_erp_workbook(payload, filename="unsafe.xlsx")


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
