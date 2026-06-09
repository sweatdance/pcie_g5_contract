# Consumer Integration Contract (PCIe Gen5 LTSSM Contract)

## 1) What this contract is for

This contract file is for downstream RTL repositories that consume this domain contract.
It defines the minimum checks and required claim boundary before using reviewed results
for CI or review automation.

## 2) Scope and claim ceiling

- Completed claim scope (this contract must be respected as complete):
  - `pcie-ltssm`, `pcie-eq`, `pcie-link-negotiation`, recovery visibility.
- Protocol-expansion surfaces are advisory-review only:
  - `pcie-pm`, `pcie-aer`, `pcie-dll`, `pcie-tlp`, `pcie-hotplug`, `pcie-cfgspace`.

Consumer tooling must not promote advisory-only slices to completed compliance status.

## 3) Required integration checks

### Mandatory for gate decisions

1. Load contract:
   - `python -X utf8 ai-governance-framework/governance_tools/domain_contract_loader.py --contract contract.yaml --format human`
2. Run required smoke suite (or equivalent CI job):
   - `python -X utf8 scripts/run_regression_smoke.py --framework-root ai-governance-framework --contract-root . --format human`
3. Validate fixture status:
   - `python -X utf8 scripts/run_fixture_smoke.py --framework-root ai-governance-framework --contract-root . --format human`

### Optional advisory checks

- `python -X utf8 scripts/run_fixture_smoke.py --framework-root ai-governance-framework --contract-root . --suite advisory --format human`
- These are useful for visibility and design review, but do not change completed claim level.

## 4) Evidence handoff for CI

When integrating in another repository, this project is expected to return:

- `contract.yaml` (aligned head)
- `fixtures/fixture_manifest.json`
- `governance/` and `docs/` slices that justify scope changes
- Validator outputs from required + advisory suites

## 5) Failure mode policy

- **Block**: any contradiction to completed claim ceiling (for example, advisory-only slice used as full compliance).
- **Warn**: advisory slice pass with incomplete boundary evidence.
- **Reject**: missing required evidence for `pcie-ltssm`, speed/width, final state, or equalization completeness.

## 6) Versioning and governance coupling

- Do not auto-bypass contract evolution. Any consumed repository must reference a pinned
  compatible contract shape and run local memory/validation flow before claiming merge-ready.

## 7) Escalation target

- Escalate to owning PCIe review lead when:
  - claim ceiling changes,
  - fixture manifest meaning changes,
  - or advisory surface evidence model is promoted to full completion.
