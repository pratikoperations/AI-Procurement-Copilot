import pandas as pd

from modules.ux_acceptance_corrections import (
    build_contextual_currency_frame,
    flatten_evidence_rows,
    install_ux_acceptance_corrections,
)


def test_procurement_intelligence_inr_display_converts_canonical_usd_columns():
    source = pd.DataFrame(
        {
            "Supplier": ["Alpha"],
            "Annual TCO USD": [100.0],
            "negotiation_saving_usd": [5.0],
            "Risk Score": [72],
        }
    )

    result = build_contextual_currency_frame(source, "INR", 83.0)

    assert "Annual TCO (INR)" in result.columns
    assert "Negotiation Saving (INR)" in result.columns
    assert result.loc[0, "Annual TCO (INR)"] == 8300.0
    assert result.loc[0, "Negotiation Saving (INR)"] == 415.0
    assert result.loc[0, "Risk Score"] == 72
    assert "Annual TCO USD" in source.columns
    assert source.loc[0, "Annual TCO USD"] == 100.0


def test_procurement_intelligence_both_mode_preserves_usd_and_adds_inr():
    source = pd.DataFrame({"Supplier": ["Alpha"], "annual_tco_usd": [100.0]})

    result = build_contextual_currency_frame(source, "Both", 83.0)

    assert result.loc[0, "Annual Tco (USD)"] == 100.0
    assert result.loc[0, "Annual Tco (INR)"] == 8300.0


def test_non_currency_procurement_evidence_is_unchanged():
    source = pd.DataFrame({"Risk": ["High"], "Score": [55]})

    result = build_contextual_currency_frame(source, "INR", 83.0)

    pd.testing.assert_frame_equal(result, source)
    assert result is not source


def test_nested_audit_payload_is_flattened_to_business_readable_rows():
    payload = {
        "raw_output": {
            "target_unit_cost_usd": 1.27,
            "approved": False,
        },
        "warnings": ["Human review required"],
        "missing": None,
    }

    rows = flatten_evidence_rows(payload)
    fields = {row["Evidence field"]: row["Value"] for row in rows}

    assert fields["Raw Output › Target Unit Cost USD"] == "1.27"
    assert fields["Raw Output › Approved"] == "No"
    assert fields["Warnings › Item 1"] == "Human review required"
    assert fields["Missing"] == "Not available"
    assert all("{" not in row["Value"] and "}" not in row["Value"] for row in rows)


def test_empty_evidence_fails_closed_without_raw_json_placeholder():
    assert flatten_evidence_rows({}) == [
        {"Evidence field": "Evidence", "Value": "Not available"}
    ]
    assert flatten_evidence_rows([]) == [
        {"Evidence field": "Evidence", "Value": "None recorded"}
    ]


def test_installation_wraps_only_presentation_entry_points():
    from modules import calculation_explorer_ui, procurement_intelligence_ui

    install_ux_acceptance_corrections()

    assert getattr(
        procurement_intelligence_ui.render_procurement_intelligence,
        "_aipc_currency_context",
        False,
    )
    assert getattr(calculation_explorer_ui._render_result, "_aipc_business_evidence", False)
