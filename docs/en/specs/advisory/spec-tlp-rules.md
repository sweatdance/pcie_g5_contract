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

## Canonical

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

## Validation

- Fixture suite: `pcie-tlp`
- Run command: `python scripts/run_fixture_smoke.py --suite pcie-tlp --format json`
- Regression path: `python scripts/run_regression_smoke.py --suite advisory --format json`

## Decision guidance

- Use as advisory evidence only.
- Any unassigned BAR access is a hard review point; classify as high-risk in consumer handoff.
- UR/CA/CRS without explanation should not be treated as nominally completed.

## Advisory evidence checks

### Pass condition

- Completion-related fields are explicit and non-empty.
- BAR access pattern is bounded to expected addresses.
- `tag_reuse_observed` is false or explained.

### Fail condition

- Non-SC completion without timeout context.
- Unassigned BAR memory access observed.
- Timeout or CRS without platform root cause fields.

### Failure pattern examples

| Pattern | Detection field | Meaning | Suggested action |
| --- | --- | --- | --- |
| Poisoned TLP unhandled | `poisoned_tlp_observed` | Higher-layer data corruption risk | Correlate with host error counters |
| UR/CRS mismatch | `cfgrd_without_cpld_observed` | Protocol completion integrity issue | Escalate as advisory blocker |
| BAR not assigned | `memory_access_to_unassigned_bar` | Direct configuration/driver fault risk | Attach BAR map evidence |

## Consumer response template

```json
{
  "slice": "pcie-tlp",
  "claim_level": "advisory_expansion",
  "result": "review_only",
  "required_fields": [
    "non_sc_completion_observed",
    "non_sc_completion_types",
    "poisoned_tlp_observed",
    "tag_reuse_observed"
  ],
  "usage": "transaction_layer_investigation"
}
```
