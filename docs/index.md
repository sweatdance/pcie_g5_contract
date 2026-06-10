---
title: PCIe Gen5 LTSSM Contract Reference
description: Governed validation reference for PCIe 5.0 link training and LTSSM evidence
---

<section class="hero-shell">

# PCIe Gen5 LTSSM Contract Reference

Governed validation reference for **PCIe 5.0 link training** and LTSSM evidence.
Structured for RTL integration review and LLM-facing automation workflows.

<div class="hero-tags">
  <span class="hero-tag">Required-gate ready</span>
  <span class="hero-tag">Evidence-driven</span>
  <span class="hero-tag">LLM-safe</span>
  <span class="hero-tag">CI-protected</span>
</div>

<div class="hero-tiles">
  <div class="hero-card">
    <strong>3</strong> required surfaces<br>
    <small>pcie-ltssm · pcie-eq · pcie-link-negotiation</small>
  </div>
  <div class="hero-card">
    <strong>6</strong> advisory surfaces<br>
    <small>pm · aer · dll · tlp · hotplug · cfgspace</small>
  </div>
  <div class="hero-card">
    <strong>24 / 24</strong> fixtures passing<br>
    <small>9 trigger-verified · 3 routing-verified · 12 advisory</small>
  </div>
</div>

</section>

## Start here

<div class="feature-grid">
<div class="feature-card">

### [Specification Library](en/specs/index.md)

Required and advisory spec pages with validation criteria, evidence fields, decision guardrails, and consumer response templates.

</div>
<div class="feature-card">

### [Consumer Integration](en/consumer-integration.md)

Mandatory onboarding workflow for downstream RTL integration — scope confirmation, fixture evidence, and claim ceiling rules.

</div>
<div class="feature-card">

### [Verification Status](en/verification-status.md)

Slice-level maturity, fixture evidence posture, CI gate status, and receipt freshness.

</div>
</div>

## Claim boundary at a glance

| Surface | Level | Gate use |
|---|---|---|
| `pcie-ltssm` | required_gate_ready | CI blocking |
| `pcie-eq` | required_gate_ready | CI blocking |
| `pcie-link-negotiation` | required_gate_ready | CI blocking |
| `pcie-pm` | advisory_expansion | Context only |
| `pcie-aer` | advisory_expansion | Context only |
| `pcie-dll` | advisory_expansion | Context only |
| `pcie-tlp` | advisory_expansion | Context only |
| `pcie-hotplug` | advisory_expansion | Context only |
| `pcie-cfgspace` | advisory_expansion | Context only |

## What this repo is — and is not

- **Is**: a scope-bounded, evidence-backed contract for PCIe 5.0 LTSSM and link-training review.
- **Is not**: a full PCIe protocol compliance handbook; SR-IOV, ATS, ordering rules, and DPC are not claimed.
- Advisory surfaces are visible for investigation but must not be used as required-gate substitutes.
- All claim decisions are traceable to `contract.yaml`, `fixtures/fixture_manifest.json`, and `artifacts/validation/fixture-smoke-receipt.json`.

!!! tip "Quick smoke check"
    ```
    python scripts/run_regression_smoke.py --suite required --format json
    ```
    `overall_ok=true` confirms required-gate + receipt freshness in one pass.
