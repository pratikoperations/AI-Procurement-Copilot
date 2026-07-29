"""Version-aware contract loading for governed ranking inputs."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1] / "planning" / "v1.3"
B1_ROOT = ROOT / "build_group_b"
B2_ROOT = ROOT / "build_group_b2"
V130_SCHEMA = B1_ROOT / "minimum_workbook_schema_v1.3.0.json"
V130_ALIASES = B1_ROOT / "sap_report_alias_registry_v1.3.0.json"
V131_SCHEMA = B2_ROOT / "minimum_workbook_schema_v1.3.1.json"
V131_ALIASES = B2_ROOT / "sap_report_alias_registry_v1.3.1.json"
FROZEN_URN = "urn:aipc:minimum-workbook:1.3.0"


class RankingContractError(ValueError):
    """Raised when a local governed contract cannot be loaded safely."""


class _V131RuntimeValidator:
    """Validate the additive workbook while preserving the frozen metadata row shape.

    The B2 schema intentionally reuses the frozen UploadMetadataRow, whose
    SCHEMA_VERSION const is 1.3.0. Runtime routing already validates the actual
    declared 1.3.1 version, so the validation copy is normalized only for the
    frozen row-reference check. Source metadata is never mutated.
    """

    def __init__(self, validator: Draft202012Validator):
        self._validator = validator

    def iter_errors(self, instance: Mapping[str, Any]):
        normalized = deepcopy(instance)
        metadata = normalized.get("UPLOAD_METADATA")
        if isinstance(metadata, list) and metadata and isinstance(metadata[0], dict):
            metadata[0]["SCHEMA_VERSION"] = "1.3.0"
        return self._validator.iter_errors(normalized)


@dataclass(frozen=True)
class ContractBundle:
    schema_version: str
    alias_registry_version: str
    schema: Mapping[str, Any]
    core_schema: Mapping[str, Any]
    alias_registry: Mapping[str, Any]
    approved_sheets: tuple[str, ...]
    row_definitions: Mapping[str, str]
    validator: Any | None


def _load(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RankingContractError(f"Contract file could not be loaded: {path}") from exc


def _reject_network_refs(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key == "$ref" and isinstance(child, str) and child.startswith(("http://", "https://")):
                raise RankingContractError("Network schema references are prohibited.")
            _reject_network_refs(child)
    elif isinstance(value, list):
        for child in value:
            _reject_network_refs(child)


def _merge_aliases(frozen: Mapping[str, Any], ranking: Mapping[str, Any]) -> dict[str, Any]:
    merged = dict(frozen)
    merged["registry_version"] = "1.3.1"
    merged["sheets"] = {**dict(frozen.get("sheets", {})), **dict(ranking.get("sheets", {}))}
    merged["field_source_classifications"] = {
        **dict(frozen.get("field_source_classifications", {})),
        **dict(ranking.get("field_source_classifications", {})),
    }
    merged["mapping_rules"] = dict(ranking.get("mapping_rules", {}))
    merged["rejected_semantic_aliases"] = dict(ranking.get("rejected_semantic_aliases", {}))
    return merged


def _frozen_bundle(frozen_schema: Mapping[str, Any], frozen_aliases: Mapping[str, Any]) -> ContractBundle:
    return ContractBundle(
        "1.3.0", "1.3.0", frozen_schema, frozen_schema, frozen_aliases,
        ("RFQ_QUOTES", "PO_HISTORY", "UPLOAD_METADATA"),
        {"RFQ_QUOTES": "RFQQuoteRow", "PO_HISTORY": "POHistoryRow", "UPLOAD_METADATA": "UploadMetadataRow"},
        None,
    )


def load_contract_bundle(version: str) -> ContractBundle:
    frozen_schema = _load(V130_SCHEMA)
    frozen_aliases = _load(V130_ALIASES)
    if str(frozen_schema.get("version")) != "1.3.0" or str(frozen_aliases.get("registry_version")) != "1.3.0":
        raise RankingContractError("Frozen v1.3.0 contract versions do not match.")
    if version != "1.3.1":
        return _frozen_bundle(frozen_schema, frozen_aliases)
    schema = _load(V131_SCHEMA)
    ranking_aliases = _load(V131_ALIASES)
    if str(schema.get("version")) != version or str(ranking_aliases.get("registry_version")) != version:
        raise RankingContractError("v1.3.1 schema and alias versions do not match.")
    _reject_network_refs(schema)
    mapping = schema.get("x-local-schema-registry", {}).get("resources", {})
    if mapping.get(FROZEN_URN) != "planning/v1.3/build_group_b/minimum_workbook_schema_v1.3.0.json":
        raise RankingContractError("Required frozen-schema URN mapping is missing or incorrect.")
    registry = Registry().with_resource(FROZEN_URN, Resource.from_contents(frozen_schema))
    validator = _V131RuntimeValidator(Draft202012Validator(schema, registry=registry))
    return ContractBundle(
        version, version, schema, frozen_schema, _merge_aliases(frozen_aliases, ranking_aliases),
        ("RFQ_QUOTES", "PO_HISTORY", "UPLOAD_METADATA", "SUPPLIER_RANKING_INPUTS"),
        {
            "RFQ_QUOTES": "RFQQuoteRow", "PO_HISTORY": "POHistoryRow",
            "UPLOAD_METADATA": "UploadMetadataRow", "SUPPLIER_RANKING_INPUTS": "SupplierRankingInputRow",
        },
        validator,
    )
