---
title: LTSSM State Transitions
description: Required-scope LTSSM legality and state machine visibility
---

# LTSSM State Transitions

## Status

- Contract surface: `pcie-ltssm`
- Claim level: `required_gate_ready`
- Source completeness: **required page**
- Default policy: eligible for required-gate workflows when smoke evidence is aligned.

## Scope

- Final state and transition-legality verification for link training.
- Recovery-visible paths are reported as review context.

## Canonical mapping

- Required source: [`PCIE5_LTSSM_STATE_TRANSITIONS.md`](../../../PCIE5_LTSSM_STATE_TRANSITIONS.md)
- Mapping entry: [`PCIE5_SPEC_TO_CONTRACT_MAPPING.md` Slice 1](../../../PCIE5_SPEC_TO_CONTRACT_MAPPING.md)
- Reviewer check index: [`PCIE5_LTSSM_CHECKLIST.md`](../../../PCIE5_LTSSM_CHECKLIST.md)

## Required validator surface

- Fixture suite: `pcie-ltssm`
- Run command: `python scripts/run_fixture_smoke.py --suite pcie-ltssm --format json`
- Regression confirmation: `python scripts/run_regression_smoke.py --suite required --format json`

## Validation

- Required-gate acceptance requires a nominal LTSSM path with:
  - `overall_status = pass`
  - `suites.pcie-ltssm.status = pass`
  - `ltssm_trace_summary.illegal_transition_count = 0`

## Key evidence fields

- `ltssm_final_state`
- `ltssm_trace_summary.illegal_transition_count`
- `ltssm_trace_summary.visited_states`
- `ltssm_trace_summary.reached_recovery`

## Required evidence checks

### Pass condition

- `ltssm_final_state` is present and stable for the nominal sequence.
- `illegal_transition_count = 0` for the nominal slice.
- Recovery visibility is explicit when retrain paths are used.

### Fail condition

- Any missing `ltssm_final_state`.
- Any positive illegal-transition count.
- Final-state changes without corresponding recovery explanation.

### Failure pattern examples

| Pattern | Detection field | Meaning | Suggested action |
| --- | --- | --- | --- |
| Unstable final state | `ltssm_final_state` | Required gate incomplete | Re-run with trace capture and route retry evidence |
| Unreported recovery | `ltssm_trace_summary.reached_recovery` | Recovery hidden | Add recovery trace to fixture output |
| Illegal transition | `ltssm_trace_summary.illegal_transition_count` | Protocol violation | Split for root-cause triage and block required-gate close |

## Decision guidance

- Use this page for required-gate questions on LTSSM legality.
- Never mix advisory evidence into required-gate assertions.
- If evidence shows legal transitions are incomplete, report `required_gate_ready` as not satisfied.
- Missing or ambiguous final-state fields should be treated as `blocked` even if suite count is otherwise green.

## Consumer response template

```json
{
  "slice": "pcie-ltssm",
  "claim_level": "required_gate_ready",
  "result": "satisfied|blocked",
  "required_fields": [
    "ltssm_final_state",
    "ltssm_trace_summary.illegal_transition_count"
  ],
  "evidence_refs": [
    "fixtures/fixture_manifest.json",
    "artifacts/validation/*"
  ]
}
```
