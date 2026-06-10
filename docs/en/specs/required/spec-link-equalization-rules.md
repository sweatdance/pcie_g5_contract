---
title: Equalization Rules
description: Required-scope equalization completion and link-training evidence
---

# Equalization Rules

## Status

- Contract surface: `pcie-eq`
- Claim level: `required_gate_ready`
- Source completeness: **required page**

## Scope

- Keeps equalization completion and phase status reviewer-safe.
- Required for nominal gen-up claims in this repository.

## Canonical mapping

- Required source: [`PCIE5_LINK_EQUALIZATION_RULES.md`](../../../PCIE5_LINK_EQUALIZATION_RULES.md)
- Mapping entry: [`PCIE5_SPEC_TO_CONTRACT_MAPPING.md` Slice 2](../../../PCIE5_SPEC_TO_CONTRACT_MAPPING.md)
- Related required speed context: [`spec-speed-width-negotiation.md`](spec-speed-width-negotiation.md)

## Evidence fields

- `equalization_complete`
- `equalization_phase_summary.completed_phases`
- `equalization_phase_summary.failed_phases`
- `lane_failures`

## Validation entrypoints

- Fixture suite: `pcie-eq`
- Run command: `python scripts/run_fixture_smoke.py --suite pcie-eq --format json`
- Required smoke: `python scripts/run_regression_smoke.py --suite required --format json`

## Decision guardrails

- Equalization failure must be explicit even if recovery still produces an L0 state.
- Unresolved lane failure summaries prevent hard required-gate completion.
- Use advisory review if phase-level evidence is partial.

## Open scope

- Add phase-specific failure examples and accepted exception patterns.
