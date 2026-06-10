---
title: Release Notes
description: Spec-facing release milestones and governance checkpoints
---

# Release Notes

## Status

- Type: artifact index
- Source completeness: source-linked page

## Purpose

- Track when governance surface additions affect downstream behavior.
- Keep completion claims traceable across versions.

## Sources

- [`CHANGELOG.md`](../../../CHANGELOG.md)

## Highlights by release

| Release | Area |
|---|---|
| v0.11.2 | Strengthened spec-library governance navigation, hard-gate guidance, term-to-evidence mappings. |
| v0.11.1 | Boundary discipline and claim-ceiling correction for completed/advisory split. |
| v0.11.0 | Expanded PM/AER/DLL/TLP/CFG/Hot-Plug evidence coverage and fixture set. |
| v0.10.0 | Added CFG/PM/AER/TLP/DLL/Hot-Plug baseline protocol slices. |
| v0.9.0 | First full-protocol expansion with advisory hard-stop/warn split and manifest updates. |
| v0.3.0 | Initial governed LTSSM link-training baseline contract surface. |

## Evidence impact

- `docs/en/specs/index.md`: hard-gate marker and consume sequence added.
- `docs/en/specs/spec-contract-mapping.md`: explicit mapping-table and routing rule.
- `docs/en/specs/spec-glossary-for-llm.md`: surface-to-term map and response schema fragment.

## Consumption rule

- Completion statements must use evidence-backed sources.
- Claims about status boundary changes should first be checked against `docs/LLM_VERIFICATION_STATUS.md` and `docs/en/verification-status.md`.
