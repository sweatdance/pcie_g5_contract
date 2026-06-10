---
title: Recovery and Fallback
description: Required traceability for recovery and fallback behavior
---

# Recovery and Fallback

## Status

- Contract surface: `pcie-ltssm`
- Claim level: `required_gate_ready` (with warning paths)
- Source completeness: **required page**

## Scope

- Required review entry for retrain/recovery dependency and fallback visibility.
- Used before downstream CI treats a run as stable convergence.

## Canonical

- Required source: [`PCIE5_RECOVERY_AND_FALLBACK.md`](../../../PCIE5_RECOVERY_AND_FALLBACK.md)
- Mapping entry: [`PCIE5_SPEC_TO_CONTRACT_MAPPING.md` Slice 4](../../../PCIE5_SPEC_TO_CONTRACT_MAPPING.md)
- Related required page: [`spec-ltssm-state-transitions.md`](spec-ltssm-state-transitions.md)

## Evidence fields

- `retry_count`
- `recovery_triggered`
- `downtrained`
- `fallback_reason`
- `recovery_reason`

## Validation

- Fixture suite: `pcie-ltssm` (recovery-visible path)
- Run command: `python scripts/run_regression_smoke.py --suite required --format json`

## Validation

- Required-gate acceptance requires:
  - `overall_passed = true`
  - `suites` includes `pcie-ltssm` with `status = pass`
  - `downtrained` and `fallback_reason` fields are explicit when fallback occurs

## Decision guardrails

- Recovery-driven convergence is valid for visibility but still must be called out explicitly.
- Missing fallback reason when `downtrained` is true blocks required-gate confidence.
- Any claim of clean nominal success must explain recovery dependency.

## Required evidence checks

### Pass condition

- Recovery or retrain evidence is present when convergence is indirect.
- `fallback_reason` populated whenever `downtrained = true`.
- `retry_count` and `recovery_reason` fields are present on recovery paths.

### Fail condition

- Recovery path without recovery reason.
- Downtrained result with no fallback rationale.
- Failed retries with no final convergence evidence.

### Failure pattern examples

| Pattern | Detection field | Meaning | Suggested action |
| --- | --- | --- | --- |
| Nominal claim after recovery | `recovery_triggered` | Incomplete disclosure | Gate with recovery warning context |
| Retry loop without reason | `retry_count` | Silent instability risk | Mark required gate blocked |
| Downtrained without rationale | `fallback_reason` | Policy violation | Reclassify claim until rationale exists |

## Consumer response template

```json
{
  "slice": "pcie-ltssm",
  "claim_level": "required_gate_ready",
  "result": "satisfied|blocked",
  "required_fields": [
    "recovery_triggered",
    "downtrained",
    "fallback_reason",
    "recovery_reason",
    "retry_count"
  ]
}
```

## Decision guidance

- Recovery behavior is visible, but does not automatically restore full required-gate success.
- Recovery without `fallback_reason` should keep required-gate status as blocked.
- For required closure, downtrained runs must carry explicit rationale and evidence path.
