"""Deterministic message-layer regression tests for Build Group S1.2."""

from io import BytesIO

import pandas as pd
import pytest

from modules import data_loader
from modules.data_loader import RFQUploadError, load_uploaded_rfq
from modules.validation import REQUIRED_RFQ_COLUMNS, validate_rfq_dataframe, validate_scored_output


class NamedBytesIO(BytesIO):
    """In-memory upload with the filename contract used by Streamlit."""

    def __init__(self, payload: bytes, name: str):
        super().__init__(payload)
        self.name = name


def test_empty_csv_returns_actionable_upload_guidance() -> None:
    upload = NamedBytesIO(b"", "empty.csv")

    with pytest.raises(RFQUploadError) as exc_info:
        load_uploaded_rfq(upload)

    message = str(exc_info.value)
    assert "empty" in message.lower()
    assert "header row" in message
    assert "supplier quotation" in message
    assert "Traceback" not in message


def test_unsupported_file_type_is_rejected_before_parsing() -> None:
    upload = NamedBytesIO(b"not an rfq", "quotes.txt")

    with pytest.raises(RFQUploadError, match=r"\.csv or \.xlsx"):
        load_uploaded_rfq(upload)


def test_normalization_failure_is_translated_to_business_guidance(monkeypatch) -> None:
    upload = NamedBytesIO(b"Supplier,Price\nA,1.2\n", "quotes.csv")

    def fail_normalization(_frame):
        raise ValueError("internal alias registry failure")

    monkeypatch.setattr(data_loader, "normalize_rfq_dataframe", fail_normalization)

    with pytest.raises(RFQUploadError) as exc_info:
        load_uploaded_rfq(upload)

    message = str(exc_info.value)
    assert "mapped reliably" in message
    assert "merged cells" in message
    assert "alias registry" not in message


def test_missing_mandatory_fields_include_a_corrective_action() -> None:
    result = validate_rfq_dataframe(pd.DataFrame({"Supplier": ["A"]}))

    assert result["is_valid"] is False
    message = result["errors"][0]
    for column in REQUIRED_RFQ_COLUMNS[1:]:
        assert column in message
    assert "rename the source headers clearly" in message
    assert "upload the file again" in message


def test_empty_dataframe_has_clear_empty_state_guidance() -> None:
    result = validate_rfq_dataframe(pd.DataFrame())

    assert result["is_valid"] is False
    assert result["warnings"] == []
    assert "No supplier quotations" in result["errors"][0]
    assert "at least one supplier quotation" in result["errors"][0]


def test_optional_fields_warning_explains_impact_without_changing_defaults() -> None:
    frame = pd.DataFrame({
        "Supplier": ["A", "B"],
        "Quoted Unit Price USD": [1.0, 1.1],
        "MOQ": [100, 100],
        "Lead Time Days": [10, 12],
        "Payment Terms": ["Net 30", "Net 45"],
        "Incoterms": ["DDP", "FOB"],
    })

    result = validate_rfq_dataframe(frame)

    assert result["is_valid"] is True
    warning = next(item for item in result["warnings"] if "governed defaults" in item)
    assert "stronger data confidence" in warning
    assert "provisional" in warning


def test_scored_output_message_remains_blocking_and_actionable() -> None:
    result = validate_scored_output(pd.DataFrame({"Supplier": ["A"]}))

    assert result["is_valid"] is False
    message = result["errors"][0]
    assert "cannot support a recommendation" in message
    assert "Re-run the analysis" in message
