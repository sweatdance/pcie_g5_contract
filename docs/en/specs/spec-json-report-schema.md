---
title: JSON Report Schema
description: Validator report schema reference for contract tooling
---

# JSON Report Schema

## Status

- Type: artifact index
- Source completeness: source-linked page

## Purpose

- Keep downstream parsers aligned to the same field names that this repo's smoke scripts and docs expect.
- Prevent wrong assumptions across required/advisory scripts.

## Canonical source

- [`PCIE5_JSON_REPORT_SCHEMA.md`](../../../PCIE5_JSON_REPORT_SCHEMA.md)

## Relevant report groups

- Required suites: `pcie-ltssm`, `pcie-eq`, `pcie-link-negotiation`
- Advisory suites: `pcie-pm`, `pcie-aer`, `pcie-dll`, `pcie-tlp`, `pcie-hotplug`, `pcie-cfgspace`

## Required fields by reporting mode

### Regression smoke (`run_regression_smoke.py`)

- Surface-level status fields:
  - `overall_passed` / `overall_status`
  - `matched_count`
  - `total_checks`
  - `matched_suites`
  - `advisory_issues`
- Suite-level evidence:
  - `suite`
  - `status`
  - `assertions`
  - `missing_requirements`
  - `next_action`

### Fixture smoke (`run_fixture_smoke.py`)

- Result envelope:
  - `suite`
  - `fixture`
  - `status`
  - `matched`
  - `passed`
  - `failed`
- Assertion payload:
  - `assertion_id`
  - `result`
  - `details`
  - `severity`
  - `rule_family`
  - `remediation_hint`

## Governance mapping

## Workflow references

- Smoke outputs: `scripts/run_fixture_smoke.py`
- Regression outputs: `scripts/run_regression_smoke.py`

## Example consumption pattern

Use this when writing gate decisions:

1. Read `overall_passed` + `matched_count / total_checks`.
2. Confirm each required surface has `status=pass`.
3. For `advisory` surfaces, keep only context/risk notes and avoid hard-stop promotion.
4. Attach the specific fixture IDs for any failed assertions.

## Open scope

- Add a compact JSON schema machine-readable sample artifact under this page once fixtures are versioned.
- Add required/advisory field-level checklist once parser contract is finalized.
