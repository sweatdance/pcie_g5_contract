---
title: PCIe Gen5 LTSSM Contract Reference
description: Topic index for governed PCIe Gen5 LTSSM and link-training evidence review
---

# PCIe Gen5 LTSSM Contract Reference

> Scope: this wiki is a governed topic index for PCIe Gen5 LTSSM, equalization, speed/width negotiation, and downstream RTL evidence review.

claim_level: `required_gate_ready` for scoped link-training surfaces, `advisory_expansion` for diagnostic surfaces, full PCIe protocol compliance not claimed.

## Wiki Goal

This wiki helps reviewers, RTL teams, and LLM agents find the correct PCIe contract topic before making a claim.

It exists to answer five practical questions:

- Which PCIe surface is being discussed?
- Is the surface required-gate, advisory, or not claimed?
- Which source document defines the rule boundary?
- Which fixture or smoke output can support the answer?
- What must an LLM or downstream CI consumer avoid claiming?

## Required Link-Training Topics

These pages are the hard-gate contract entry points for scoped RTL evidence review.

| Topic | Description |
| --- | --- |
| [LTSSM State Transitions](en/specs/required/spec-ltssm-state-transitions.md) | Legal LTSSM movement, final-state evidence, illegal-transition checks |
| [LTSSM Checklist](en/specs/required/spec-ltssm-checklist.md) | Reviewer checklist for LTSSM evidence completeness |
| [Equalization Rules](en/specs/required/spec-link-equalization-rules.md) | Equalization phase completion, lane failure handling, Gen5 link-training evidence |
| [Speed & Width Negotiation](en/specs/required/spec-speed-width-negotiation.md) | Negotiated speed, negotiated width, downtrain status, fallback rationale |
| [Recovery and Fallback](en/specs/required/spec-recovery-and-fallback.md) | Recovery visibility, fallback reason, retrain handling |

## Advisory PCIe Topics

These pages support investigation and review notes. They are not required gates by default.

| Topic | Description |
| --- | --- |
| [Power Management](en/specs/advisory/spec-power-management.md) | L-state and D-state context for link-training review |
| [AER Rules](en/specs/advisory/spec-aer-rules.md) | Error reporting, AER logging, recovery triage |
| [DLL Rules](en/specs/advisory/spec-dll-rules.md) | DLLP and data-link-layer diagnostic context |
| [TLP Rules](en/specs/advisory/spec-tlp-rules.md) | Transaction-layer review context and non-gate evidence |
| [Hot-Plug Rules](en/specs/advisory/spec-hotplug-rules.md) | Surprise-removal, insertion timing, enumeration interaction |
| [Config Space](en/specs/advisory/spec-config-space.md) | VID/DID reads, BAR sizing, command register and enumeration checks |

## Reference & Governance

Use these pages to understand how the topics are mapped, verified, and consumed.

| Topic | Description |
| --- | --- |
| [Specification Library](en/specs/index.md) | Complete required, advisory, and artifact page index |
| [Contract Mapping](en/specs/spec-contract-mapping.md) | Maps source documents to governed contract surfaces |
| [Spec Surface Matrix](en/specs/spec-surface-matrix.md) | One-page claim-level and fixture-suite matrix |
| [Verification Status](en/verification-status.md) | Current evidence posture and required/advisory maturity |
| [Consumer Integration](en/consumer-integration.md) | Downstream RTL integration contract and command sequence |
| [Evidence Grid](en/evidence-grid.md) | Claim-to-artifact and smoke-output mapping |
| [JSON Report Schema](en/specs/spec-json-report-schema.md) | Machine-readable smoke and fixture report fields |
| [Glossary](en/glossary-and-mapping.md) | Terminology used by this contract and LLM-facing docs |
| [Coverage Audit](en/specs/spec-coverage-audit.md) | Current page/index/mapping alignment report |

## Important Boundary

This reference is a governed contract wiki, not a PCI-SIG certification claim and not a full PCIe protocol handbook.

Required surfaces can support scoped link-training review. Advisory surfaces explain related evidence and risks. Anything outside those surfaces is `not_claimed` unless a future contract version explicitly adds it.
