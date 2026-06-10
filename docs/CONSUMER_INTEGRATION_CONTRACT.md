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
   - `python -X utf8 scripts/run_regression_smoke.py --suite required --format human`
3. Run advisory smoke suite (review surface only):
   - `python -X utf8 scripts/run_regression_smoke.py --suite advisory --format human`
4. Run merged decision view and persist evidence:
   - `python -X utf8 scripts/run_regression_smoke.py --suite all --format json > artifacts/validation/required-advisory-smoke.json`

### Optional advisory checks

- Optional fixture-level check:
  - `python -X utf8 scripts/run_fixture_smoke.py --suite all --format human`
- Optional fixture-level split:
  - `python -X utf8 scripts/run_fixture_smoke.py --suite required --format human`
  - `python -X utf8 scripts/run_fixture_smoke.py --suite advisory --format human`
- These are useful for visibility and design review, but do not change completed claim level.

### Required file contract before consume

- Use `exports/pcie_governed_surface_manifest.yaml` as the stable manifest entry point.
- Use `fixtures/fixture_manifest.json` as the fixture claim authority.
- Use `docs/LLM_VERIFICATION_STATUS.md` only after steps 2~4 are done and evidence is refreshed.
- Use `python -X utf8 scripts/run_regression_smoke.py --suite all --format json` as the single source for merged pass/fail decision.

## 4) Evidence handoff for CI

When integrating in another repository, this project is expected to return:

- `contract.yaml` (aligned head)
- `fixtures/fixture_manifest.json` (authoritative fixture surface)
- `exports/pcie_governed_surface_manifest.yaml` (consumer entry surface)
- `artifacts/validation/required-advisory-smoke.json` (merged evidence output)
- `governance/` and `docs/` slices that justify scope changes
- `memory/2026-*.md` with post-push evidence entries for the same commit window

## 5) Failure mode policy

- **Block**: any contradiction to completed claim ceiling (for example, advisory-only slice used as full compliance).
- **Warn**: advisory slice pass with incomplete boundary evidence.
- **Reject**: missing required evidence for `pcie-ltssm`, speed/width, final state, or equalization completeness.

## 5a) Minimal consume recipe (paste into RTL CI)

```powershell
# 1) Check manifest is loadable
python -X utf8 ai-governance-framework/governance_tools/domain_contract_loader.py --contract <path-to-pcie-contract>/contract.yaml --format human

# 2) Required gate first
python -X utf8 <path-to-pcie-contract>/scripts/run_regression_smoke.py --framework-root ai-governance-framework --contract-root <path-to-pcie-contract> --suite required --format human

# 3) Advisory visibility (non-gating)
python -X utf8 <path-to-pcie-contract>/scripts/run_regression_smoke.py --framework-root ai-governance-framework --contract-root <path-to-pcie-contract> --suite advisory --format human

# 4) Single merged evidence snapshot
python -X utf8 <path-to-pcie-contract>/scripts/run_regression_smoke.py --framework-root ai-governance-framework --contract-root <path-to-pcie-contract> --suite all --format json | Out-File artifacts/pcie_governance_smoke_all.json
```

## 6) Versioning and governance coupling

- Do not auto-bypass contract evolution. Any consumed repository must reference a pinned
  compatible contract shape and run local memory/validation flow before claiming merge-ready.

## 7) Escalation target

- Escalate to owning PCIe review lead when:
  - claim ceiling changes,
  - fixture manifest meaning changes,
  - or advisory surface evidence model is promoted to full completion.
