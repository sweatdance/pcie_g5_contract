---
title: Spec-to-Contract Mapping
description: Governance mapping surface from PCIe 5 slices to contract surfaces
---

# Spec-to-Contract Mapping

## Status

- Type: artifact index
- Source completeness: complete
- Source of truth: [`PCIE5_SPEC_TO_CONTRACT_MAPPING.md`](../../../PCIE5_SPEC_TO_CONTRACT_MAPPING.md)

## Scope map

- Required: `pcie-ltssm`, `pcie-eq`, `pcie-link-negotiation`
- Advisory: `pcie-pm`, `pcie-aer`, `pcie-dll`, `pcie-tlp`, `pcie-hotplug`, `pcie-cfgspace`
- Rule families: `PCIE5-...` by slice.

## How to use this page

- Start from a term or question in a source doc.
- Find corresponding slice in this mapping.
- Route to the matching page under `Required` or `Advisory`.
- Validate with the associated fixture suite before making any claim.

## Related pages

- [`spec-ltssm-state-transitions`](required/spec-ltssm-state-transitions.md)
- [`spec-link-equalization-rules`](required/spec-link-equalization-rules.md)
- [`spec-speed-width-negotiation`](required/spec-speed-width-negotiation.md)
- [`spec-power-management`](advisory/spec-power-management.md)
