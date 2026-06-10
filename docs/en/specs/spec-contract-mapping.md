---
title: Spec-to-Contract Mapping
description: Governance mapping surface from PCIe 5 slices to contract surfaces
---

# Spec-to-Contract Mapping

## Status

- Type: artifact index
- Source completeness: complete
- Source of truth: [`PCIE5_SPEC_TO_CONTRACT_MAPPING.md`](../../PCIE5_SPEC_TO_CONTRACT_MAPPING.md)

## Canonical

- Source: [`PCIE5_SPEC_TO_CONTRACT_MAPPING.md`](../../PCIE5_SPEC_TO_CONTRACT_MAPPING.md)
- Consumer binding: [`docs/PCIE5_SPEC_TO_CONTRACT_MAPPING.md`](../../PCIE5_SPEC_TO_CONTRACT_MAPPING.md) and fixture declarations in `fixtures/fixture_manifest.json`

## Scope

- This page defines only the surfaced PCIe 5 claim routing for LTSSM, link-training, and adjacent operational slices in this contract.

## Scope map

- Required: `pcie-ltssm`, `pcie-eq`, `pcie-link-negotiation`
- Advisory: `pcie-pm`, `pcie-aer`, `pcie-dll`, `pcie-tlp`, `pcie-hotplug`, `pcie-cfgspace`
- Rule families: `PCIE5-...` by slice.
- Hard-gate slices: `pcie-ltssm`, `pcie-eq`, `pcie-link-negotiation`.
- Advisory-only slices: `pcie-pm`, `pcie-aer`, `pcie-dll`, `pcie-tlp`, `pcie-hotplug`, `pcie-cfgspace`.

## Mapping table

| Surface | Contract slice | Claim level | Fixture suite | Rule family examples |
|---|---|---|---|---|
| LTSSM state transitions | `pcie-ltssm` | required_gate_ready | `run_fixture_smoke.py --suite pcie-ltssm` | `PCIE5-LTSSM-...` |
| LTSSM checklist | `pcie-ltssm` | required_gate_ready | `run_fixture_smoke.py --suite pcie-ltssm` | `PCIE5-LTSSM-...` |
| Link equalization | `pcie-eq` | required_gate_ready | `run_fixture_smoke.py --suite pcie-eq` | `PCIE5-EQ-...` |
| Speed/width negotiation | `pcie-link-negotiation` | required_gate_ready | `run_fixture_smoke.py --suite pcie-link-negotiation` | `PCIE5-LINK-NEG-...` |
| Power management | `pcie-pm` | advisory_expansion | `run_fixture_smoke.py --suite pcie-pm` | `PCIE5-PM-...` |
| AER | `pcie-aer` | advisory_expansion | `run_fixture_smoke.py --suite pcie-aer` | `PCIE5-AER-...` |
| DLL | `pcie-dll` | advisory_expansion | `run_fixture_smoke.py --suite pcie-dll` | `PCIE5-DLL-...` |
| TLP | `pcie-tlp` | advisory_expansion | `run_fixture_smoke.py --suite pcie-tlp` | `PCIE5-TLP-...` |
| Hot-plug | `pcie-hotplug` | advisory_expansion | `run_fixture_smoke.py --suite pcie-hotplug` | `PCIE5-HP-...` |
| CFG space | `pcie-cfgspace` | advisory_expansion | `run_fixture_smoke.py --suite pcie-cfgspace` | `PCIE5-CFG-...` |

## Validation

- Required-surface validation command: `python scripts/run_regression_smoke.py --suite required --format json`
- Advisory-surface validation command: `python scripts/run_regression_smoke.py --suite advisory --format json`
- Fixture routing verification: `python scripts/run_fixture_smoke.py --suite all --format json`

## How to use this page

- Start from a term or question in a source doc.
- Find corresponding slice in this mapping.
- Route to the matching page under `Required` or `Advisory`.
- Validate with the associated fixture suite before making any claim.

## Evidence routing rule

- Only `required` and `required_gate_ready` slices may drive hard gate decisions.
- Advisory slices must be routed as review evidence and flagged as non-blocking unless downstream policy rewrites them.

## Decision guidance

- Resolve each question by contract slice first; only then consult `required`/`advisory` smoke outputs.
- Missing required-slice evidence should immediately block hard-stop language even if other evidence looks good.

## Related pages

- [`spec-ltssm-state-transitions`](required/spec-ltssm-state-transitions.md)
- [`spec-link-equalization-rules`](required/spec-link-equalization-rules.md)
- [`spec-speed-width-negotiation`](required/spec-speed-width-negotiation.md)
- [`spec-power-management`](advisory/spec-power-management.md)

## Consumer response template

```json
{
  "mapped_surface": "pcie-ltssm|pcie-eq|pcie-link-negotiation|pcie-pm|pcie-aer|pcie-dll|pcie-tlp|pcie-hotplug|pcie-cfgspace",
  "claim_level": "required_gate_ready|advisory_expansion",
  "suite": "pcie-ltssm|pcie-eq|pcie-link-negotiation|pcie-pm|pcie-aer|pcie-dll|pcie-tlp|pcie-hotplug|pcie-cfgspace",
  "result": "pass|warn|blocked",
  "evidence": "PCIE5_SPEC_TO_CONTRACT_MAPPING.md + fixture smoke output"
}
```
