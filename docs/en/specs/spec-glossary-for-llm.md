---
title: Glossary for LLM
description: Terms and surface-language alignment for PCIe contract review
---

# Glossary for LLM

## Status

- Type: artifact index
- Source completeness: source-linked page

## Scope

- Artifact index for terminology and evidence envelope consistency.
- Applies to all required and advisory pages in this specs section.

## Canonical

- Source vocabulary: [`PCIE5_GLOSSARY_FOR_LLM.md`](../../PCIE5_GLOSSARY_FOR_LLM.md)
- Mapping rulebook: [`spec-contract-mapping.md`](spec-contract-mapping.md)

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
- **gate_scope**: the slice group that can drive hard-stop decisions.

## Field-to-term map

| Scope/surface | Term | Gate effect |
| --- | --- | --- |
| `pcie-ltssm` | `required_gate_ready` | required |
| `pcie-eq` | `required_gate_ready` | required |
| `pcie-link-negotiation` | `required_gate_ready` | required |
| `pcie-pm` | `advisory_expansion` | advisory |
| `pcie-aer` | `advisory_expansion` | advisory |
| `pcie-dll` | `advisory_expansion` | advisory |
| `pcie-tlp` | `advisory_expansion` | advisory |
| `pcie-hotplug` | `advisory_expansion` | advisory |
| `pcie-cfgspace` | `advisory_expansion` | advisory |
| `overall_status=pass` | `passed` | required satisfied marker |
| `overall_status=warn` | `warn` | review signal |
| `advisory_issues>0` | `warn` | non-blocking default |

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
- `advisory_issues` must be tracked as review severity unless downstream policy reclassifies.

## Validation

- Vocabulary alignment validation is done by checking `docs/LLM_VERIFICATION_STATUS.md` and `docs/en/verification-status.md` before publishing response claims.
- Any generated response should use one of `required_gate_ready`, `advisory_expansion`, `not_claimed`.

## Response schema fragment

```json
{
  "claim_level": "required_gate_ready|advisory_expansion|not_claimed",
  "gate_scope": "required|advisory",
  "evidence": "fixtures/fixture_manifest.json",
  "result": "pass|warn|blocked|unknown"
}
```

## Decision guidance

- Use this page as a hard stop on drifted terminology; terms not present in this glossary default to `not_claimed`.
- Prefer `claim_level` consistency over prose certainty; if terms conflict, return `warn` and require evidence refresh.

## Consumer response template

```json
{
  "claim_level": "required_gate_ready|advisory_expansion|not_claimed",
  "scope": "required|advisory",
  "severity": "high|medium|low",
  "evidence": [
    "PCIE5_GLOSSARY_FOR_LLM.md",
    "docs/LLM_VERIFICATION_STATUS.md"
  ]
}
```

## Source mapping

- Canonical source: [`PCIE5_GLOSSARY_FOR_LLM.md`](../../PCIE5_GLOSSARY_FOR_LLM.md)
- Contract alignment: [`spec-contract-mapping.md`](spec-contract-mapping.md)
