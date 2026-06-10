---
title: Hot-Plug Rules
description: Advisory hot-plug lifecycle and timing visibility
---

# Hot-Plug Rules

## Status

- Contract surface: `pcie-hotplug`
- Claim level: `advisory_expansion`
- Source completeness: **advisory page**

## Scope

- Hot-plug event ordering, Slot register sequencing, and surprise-remove race detection.
- Advisories include MUX-switch scenarios and timing gap risks.

## Canonical mapping

- Required source: [`PCIE5_HOTPLUG_RULES.md`](../../../PCIE5_HOTPLUG_RULES.md)
- Mapping entry: [`PCIE5_SPEC_TO_CONTRACT_MAPPING.md` Slice 10](../../../PCIE5_SPEC_TO_CONTRACT_MAPPING.md)
- Rule IDs: `PCIE5-HP-001` .. `PCIE5-HP-016`

## Key fields to inspect

- `surprise_down_timestamp`
- `pm_l1_before_enum_complete`
- `pm_request_ack_in_enum_window`
- `aer_cleared_before_new_enum`
- `time_surprise_down_to_first_cfgrd_ms`
- `upstream_ts1_rate_at_first_linkup`

## Validation entrypoints

- Fixture suite: `pcie-hotplug`
- Run command: `python scripts/run_fixture_smoke.py --suite pcie-hotplug --format json`
- Regression path: `python scripts/run_regression_smoke.py --suite advisory --format json`

## Decision guidance

- This page is advisory in this contract profile.
- A sub-500ms gap from surprise removal to first enumeration is warning-level evidence of host-queue overlap.
- This surface is a good source for race-condition mitigation planning.

## Advisory evidence checks

### Pass condition

- Surprise-hotplug fields are explicit in run output.
- Queue transition timing is measurable and documented.
- OS enumeration timing fields are populated.

### Fail condition

- Surprise remove/insert without timestamps.
- AER clear or cfg-read sequencing missing.
- Long gap indicates host queue overlap with no recovery explanation.

### Failure pattern examples

| Pattern | Detection field | Meaning | Suggested action |
| --- | --- | --- | --- |
| Tight surprise gap | `time_surprise_down_to_first_cfgrd_ms` | Race risk | Add platform timing notes |
| No CFG clear | `aer_cleared_before_new_enum` | Incomplete transition path | Advise firmware/driver reset sequence |
| Incomplete linkup timing | `upstream_ts1_rate_at_first_linkup` | Upstream instability | Correlate PHY link retrain path |

## Consumer response template

```json
{
  "slice": "pcie-hotplug",
  "claim_level": "advisory_expansion",
  "result": "review_only",
  "required_fields": [
    "surprise_down_timestamp",
    "time_surprise_down_to_first_cfgrd_ms",
    "pm_request_ack_in_enum_window",
    "aer_cleared_before_new_enum"
  ],
  "usage": "hotplug_risk_review"
}
```
