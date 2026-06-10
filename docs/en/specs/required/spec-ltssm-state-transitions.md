---
title: LTSSM State Transitions
description: Required-scope LTSSM legality and state machine visibility
---

# LTSSM State Transitions

## Scope

- Contract slice: `pcie-ltssm`
- Claim level: `required_gate_ready`
- Canonical source: `docs/PCIE5_LTSSM_STATE_TRANSITIONS.md`
- Evidence mode: required fixture/regression path

## Canonical mapping

- [LTSSM state transition source](../../../PCIE5_LTSSM_STATE_TRANSITIONS.md)
- [Contract slice mapping reference](../../../PCIE5_SPEC_TO_CONTRACT_MAPPING.md) (Slice 1)
- [LTSSM checklist source](../../../PCIE5_LTSSM_CHECKLIST.md)

## Coverage status snapshot

- Fixture suite: required (`pcie-ltssm`)
- Pass/Fail pattern follows required gate alignment rules in this repo.
- Status policy: only required-surface claims are used for CI gates; advisory-only evidence is not merged into this boundary.

## Notes for consumers

Use this page as the first landing for any question requiring LTSSM transition legality, illegal-transition detection, or final-state legality checks.
For policy-safe gating, combine this with the required EQ and link-negotiation slices.
