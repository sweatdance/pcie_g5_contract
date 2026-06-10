---
title: Specification Library
description: Complete PCIe 5.x surface coverage map, with required and advisory slices.
---

# Specification Library

This section mirrors a full-reference navigation pattern and exposes every PCIe 5.x governance document surface available in this repo.

## Navigation guidance

- Required scope for hard gate starts here.
- Advisory scope stays contextual unless downstream policy explicitly promotes it.
- Use artifact pages for evidence schema, scope matrix, and integration contract.

<section class="hero-shell">

### Portal entry cards

<div class="hero-tags">
  <span class="hero-tag">Required-first review</span>
  <span class="hero-tag">Advisory context</span>
  <span class="hero-tag">Schema + evidence maps</span>
</div>

<div class="hero-tiles">
  <div class="hero-card">
    Start from **Required** pages for LTSSM/EQ/Link-negotiation gate decisions.
  </div>
  <div class="hero-card">
    Use **Advisory** pages for diagnostics, errors, and triage investigation.
  </div>
  <div class="hero-card">
    Use **Artifacts** for contract mapping, schema, glossary, and release traceability.
  </div>
</div>

</section>

## Library map

## Required scope

- [LTSSM State Transitions](required/spec-ltssm-state-transitions.md)
- [LTSSM Checklist](required/spec-ltssm-checklist.md)
- [Equalization Rules](required/spec-link-equalization-rules.md)
- [Speed & Width Negotiation](required/spec-speed-width-negotiation.md)
- [Recovery and Fallback](required/spec-recovery-and-fallback.md)

## Advisory scope

- [Power Management](advisory/spec-power-management.md)
- [AER Rules](advisory/spec-aer-rules.md)
- [DLL Rules](advisory/spec-dll-rules.md)
- [TLP Rules](advisory/spec-tlp-rules.md)
- [Hot-Plug Rules](advisory/spec-hotplug-rules.md)
- [Config Space](advisory/spec-config-space.md)

## Governance and reference artifacts

- [Spec-to-Contract Mapping](spec-contract-mapping.md)
- [Spec Surface Matrix](spec-surface-matrix.md)
- [Glossary for LLM](spec-glossary-for-llm.md)
- [JSON Report Schema](spec-json-report-schema.md)
- [Release Notes](spec-release-notes.md)
- [Consumer Integration (contract)](spec-consumer-integration-contract.md)

## Coverage completion

All listed surfaces are reachable from the navigation tree and linked to canonical source artifacts.

- Required pages: done
- Advisory pages: done
- Artifact pages: done
- Source-copy depth: required pages are now expanded with validation entrypoints and decision guidance.

## How to consume this library

- Start in `Required` for LTSSM/link-training gate decisions.
- Use `Advisory` for investigation and root-cause paths.
- Use `Artifacts` when you need boundary references and integration rules.

## Hard-gate readiness matrix

| Surface group | Allowed gate use | Required outputs |
| --- | --- | --- |
| Required | Allowed | `run_regression_smoke.py --suite required` |
| Advisory | Not allowed | `run_regression_smoke.py --suite advisory` |
| Artifacts | Context only | `docs/en/verification-status.md`, `docs/LLM_VERIFICATION_STATUS.md` |

## Consumption sequence

1. Open the matching page under `Required` or `Advisory`.
2. Confirm `claim level` and `required` flags.
3. Read corresponding entrypoint in `Artifacts`.
4. Execute smoke output validation before any hard-gate claim.

## Completion policy

- Do not use advisory pages to close required-gate status.
- Use rule IDs in source specs as the evidence anchor for each review response.
