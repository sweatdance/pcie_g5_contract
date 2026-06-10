---
title: Consumer Integration Contract
description: Downstream integration contract and boundary rules
---

# Consumer Integration Contract

## Status

- Type: artifact index
- Source completeness: source-linked page

## Scope

- Defines how downstream RTL consumers should interpret required vs advisory slices.
- Describes expected claim discipline for CI, review, and triage contexts.

## Canonical source

- [`CONSUMER_INTEGRATION_CONTRACT.md`](../../../CONSUMER_INTEGRATION_CONTRACT.md)

## Decision matrix

- Required gate consumers: `pcie-ltssm`, `pcie-eq`, `pcie-link-negotiation`
- Advisory consumers: `pcie-pm`, `pcie-aer`, `pcie-dll`, `pcie-tlp`, `pcie-hotplug`, `pcie-cfgspace`
- Required assertions must be backed by required fixture and regression suites.

## Mandatory consume sequence

1. `domain_contract_loader.py` validates local contract loadability and surface map.
2. Required suite smoke establishes hard-gate readiness.
3. Advisory suite smoke populates investigation surface only.
4. All-scope smoke creates a merged evidence summary for traceability.
5. CI decisions consume only `pcie-ltssm`, `pcie-eq`, `pcie-link-negotiation` for required pass/fail transitions.

## Required artifacts

- `exports/pcie_governed_surface_manifest.yaml`
- `fixtures/fixture_manifest.json`
- `docs/LLM_VERIFICATION_STATUS.md`
- `docs/en/verification-status.md`
- `artifacts/validation/pcie_governance_smoke_all.json` (or equivalent)

## Minimal command recipe

```powershell
python -X utf8 ai-governance-framework/governance_tools/domain_contract_loader.py `
  --contract contract.yaml --format human
python -X utf8 scripts/run_regression_smoke.py --suite required --format json
python -X utf8 scripts/run_regression_smoke.py --suite advisory --format json
python -X utf8 scripts/run_regression_smoke.py --suite all --format json | Out-File artifacts/pcie_governance_smoke_all.json
```

## Open scope

- Add optional fixture split recipes for strict/safe/observability profiles.
- Add a version-specific consume matrix by repo integration profile (RTL CI, observability, and exploratory testing).
