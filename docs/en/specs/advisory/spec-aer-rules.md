---
title: AER Rules
description: Advisory error handling and AER register management slice
---

# AER Rules

## Status

- Contract surface: `pcie-aer`
- Claim level: `advisory_expansion`
- Source completeness: **advisory page**

## Scope

- AER uncorrectable/correctable visibility, surprise-down surfacing, and logging completeness.
- Used for debug and triage around WHEA-class faults and completion error context.

## Canonical mapping

- Required source: [`PCIE5_AER_RULES.md`](../../../PCIE5_AER_RULES.md)
- Mapping entry: [`PCIE5_SPEC_TO_CONTRACT_MAPPING.md` Slice 7](../../../PCIE5_SPEC_TO_CONTRACT_MAPPING.md)
- Rule IDs: `PCIE5-AER-001` .. `PCIE5-AER-006`

## Key fields to inspect

- `surprise_down_observed`
- `aer_surprise_down_logged`
- `aer_uncorrectable_error_value`
- `aer_uncorrectable_mask_value`
- `aer_severity_value`
- `poisoned_tlp_observed`
- `unexpected_completion_observed`

## Validation entrypoints

- Fixture suite: `pcie-aer`
- Run command: `python scripts/run_fixture_smoke.py --suite pcie-aer --format json`
- Regression path: `python scripts/run_regression_smoke.py --suite advisory --format json`

## Decision guidance

- Keep this in advisory mode for required-gate workflows.
- A surprise-down event without logging is review-critical even when required paths remain green.
- Use rule IDs directly when correlating BSOD or WHEA output.

## Open scope

- Add a short table linking common BSOD codes to expected AER fields.
