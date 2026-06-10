---
title: Release Notes
description: Spec-facing release milestones and governance checkpoints
---

# Release Notes

## Status

- Type: artifact index
- Source completeness: source-linked page

## Scope

- Release-note surface for governance behavior and docs/specs portal milestones.

## Canonical

- Base changelog: [CHANGELOG.md](https://github.com/sweatdance/pcie_g5_contract/blob/main/CHANGELOG.md)

## Purpose

- Track when governance surface additions affect downstream behavior.
- Keep completion claims traceable across versions.

## Validation

- Release entries should only be changed with matching `contract.yaml` or fixture/report evidence changes.
- Keep this page synchronized with `docs/en/verification-status.md` and `docs/LLM_VERIFICATION_STATUS.md` when evidence posture changes.

## Sources

- [CHANGELOG.md](https://github.com/sweatdance/pcie_g5_contract/blob/main/CHANGELOG.md)

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

## Decision guidance

- For any release milestone, prefer scoped updates (documentation, schema, fixture, smoke) over broad protocol status language.
- If evidence is not present, place item as pending/planned and avoid marking as closed.

## Consumer response template

```json
{
  "release": "v0.x.x",
  "change_type": "docs|schema|fixture|workflow|policy",
  "evidence_gate": "required|advisory|not_claimed",
  "status": "published|planned|blocked"
}
```
