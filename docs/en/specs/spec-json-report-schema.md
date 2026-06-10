---
title: JSON Report Schema
description: Validator report schema reference for contract tooling
---

# JSON Report Schema

## Status

- Type: artifact index
- Source completeness: source-linked page

## Scope

- Contract outputs this parser schema covers: required and advisory smoke report JSON.
- Used for both local docs guidance and downstream automation.

## Purpose

- Keep downstream parsers aligned to the same field names that this repo's smoke scripts and docs expect.
- Prevent wrong assumptions across required/advisory scripts.

## Canonical

- [`PCIE5_JSON_REPORT_SCHEMA.md`](../../PCIE5_JSON_REPORT_SCHEMA.md)

## Relevant report groups

- Required suites: `pcie-ltssm`, `pcie-eq`, `pcie-link-negotiation`
- Advisory suites: `pcie-pm`, `pcie-aer`, `pcie-dll`, `pcie-tlp`, `pcie-hotplug`, `pcie-cfgspace`

## Report schema coverage

The authoritative schema is declared in `PCIE5_JSON_REPORT_SCHEMA.md` and this page maps it to smoke outputs consumed by this repo.

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

### Required boundary (`required_gate_ready`)

- Required gates must be supported by:
  - `pcie-ltssm_report.overall_status = pass`
  - all required evidence fields present in `PCIE5_JSON_REPORT_SCHEMA.md`

### Advisory visibility (`advisory_expansion`)

- Advisory suite pass can be recorded as context.
- Any advisory-hard-stop pattern should still be promoted to CI warning even when required scope passes.

## Workflow references

- Smoke outputs: `scripts/run_fixture_smoke.py`
- Regression outputs: `scripts/run_regression_smoke.py`
## Decision guidance

- Missing required schema fields should downgrade the claim to `warn` and require refresh.
- Required gate closure needs both `overall_status=pass` and required-surface suite pass in the same report.

## Example consumption pattern

Use this when writing gate decisions:

1. Read `overall_passed` + `matched_count / total_checks`.
2. Confirm each required surface has `status=pass`.
3. For `advisory` surfaces, keep only context/risk notes and avoid hard-stop promotion.
4. Attach the specific fixture IDs for any failed assertions.

## Validation samples

Use this base shape when consuming JSON downstream:

```json
{
  "overall_passed": true,
  "overall_status": "pass",
  "matched_count": 24,
  "total_checks": 24,
  "matched_suites": ["pcie-ltssm","pcie-eq","pcie-link-negotiation"],
  "advisory_issues": 0,
  "suites": []
}
```

## Validation

### Per-surface decision payload examples

#### Required slice payload

```json
{
  "suite": "pcie-ltssm",
  "status": "pass",
  "overall_passed": true,
  "matched_count": 12,
  "total_checks": 12,
  "matched_suites": ["pcie-ltssm"],
  "advisory_issues": 0
}
```

#### Advisory slice payload

```json
{
  "suite": "pcie-aer",
  "status": "pass_with_warnings",
  "overall_passed": true,
  "matched_count": 2,
  "total_checks": 3,
  "matched_suites": ["pcie-aer"],
  "advisory_issues": 2
}
```

## Field alignment update rule

- This page is aligned to `PCIE5_JSON_REPORT_SCHEMA.md` and must be updated when parser key names change in `governance_tools`.
- For any key drift, first update source schema and manifest pages, then regenerate the LLM-facing samples together.

## Consumer response template

```json
{
  "report_mode": "regression|fixture",
  "overall_status": "pass|warn|blocked",
  "overall_passed": true,
  "matched_count": 24,
  "total_checks": 24,
  "matched_suites": ["pcie-ltssm", "pcie-eq", "pcie-link-negotiation"],
  "advisory_issues": 0,
  "evidence": "scripts outputs + PCIE5_JSON_REPORT_SCHEMA.md"
}
```

