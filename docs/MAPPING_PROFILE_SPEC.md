# Mapping Profile Specification

## Status
Planning only. No application code or Version 1.0 changes.

## Purpose
Define reusable, auditable mapping profiles that convert SAP, Oracle, or custom ERP export fields into the canonical Copilot schema.

## Supported Profile Types
- `SAP_ECC_STANDARD`
- `SAP_S4_STANDARD`
- `ORACLE_EBS_STANDARD`
- `ORACLE_FUSION_STANDARD`
- `CUSTOM_ERP`

## Profile Metadata
Each profile must contain:
- `profile_id`
- `profile_name`
- `profile_version`
- `erp_family`
- `erp_product`
- `organization_name`
- `created_by`
- `created_date`
- `approved_by`
- `approved_date`
- `status`
- `notes`

Allowed status values:
- Draft
- Under Review
- Approved
- Retired

## JSON Structure

```json
{
  "profile_id": "SAP_S4_STANDARD_V1",
  "profile_name": "SAP S/4HANA Standard Procurement Mapping",
  "profile_version": "1.0",
  "erp_family": "SAP",
  "erp_product": "S/4HANA",
  "status": "Approved",
  "sheet_mappings": {
    "Supplier_Master": {
      "source_sheet": "Supplier_Master",
      "columns": [
        {
          "source_column": "LIFNR",
          "canonical_column": "Supplier_ID",
          "required": true,
          "transformation": "preserve_as_text",
          "date_format": null,
          "unit_mapping": null,
          "default_value": null,
          "approval_required": false
        }
      ]
    }
  }
}
```

## Column Mapping Attributes
Each mapping entry must define:
- Source sheet
- Source column
- Canonical column
- Required status
- Transformation
- Source data type
- Canonical data type
- Date format where applicable
- Unit mapping where applicable
- Currency rule where applicable
- Default value where allowed
- Validation rule
- Approval-required flag
- Notes

## Allowed Transformations
Initial controlled transformations:
- `preserve_as_text`
- `trim_whitespace`
- `uppercase`
- `lowercase`
- `parse_date`
- `parse_decimal`
- `map_controlled_value`
- `apply_unit_conversion`
- `apply_currency_normalization`
- `concatenate_fields`
- `constant_value`

Arbitrary executable code is not allowed in profile files.

## Unit Mapping
Example:

```json
{
  "source_unit": "TO",
  "canonical_unit": "MT",
  "conversion_factor": 1.0,
  "approved": true
}
```

Mappings involving piece-to-weight conversion require material-specific conversion evidence and human approval.

## Currency Mapping
Currency rules must preserve:
- Original currency
- Original amount
- FX source
- FX rate
- FX effective date
- Normalized currency
- Normalized amount

A profile may map field names but must not embed an undisclosed FX rate.

## Date Mapping
Each date field must declare:
- Source format
- Locale assumption
- Canonical format
- Governing-date role
- Missing-date behavior

Missing dates must remain missing.

## Required-Field Overrides
Profiles may make an optional canonical field mandatory for a specific organization, but may not make a globally critical field optional.

Globally critical examples:
- Supplier_ID
- Material_ID where material analysis is required
- Original_Unit_Price
- Original_Currency
- Original_Unit
- RFQ_Date

## Mapping Confidence
Suggested mapping confidence levels:
- High: exact approved field match
- Medium: approved alias or transformation
- Low: semantic suggestion requiring review

Low-confidence mappings cannot be auto-approved for critical fields.

## Versioning Rules
- Every approved change creates a new profile version.
- Existing approved versions remain readable.
- Retired profiles remain available for historical audit.
- Profile ID and version are recorded in every ingestion audit.

## Governance
A mapping profile is approved only when:
- Required fields are mapped.
- Transformations are documented.
- Unit conversions are validated.
- Currency handling is reviewed.
- Sample source files pass.
- Data owner approval is recorded.

## Security Controls
- JSON only
- No scripts
- No macros
- No external execution
- No credentials
- No API tokens
- No confidential sample data

## Acceptance Criteria
- SAP and Oracle profiles can map equivalent business fields to the same canonical schema.
- Custom profiles can be created without code changes.
- Mapping changes are auditable.
- Critical ambiguous mappings require human approval.
- Original source columns remain traceable.
