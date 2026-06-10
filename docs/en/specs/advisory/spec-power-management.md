---
title: Power Management
description: Advisory PM / ASPM governance slice
---

# Power Management

## Scope

- Contract slice: `pcie-pm`
- Claim level: `advisory_expansion`
- Canonical source: `docs/PCIE5_POWER_MANAGEMENT.md`

## Canonical mapping

- [Power management source](../../../PCIE5_POWER_MANAGEMENT.md)
- [Contract mapping crosswalk](../../../PCIE5_SPEC_TO_CONTRACT_MAPPING.md) (Slice 5)

## Coverage view

- Fixture scope: advisory (`pcie-pm`)
- Advisory visibility is important for review and regression triage, but not a required hard-gate input by default.
- Evidence may include AER/PM timing and ASPM sequencing.
