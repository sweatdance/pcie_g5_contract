---
title: LTSSM Checklist
description: Required LTSSM readiness checklist and checklist-to-evidence mapping
---

# LTSSM Checklist

## Status

- Contract surface: `pcie-ltssm`
- Claim level: `required_gate_ready`
- Source completeness: **required page**

## Purpose

- Provide a reviewer checklist for LTSSM + training readiness decisions.
- Prevent nominal claims from passing with partial traces or silent recovery paths.

## Scope

- Required slice scope for LTSSM nominal convergence and readiness confidence.
- This page is only considered mandatory for required-gate decisions when all required fields are aligned.

## Canonical

- Required source: [`PCIE5_LTSSM_CHECKLIST.md`](../../../PCIE5_LTSSM_CHECKLIST.md)
- Mapping entry: [`PCIE5_SPEC_TO_CONTRACT_MAPPING.md` Slice 1](../../../PCIE5_SPEC_TO_CONTRACT_MAPPING.md)
- Related state transition page: [`spec-ltssm-state-transitions.md`](spec-ltssm-state-transitions.md)

## What to validate

- Target/negotiated speed and width are explicit.
- `ltssm_final_state` is visible and stable.
- `ltssm_trace_summary.illegal_transition_count` is zero for nominal runs.
- Equalization summary fields are not empty when equalization should run.
- Recovery/retrain evidence is attached when convergence is indirect.

## Validation

- Fixture suite: `pcie-ltssm`
- Run command: `python scripts/run_fixture_smoke.py --suite required --format json`
- Required smoke: `python scripts/run_regression_smoke.py --suite required --format json`

## Required evidence checks

### Pass condition

- `ltssm_final_state` exists and is non-empty.
- `ltssm_trace_summary.illegal_transition_count = 0`.
- `equalization_summary` is populated whenever EQ is expected in the flow.
- Recovery/retrain traces are explicitly marked when present.

### Fail condition

- Missing final-state field in required trace payloads.
- Empty or partial equalization summary while required negotiation is exercised.
- Recovery or fallback without reason tags in result payload.

### Failure pattern examples

| Pattern | Detection field | Meaning | Suggested action |
| --- | --- | --- | --- |
| Nominal run has recovery traces | `ltssm_trace_summary.recovery_count` | Review context risk, not clean required state | Keep claim as guarded and escalate recovery details |
| Nominal transition with hidden path | `ltssm_final_state` only | Route mismatch in fixture expectations | Align smoke routing and update expectations |
| No trace summary | `ltssm_trace_summary` | Incomplete capture | Block required closure and rerun fixture suite |

## Consumer response template

```json
{
  "slice": "pcie-ltssm",
  "claim_level": "required_gate_ready",
  "required_artifacts": ["fixture_manifest", "run_regression_smoke"],
  "result": "satisfied|blocked",
  "notable_fields": [
    "ltssm_final_state",
    "ltssm_trace_summary.illegal_transition_count",
    "ltssm_trace_summary.visited_states"
  ]
}
```

## Decision guardrails

- Missing final-state fields means no required-gate claim.
- Partial traces are treated as review context unless confirmed stable.
- If recovery is present, record it as explicit caution rather than full completion.

## Decision guidance

- Use checklist output as the first hard-stop checkpoint for required-gate qualification.
- Any checklist item with partial traces or missing rationale should be classified as `guarded` and not hard-closed.
- Advisory pages can continue investigation, but required gate can only progress after checklist criteria are clean.
