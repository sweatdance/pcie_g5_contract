# PCIe Gen5 LTSSM Link Training Contract

This repository is a private external domain contract for the AI Governance Framework.

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

## Layout

- contract.yaml: machine-readable contract entrypoint
- AGENTS.md: reviewer-facing behavior override
- docs/: narrow domain guidance and evidence contract
- rules/: external rule packs consumed by the framework
- validators/: domain validators executed during post-task checks
- fixtures/: minimal smoke fixtures for contract validation

## Usage

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
