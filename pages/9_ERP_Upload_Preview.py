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

st.set_page_config(page_title="ERP Upload Preview", page_icon="📄", layout="wide")

st.title("ERP Workbook Upload Preview")
st.caption("Read-only structural validation — no procurement analysis")
st.info(
    "This page performs package-safety and structural checks only. It does not "
    "normalize, persist, analyze, score, recommend, or connect to an ERP system."
)

profiles = load_default_mapping_profiles()
profile_labels = {
    "SAP S/4HANA — Draft static mapping": "SAP_S4HANA",
    "Oracle Fusion — Draft static mapping": "ORACLE_FUSION",
    "Custom template — Draft": "CUSTOM",
}
selected_label = st.selectbox("Static draft mapping profile", tuple(profile_labels))
st.caption(
    "SAP and Oracle selections are illustrative draft field mappings, not live "
    "integrations, certified universal mappings, or automated transformations."
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
metric_columns = st.columns(5)
metric_columns[0].metric("Filename", metrics["filename"])
metric_columns[1].metric("File size (bytes)", metrics["file_size_bytes"])
metric_columns[2].metric("Detected sheets", metrics["detected_sheet_count"])
metric_columns[3].metric("Required sheets", metrics["required_sheet_count"])
metric_columns[4].metric("Unknown sheets", metrics["unknown_sheet_count"])

st.subheader("Detected sheet metadata")
st.dataframe(build_sheet_inventory(summary), use_container_width=True, hide_index=True)
st.caption("Headers and structural counts only; workbook business-data rows are not displayed.")

validation = validate_workbook_structure(summary)
gate = build_processing_gate(validation)

st.subheader("Structural validation result")
if gate["status"] == "PASS":
    st.success(gate["status"])
elif gate["status"] == "PASS WITH WARNINGS":
    st.warning(gate["status"])
else:
    st.error(gate["status"])
st.write(gate["status_message"])

finding_rows = build_finding_rows(validation)
if finding_rows:
    st.dataframe(finding_rows, use_container_width=True, hide_index=True)
else:
    st.write("No structural findings were recorded.")

if validation.status == BLOCKED:
    st.error("Static mapping preview is suppressed while the workbook is BLOCKED.")
    st.caption("No data was saved. No procurement analysis or ERP connection was made.")
    st.stop()

selected_profile = profiles[profile_labels[selected_label]]
st.subheader("Static draft mapping preview")
st.write(
    f"Profile: **{selected_profile.profile_id}** | Status: **{selected_profile.status}**"
)
mapping_rows = build_mapping_rows(selected_profile)
if mapping_rows:
    st.dataframe(mapping_rows, use_container_width=True, hide_index=True)
else:
    st.info("The custom draft template contains no configured field mappings.")

st.success("Preview complete.")
st.caption(
    "No data was saved. No normalization, matching, procurement decision, ERP "
    "connection, or downstream processing was performed. Human review remains mandatory."
)
