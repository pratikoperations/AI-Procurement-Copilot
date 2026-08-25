from pathlib import Path

from modules.ux_maturity_ui import SEMANTIC_FAMILIES, UX_MATURITY_CONTRACT


def test_ux_maturity_contract_and_semantic_families_are_bounded():
    assert UX_MATURITY_CONTRACT == "AIPC-UX-MATURITY-1.0"
    assert SEMANTIC_FAMILIES == {
        "supplier": {"accent": "#3B82F6", "label": "RFQ / SUPPLIER EVALUATION"},
        "cost": {"accent": "#0F766E", "label": "TCO / SHOULD COST"},
        "allocation": {"accent": "#0F8B8D", "label": "ALLOCATION / SCENARIOS"},
        "negotiation": {"accent": "#A16207", "label": "NEGOTIATION INTELLIGENCE"},
        "governance": {"accent": "#64748B", "label": "GOVERNANCE / ASSUMPTIONS"},
        "output": {"accent": "#2563EB", "label": "SYSTEM ANALYSIS / OUTPUT"},
    }


def test_status_chip_is_text_first_and_accessible():
    source = Path("modules/ux_maturity_ui.py").read_text(encoding="utf-8")
    assert "role='status'" in source
    assert "aria-label=" in source
    assert "{_escape(label)} · {_escape(text)}" in source
    assert '"eligible": "#2E8B57"' in source
    assert '"eligible with conditions": "#B7791F"' in source
    assert '"human review required": "#B7791F"' in source
    assert '"blocked": "#C53030"' in source
    assert '"infeasible": "#C53030"' in source
    assert '"unknown": "#64748B"' in source


def test_maturity_installer_wraps_presentation_only_surfaces():
    source = Path("modules/ux_maturity_install.py").read_text(encoding="utf-8")
    for renderer in (
        "render_supplier_snapshot",
        "render_should_cost_section",
        "render_tco_breakdown",
        "render_executive_value",
        "render_allocation",
        "render_scenario_table",
        "render_negotiation",
        "render_procurement_intelligence",
        "render_supplier_intelligence",
    ):
        assert renderer in source
    assert "semantic_section" in source
    assert "calculate_" not in source
    assert "answer_question" not in source
    assert "sourcemate_conversation" not in source


def test_global_bootstrap_installs_maturity_after_existing_acceptance_layer():
    source = Path("sitecustomize.py").read_text(encoding="utf-8")
    assert "install_ux_acceptance_corrections()" in source
    assert "install_ux_maturity_layer()" in source
    assert source.index("install_ux_acceptance_corrections()") < source.index("install_ux_maturity_layer()")
    assert "SUPPORTED_INTENTS = _LEGACY_PUBLIC_INTENTS" in source


def test_decision_clarity_separates_inputs_outputs_and_governance():
    source = Path("modules/decision_clarity_ui.py").read_text(encoding="utf-8")
    assert "render_input_block(" in source
    assert "render_result_summary(" in source
    assert "render_governance_disclosure(" in source
    assert "Current sourcing context" in source
    assert "Current governed decision result" in source
    assert "Recommended next action" in source
    assert "Human procurement approval required" in source


def test_explicit_pages_use_shared_hierarchy_without_touching_business_services():
    explorer = Path("pages/8_Governed_Calculation_Explorer.py").read_text(encoding="utf-8")
    erp = Path("pages/9_ERP_Upload_Preview.py").read_text(encoding="utf-8")

    assert "render_page_context(" in explorer
    assert "semantic_section(" in explorer
    assert "render_result_summary(" in explorer
    assert "render_governance_disclosure(" in explorer
    assert 'mount_global_sourcemate("Governed Calculation Explorer")' in explorer
    assert "render_currency_aware_calculation_explorer(" in explorer
    assert "publish_selected_presentation(presentation)" in explorer

    assert "render_page_context(" in erp
    assert "semantic_section(" in erp
    assert "render_input_block(" in erp
    assert "render_result_summary(" in erp
    assert "render_governance_disclosure(" in erp
    assert 'mount_global_sourcemate("ERP Upload Preview")' in erp
    assert "load_erp_workbook(" in erp
    assert "validate_workbook_structure(summary)" in erp


def test_source_mate_chat_implementation_is_not_modified_by_maturity_layer():
    maturity = Path("modules/ux_maturity_ui.py").read_text(encoding="utf-8")
    installer = Path("modules/ux_maturity_install.py").read_text(encoding="utf-8")
    combined = (maturity + installer).lower()
    assert "chat_input" not in combined
    assert "answer_question" not in combined
    assert "external llm" not in combined
    assert "rag" not in combined
