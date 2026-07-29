"""Version-aware contract loading for governed ranking inputs."""
from __future__ import annotations

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


@dataclass(frozen=True)
class ContractBundle:
    schema_version: str
    alias_registry_version: str
    schema: Mapping[str, Any]
    alias_registry: Mapping[str, Any]
    approved_sheets: tuple[str, ...]
    row_definitions: Mapping[str, str]
    validator: Draft202012Validator | None


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


def load_contract_bundle(version: str) -> ContractBundle:
    if version == "1.3.0":
        schema = _load(V130_SCHEMA)
        aliases = _load(V130_ALIASES)
        if str(schema.get("version")) != version or str(aliases.get("registry_version")) != version:
            raise RankingContractError("Frozen v1.3.0 contract versions do not match.")
        return ContractBundle(
            schema_version=version,
            alias_registry_version=version,
            schema=schema,
            alias_registry=aliases,
            approved_sheets=("RFQ_QUOTES", "PO_HISTORY", "UPLOAD_METADATA"),
            row_definitions={
                "RFQ_QUOTES": "RFQQuoteRow",
                "PO_HISTORY": "POHistoryRow",
                "UPLOAD_METADATA": "UploadMetadataRow",
            },
            validator=None,
        )
    if version != "1.3.1":
        raise RankingContractError(f"Unsupported schema version '{version}'.")
    frozen = _load(V130_SCHEMA)
    schema = _load(V131_SCHEMA)
    aliases = _load(V131_ALIASES)
    if str(frozen.get("version")) != "1.3.0":
        raise RankingContractError("Frozen schema version is not 1.3.0.")
    if str(schema.get("version")) != version or str(aliases.get("registry_version")) != version:
        raise RankingContractError("v1.3.1 schema and alias versions do not match.")
    _reject_network_refs(schema)
    mapping = schema.get("x-local-schema-registry", {}).get("resources", {})
    if mapping.get(FROZEN_URN) != "planning/v1.3/build_group_b/minimum_workbook_schema_v1.3.0.json":
        raise RankingContractError("Required frozen-schema URN mapping is missing or incorrect.")
    registry = Registry().with_resource(FROZEN_URN, Resource.from_contents(frozen))
    validator = Draft202012Validator(schema, registry=registry)
    return ContractBundle(
        schema_version=version,
        alias_registry_version=version,
        schema=schema,
        alias_registry=aliases,
        approved_sheets=("RFQ_QUOTES", "PO_HISTORY", "UPLOAD_METADATA", "SUPPLIER_RANKING_INPUTS"),
        row_definitions={
            "RFQ_QUOTES": "RFQQuoteRow",
            "PO_HISTORY": "POHistoryRow",
            "UPLOAD_METADATA": "UploadMetadataRow",
            "SUPPLIER_RANKING_INPUTS": "SupplierRankingInputRow",
        },
        validator=validator,
    )
