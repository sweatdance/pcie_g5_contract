---
title: TLP Rules
description: Advisory transaction-layer evidence slice
---

# TLP Rules

## Status

- Contract surface: `pcie-tlp`
- Claim level: `advisory_expansion`
- Source completeness: **advisory page**

## Scope

- Transaction-layer completion status, address-boundary checks, and tag/replay side effects.
- Useful for post-mortem on UR/CA/CRS and completion timeout patterns.

## Canonical mapping

- Required source: [`PCIE5_TLP_RULES.md`](../../../PCIE5_TLP_RULES.md)
- Mapping entry: [`PCIE5_SPEC_TO_CONTRACT_MAPPING.md` Slice 9](../../../PCIE5_SPEC_TO_CONTRACT_MAPPING.md)
- Rule IDs: `PCIE5-TLP-001` .. `PCIE5-TLP-006`

## Key fields to inspect

- `non_sc_completion_observed`
- `non_sc_completion_types`
- `poisoned_tlp_observed`
- `cfgrd_without_cpld_observed`
- `memory_access_to_unassigned_bar`
- `tag_reuse_observed`

## Validation entrypoints

- Fixture suite: `pcie-tlp`
- Run command: `python scripts/run_fixture_smoke.py --suite pcie-tlp --format json`
- Regression path: `python scripts/run_regression_smoke.py --suite advisory --format json`

## Decision guidance

- Use as advisory evidence only.
- Any unassigned BAR access is a hard review point; classify as high-risk in consumer handoff.
- UR/CA/CRS without explanation should not be treated as nominally completed.

## Open scope

- Add explicit examples for each non-SC completion type and typical platform impact.
