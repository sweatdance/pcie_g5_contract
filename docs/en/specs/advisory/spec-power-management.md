---
title: Power Management
description: Advisory PM / ASPM governance slice
---

# Power Management

## Status

- Contract surface: `pcie-pm`
- Claim level: `advisory_expansion`
- Source completeness: **advisory page**

## Scope

- PM/ASPM sequencing, PM_REQ_ACK timing, and PM lifecycle risks during enumeration.
- Advisory evidence only unless explicitly reclassified by a downstream consumer.

## Canonical

- Required source: [`PCIE5_POWER_MANAGEMENT.md`](../../../PCIE5_POWER_MANAGEMENT.md)
- Mapping entry: [`PCIE5_SPEC_TO_CONTRACT_MAPPING.md` Slice 5](../../../PCIE5_SPEC_TO_CONTRACT_MAPPING.md)
- Rule IDs: `PCIE5-PM-001` .. `PCIE5-PM-017`

## Key fields to inspect

- `enumeration_complete`
- `pm_l1_observed`
- `aspm_enabled_by_cfgwr`
- `pm_request_ack_in_enum_window`
- `pm_l1_before_enum_complete` / advisory alias
- `l1_substate_mode`

## Validation

- Fixture suite: `pcie-pm`
- Run command: `python scripts/run_fixture_smoke.py --suite pcie-pm --format json`
- Required smoke: `python scripts/run_regression_smoke.py --suite advisory --format json`

## Decision guidance

- Use this for root-cause review and advisory warnings.
- For hard stop in this repo, this page supports downstream interpretation but does not by itself produce required-gate claims.

## Advisory evidence checks

### Pass condition

- PM lifecycle fields are present for enumeration and post-enumeration windows.
- `aspm_enabled_by_cfgwr` and `pm_request_ack_in_enum_window` align with observed behavior.
- `pm_l1_before_enum_complete` is explicit when L1 activity is seen.

### Fail condition

- Missing critical PM sequencing fields.
- PM event observed but no corresponding acknowledgement timeline.
- ASPM state indicates unexpected power transition during required visibility.

### Failure pattern examples

| Pattern | Detection field | Meaning | Suggested action |
| --- | --- | --- | --- |
| ASPM on but no ack | `pm_request_ack_in_enum_window` | Incomplete PM negotiation | Keep advisory warning and request trace |
| PM before complete | `pm_l1_before_enum_complete` | Enumeration coupling risk | Escalate for platform timing review |
| Inconsistent PM_REQ_ACK | `pm_l1_before_enum_complete` | Policy misalignment | Add cross-field check before closeout |

## Consumer response template

```json
{
  "slice": "pcie-pm",
  "claim_level": "advisory_expansion",
  "result": "review_only",
  "required_fields": [
    "pm_request_ack_in_enum_window",
    "pm_l1_observed",
    "pm_l1_before_enum_complete",
    "aspm_enabled_by_cfgwr"
  ],
  "usage": "investigation_only"
}
```
