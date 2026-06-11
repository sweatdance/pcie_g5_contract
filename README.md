# PCIe Gen5 LTSSM Link Training Contract

> Scope: governed reference for PCIe Gen5 LTSSM, equalization, speed/width negotiation, recovery/fallback, and downstream RTL evidence review.

**claim_level:** `required_gate_ready` for scoped LTSSM / EQ / link-negotiation surfaces; `advisory_expansion` for PM / AER / DLL / TLP / Hot-Plug / Config Space; full PCIe protocol compliance and PCI-SIG certification are **not claimed**.

## What this contract covers

- LTSSM state transition visibility
- Link equalization review gates
- Speed and width negotiation evidence
- Recovery and fallback visibility
- Downstream RTL evidence-review integration
- LLM-safe claim boundaries for governed automation

## Start here

| Entry | Purpose |
| --- | --- |
| [LLM Wiki](docs/LLM_WIKI.md) | Contract boundary summary for agent and reviewer consumption |
| [Verification Status](docs/LLM_VERIFICATION_STATUS.md) | Slice maturity, fixture visibility, and evidence posture |
| [Consumer Integration Contract](docs/CONSUMER_INTEGRATION_CONTRACT.md) | Downstream RTL integration rules and non-claim boundaries |
| [Governed Surface Manifest](exports/pcie_governed_surface_manifest.yaml) | Machine-readable governed surface list |
| [Documentation Site](https://sweatdance.github.io/pcie_g5_contract/) | Public MkDocs reference portal |

## Contract slices

| Slice | Contract role |
| --- | --- |
| [PCIe 5.0 Spec-to-Contract Mapping](docs/PCIE5_SPEC_TO_CONTRACT_MAPPING.md) | Maps review slices into reusable contract surfaces |
| [LTSSM State Transitions](docs/PCIE5_LTSSM_STATE_TRANSITIONS.md) | State-trace evidence expected for nominal success claims |
| [Link Equalization Rules](docs/PCIE5_LINK_EQUALIZATION_RULES.md) | Equalization review requirements |
| [Speed / Width Negotiation](docs/PCIE5_SPEED_WIDTH_NEGOTIATION.md) | Negotiated speed, negotiated width, and fallback evidence |
| [Recovery and Fallback](docs/PCIE5_RECOVERY_AND_FALLBACK.md) | Recovery, retrain, and fallback visibility |

## Advisory surfaces

| Surface | Contract role |
| --- | --- |
| [Power Management](docs/PCIE5_POWER_MANAGEMENT.md) | Advisory power-state context |
| [AER Rules](docs/PCIE5_AER_RULES.md) | Advisory error-reporting context |
| [DLL Rules](docs/PCIE5_DLL_RULES.md) | Advisory data-link-layer context |
| [TLP Rules](docs/PCIE5_TLP_RULES.md) | Advisory transaction-layer context |
| [Hot-Plug Rules](docs/PCIE5_HOTPLUG_RULES.md) | Advisory hot-plug and enumeration context |
| [Config Space](docs/PCIE5_CONFIG_SPACE.md) | Advisory configuration-space context |

## Downstream usage

This contract is scoped to **LTSSM / EQ / link-negotiation** as required gate scope. Advisory slices must not be treated as required gates.

```powershell
python -X utf8 <framework_root>\governance_tools\external_repo_readiness.py `
  --repo <target-rtl-repo> `
  --contract <pcie_contract_root>\contract.yaml `
  --framework-root <framework_root> `
  --format json

python <pcie_contract_root>\scripts\run_fixture_smoke.py `
  --framework-root <framework_root> `
  --contract-root <pcie_contract_root> `
  --suite required `
  --format json

python <framework_root>\governance_tools\external_repo_smoke.py `
  --repo <pcie_contract_root> `
  --contract <pcie_contract_root>\contract.yaml `
  --framework-root <framework_root> `
  --format json
```

Persist generated JSON as evidence for local intake and status updates. Do not turn advisory output into a required-gate result without an explicit contract change.

## Documentation site

The public reference portal is built with MkDocs Material and deployed through GitHub Actions.

```powershell
python -m pip install mkdocs mkdocs-material
mkdocs serve
```

The Pages workflow builds `site/` from `mkdocs.yml`; Jekyll is not used.

## CI

The contract regression workflow:

- checks out this contract repository
- checks out `Gavin0099/ai-governance-framework`
- installs framework dependencies
- runs the regression smoke script
- uploads a machine-readable regression report artifact

If you need to pin a different framework version, update `FRAMEWORK_REF` in the workflow file.

## Versioning

- Start narrow at v0.1.0.
- Expand to v0.2.0 with state-transition, equalization, negotiation, and recovery slices.
- Expand further only after JSON evidence shape and reviewer expectations are stable.
- Tag releases when contract semantics change.

## Important boundary

This repository is intended to align with authorized PCIe 5.0 review access and internal evidence workflows. It deliberately avoids reproducing PCI-SIG specification text. Keep detailed normative interpretation in internal review artifacts, not in the public-facing contract structure.

## Maintainer source files

These paths are for maintainers who need to edit the underlying repository sources. They are not the primary reviewer navigation surface.

- `contract.yaml`
- `docs/LLM_WIKI.md`
- `docs/LLM_VERIFICATION_STATUS.md`
- `docs/CONSUMER_INTEGRATION_CONTRACT.md`
- `fixtures/fixture_manifest.json`
- `exports/pcie_governed_surface_manifest.yaml`
- `.github/workflows/deploy-pages.yml`
- `.github/workflows/contract-regression.yml`
