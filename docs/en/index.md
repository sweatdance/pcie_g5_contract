---
title: PCIe Gen5 LTSSM Contract Wiki
description: English topic index for governed PCIe Gen5 LTSSM and link-training evidence review
hide:
  - toc
---

# PCIe Gen5 LTSSM Contract Wiki

> Scope: this page is the English topic index for the governed PCIe Gen5 LTSSM and link-training contract.

Goal: help consumers find the right contract surface, evidence source, validation command, and claim ceiling before using this repository in RTL review or LLM automation.

## Required Link-Training Topics

These pages are the default hard-gate surfaces in this contract profile.

| Topic | Description |
| --- | --- |
| [LTSSM State Transitions](specs/required/spec-ltssm-state-transitions.md) | LTSSM state legality, final-state evidence, and illegal-transition checks |
| [LTSSM Checklist](specs/required/spec-ltssm-checklist.md) | Reviewer checklist for LTSSM evidence completeness |
| [Equalization Rules](specs/required/spec-link-equalization-rules.md) | Equalization phase completion, lane failures, and Gen5 link-training evidence |
| [Speed & Width Negotiation](specs/required/spec-speed-width-negotiation.md) | Negotiated speed, negotiated width, downtrain status, and fallback rationale |
| [Recovery and Fallback](specs/required/spec-recovery-and-fallback.md) | Recovery visibility, fallback reason, and retrain handling |

## Advisory PCIe Topics

These pages are visible for diagnostics and expansion planning. They do not become required gates unless a future contract version promotes them.

| Topic | Description |
| --- | --- |
| [Power Management](specs/advisory/spec-power-management.md) | L-state and D-state context for link-training review |
| [AER Rules](specs/advisory/spec-aer-rules.md) | Error reporting, AER logging, and recovery triage |
| [DLL Rules](specs/advisory/spec-dll-rules.md) | DLLP and data-link-layer diagnostic context |
| [TLP Rules](specs/advisory/spec-tlp-rules.md) | Transaction-layer review context and non-gate evidence |
| [Hot-Plug Rules](specs/advisory/spec-hotplug-rules.md) | Surprise-removal, insertion timing, and enumeration interaction |
| [Config Space](specs/advisory/spec-config-space.md) | VID/DID reads, BAR sizing, command register, and enumeration checks |

## Reference & Governance

These pages explain how the contract is mapped, verified, exported, and consumed.

| Topic | Description |
| --- | --- |
| [Specification Library](specs/index.md) | Complete required, advisory, and artifact page index |
| [Contract Mapping](specs/spec-contract-mapping.md) | Maps PCIe source documents to governed contract surfaces |
| [Spec Surface Matrix](specs/spec-surface-matrix.md) | One-page claim-level and fixture-suite matrix |
| [Verification Status](verification-status.md) | Current maturity and evidence posture for required/advisory slices |
| [Consumer Integration](consumer-integration.md) | Downstream RTL integration contract and command sequence |
| [Evidence Grid](evidence-grid.md) | Claim-to-artifact and smoke-output mapping |
| [JSON Report Schema](specs/spec-json-report-schema.md) | Machine-readable smoke and fixture report fields |
| [Advisory Failure Playbook](specs/spec-advisory-failure-playbook.md) | Shared triage policy for advisory findings |
| [Version Source Map](version-source-map.md) | PCIe source authority boundaries and version scope |
| [Glossary](glossary-and-mapping.md) | Terminology used by this contract and LLM-facing docs |
| [Coverage Audit](specs/spec-coverage-audit.md) | Current page/index/mapping alignment report |

## Claim Boundary

| Claim class | Meaning | Allowed use |
| --- | --- | --- |
| `required_gate_ready` | Fixture-backed required scope for LTSSM/EQ/link negotiation | Scoped RTL gate decisions |
| `advisory_expansion` | Diagnostic surface with non-blocking evidence | Warnings, triage, and future expansion |
| `not_claimed` | Outside this repository contract | Do not infer or summarize as completed |

This wiki does not claim PCIe full-stack compliance, PCI-SIG certification, driver correctness, runtime silicon behavior, SR-IOV, ATS, DPC, or complete transaction-layer coverage.

## Quick Evidence Commands

```powershell
python scripts/run_regression_smoke.py --suite required --format json
python scripts/run_fixture_smoke.py --suite required --format json
python scripts/run_regression_smoke.py --suite all --format json
```

Use `--suite required` before making a hard-gate statement. Use `--suite advisory` or `--suite all` only to add non-blocking diagnostic context.
