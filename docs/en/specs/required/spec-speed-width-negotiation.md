---
title: Speed and Width Negotiation
description: Required-scope speed/width negotiation evidence and policy
---

# Speed and Width Negotiation

## Status

- Contract surface: `pcie-link-negotiation`
- Claim level: `required_gate_ready`
- Source completeness: **required page**

## Scope

- Prevents silent downtrain or degraded-width claims without explicit rationale.
- Bridges required negotiation checks with required link-up assertions.

## Canonical mapping

- Required source: [`PCIE5_SPEED_WIDTH_NEGOTIATION.md`](../../../PCIE5_SPEED_WIDTH_NEGOTIATION.md)
- Mapping entry: [`PCIE5_SPEC_TO_CONTRACT_MAPPING.md` Slice 3](../../../PCIE5_SPEC_TO_CONTRACT_MAPPING.md)
- Related required pages: [`spec-link-equalization-rules.md`](spec-link-equalization-rules.md), [`spec-ltssm-state-transitions.md`](spec-ltssm-state-transitions.md)

## Evidence fields

- `target_speed_gtps`
- `negotiated_speed_gtps`
- `target_width`
- `negotiated_width`
- `downtrained`
- `degraded_width_expected`
- `degraded_width_reason`
- `fallback_reason`

## Validation entrypoints

- Fixture suite: `pcie-link-negotiation`
- Run command: `python scripts/run_fixture_smoke.py --suite pcie-link-negotiation --format json`
- Required smoke: `python scripts/run_regression_smoke.py --suite required --format json`

## Validation

- Required-gate acceptance requires:
  - `overall_status = pass`
  - `suites` includes `pcie-link-negotiation` with `status = pass`
  - `target_speed_gtps` and `negotiated_speed_gtps` align with explicit downtrain rationale when `downtrained = true`

## Decision guardrails

- A nominal claim must explicitly avoid presenting downtrained results as full Gen5 success.
- Width mismatch is acceptable only when expected and reasoned.
- Treat `fallback_reason` absence as review risk, even if speed still nominal.

## Required evidence checks

### Pass condition

- `target_speed_gtps`, `negotiated_speed_gtps`, `target_width`, and `negotiated_width` are present.
- `downtrained` is false OR `degraded_width_expected` is true with `degraded_width_reason` present.
- `fallback_reason` is present whenever fallback flags are set.

### Fail condition

- Negotiated width/speed fields missing in required payload.
- `downtrained = true` with no reason.
- Any fallback path without explicit rationale.

### Failure pattern examples

| Pattern | Detection field | Meaning | Suggested action |
| --- | --- | --- | --- |
| Silent downtrain | `downtrained` | Required gate may be overclaimed | Demand speed/width mismatch documentation |
| Width mismatch with no reason | `degraded_width_expected` | Policy boundary breach | Block required-gate claim |
| Missing negotiated speed | `negotiated_speed_gtps` | Negotiation capture incomplete | Re-run with trace-level output |

## Consumer response template

```json
{
  "slice": "pcie-link-negotiation",
  "claim_level": "required_gate_ready",
  "result": "satisfied|blocked",
  "required_fields": [
    "target_speed_gtps",
    "negotiated_speed_gtps",
    "target_width",
    "negotiated_width",
    "fallback_reason"
  ]
}
```

## Decision guidance

- Negotiation outputs are required-gate relevant whenever link-up claims are made.
- Silent downtrain is a hard reason to block required-gate completion unless `degraded_width_expected` and reasons are complete.
- If `degraded_width_expected` is false, any fallback/rationale gap is not acceptable for required closure.
