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

## Key evidence fields

- `ltssm_final_state`
- `ltssm_trace_summary.illegal_transition_count`
- `ltssm_trace_summary.visited_states`
- `ltssm_trace_summary.reached_recovery`

## Decision guidance

- Use this page for required-gate questions on LTSSM legality.
- Never mix advisory evidence into required-gate assertions.
- If evidence shows legal transitions are incomplete, report `required_gate_ready` as not satisfied.

## Open scope

- Add fixture-by-failure examples for common illegal transitions.
- Add path-template cards for the most common recovery loops.
