# Verification Status

This page summarizes current contract maturity and evidence boundaries.

## Current scope stance

- Required slice set: `pcie-ltssm`, `pcie-eq`, `pcie-link-negotiation`
- Advisory slice set: `pcie-pm`, `pcie-aer`, `pcie-dll`, `pcie-tlp`, `pcie-hotplug`, `pcie-cfgspace`

## Fixture reality

- Use `artifacts/validation/*` and `fixtures/fixture_manifest.json` as source-of-truth.
- Keep advisory counts visible as advisory-only even when fixtures exist.

## Governance visibility

- `docs/LLM_VERIFICATION_STATUS.md` is the canonical status companion file in-repo.
- `runtime` smoke output JSON should be treated as evidence for gating behavior, not prose-only claims.
