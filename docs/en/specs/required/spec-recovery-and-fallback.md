---
title: Recovery and Fallback
description: Required traceability for recovery and fallback behavior
---

# Recovery and Fallback

## Scope

- Contract slice: `pcie-ltssm` (recovery visibility in required domain)
- Claim level: `required_gate_ready` (with caution on warning paths)
- Canonical source: `docs/PCIE5_RECOVERY_AND_FALLBACK.md`

## Canonical mapping

- [Recovery/fallback source](../../../PCIE5_RECOVERY_AND_FALLBACK.md)
- [Contract mapping crosswalk](../../../PCIE5_SPEC_TO_CONTRACT_MAPPING.md) (Slice 4)

## Coverage view

- Recovery and retrain events are reviewed as part of required governance because they affect link stability assertion.
- For hard-gate behavior, ensure required fixture expectations are satisfied end-to-end in `run_regression_smoke.py`.
