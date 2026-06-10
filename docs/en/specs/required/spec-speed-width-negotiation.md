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

## Decision guardrails

- A nominal claim must explicitly avoid presenting downtrained results as full Gen5 success.
- Width mismatch is acceptable only when expected and reasoned.
- Treat `fallback_reason` absence as review risk, even if speed still nominal.

## Open scope

- Add a quick comparison table between speed/width expectation and required outcome by scenario.
