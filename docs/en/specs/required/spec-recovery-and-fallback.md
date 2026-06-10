---
title: Recovery and Fallback
description: Required traceability for recovery and fallback behavior
---

# Recovery and Fallback

## Status

- Contract surface: `pcie-ltssm`
- Claim level: `required_gate_ready` (with warning paths)
- Source completeness: **required page**

## Scope

- Required review entry for retrain/recovery dependency and fallback visibility.
- Used before downstream CI treats a run as stable convergence.

## Canonical mapping

- Required source: [`PCIE5_RECOVERY_AND_FALLBACK.md`](../../../PCIE5_RECOVERY_AND_FALLBACK.md)
- Mapping entry: [`PCIE5_SPEC_TO_CONTRACT_MAPPING.md` Slice 4](../../../PCIE5_SPEC_TO_CONTRACT_MAPPING.md)
- Related required page: [`spec-ltssm-state-transitions.md`](spec-ltssm-state-transitions.md)

## Evidence fields

- `retry_count`
- `recovery_triggered`
- `downtrained`
- `fallback_reason`
- `recovery_reason`

## Validation entrypoints

- Fixture suite: `pcie-ltssm` (recovery-visible path)
- Run command: `python scripts/run_regression_smoke.py --suite required --format json`

## Decision guardrails

- Recovery-driven convergence is valid for visibility but still must be called out explicitly.
- Missing fallback reason when `downtrained` is true blocks required-gate confidence.
- Any claim of clean nominal success must explain recovery dependency.

## Open scope

- Add a compact rule of what qualifies as acceptable recovery-to-stable convergence.
