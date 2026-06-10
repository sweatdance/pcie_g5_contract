---
title: Glossary for LLM
description: Terms and surface-language alignment for PCIe contract review
---

# Glossary for LLM

## Status

- Type: artifact index
- Source completeness: source-linked page

## Purpose

- Keep response phrasing consistent with this repository's claim levels.
- Prevent over-claiming of "completed" across advisory slices.

## Core terms

- **required_gate_ready**: verified and suitable for required-gate posture.
- **advisory_expansion**: implemented for review visibility, not default required evidence.
- **not_claimed**: present but not in this contract boundary.
- **fixture**: deterministic smoke input/output case used by this repo.
- **surprise down**: topology loss without formal removal sequence.
- **hard_stop**: evidence condition that blocks completed claims for required scope.
- **warn**: evidence condition that requires operator review but does not convert advisory evidence into required completeness.

## Claim semantics mapping

| Source term | LLM term | Meaning |
|---|---|---|
| `complete` | `required_gate_ready` | This scope can contribute to hard-stop contract decisions. |
| `advisory` | `advisory_expansion` | This scope is visible for triage, not for required completion. |
| `hard_stop` | `hard_stop` | Failing this condition blocks required-gate success. |
| `warn` | `warn` | Failing this condition raises review-level caution. |
| `non_claim` | `not_claimed` | Must not be asserted in protocol completion responses. |

## Decision vocabulary

- `advisory_expansion` pages must not be collapsed into `required_gate_ready`.
- `required_gate_ready` is scoped to `pcie-ltssm`, `pcie-eq`, `pcie-link-negotiation`, and recovery visibility.
- `not_claimed` is the correct label for statements outside this repo boundary.

## Source mapping

- Canonical source: [`PCIE5_GLOSSARY_FOR_LLM.md`](../../../PCIE5_GLOSSARY_FOR_LLM.md)
- Contract alignment: [`spec-contract-mapping.md`](spec-contract-mapping.md)
