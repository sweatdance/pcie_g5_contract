---
title: AER Rules
description: Advisory error handling and AER register management slice
---

# AER Rules

## Scope

- Contract slice: `pcie-aer`
- Claim level: `advisory_expansion`
- Canonical source: `docs/PCIE5_AER_RULES.md`

## Canonical mapping

- [AER source](../../../PCIE5_AER_RULES.md)
- [Contract mapping crosswalk](../../../PCIE5_SPEC_TO_CONTRACT_MAPPING.md) (Slice 7)

## Coverage view

- Fixture scope: advisory (`pcie-aer`)
- Advisory evidence can be used for error-path diagnostics; do not promote to required-completion claims without explicit consumer reclassification.
