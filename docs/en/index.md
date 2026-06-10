---
title: PCIe Gen5 LTSSM Contract Reference
description: Governed reference for RTL evidence and automation-facing contract guidance
---

<section class="hero-shell">

# PCIe Gen5 LTSSM Contract Reference

Structured governance content for **required** versus **advisory** scope, optimized for RTL integration and LLM automation.

<div class="hero-tags">
  <span class="hero-tag">Scope-boundary-first</span>
  <span class="hero-tag">Evidence-driven</span>
  <span class="hero-tag">RTL integration ready</span>
</div>

</section>

## What this site is

- This is a governed **reference portal** for contract navigation and evidence workflows.
- This repository is scoped to **PCIe 5.0 LTSSM and link-training** for review and automation.
- It is not a full protocol compliance handbook and does not claim driver/runtime behavior completeness.

## Governance status at a glance

### What can be required-gated today

`pcie-ltssm`, `pcie-eq`, and `pcie-link-negotiation` are the current required-gate surfaces.

They can be used as hard boundaries only when:

- contract surface claims are within documented scope
- fixture/smoke evidence exists for the corresponding suite
- downstream integration contract is accepted for that callsite

### What is advisory only

- PM
- AER
- DLL
- TLP
- Hot-Plug
- CFG

These surfaces are visible for investigation and expansion work, but they must not be used as full protocol-completion substitutes.

### Claim ceiling

- **Required** = evidence-backed hard boundary for RTL review automation.
- **Advisory** = partial guidance with no mandatory gate effect.
- **Source copy** = the canonical PCIe spec/contract artifacts in repo root (preferred traceability source).

## Entry points

- [Consumer Integration](consumer-integration.md): mandatory onboarding workflow for downstream RTL.
- [LLM Wiki](../LLM_WIKI.md): claim boundaries and policy language.
- [Verification Status](../LLM_VERIFICATION_STATUS.md): slice-level maturity and evidence posture.
- [Contract Mapping](contract-mapping.md): source mapping from review artifacts to contract surfaces.
- [Evidence Grid](evidence-grid.md): what proves what, where.

## Non-goals and anti-patterns

Use this list to avoid over-claiming:

- Do not imply full PCIe stack completion from this repo.
- Do not mark advisory surface failures as required-gate blockers.
- Do not skip fixture evidence when asserting contract readiness.
- Do not infer behavior without mapping to a declared rule source and scope.

<div class="feature-grid">
<div class="feature-card">

### Required scope first

Use `pcie-ltssm`, `pcie-eq`, and `pcie-link-negotiation` as the required evidence foundation.  
These are the only surfaces used by default for downstream required-gate automation.

</div>
<div class="feature-card">

### Advisory support

PM/AER/DLL/TLP/Hot-Plug/CFG are visible for investigation, but they are **not** equivalent to required protocol completion.

</div>
<div class="feature-card">

### Machine-readable entry

- `contract.yaml`
- `fixtures/fixture_manifest.json`
- `exports/pcie_governed_surface_manifest.yaml`
- `memory/` trace and evidence records

</div>
</div>

## Recommended read path

1. [Consumer Integration](consumer-integration.md): confirm scope and mandatory sequence.
2. [LLM Wiki](../LLM_WIKI.md): load claim policy and anti-pattern checklist.
3. [Verification Status](../LLM_VERIFICATION_STATUS.md): read decision behavior and required/advisory outcomes.
4. [Contract Mapping](contract-mapping.md): trace question to a contract surface.
5. [Specification Library](specs/index.md): read required/advisory page details.
6. [Evidence Grid](evidence-grid.md): align every claim with concrete source files and runbook.

## Evidence refresh pattern

When status documents change, follow this order:

1. Run contract-relevant smoke.
2. Update `docs/LLM_VERIFICATION_STATUS.md`.
3. Keep claim ceiling text unchanged unless proof is fully refreshed.
4. Record closeout evidence in `memory/` before push.

## LLM decision envelope

For every upstream pull request or automation summary, emit:

```json
{
  "decision": "pass|warn|blocked",
  "scope": "required|advisory|both",
  "required_slice_status": {
    "pcie-ltssm": "pass|fail|not_run",
    "pcie-eq": "pass|fail|not_run",
    "pcie-link-negotiation": "pass|fail|not_run"
  },
  "advisory_notices": [
    {
      "slice": "pcie-pm|pcie-aer|pcie-dll|pcie-tlp|pcie-hotplug|pcie-cfgspace",
      "status": "pass|warn|issue",
      "blocking": false
    }
  ]
}
```

If any required slice is `fail`, set `decision=blocked`.
If required passes and advisory has issues, set `decision=warn`.
If required and advisory both pass, set `decision=pass`.

## Evidence freshness checklist

- Last evidence source must include `run_fixture_smoke.py` and `run_regression_smoke.py`.
- Required and advisory suite outputs must use `--format json`.
- `docs/LLM_VERIFICATION_STATUS.md` must be updated before publication.
- `memory/YYYY-MM-DD.md` must include a post-push governance entry for the same commit range.

## Command quick start

```powershell
python -X utf8 <framework_root>\governance_tools\external_repo_readiness.py `
  --repo <target-rtl-repo> `
  --contract <pcie_contract_root>\contract.yaml `
  --framework-root <framework_root> `
  --format json

python <pcie_contract_root>\scripts\run_fixture_smoke.py `
  --framework-root <framework_root> `
  --contract-root <pcie_contract_root> `
  --suite required --format json

python <framework_root>\governance_tools\external_repo_smoke.py `
  --repo <pcie_contract_root> `
  --contract <pcie_contract_root>\contract.yaml `
  --framework-root <framework_root> `
  --format json
```

!!! danger "Claim discipline"
    If required-surface final-state fields are missing, do not assert completed protocol claims.

## Source index

- [LLM Wiki (source)](../LLM_WIKI.md)
- [Verification status source](../LLM_VERIFICATION_STATUS.md)
- [Consumer contract source](../CONSUMER_INTEGRATION_CONTRACT.md)
- [Contract scope matrix source](../PCIE5_SPEC_TO_CONTRACT_MAPPING.md)

Use this portal as the first place to orient downstream agents and reviewers before opening raw sources.
