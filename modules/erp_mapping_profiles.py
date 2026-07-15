"""Load and validate static ERP mapping profiles for Version 1.1.

This module reads static JSON profile definitions only. It does not execute
transformations, load workbooks, normalize data, or call Version 1.0 business
logic.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from modules.erp_schema_registry import REQUIRED_SHEETS, SHEET_SCHEMAS


DEFAULT_PROFILE_DIRECTORY = Path("config/mappings")
DEFAULT_PROFILE_FILES: Mapping[str, str] = {
    "SAP_S4HANA": "sap_s4hana_mapping_profile.json",
    "ORACLE_FUSION": "oracle_fusion_mapping_profile.json",
    "CUSTOM": "custom_mapping_profile_template.json",
}


class MappingProfileError(ValueError):
    """Raised when an ERP mapping profile is missing or malformed."""


@dataclass(frozen=True)
class MappingProfile:
    """Validated static ERP mapping profile."""

    profile_id: str
    profile_version: str
    erp_family: str
    erp_product: str
    status: str
    sheet_mappings: Mapping[str, Mapping[str, str]]
    source_path: Path

    def mapping_for(self, sheet_name: str) -> Mapping[str, str]:
        """Return the source-to-canonical mapping for one approved sheet."""

        if sheet_name not in REQUIRED_SHEETS:
            raise MappingProfileError(f"Unsupported ERP sheet: {sheet_name}")
        return self.sheet_mappings[sheet_name]


def _require_nonempty_string(payload: Mapping[str, Any], field: str, path: Path) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise MappingProfileError(
            f"Mapping profile '{path}' must define non-empty string field '{field}'."
        )
    return value.strip()


def _validate_sheet_mappings(
    raw_mappings: Any,
    path: Path,
) -> dict[str, dict[str, str]]:
    if not isinstance(raw_mappings, dict):
        raise MappingProfileError(
            f"Mapping profile '{path}' field 'sheet_mappings' must be an object."
        )

    missing_sheets = [sheet for sheet in REQUIRED_SHEETS if sheet not in raw_mappings]
    extra_sheets = [sheet for sheet in raw_mappings if sheet not in REQUIRED_SHEETS]

    if missing_sheets:
        raise MappingProfileError(
            f"Mapping profile '{path}' is missing required sheet mappings: "
            f"{', '.join(missing_sheets)}."
        )
    if extra_sheets:
        raise MappingProfileError(
            f"Mapping profile '{path}' contains unsupported sheet mappings: "
            f"{', '.join(extra_sheets)}."
        )

    validated: dict[str, dict[str, str]] = {}
    for sheet_name in REQUIRED_SHEETS:
        mapping = raw_mappings[sheet_name]
        if not isinstance(mapping, dict):
            raise MappingProfileError(
                f"Mapping for sheet '{sheet_name}' in '{path}' must be an object."
            )

        approved_targets = SHEET_SCHEMAS[sheet_name].known_columns
        validated_mapping: dict[str, str] = {}
        target_sources: dict[str, str] = {}

        for source_column, canonical_column in mapping.items():
            if not isinstance(source_column, str) or not source_column.strip():
                raise MappingProfileError(
                    f"Sheet '{sheet_name}' in '{path}' contains an invalid source column name."
                )
            if not isinstance(canonical_column, str) or not canonical_column.strip():
                raise MappingProfileError(
                    f"Sheet '{sheet_name}' in '{path}' maps '{source_column}' "
                    "to an invalid canonical column name."
                )

            source = source_column.strip()
            target = canonical_column.strip()

            if target not in approved_targets:
                raise MappingProfileError(
                    f"Mapping profile '{path}' sheet '{sheet_name}' contains unsupported "
                    f"canonical target '{target}'."
                )

            previous_source = target_sources.get(target)
            if previous_source is not None:
                raise MappingProfileError(
                    f"Mapping profile '{path}' sheet '{sheet_name}' maps canonical target "
                    f"'{target}' more than once from source columns "
                    f"'{previous_source}' and '{source}'."
                )

            validated_mapping[source] = target
            target_sources[target] = source

        validated[sheet_name] = validated_mapping

    return validated


def load_mapping_profile(path: str | Path) -> MappingProfile:
    """Load one JSON profile and return a validated immutable representation."""

    profile_path = Path(path)
    if not profile_path.exists():
        raise MappingProfileError(f"Mapping profile not found: {profile_path}")
    if not profile_path.is_file():
        raise MappingProfileError(f"Mapping profile path is not a file: {profile_path}")

    try:
        raw_text = profile_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise MappingProfileError(
            f"Mapping profile '{profile_path}' could not be read: {exc}"
        ) from exc

    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise MappingProfileError(
            f"Mapping profile '{profile_path}' contains invalid JSON at "
            f"line {exc.lineno}, column {exc.colno}: {exc.msg}."
        ) from exc

    if not isinstance(payload, dict):
        raise MappingProfileError(
            f"Mapping profile '{profile_path}' root must be a JSON object."
        )

    return MappingProfile(
        profile_id=_require_nonempty_string(payload, "profile_id", profile_path),
        profile_version=_require_nonempty_string(payload, "profile_version", profile_path),
        erp_family=_require_nonempty_string(payload, "erp_family", profile_path),
        erp_product=_require_nonempty_string(payload, "erp_product", profile_path),
        status=_require_nonempty_string(payload, "status", profile_path),
        sheet_mappings=_validate_sheet_mappings(
            payload.get("sheet_mappings"), profile_path
        ),
        source_path=profile_path,
    )


def load_default_mapping_profiles(
    profile_directory: str | Path = DEFAULT_PROFILE_DIRECTORY,
) -> dict[str, MappingProfile]:
    """Load the three repository-controlled draft profile files."""

    directory = Path(profile_directory)
    return {
        profile_name: load_mapping_profile(directory / filename)
        for profile_name, filename in DEFAULT_PROFILE_FILES.items()
    }
