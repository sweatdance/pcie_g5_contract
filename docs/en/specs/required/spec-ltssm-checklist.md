---
title: LTSSM Checklist
description: Required LTSSM readiness checklist and checklist-to-evidence mapping
---

# LTSSM Checklist

## Scope

- Contract slice: `pcie-ltssm`
- Claim level: `required_gate_ready`
- Canonical source: `docs/PCIE5_LTSSM_CHECKLIST.md`

## Canonical mapping

- [LTSSM checklist source](../../../PCIE5_LTSSM_CHECKLIST.md)
- [Contract mapping crosswalk](../../../PCIE5_SPEC_TO_CONTRACT_MAPPING.md) (Slice 1)
- [LTSSM state transitions source](../../../PCIE5_LTSSM_STATE_TRANSITIONS.md)

## What to check

- Terminal state and final-state expectations
- Illegal transition detection visibility
- Regression/fallback guardrails that influence required success claims

## Evidence policy

Checklist findings are review-visible and only promoted to required-gate posture when they align with fixture expectations in `fixtures/fixture_manifest.json`.
