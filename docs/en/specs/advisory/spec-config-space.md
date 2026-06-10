---
title: Config Space
description: Advisory configuration-space access and enumeration boundary
---

# Config Space

## Status

- Contract surface: `pcie-cfgspace`
- Claim level: `advisory_expansion`
- Source completeness: **advisory page**

## Scope

- VID/DID enumeration checks, BAR probe sequence, command register readiness, and extended capability walks.
- Warn-only posture in this contract profile unless consumer explicitly promotes.

## Canonical mapping

- Required source: [`PCIE5_CONFIG_SPACE.md`](../../../PCIE5_CONFIG_SPACE.md)
- Mapping entry: [`PCIE5_SPEC_TO_CONTRACT_MAPPING.md` Slice 6](../../../PCIE5_SPEC_TO_CONTRACT_MAPPING.md)
- Rule IDs: `PCIE5-CFG-001` .. `PCIE5-CFG-005`

## Key fields to inspect

- `vidpid_read_observed`
- `vidpid_value`
- `bar_sizing_observed`
- `enumeration_sequence_complete`
- `link_control_read_before_write`
- `bus_master_enabled`

## Validation entrypoints

- Fixture suite: `pcie-cfgspace`
- Run command: `python scripts/run_fixture_smoke.py --suite pcie-cfgspace --format json`
- Regression path: `python scripts/run_regression_smoke.py --suite advisory --format json`

## Decision guidance

- Advisory-only boundary here: use for consumer diagnostics, not for required-gate closure.
- Incomplete enumeration evidence means hard caution even if other required slices are nominal.

## Open scope

- Add a quick register-order matrix (read-before-write and BAR readiness checks).
