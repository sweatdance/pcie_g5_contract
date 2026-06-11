---
title: Version Source Map
description: PCIe source authority boundaries and version scope for this contract wiki
---

# Version Source Map

> This page maps PCIe source authority boundaries. It does not reproduce PCI-SIG specification text.

## Purpose

- Identify which PCIe version and review source each contract surface belongs to.
- Distinguish public contract summaries from internal normative review artifacts.
- Prevent LLM or downstream RTL consumers from upgrading advisory text into compliance truth.

## Source categories

| Category | Authority level | Usage |
| --- | --- | --- |
| PCI-SIG Base Specification access | `normative_internal` | Primary source for PCIe 5.0 semantics; do not reproduce text publicly |
| PCI-SIG ECNs / errata | `normative_internal` | Version-specific deltas and corrections |
| Internal review packets | `governed_internal` | Evidence packets and reviewer decisions |
| Public contract pages | `contract_summary` | Claim boundary, evidence routing, non-claims |
| Community references | `context_only` | Helpful background, never normative alone |

## Version summary

| Version / surface | Contract use | Boundary |
| --- | --- | --- |
| PCIe 5.0 LTSSM | required | scoped link-training evidence |
| Gen5 equalization | required | phase completion and lane evidence |
| Speed/width negotiation | required | negotiated result and fallback rationale |
| Recovery/fallback | required | visibility and rationale for scoped link-training claims |
| PM / AER / DLL / TLP / Hot-Plug / Config Space | advisory | diagnostic visibility only |

## Public-source rule

This wiki may summarize governed contract behavior, validation routing, and claim boundaries. It must not quote or reconstruct proprietary PCI-SIG specification text.

If a downstream reviewer needs normative wording, they must use their authorized PCI-SIG access path and keep that review separate from public wiki content.

## LLM use rule

An LLM or agent may cite this page for authority boundaries only. It must not infer:

- full PCIe protocol completion
- PCI-SIG certification readiness
- silicon runtime behavior
- driver or firmware correctness
- unlisted version support beyond this contract
