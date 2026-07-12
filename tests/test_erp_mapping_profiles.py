import json
from pathlib import Path

import pytest

from modules.erp_mapping_profiles import (
    DEFAULT_PROFILE_FILES,
    MappingProfileError,
    load_default_mapping_profiles,
    load_mapping_profile,
)
from modules.erp_schema_registry import REQUIRED_SHEETS


PROFILE_DIR = Path("config/mappings")


def test_all_three_default_profiles_load():
    profiles = load_default_mapping_profiles(PROFILE_DIR)

    assert set(profiles) == {"SAP_S4HANA", "ORACLE_FUSION", "CUSTOM"}
    assert profiles["SAP_S4HANA"].erp_family == "SAP"
    assert profiles["ORACLE_FUSION"].erp_family == "Oracle"
    assert profiles["CUSTOM"].erp_family == "Custom"


def test_default_profile_files_match_repository_assets():
    assert DEFAULT_PROFILE_FILES == {
        "SAP_S4HANA": "sap_s4hana_mapping_profile.json",
        "ORACLE_FUSION": "oracle_fusion_mapping_profile.json",
        "CUSTOM": "custom_mapping_profile_template.json",
    }

    for filename in DEFAULT_PROFILE_FILES.values():
        assert (PROFILE_DIR / filename).is_file()


def test_every_default_profile_covers_all_seven_sheets():
    profiles = load_default_mapping_profiles(PROFILE_DIR)

    for profile in profiles.values():
        assert tuple(profile.sheet_mappings) == REQUIRED_SHEETS
        for sheet_name in REQUIRED_SHEETS:
            assert isinstance(profile.mapping_for(sheet_name), dict)


def test_sap_and_oracle_profiles_map_critical_identifiers():
    profiles = load_default_mapping_profiles(PROFILE_DIR)

    sap_supplier = profiles["SAP_S4HANA"].mapping_for("Supplier_Master")
    oracle_supplier = profiles["ORACLE_FUSION"].mapping_for("Supplier_Master")
    sap_rfq = profiles["SAP_S4HANA"].mapping_for("RFQ_Quotes")
    oracle_rfq = profiles["ORACLE_FUSION"].mapping_for("RFQ_Quotes")

    assert sap_supplier["LIFNR"] == "Supplier_ID"
    assert oracle_supplier["SUPPLIER_ID"] == "Supplier_ID"
    assert sap_rfq["MATNR"] == "Material_ID"
    assert oracle_rfq["ITEM_ID"] == "Material_ID"


def test_invalid_json_raises_clear_error(tmp_path):
    path = tmp_path / "invalid.json"
    path.write_text('{"profile_id": ', encoding="utf-8")

    with pytest.raises(MappingProfileError, match="invalid JSON"):
        load_mapping_profile(path)


def test_missing_required_metadata_raises_clear_error(tmp_path):
    path = tmp_path / "missing_metadata.json"
    path.write_text(
        json.dumps(
            {
                "profile_id": "TEST",
                "profile_version": "1.0",
                "erp_family": "Custom",
                "erp_product": "Test",
                "sheet_mappings": {sheet: {} for sheet in REQUIRED_SHEETS},
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(MappingProfileError, match="field 'status'"):
        load_mapping_profile(path)


def test_missing_sheet_mapping_raises_clear_error(tmp_path):
    path = tmp_path / "missing_sheet.json"
    mappings = {sheet: {} for sheet in REQUIRED_SHEETS if sheet != "Receipts"}
    path.write_text(
        json.dumps(
            {
                "profile_id": "TEST",
                "profile_version": "1.0",
                "erp_family": "Custom",
                "erp_product": "Test",
                "status": "Draft",
                "sheet_mappings": mappings,
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(MappingProfileError, match="missing required sheet mappings: Receipts"):
        load_mapping_profile(path)


def test_unknown_sheet_lookup_raises_clear_error():
    profile = load_default_mapping_profiles(PROFILE_DIR)["SAP_S4HANA"]

    with pytest.raises(MappingProfileError, match="Unsupported ERP sheet: Invoices"):
        profile.mapping_for("Invoices")
