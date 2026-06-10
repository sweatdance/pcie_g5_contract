---
title: Spec Coverage Audit
description: Auto-generated coverage audit for spec-to-contract mapping completeness
---

# Spec Coverage Audit

Generated: 2026-06-10T07:50:47Z

## Status

- Type: audit report
- Claim level: governance reference (not a surface gate)
- Source completeness: **auto-generated**

## Canonical

- Source manifests: [`PCIE5_SPEC_TO_CONTRACT_MAPPING.md`](../../PCIE5_SPEC_TO_CONTRACT_MAPPING.md), [`docs/en/specs/index.md`](index.md)
- Coverage authority: [`spec-contract-mapping.md`](spec-contract-mapping.md)

## Spec-to-contract mapping coverage

- Mapping rows: 11
- Missing mapped surface page targets: none

## Spec index coverage

- Required pages on disk: 5
- Advisory pages on disk: 6
- Total spec pages on disk: 11
- Total pages listed in index: 11
- Missing in index: none
- Extra in index: none

## Claim-class split status

- Required surfaces expected in pages: pcie-ltssm, pcie-eq, pcie-link-negotiation, pcie-ltssm(recovery)
- Advisory surfaces expected in pages: pcie-pm, pcie-aer, pcie-dll, pcie-tlp, pcie-hotplug, pcie-cfgspace

## Validation

- Regenerate audit: `python scripts/audit_spec_coverage.py --format md > docs/en/specs/spec-coverage-audit.md`
- Cross-check index completeness: compare `index.md` Library map against files on disk

## Decision guidance

- Missing mapped surface page targets block new required-gate claims until a page is created.
- Advisory page count below 6 or required below 5 should trigger a spec gap review.
- "Extra in index" entries indicate stale navigation — remove before next release cut.

## Related

- [`spec-contract-mapping.md`](spec-contract-mapping.md) — canonical surface routing table
- [`spec-glossary-for-llm.md`](spec-glossary-for-llm.md) — term definitions
- [`spec-surface-matrix.md`](spec-surface-matrix.md) — full surface decision matrix
