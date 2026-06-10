---
title: PCIe Gen5 LTSSM Contract Reference
description: LLM-facing wiki for governed PCIe Gen5 LTSSM and link-training evidence review
---

<section class="reference-hero">

# PCIe Gen5 LTSSM Contract Reference

LLM-facing wiki for PCIe Gen5 LTSSM, equalization, speed/width negotiation, and RTL evidence review.

<p class="claim-line">
claim_level: required_gate_ready for scoped link-training surfaces; advisory_expansion for diagnostics; full PCIe protocol compliance is not claimed.
</p>

<div class="reference-actions">
  <a href="en/specs/index.md" class="reference-action primary">Specification Library</a>
  <a href="en/consumer-integration.md" class="reference-action">Consumer Integration</a>
  <a href="en/verification-status.md" class="reference-action">Verification Status</a>
</div>

</section>

## Wiki Goal

This wiki exists to make the PCIe Gen5 contract usable by reviewers, RTL teams, and LLM agents without turning partial evidence into full-protocol claims.

It provides:

- a governed surface map for required and advisory PCIe review slices
- stable entry points for LTSSM/link-training evidence review
- consumer rules for downstream RTL repositories
- machine-readable references for contract, fixture, and manifest tooling
- claim boundaries that prevent LLMs from inventing unverified PCIe behavior

## Primary References

<div class="reference-grid">
  <a class="reference-card" href="en/specs/required/spec-ltssm-state-transitions.md">
    <strong>LTSSM State Transitions</strong>
    <span>Required gate for legal state movement and final-state evidence.</span>
  </a>
  <a class="reference-card" href="en/specs/required/spec-link-equalization-rules.md">
    <strong>Equalization Rules</strong>
    <span>Required gate for Gen5 equalization completion and lane evidence.</span>
  </a>
  <a class="reference-card" href="en/specs/required/spec-speed-width-negotiation.md">
    <strong>Speed & Width Negotiation</strong>
    <span>Required gate for negotiated speed, width, downtrain, and fallback rationale.</span>
  </a>
  <a class="reference-card" href="en/specs/spec-contract-mapping.md">
    <strong>Contract Mapping</strong>
    <span>Surface-to-source routing for all required and advisory pages.</span>
  </a>
  <a class="reference-card" href="en/specs/spec-surface-matrix.md">
    <strong>Surface Matrix</strong>
    <span>One-page table of claim level, fixture suite, gate use, and status.</span>
  </a>
  <a class="reference-card" href="en/specs/spec-coverage-audit.md">
    <strong>Coverage Audit</strong>
    <span>Index and mapping alignment report for the published spec pages.</span>
  </a>
</div>

## Surface Map

| Group | Surfaces | Gate meaning |
| --- | --- | --- |
| Required | `pcie-ltssm`, `pcie-eq`, `pcie-link-negotiation` | May block required RTL evidence review when fixture evidence supports the claim |
| Advisory | `pcie-pm`, `pcie-aer`, `pcie-dll`, `pcie-tlp`, `pcie-hotplug`, `pcie-cfgspace` | Review and diagnostic context only |
| Artifacts | mapping, schema, manifest, glossary, release notes | Traceability and machine-readable consumption support |

## Read Path

1. Start with [Specification Library](en/specs/index.md) to choose the matching surface.
2. Open [Contract Mapping](en/specs/spec-contract-mapping.md) to trace the source document.
3. Check [Verification Status](en/verification-status.md) before using any gate result.
4. Apply [Consumer Integration](en/consumer-integration.md) before wiring a downstream RTL repo.
5. Use [Evidence Grid](en/evidence-grid.md) to anchor every claim to files and smoke output.

## Boundary

This reference is a governed contract wiki. It does not claim full PCIe compliance, vendor RTL correctness, PCI-SIG certification status, driver behavior, firmware policy, or runtime silicon behavior.

The safest interpretation is: required surfaces can support scoped link-training review; advisory surfaces explain related evidence and risks.
