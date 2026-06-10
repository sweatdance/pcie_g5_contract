# PCIe Gen5 LTSSM Link Training Contract

This repository is a private external domain contract for the AI Governance Framework.

Suggested GitHub repository description:

PCIe Gen5 LTSSM and link-training governance contract for RTL evidence review, JSON report validation, and reusable AI Governance Framework integration.

Suggested GitHub topics:

- pcie
- pcie-gen5
- ltssm
- link-training
- rtl
- verification
- governance
- ai-governance-framework

Scope:
- PCIe 5.0 LTSSM and link training
- RTL-oriented design and review workflows
- JSON evidence reports produced by simulation, emulation, or lab-adjacent infrastructure
- LTSSM state transition visibility
- equalization reviewer gates
- speed and width negotiation evidence
- recovery and fallback visibility

Non-scope:
- full PCIe 5.0 protocol coverage
- software driver behavior
- compliance certification automation
- retimer, SRIS, or protocol analyzer decoding breadth beyond the first LTSSM slice
- protocol-expansion slices (PM/AER/DLL/TLP/Hot-Plug/CFG) are implemented for evidence coverage only
- completeness claims currently remain LTSSM/link-training only

## Layout

- contract.yaml: machine-readable contract entrypoint
- AGENTS.md: reviewer-facing behavior override
- docs/: narrow domain guidance and evidence contract
- rules/: external rule packs consumed by the framework
- validators/: domain validators executed during post-task checks
- fixtures/: minimal smoke fixtures for contract validation
- docs/LLM_WIKI.md: LLM-friendly contract entry and boundary summary
- docs/LLM_VERIFICATION_STATUS.md: visibility summary for slice maturity and fixture coverage
- docs/CONSUMER_INTEGRATION_CONTRACT.md: integration rules for downstream RTL repos
- exports/pcie_governed_surface_manifest.yaml: governed surface manifest for automated consumption
- docs/en/: generated documentation website source used for LLM-first navigation

## Documentation Site

- GitHub Pages (LLM-first): `https://sweatdance.github.io/pcie_g5_contract/en/` (after Pages enabled and workflow run)
- Local preview:

```powershell
python -m pip install mkdocs mkdocs-material
mkdocs serve
```

## CI

This repo includes a GitHub Actions workflow at `.github/workflows/contract-regression.yml`.

The workflow:

- checks out this contract repo
- checks out `Gavin0099/ai-governance-framework`
- installs the framework dependencies from `ai-governance-framework/requirements.txt`
- runs `scripts/run_regression_smoke.py`
- uploads a machine-readable regression report artifact

If you want to pin a different framework version, update `FRAMEWORK_REF` in the workflow file.

## Usage

### Consume contract in a downstream RTL repo

This contract is scoped to **LTSSM / EQ / link-negotiation** as required gate scope.
Advisory slices (PM/AER/DLL/TLP/Hot-Plug/CFG) must not be treated as required.

```powershell
# 1) Ensure the target RTL repo has this contract wired for consumption
python -X utf8 <framework_root>\governance_tools\external_repo_readiness.py `
  --repo <target-rtl-repo> `
  --contract <pcie_contract_root>\contract.yaml `
  --framework-root <framework_root> `
  --format json

# 2) Validate fixture mapping for required/advisory slices
python <pcie_contract_root>\scripts\run_fixture_smoke.py `
  --framework-root <framework_root> `
  --contract-root <pcie_contract_root> `
  --format json

# 3) Verify contract-level evidence report
python <framework_root>\governance_tools\external_repo_smoke.py `
  --repo <pcie_contract_root> `
  --contract <pcie_contract_root>\contract.yaml `
  --framework-root <framework_root> `
  --format json
```

Run these and copy the generated JSON into `docs/LLM_VERIFICATION_STATUS.md` / consumer checks as part of your local intake.

Load the contract:

```powershell
D:\SPEC\PCI_Express\PCIe_Gen5_SKILL\.venv\Scripts\python.exe D:\SPEC\PCI_Express\PCIe_Gen5_SKILL\ai-governance-framework\governance_tools\domain_contract_loader.py --contract D:\SPEC\PCI_Express\PCIe_Gen5_SKILL\pcie-gen5-ltssm-contract\contract.yaml --format human
```

Replay a runtime smoke:

```powershell
D:\SPEC\PCI_Express\PCIe_Gen5_SKILL\.venv\Scripts\python.exe D:\SPEC\PCI_Express\PCIe_Gen5_SKILL\ai-governance-framework\runtime_hooks\smoke_test.py --event-type session_start --contract D:\SPEC\PCI_Express\PCIe_Gen5_SKILL\pcie-gen5-ltssm-contract\contract.yaml --format human
```

Run positive and negative fixture smoke checks:

```powershell
D:\SPEC\PCI_Express\PCIe_Gen5_SKILL\.venv\Scripts\python.exe D:\SPEC\PCI_Express\PCIe_Gen5_SKILL\pcie-gen5-ltssm-contract\scripts\run_fixture_smoke.py --framework-root D:\SPEC\PCI_Express\PCIe_Gen5_SKILL\ai-governance-framework --contract-root D:\SPEC\PCI_Express\PCIe_Gen5_SKILL\pcie-gen5-ltssm-contract --format human
```

Convert packet monitor logs into `pcie_ltssm_report` or `checks` JSON:

```powershell
D:\SPEC\PCI_Express\PCIe_Gen5_SKILL\.venv\Scripts\python.exe D:\SPEC\PCI_Express\PCIe_Gen5_SKILL\pcie-gen5-ltssm-contract\scripts\extract_pcie_log_artifact.py D:\SPEC\PCI_Express\PCIe_Gen5_SKILL\aspm_l1_pciebfm_pkt.txt --output D:\SPEC\PCI_Express\PCIe_Gen5_SKILL\pcie-gen5-ltssm-contract\artifacts\aspm_l1.checks.json --format checks --target-speed-gtps 32 --target-width 16 --equalization-complete --completed-phases phase0 phase1 phase2 phase3
```

Create the release entry from the existing `v0.3.0` tag:

```text
https://github.com/sweatdance/pcie_g5_contract/releases/new?tag=v0.3.0
```

Use `docs/RELEASE_NOTES_v0.3.0.md` as the release body.

Run the full regression smoke command:

```powershell
D:\SPEC\PCI_Express\PCIe_Gen5_SKILL\.venv\Scripts\python.exe D:\SPEC\PCI_Express\PCIe_Gen5_SKILL\pcie-gen5-ltssm-contract\scripts\run_regression_smoke.py --framework-root D:\SPEC\PCI_Express\PCIe_Gen5_SKILL\ai-governance-framework --contract-root D:\SPEC\PCI_Express\PCIe_Gen5_SKILL\pcie-gen5-ltssm-contract --format human
```

Run the external repo smoke against this contract repo:

```powershell
D:\SPEC\PCI_Express\PCIe_Gen5_SKILL\.venv\Scripts\python.exe D:\SPEC\PCI_Express\PCIe_Gen5_SKILL\ai-governance-framework\governance_tools\external_repo_smoke.py --repo D:\SPEC\PCI_Express\PCIe_Gen5_SKILL\pcie-gen5-ltssm-contract --contract D:\SPEC\PCI_Express\PCIe_Gen5_SKILL\pcie-gen5-ltssm-contract\contract.yaml --format human
```

Use it from another RTL repo:

```powershell
D:\SPEC\PCI_Express\PCIe_Gen5_SKILL\.venv\Scripts\python.exe D:\SPEC\PCI_Express\PCIe_Gen5_SKILL\ai-governance-framework\governance_tools\external_repo_readiness.py --repo <target-rtl-repo> --contract D:\SPEC\PCI_Express\PCIe_Gen5_SKILL\pcie-gen5-ltssm-contract\contract.yaml --framework-root D:\SPEC\PCI_Express\PCIe_Gen5_SKILL\ai-governance-framework --format human
```

## Versioning

- Start narrow at v0.1.0
- Expand to v0.2.0 with state-transition, equalization, negotiation, and recovery slices
- Only expand further after the JSON evidence shape and reviewer expectations are stable
- Tag releases when contract semantics change

## Authoritative source

This repo is intended to be aligned with your internal PCIe 5.0 spec access and review process.
It deliberately avoids reproducing spec text. Keep detailed normative interpretation in internal review artifacts, not in this public-facing contract structure.

## Contract slices

- `docs/PCIE5_SPEC_TO_CONTRACT_MAPPING.md` maps internal spec study slices into reusable contract surfaces.
- `docs/PCIE5_LTSSM_STATE_TRANSITIONS.md` defines the state-trace evidence expected for nominal success claims.
- `docs/PCIE5_LINK_EQUALIZATION_RULES.md` defines equalization review requirements.
- `docs/PCIE5_SPEED_WIDTH_NEGOTIATION.md` defines speed and width negotiation evidence expectations.
- `docs/PCIE5_RECOVERY_AND_FALLBACK.md` defines recovery, retrain, and fallback visibility requirements.
