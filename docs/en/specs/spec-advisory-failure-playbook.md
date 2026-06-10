---
title: Advisory Failure Playbook
description: Shared triage and non-gating policy for advisory PCIe slices
---

# Advisory Failure Playbook

## Scope

- This page is for advisory-only slices in this repo: `pcie-pm`, `pcie-aer`, `pcie-dll`, `pcie-tlp`, `pcie-hotplug`, `pcie-cfgspace`.
- It standardizes escalation and response formats for review context.

## Canonical

- `contract.yaml` claim surface for advisory routes
- Source slices in root `docs/` spec pages
- Fixture routing in `fixtures/fixture_manifest.json`

## Validation

- Advisory smoke command:

```powershell
python scripts/run_regression_smoke.py --suite advisory --format json
```

- Fixture routing command:

```powershell
python scripts/run_fixture_smoke.py --suite all --format json
```

- Evidence for a triage event should include:
  - suite status
  - `advisory_issues`
  - `advisory_findings[]`
  - related `rule_id`s

## Decision guidance

- Advisory slices are never hard-gates unless a downstream policy explicitly promotes them.
- A required gate can be `pass` while advisory is failing; this is `warn` not `blocked`.
- Missing advisory evidence downgrades documentation confidence, but does not auto-block required gates.
- Keep each advisory finding paired with a concrete fixture/rule identifier.

## Advisory failure taxonomy

| Severity | Typical signal | Next step |
| --- | --- | --- |
| critical | Required-surface invariant missing in advisory correlation | Add fixture context + route to platform triage |
| high | Repeated surprise or malformed packet class in advisory-only suite | Create advisory issue with rule-level evidence bundle |
| medium | Single isolated warning with full logging | Annotate as observation + monitor |
| low | Soft anomaly with stable counters | Track trend in next smoke cycle |

## Standard consumer response payload

Use this for all advisory-only triage records.

```json
{
  "scope": "advisory",
  "surface": [
    "pcie-aer",
    "pcie-pm",
    "pcie-dll",
    "pcie-tlp",
    "pcie-hotplug",
    "pcie-cfgspace"
  ],
  "claim_level": "advisory_expansion",
  "status": "warn|review_only",
  "blocking": false,
  "required_overlap": "none",
  "finding_count": 0,
  "findings": [
    {
      "slice": "pcie-aer",
      "rule_id": "PCIE5-AER-001",
      "severity": "high",
      "message": "surprise-down observed without matching logging envelope",
      "remediation_hint": "capture one additional regression cycle with explicit root-cause fixture"
    }
  ],
  "evidence": [
    "scripts/run_regression_smoke.py --suite advisory --format json",
    "scripts/run_fixture_smoke.py --suite all --format json",
    "fixtures/fixture_manifest.json"
  ]
}
```

## Related advisory surfaces

- [Power Management](advisory/spec-power-management.md)
- [AER Rules](advisory/spec-aer-rules.md)
- [DLL Rules](advisory/spec-dll-rules.md)
- [TLP Rules](advisory/spec-tlp-rules.md)
- [Hot-Plug Rules](advisory/spec-hotplug-rules.md)
- [Config Space](advisory/spec-config-space.md)
