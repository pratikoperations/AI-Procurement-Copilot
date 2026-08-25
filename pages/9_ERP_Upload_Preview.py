"""Governed read-only ERP workbook upload preview."""

from __future__ import annotations

import streamlit as st

from modules.erp_mapping_profiles import load_default_mapping_profiles
from modules.erp_structure_validator import BLOCKED, validate_workbook_structure
from modules.erp_upload_preview import (
    build_finding_rows,
    build_mapping_rows,
    build_processing_gate,
    build_sheet_inventory,
    build_workbook_metrics,
)
from modules.erp_workbook_loader import WorkbookLoadError, load_erp_workbook
from modules.sourcemate_application_shell import mount_global_sourcemate
from modules.ux_maturity_ui import (
    render_governance_disclosure,
    render_input_block,
    render_page_context,
    render_result_summary,
    semantic_section,
)

st.set_page_config(page_title="ERP Upload Preview", page_icon="📄", layout="wide")
mount_global_sourcemate("ERP Upload Preview")

render_page_context(
    "ERP Workbook Upload Preview",
    "Read-only structural validation — no procurement analysis.",
    (("Mode", "Read-only"), ("Scope", "Structural preview"), ("Decision authority", "Human review")),
)

render_governance_disclosure(
    (
        "This page performs package-safety and structural checks only.",
        "It does not normalize, persist, analyze, score, recommend or connect to an ERP system.",
        "SAP and Oracle mappings are illustrative draft static mapping profiles, not certified live integrations.",
    ),
    title="ERP preview governance",
)

profiles = load_default_mapping_profiles()
profile_labels = {
    "SAP S/4HANA — Draft static mapping": "SAP_S4HANA",
    "Oracle Fusion — Draft static mapping": "ORACLE_FUSION",
    "Custom template — Draft": "CUSTOM",
}

with semantic_section(
    "governance",
    "INPUT / ASSUMPTION",
    "Choose the existing draft mapping profile and provide one workbook for structural review.",
):
    selected_label = st.selectbox("Static draft mapping profile", tuple(profile_labels))
    st.caption(
        "Selected mapping is display/review context only; no automated transformation or ERP connection is created."
    )
    uploaded_file = st.file_uploader(
        "Upload one XLSX workbook",
        type=["xlsx"],
        accept_multiple_files=False,
    )

if uploaded_file is None:
    st.warning("Upload one .xlsx workbook to begin the structural preview.")
    st.stop()

try:
    summary = load_erp_workbook(uploaded_file, filename=uploaded_file.name)
except WorkbookLoadError as exc:
    st.error(f"BLOCKED — workbook package failed safety checks: {exc}")
    st.caption("No data was saved. No procurement analysis or ERP connection was made.")
    st.stop()

metrics = build_workbook_metrics(summary)
render_input_block(
    (
        ("Filename", metrics["filename"]),
        ("File size (bytes)", metrics["file_size_bytes"]),
        ("Mapping profile", selected_label),
    ),
    title="Workbook review context",
    columns=3,
)

validation = validate_workbook_structure(summary)
gate = build_processing_gate(validation)
render_result_summary(
    (
        ("Detected sheets", metrics["detected_sheet_count"]),
        ("Required sheets", metrics["required_sheet_count"]),
        ("Unknown sheets", metrics["unknown_sheet_count"]),
    ),
    title="Structural validation result",
    family="governance",
    status=gate["status"],
    status_label="Structural gate",
    columns=3,
)
st.write(gate["status_message"])

with st.expander("Workbook structure detail", expanded=False):
    st.dataframe(build_sheet_inventory(summary), use_container_width=True, hide_index=True)
    st.caption("Headers and structural counts only; workbook business-data rows are not displayed.")

finding_rows = build_finding_rows(validation)
with st.expander("Structural findings", expanded=gate["status"] != "PASS"):
    if finding_rows:
        st.dataframe(finding_rows, use_container_width=True, hide_index=True)
    else:
        st.write("No structural findings were recorded.")

if validation.status == BLOCKED:
    st.error("Static mapping preview is suppressed while the workbook is BLOCKED.")
    st.caption("No data was saved. No procurement analysis or ERP connection was made.")
    st.stop()

selected_profile = profiles[profile_labels[selected_label]]
with semantic_section(
    "governance",
    "ANALYSIS",
    "Review the existing static draft mapping after the workbook has passed the structural gate.",
):
    st.write(
        f"Profile: **{selected_profile.profile_id}** | Status: **{selected_profile.status}**"
    )
    mapping_rows = build_mapping_rows(selected_profile)
    with st.expander("Static draft mapping detail", expanded=False):
        if mapping_rows:
            st.dataframe(mapping_rows, use_container_width=True, hide_index=True)
        else:
            st.info("The custom draft template contains no configured field mappings.")

st.success("Preview complete.")
render_governance_disclosure(
    (
        "No data was saved.",
        "No normalization, matching, procurement decision, ERP connection or downstream processing was performed.",
        "Human review remains mandatory.",
    ),
    title="Completion boundary",
)
