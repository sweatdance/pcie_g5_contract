# PCIe Gen5 LTSSM Contract Reference

Welcome to the PCIe Gen5 LTSSM and link-training governance reference.

## What this repository is

- Scope: LTSSM and link-training review for RTL evidence and governance workflows.
- Not scope: full PCIe 5.0 protocol compliance claims.
- Entry surface for governance tooling: `contract.yaml`.

## Quick start

1. Read [Consumer integration](consumer-integration.md) for downstream RTL onboarding.
2. Read [LLM Wiki](llm-wiki.md) for boundary-aware claim policy.
3. Read [Verification status](verification-status.md) for current slice maturity.
4. Open [Spec mapping](contract-mapping.md) before writing any protocol claim.

## Primary docs

- [LLM Wiki (governance source)](LLM_WIKI.md)
- [Consumer contract](CONSUMER_INTEGRATION_CONTRACT.md)
- [Verification status](LLM_VERIFICATION_STATUS.md)

## External checks

- For integration smoke: `external_repo_readiness.py`
- For fixture smoke: `run_fixture_smoke.py`
- For regression smoke: `run_regression_smoke.py`

See the consumer integration page for copy/paste command forms.
