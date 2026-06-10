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

## Entry points

- [Consumer Integration](consumer-integration.md): mandatory onboarding workflow for downstream RTL.
- [LLM Wiki](llm-wiki.md): claim boundaries and policy language.
- [Verification Status](verification-status.md): slice-level maturity and evidence posture.
- [Contract Mapping](contract-mapping.md): source mapping from review artifacts to contract surfaces.
- [Evidence Grid](evidence-grid.md): what proves what, where.

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
2. [LLM Wiki](llm-wiki.md): load claim policy and anti-pattern checklist.
3. [Verification Status](verification-status.md): read decision behavior and required/advisory outcomes.
4. [Contract Mapping](contract-mapping.md): trace question to a contract surface.
5. [Specification Library](specs/index.md): read required/advisory page details.
6. [Evidence Grid](evidence-grid.md): align every claim with concrete source files and runbook.

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

- [LLM Wiki (source)](LLM_WIKI.md)
- [Verification status source](LLM_VERIFICATION_STATUS.md)
- [Consumer contract source](CONSUMER_INTEGRATION_CONTRACT.md)
- [Contract scope matrix source](PCIE5_SPEC_TO_CONTRACT_MAPPING.md)

Use this portal as the first place to orient downstream agents and reviewers before opening raw sources.
