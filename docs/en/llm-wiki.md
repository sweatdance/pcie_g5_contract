# LLM Wiki

This page is the LLM-facing entry for this contract.

## Claim boundary

- Completed scope: LTSSM state transitions, equalization, speed/width negotiation, recovery visibility.
- Advisory scope: PM, AER, DLL, TLP, Hot-Plug, CFG space.
- Never escalate advisory evidence to full protocol completion.

## Canonical authority

- `contract.yaml`
- `fixtures/fixture_manifest.json`
- `exports/pcie_governed_surface_manifest.yaml`
- `docs/LLM_VERIFICATION_STATUS.md`
- `docs/LLM_WIKI.md` (source doc)

## Validation surface

- `scripts/run_regression_smoke.py`
- `scripts/run_fixture_smoke.py`
- `governance_tools/external_repo_readiness.py` (external-readiness check)

## Policy

- Claims must include claim level (`required` / `advisory`) and evidence references.
- If final-state evidence is missing, block completed success assertions.
- If only advisory evidence is present, do not imply full protocol compliance.
