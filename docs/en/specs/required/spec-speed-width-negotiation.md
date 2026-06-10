---
title: Speed and Width Negotiation
description: Required-scope speed/width negotiation evidence and policy
---

# Speed and Width Negotiation

## Scope

- Contract slice: `pcie-link-negotiation`
- Claim level: `required_gate_ready`
- Canonical source: `docs/PCIE5_SPEED_WIDTH_NEGOTIATION.md`

## Canonical mapping

- [Speed/width source](../../../PCIE5_SPEED_WIDTH_NEGOTIATION.md)
- [Contract mapping crosswalk](../../../PCIE5_SPEC_TO_CONTRACT_MAPPING.md) (Slice 3)

## Coverage view

- Required suite: `pcie-link-negotiation`
- Use this only for contract-level required assertions when speed and width evidence matches manifest expectations.
- If degradation reasons are present, retain visibility and avoid blanket `completed` claims until explicit policy documents allow.
