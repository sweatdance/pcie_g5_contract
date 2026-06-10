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

## Canonical mapping

- Required source: [`PCIE5_LTSSM_CHECKLIST.md`](../../../PCIE5_LTSSM_CHECKLIST.md)
- Mapping entry: [`PCIE5_SPEC_TO_CONTRACT_MAPPING.md` Slice 1](../../../PCIE5_SPEC_TO_CONTRACT_MAPPING.md)
- Related state transition page: [`spec-ltssm-state-transitions.md`](spec-ltssm-state-transitions.md)

## What to validate

- Target/negotiated speed and width are explicit.
- `ltssm_final_state` is visible and stable.
- `ltssm_trace_summary.illegal_transition_count` is zero for nominal runs.
- Equalization summary fields are not empty when equalization should run.
- Recovery/retrain evidence is attached when convergence is indirect.

## Validation entrypoints

- Fixture suite: `pcie-ltssm`
- Run command: `python scripts/run_fixture_smoke.py --suite required --format json`
- Required smoke: `python scripts/run_regression_smoke.py --suite required --format json`

## Decision guardrails

- Missing final-state fields means no required-gate claim.
- Partial traces are treated as review context unless confirmed stable.
- If recovery is present, record it as explicit caution rather than full completion.

## Open scope

- Add a compact failure catalog per checklist item (advisory only for now).
