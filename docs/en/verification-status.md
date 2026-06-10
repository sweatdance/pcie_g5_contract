---
title: Verification Status
description: Evidence posture and governance boundary by contract slice
---

# Verification Status

This page summarizes current contract maturity and evidence boundaries for AI/agent consumption.

## Latest evidence summary

- Scope model: required slices are the only hard gate inputs; advisory slices are review context.
- Required hard gate slices: `pcie-ltssm`, `pcie-eq`, `pcie-link-negotiation`.
- Advisory-only slices: `pcie-pm`, `pcie-aer`, `pcie-dll`, `pcie-tlp`, `pcie-hotplug`, `pcie-cfgspace`.
- Canonical status source: `LLM_VERIFICATION_STATUS.md` in repository root.

## Current scope stance

- Required slice set: `pcie-ltssm`, `pcie-eq`, `pcie-link-negotiation`
- Advisory slice set: `pcie-pm`, `pcie-aer`, `pcie-dll`, `pcie-tlp`, `pcie-hotplug`, `pcie-cfgspace`

## Fixture reality

- Use `artifacts/validation/*` and `fixtures/fixture_manifest.json` as source-of-truth.
- Keep advisory counts visible as advisory-only even when fixtures exist.
- Fixture routing and smoke outputs are the only evidence anchor for this site; maturity updates are declared only after evidence refresh.

## Contract decision outputs

### Required scope output

- `required` suite outcome determines CI gate status.
- Required output must provide:
  - `overall_status = pass`
- Any required-surface failure blocks required-gate acceptance.

### Advisory scope output

- Advisory suites are used for triage and debugging only.
- Advisory failures must be surfaced to reviewers with severity tags.
- Advisory output never overrides required pass/fail for CI unless a downstream policy explicitly reclassifies.

## Verification entry matrix

| Use case | Command | Expected consumer behavior |
| --- | --- | --- |
| Required CI gate | `python scripts/run_regression_smoke.py --suite required --format json` | Assert gate pass only from `pcie-ltssm` / `pcie-eq` / `pcie-link-negotiation` |
| Advisory review | `python scripts/run_regression_smoke.py --suite advisory --format json` | Aggregate warnings and route to investigation |
| Full traceability | `python scripts/run_regression_smoke.py --suite all --format json` | Persist evidence artifact and trace all surface outcomes |
| Fixture audit | `python scripts/run_fixture_smoke.py --suite all --format json` | Validate fixture routing and expected fixture match counts |

## Governance visibility

- `docs/LLM_VERIFICATION_STATUS.md` is the canonical status companion file in-repo.
- `runtime` smoke output JSON should be treated as evidence for gating behavior, not prose-only claims.
