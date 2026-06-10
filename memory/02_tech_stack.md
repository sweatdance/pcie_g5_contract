# Tech Stack

## Repo Facts

- Primary language/runtime: Python validator and utility scripts executed from PowerShell and CI.
- Contract surfaces: `contract.yaml`, `rules/`, `validators/`, `fixtures/`, `docs/`, `.github/workflows/`.
- Validation entrypoints: `scripts/run_fixture_smoke.py`, `scripts/run_regression_smoke.py`, `scripts/extract_pcie_log_artifact.py`.
- Governance dependency model: this repo validates against an external checkout of `Gavin0099/ai-governance-framework`.
- Accepted memory alias schema in this repo is `02_tech_stack.md`, not `02_workflow.md`.

## Workflow Facts

- `governance-drift.yml` must checkout the external framework and run its `governance_tools/governance_drift_checker.py`.
- `governance-validation.yml` and `contract-regression.yml` split required LTSSM checks from advisory protocol-expansion checks.
- Required scope is LTSSM plus link training; advisory scope remains evidence-only until slice-specific JSON evidence exists.
