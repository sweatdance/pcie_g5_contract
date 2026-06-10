---
title: DLL Rules
description: Advisory data link-layer event visibility slice
---

# DLL Rules

## Status

- Contract surface: `pcie-dll`
- Claim level: `advisory_expansion`
- Source completeness: **advisory page**

## Scope

- InitFC sequencing, DL_Active gating, ACK/NAK protocol order, and replay edge cases.
- Advisory reviewer surface (not required for required-gate closure).

## Canonical

- Required source: [`PCIE5_DLL_RULES.md`](../../../PCIE5_DLL_RULES.md)
- Mapping entry: [`PCIE5_SPEC_TO_CONTRACT_MAPPING.md` Slice 8](../../../PCIE5_SPEC_TO_CONTRACT_MAPPING.md)
- Rule IDs: `PCIE5-DLL-001` .. `PCIE5-DLL-005`

## Key fields to inspect

- `initfc_complete`
- `dl_up_confirmed`
- `nak_observed`
- `nak_followed_by_replay`
- `updatefc_observed`
- `capture_duration_ms`

## Validation

- Fixture suite: `pcie-dll`
- Run command: `python scripts/run_fixture_smoke.py --suite pcie-dll --format json`
- Regression path: `python scripts/run_regression_smoke.py --suite advisory --format json`

## Decision guidance

- Advisory evidence for replay and ordering risks.
- NAK without replay sequence should be treated as protocol violation in review logs.
- Required-gate decisions should stay anchored on required slices.

## Advisory evidence checks

### Pass condition

- InitFC completion and DL Active assertion are present.
- NAK events are followed by replay sequence visibility.
- `updatefc_observed` aligns with negotiated width/speed context.

### Fail condition

- DL_Active without InitFC completion.
- NAK events without replay.
- Replay duration anomalies indicating link churn.

### Failure pattern examples

| Pattern | Detection field | Meaning | Suggested action |
| --- | --- | --- | --- |
| InitFC missing | `initfc_complete` | Transport never entered stable active | Advisory hard-stop |
| NAK replay gap | `nak_observed`, `nak_followed_by_replay` | Possible ordering bug | Keep in review-only mode |
| Long capture duration | `capture_duration_ms` | Potential throughput/latency risk | Add timing benchmark context |


## Advisory failure playbook
- Use the shared triage policy and payload format: [Advisory Failure Playbook](../spec-advisory-failure-playbook.md)

## Consumer response template

```markdown
--8<-- "../snippets/advisory-decision-response-template.txt"
```

```json
{
  "slice": "pcie-dll",
  "claim_level": "advisory_expansion",
  "result": "review_only",
  "required_fields": [
    "initfc_complete",
    "dl_up_confirmed",
    "nak_observed",
    "nak_followed_by_replay"
  ],
  "usage": "dll_protocol_risk"
}
```
