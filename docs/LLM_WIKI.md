# PCIe Gen5 LTSSM Contract - LLM Wiki

This wiki defines how to read this contract as evidence-based contract claims for
LLM and automation workflows.

## 1) Claim boundary (must read first)

- Scope is this repo: **PCIe Gen5 LTSSM + link-training** for RTL review.
- This is a reusable governed contract for review automation, not a replacement for
  device/board sign-off.
- Claim ceiling is intentionally explicit:
  - **Completed claims**: LTSSM, link training, equalization, speed/width negotiation,
    recovery visibility.
  - **Advisory slices**: PM, AER, DLL, TLP, Hot-Plug, CFG only. These are review-visible
    and rule-checked, but not treated as completed protocol-compliance claims yet.
- Never infer a completed protocol claim from advisory-only evidence.

## 2) Governed authority and source-of-truth

- Contract machine-readable entrypoint: `contract.yaml`
- Verification driver: AI governance framework + repo scripts
  - `scripts/run_regression_smoke.py`
  - `scripts/run_fixture_smoke.py`
- Contract docs are listed in `contract.yaml` `documents:` section.
- Memory authority for this repo is the local `memory/` directory.

Do not treat rendered pages, prose, or external websites as the authority source;
they are references.

## 3) Contract surface matrix

| Surface | Rule pack | Claim level | Evidence gate | Current status |
| --- | --- | --- | --- | --- |
| LTSSM | `pcie-ltssm` | Complete | `common`, `pcie-ltssm`, `pcie-eq`, `pcie-link-negotiation` | Required |
| Equalization | `pcie-eq` | Complete | same as LTSSM group | Required |
| Speed/width negotiation | `pcie-link-negotiation` | Complete | same as LTSSM group | Required |
| Recovery/fallback | `pcie-eq`/`pcie-ltssm` | Complete | same as LTSSM group | Required |
| Power Management | `pcie-pm` | Advisory-completed for trace visibility | `common`, `pcie-pm` | Advisory |
| AER | `pcie-aer` | Advisory-completed for trace visibility | `common`, `pcie-aer` | Advisory |
| DLL | `pcie-dll` | Advisory-completed for trace visibility | `common`, `pcie-dll` | Advisory |
| TLP | `pcie-tlp` | Advisory-completed for trace visibility | `common`, `pcie-tlp` | Advisory |
| Hot-Plug | `pcie-hotplug` | Advisory-completed for trace visibility | `common`, `pcie-hotplug` | Advisory |
| CFG space | `pcie-cfgspace` | Advisory/warn-grade | `common`, `pcie-cfgspace` | Advisory/warn |

## 4) Validation workflow (copy-paste)

- Load contract:
  - `python -X utf8 ai-governance-framework/governance_tools/domain_contract_loader.py --contract contract.yaml --format human`
- Required surface smoke (complete scope):
  - `python -X utf8 scripts/run_regression_smoke.py --framework-root ai-governance-framework --contract-root . --format human`
- Per-fixture validation:
  - `python -X utf8 scripts/run_fixture_smoke.py --framework-root ai-governance-framework --contract-root . --suite required --format human`
  - `python -X utf8 scripts/run_fixture_smoke.py --framework-root ai-governance-framework --contract-root . --suite advisory --format human`
- External repo read-in:
  - `python -X utf8 ai-governance-framework/governance_tools/external_repo_readiness.py --repo <rtl_repo_path> --contract contract.yaml --framework-root ai-governance-framework --format human`

## 5) Validation status to trust

- `fixtures/fixture_manifest.json` is the current fixture authority.
- Current run-level summary from manifest:
  - 24 fixtures total
  - 10 expected pass, 14 expected fail
- Slice fixture counts:
  - `pcie-ltssm`: 12 fixtures
  - `pcie-eq`: 12 fixtures
  - `pcie-link-negotiation`: 12 fixtures
  - `pcie-pm`: 3 fixtures
  - `pcie-hotplug`: 3 fixtures
  - `pcie-aer`: 2 fixtures
  - `pcie-cfgspace`: 2 fixtures
  - `pcie-dll`: 1 fixture
  - `pcie-tlp`: 1 fixture

Note: `pcie-ltssm`, `pcie-eq`, and `pcie-link-negotiation` share the same LTSSM fixture set,
so their counts overlap by design.

## 6) LLM decision policy

- If speed/width or final state is missing in the evidence, block completed success claims.
- If advisory slice is present without required fields, keep scope advisory and do not
  escalate to completed protocol claim.
- For any assertion about this repo, always include:
  - claim level used (`complete` or `advisory`)
  - evidence surface touched (`pcie-ltssm` etc.)
  - fixture or validator reference.

## 7) Escalation triggers (when to stop and escalate)

- Missing final LTSSM state or missing legal-transition visibility.
- Explicit advisory warning escalation with repeated same failure pattern.
- Contradiction between contract claim boundary and evidence (for example, protocol-level
  claim from advisory-only slices).
- Missing `memory/` governance updates required by repo workflow.

## 8) Consumer entry contracts

- `docs/CONSUMER_INTEGRATION_CONTRACT.md`
- `governance/AI_GOVERNANCE_UPDATE_PROTOCOL.md`
- `fixtures/fixture_manifest.json`
- `exports/pcie_governed_surface_manifest.yaml`
