---
title: Evidence Grid
description: Evidence matrix for required and advisory contract slices
---

# Evidence Grid

This page summarizes where each proof path lives and how to consume it.

## Evidence by slice

## Surface classes

| Surface | Evidence type | Evidence file | Scope | Required output | Advisory output |
| --- | --- | --- | --- | --- | --- |
| LTSSM | required | `fixtures/fixture_manifest.json` + `artifacts/validation/*` | required | gate-relevant | review context |
| EQ | required | `fixtures/fixture_manifest.json` + `artifacts/validation/*` | required | gate-relevant | review context |
| Link negotiation | required | `fixtures/fixture_manifest.json` + `artifacts/validation/*` | required | gate-relevant | review context |
| PM | advisory | `artifacts/validation/*` + PM fixture entries | advisory | non-gating | triage |
| AER | advisory | `artifacts/validation/*` + AER fixture entries | advisory | non-gating | triage |
| DLL | advisory | `artifacts/validation/*` + DLL fixture entries | advisory | non-gating | triage |
| TLP | advisory | `artifacts/validation/*` + TLP fixture entries | advisory | non-gating | triage |
| Hot-Plug | advisory | `artifacts/validation/*` + Hot-Plug fixture entries | advisory | non-gating | triage |
| CFG space | advisory | `artifacts/validation/*` + cfgspace fixture entries | advisory | non-gating | triage |

## Evidence fields by scope

- Required core fields:
  - `overall_status`
  - `overall_passed`
  - `matched_count`
  - `total_checks`
  - `suites[].status`
- Required gate hard-stop fields:
  - `matched_count == total_checks` (within required scope)
  - `suites` includes `pcie-ltssm`, `pcie-eq`, `pcie-link-negotiation` with `status = pass`
- Advisory-only risk fields:
  - `advisory_issues`
  - `advisory_findings[]`
  - `severity`

## Required workflow

- Run `run_fixture_smoke.py --suite required --format json` for gate-surface verification.
- Run `run_regression_smoke.py --suite required --format json` for contract claim alignment.
- Keep advisory suites visible, but do not mix into required gate decisions.

## Consumption snippets

### Required gate snippet

```json
{
  "suites": ["pcie-ltssm", "pcie-eq", "pcie-link-negotiation"],
  "overall_status": "pass",
  "overall_passed": true
}
```

### Advisory review snippet

```json
{
  "suite": "pcie-hotplug",
  "status": "warn",
  "advisory_issues": 2,
  "severity": "medium"
}
```

## Non-claims

- Advisory evidence visibility does not imply full protocol compliance.
- Missing final-state fields or mismatched fixture routing must not be used to close required gates.
