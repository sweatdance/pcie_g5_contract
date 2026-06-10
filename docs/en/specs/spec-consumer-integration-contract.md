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

## Integration profiles

### Strict profile (required gates only)

- Required suites: `--suite required`
- Decision rule: required failures block merge
- Scope: `pcie-ltssm`, `pcie-eq`, `pcie-link-negotiation`

### Safe profile (required + advisory for triage)

- Required suites: `--suite required`
- Advisory suites: `--suite advisory`
- Decision rule: advisory failures are review context only, not blocking by default

### Observatory profile (all suites)

- Required + advisory suites: `--suite all`
- Decision rule: advisory hard-stops still non-blocking unless a downstream policy reclassifies

## Consume matrix by integration type

- RTL CI:
  - Block on required suite failure
  - Log advisory issues for investigation
- Formal verification:
  - Require `advisory_issues = 0` before full signoff, if the downstream policy defines it
- Exploratory testing:
  - Publish merged output artifact and allow advisory-rich analysis

## Example output contract

```json
{
  "required": {
    "gate": "required_gate_ready",
    "status": "pass|fail"
  },
  "advisory": {
    "status": "observed",
    "issues": 3,
    "promotion": "review_only"
  }
}
```
