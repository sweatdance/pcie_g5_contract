---
title: Consumer Integration
description: Required and advisory onboarding workflow for downstream RTL use
---

# Consumer Integration

This page defines the minimum governed path for a downstream RTL repository to consume this contract safely.

## Scope guard (important)

!!! warning "Scope rule"
    Advisory slices must never be used as required protocol gates.

- Required scope: **`pcie-ltssm`**, **`pcie-eq`**, **`pcie-link-negotiation`**
- Advisory scope: **`pcie-pm`**, **`pcie-aer`**, **`pcie-dll`**, **`pcie-tlp`**, **`pcie-hotplug`**, **`pcie-cfgspace`**
  - `pcie-cfgspace` routing is present for completeness checks only.

## Required commands

```powershell
python -X utf8 <framework_root>\governance_tools\external_repo_readiness.py \
  --repo <target-rtl-repo> \
  --contract <pcie_contract_root>\contract.yaml \
  --framework-root <framework_root> \
  --format json

python <pcie_contract_root>\scripts\run_fixture_smoke.py \
  --framework-root <framework_root> \
  --contract-root <pcie_contract_root> \
  --suite required --format json

python <framework_root>\governance_tools\external_repo_smoke.py \
  --repo <pcie_contract_root> \
  --contract <pcie_contract_root>\contract.yaml \
  --framework-root <framework_root> \
  --format json
```
!!! note "Command notes"
    Keep placeholders consistent across all three commands. The placeholders are intentionally explicit:
    `<pcie_contract_root>` and `<framework_root>`.

## Contract ingestion pattern

- Validate `exports/pcie_governed_surface_manifest.yaml` before claiming machine-readable use.
- Keep `fixtures/fixture_manifest.json` aligned with the same scope.
- Update this page and the canonical `docs/CONSUMER_INTEGRATION_CONTRACT.md` when scope changes.

## Exact minimum sequence

1. Read and verify `contract.yaml`.
2. Run required smoke first: `run_regression_smoke --suite required`.
3. Run advisory smoke as review context: `run_regression_smoke --suite advisory`.
4. Publish merged decision artifact:
   `run_regression_smoke --suite all --format json`.

## Recommended workflow

1. Run required smoke and required fixtures.
2. Only gate CI on required scope for RTL-required decisions.
3. Keep advisory results in non-blocking status until explicit validator routing is proven.
