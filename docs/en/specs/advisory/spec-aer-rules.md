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

## Canonical

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

## Validation

- Fixture suite: `pcie-aer`
- Run command: `python scripts/run_fixture_smoke.py --suite pcie-aer --format json`
- Regression path: `python scripts/run_regression_smoke.py --suite advisory --format json`

## Decision guidance

- Keep this in advisory mode for required-gate workflows.
- A surprise-down event without logging is review-critical even when required paths remain green.
- Use rule IDs directly when correlating BSOD or WHEA output.

## Advisory evidence checks

### Pass condition

- AER severity and mask values are captured with surprise-down context.
- Logging paths are present for each surprise-down or uncorrectable event.
- Completion and tag counters are present for error correlation.

### Fail condition

- Logged AER fields without corresponding surprise-down context.
- Unassigned completion with no AER correlation.
- High-severity event with incomplete payload.

### Failure pattern examples

| Pattern | Detection field | Meaning | Suggested action |
| --- | --- | --- | --- |
| Surprise-down without log | `aer_surprise_down_logged` | Hidden error context | Classify as advisory critical |
| Poisoned TLP only | `poisoned_tlp_observed` | Silent packet health risk | Link with platform error log |
| Unexpected completion | `unexpected_completion_observed` | Completion integrity concern | Correlate route in host log |

## Consumer response template

```json
{
  "slice": "pcie-aer",
  "claim_level": "advisory_expansion",
  "result": "review_only",
  "required_fields": [
    "surprise_down_observed",
    "aer_surprise_down_logged",
    "poisoned_tlp_observed",
    "aer_severity_value"
  ],
  "usage": "error_correlation"
}
```
