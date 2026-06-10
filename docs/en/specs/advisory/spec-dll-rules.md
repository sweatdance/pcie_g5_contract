---
title: DLL Rules
description: Advisory data link-layer event visibility slice
---

# DLL Rules

## Status

- Contract surface: `pcie-dll`
- Claim level: `advisory_expansion`
- Source completeness: **advisory page**

## Scope

- InitFC sequencing, DL_Active gating, ACK/NAK protocol order, and replay edge cases.
- Advisory reviewer surface (not required for required-gate closure).

## Canonical mapping

- Required source: [`PCIE5_DLL_RULES.md`](../../../PCIE5_DLL_RULES.md)
- Mapping entry: [`PCIE5_SPEC_TO_CONTRACT_MAPPING.md` Slice 8](../../../PCIE5_SPEC_TO_CONTRACT_MAPPING.md)
- Rule IDs: `PCIE5-DLL-001` .. `PCIE5-DLL-005`

## Key fields to inspect

- `initfc_complete`
- `dl_up_confirmed`
- `nak_observed`
- `nak_followed_by_replay`
- `updatefc_observed`
- `capture_duration_ms`

## Validation entrypoints

- Fixture suite: `pcie-dll`
- Run command: `python scripts/run_fixture_smoke.py --suite pcie-dll --format json`
- Regression path: `python scripts/run_regression_smoke.py --suite advisory --format json`

## Decision guidance

- Advisory evidence for replay and ordering risks.
- NAK without replay sequence should be treated as protocol violation in review logs.
- Required-gate decisions should stay anchored on required slices.

## Open scope

- Add explicit handling guidance for CATC artifacts versus real InitFC initialization failures.
