---
title: Evidence Grid
description: Evidence matrix for required and advisory contract slices
---

# Evidence Grid

This page summarizes where each proof path lives and how to consume it.

## Surface classes

| Surface | Evidence type | Evidence file | Scope |
| --- | --- | --- | --- |
| LTSSM | required | `fixtures/fixture_manifest.json` + `artifacts/validation/*` | required |
| EQ | required | `fixtures/fixture_manifest.json` + `artifacts/validation/*` | required |
| Link negotiation | required | `fixtures/fixture_manifest.json` + `artifacts/validation/*` | required |
| PM | advisory | `artifacts/validation/*` + PM fixture entries | advisory |
| AER | advisory | `artifacts/validation/*` + AER fixture entries | advisory |
| DLL | advisory | `artifacts/validation/*` + DLL fixture entries | advisory |
| TLP | advisory | `artifacts/validation/*` + TLP fixture entries | advisory |
| Hot-Plug | advisory | `artifacts/validation/*` + Hot-Plug fixture entries | advisory |
| CFG space | advisory | `artifacts/validation/*` + cfgspace fixture entries | advisory |

## Required workflow

- Run `run_fixture_smoke.py --suite required --format json` for gate-surface verification.
- Run `run_regression_smoke.py --suite required --format json` for contract claim alignment.
- Keep advisory suites visible, but do not mix into required gate decisions.

## Non-claims

- Advisory evidence visibility does not imply full protocol compliance.
- Missing final-state fields or mismatched fixture routing must not be used to close required gates.
