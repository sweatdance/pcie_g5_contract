---
title: PCIe Gen5 LTSSM Contract Wiki
description: Governed wiki for PCIe Gen5 LTSSM and link-training evidence review
---

<section class="reference-hero">

# PCIe Gen5 LTSSM Contract Wiki

A governed reference wiki for RTL evidence review, contract integration, and LLM-safe PCIe Gen5 link-training answers.

<p class="claim-line">
Goal: help consumers find the right contract surface, required evidence, validation command, and claim ceiling before making an RTL or automation decision.
</p>

<div class="reference-actions">
  <a href="specs/index.md" class="reference-action primary">Open Specification Library</a>
  <a href="consumer-integration.md" class="reference-action">Downstream Contract</a>
  <a href="verification-status.md" class="reference-action">Evidence Status</a>
</div>

</section>

## What This Wiki Is For

This wiki is the first stop for interpreting the `pcie_g5_contract` repository. It turns the raw contract files, fixtures, source spec notes, and governance rules into a browsable reference for:

- RTL reviewers checking PCIe Gen5 LTSSM and link-training evidence
- downstream repositories consuming the contract through CI or agent workflows
- LLM agents that need a bounded source of truth before producing summaries
- maintainers tracking which surfaces are required, advisory, mapped, or not claimed

It is intentionally scoped. Required pages support link-training contract review; advisory pages support investigation and expansion planning.

## Start Here

<div class="reference-grid">
  <a class="reference-card" href="specs/index.md">
    <strong>Specification Library</strong>
    <span>All required pages, advisory pages, and governance artifacts in one navigation tree.</span>
  </a>
  <a class="reference-card" href="consumer-integration.md">
    <strong>Consumer Integration</strong>
    <span>Minimum downstream RTL workflow, scope guard, and command sequence.</span>
  </a>
  <a class="reference-card" href="verification-status.md">
    <strong>Verification Status</strong>
    <span>Current maturity and evidence posture for required and advisory slices.</span>
  </a>
  <a class="reference-card" href="contract-mapping.md">
    <strong>Contract Mapping</strong>
    <span>Routes questions from a PCIe topic to contract surface and source file.</span>
  </a>
  <a class="reference-card" href="evidence-grid.md">
    <strong>Evidence Grid</strong>
    <span>Explains which files and smoke outputs can support each claim.</span>
  </a>
  <a class="reference-card" href="glossary-and-mapping.md">
    <strong>Glossary & Mapping</strong>
    <span>Terminology guardrails for consistent human and LLM responses.</span>
  </a>
</div>

## Required Surfaces

These are the only default hard-gate surfaces in this contract profile.

| Page | Contract surface | Evidence intent |
| --- | --- | --- |
| [LTSSM State Transitions](specs/required/spec-ltssm-state-transitions.md) | `pcie-ltssm` | state legality and final state |
| [LTSSM Checklist](specs/required/spec-ltssm-checklist.md) | `pcie-ltssm` | reviewer checklist completion |
| [Equalization Rules](specs/required/spec-link-equalization-rules.md) | `pcie-eq` | equalization phase completion |
| [Speed & Width Negotiation](specs/required/spec-speed-width-negotiation.md) | `pcie-link-negotiation` | negotiated speed, width, downtrain rationale |
| [Recovery and Fallback](specs/required/spec-recovery-and-fallback.md) | `pcie-ltssm` | recovery visibility and fallback explanation |

## Advisory Surfaces

Advisory pages are useful for diagnosis, but they do not become required gates unless a future contract version explicitly promotes them.

| Page | Contract surface | Typical use |
| --- | --- | --- |
| [Power Management](specs/advisory/spec-power-management.md) | `pcie-pm` | L1/L2/L3 and D-state review context |
| [AER Rules](specs/advisory/spec-aer-rules.md) | `pcie-aer` | error logging and recovery triage |
| [DLL Rules](specs/advisory/spec-dll-rules.md) | `pcie-dll` | DLLP and link-layer diagnosis |
| [TLP Rules](specs/advisory/spec-tlp-rules.md) | `pcie-tlp` | transaction-layer review context |
| [Hot-Plug Rules](specs/advisory/spec-hotplug-rules.md) | `pcie-hotplug` | surprise-removal and enumeration timing |
| [Config Space](specs/advisory/spec-config-space.md) | `pcie-cfgspace` | VID/DID, BAR, and enumeration checks |

## Claim Discipline

| Claim class | Meaning | Allowed response |
| --- | --- | --- |
| `required_gate_ready` | Fixture-backed required scope for LTSSM/EQ/link negotiation | Can support scoped RTL gate decisions |
| `advisory_expansion` | Documented diagnostic surface with partial or non-blocking evidence | Can support warnings and review notes |
| `not_claimed` | Outside the repository contract | Must not be inferred by LLM or CI consumers |

This wiki does not claim PCIe full-stack compliance, PCI-SIG certification, driver correctness, runtime silicon behavior, SR-IOV, ATS, DPC, or complete transaction-layer coverage.

## Quick Evidence Commands

```powershell
python scripts/run_regression_smoke.py --suite required --format json
python scripts/run_fixture_smoke.py --suite required --format json
python scripts/run_regression_smoke.py --suite all --format json
```

Use `--suite required` before making a hard-gate statement. Use `--suite advisory` or `--suite all` only to add non-blocking diagnostic context.

## LLM Response Rule

When an agent answers from this wiki, it should name:

1. the contract surface
2. the claim class
3. the evidence source
4. the validation command or receipt
5. the non-claim boundary

If any required field is missing, the answer should be `blocked` or `warn`, not `pass`.
