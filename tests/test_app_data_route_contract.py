from pathlib import Path


def app_source() -> str:
    return Path("app.py").read_text(encoding="utf-8")


def test_global_v12_release_label_is_preserved():
    source = app_source()
    assert 'st.title(f"{APP_NAME} v1.2")' in source
    assert "Governed v1.3 Workbook Review Preview" in source


def test_governed_route_bypasses_legacy_normalization_branch():
    source = app_source()
    governed_position = source.index("if is_governed_route:")
    legacy_position = source.index("else:\n    try:\n        suppliers_df = load_uploaded_rfq", governed_position)
    normalization_position = source.index("normalize_comparison_basis", legacy_position)
    assert governed_position < legacy_position < normalization_position
    governed_block = source[governed_position:legacy_position]
    assert "normalize_comparison_basis" not in governed_block
    assert "load_uploaded_rfq" not in governed_block


def test_scoring_occurs_only_after_route_resolution():
    source = app_source()
    handoff_guard = source.index("if governed_result.dataframe is None or not governed_result.analysis_handoff_allowed")
    scoring = source.index("scored_df = enrich_supplier_scores")
    assert handoff_guard < scoring


def test_incompatible_governed_data_stops_without_fallback():
    source = app_source()
    guard = "if governed_result.dataframe is None or not governed_result.analysis_handoff_allowed:\n        st.stop()"
    assert guard in source


def test_legacy_route_does_not_invoke_build_c_or_d():
    source = app_source()
    legacy_start = source.index("else:\n    try:\n        suppliers_df = load_uploaded_rfq")
    legacy_end = source.index("for warning in validate_category_unit", legacy_start)
    legacy_block = source[legacy_start:legacy_end]
    assert "run_governed_review" not in legacy_block
    assert "orchestrate_adapter_result" not in legacy_block
