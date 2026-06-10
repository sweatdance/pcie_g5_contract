---
title: Power Management
description: Advisory PM / ASPM governance slice
---

# Power Management

## Status

- Contract surface: `pcie-pm`
- Claim level: `advisory_expansion`
- Source completeness: **advisory page**

## Scope

- PM/ASPM sequencing, PM_REQ_ACK timing, and PM lifecycle risks during enumeration.
- Advisory evidence only unless explicitly reclassified by a downstream consumer.

## Canonical mapping

- Required source: [`PCIE5_POWER_MANAGEMENT.md`](../../../PCIE5_POWER_MANAGEMENT.md)
- Mapping entry: [`PCIE5_SPEC_TO_CONTRACT_MAPPING.md` Slice 5](../../../PCIE5_SPEC_TO_CONTRACT_MAPPING.md)
- Rule IDs: `PCIE5-PM-001` .. `PCIE5-PM-017`

## Key fields to inspect

- `enumeration_complete`
- `pm_l1_observed`
- `aspm_enabled_by_cfgwr`
- `pm_request_ack_in_enum_window`
- `pm_l1_before_enum_complete` / advisory alias
- `l1_substate_mode`

## Validation entrypoints

- Fixture suite: `pcie-pm`
- Run command: `python scripts/run_fixture_smoke.py --suite pcie-pm --format json`
- Required smoke: `python scripts/run_regression_smoke.py --suite advisory --format json`

## Decision guidance

- Use this for root-cause review and advisory warnings.
- For hard stop in this repo, this page supports downstream interpretation but does not by itself produce required-gate claims.

## Open scope

- Add explicit examples for D-state and ASPM hard-stop versus warn patterns.
