---
title: Config Space
description: Advisory configuration-space access and enumeration boundary
---

# Config Space

## Status

- Contract surface: `pcie-cfgspace`
- Claim level: `advisory_expansion`
- Source completeness: **advisory page**

## Scope

- VID/DID enumeration checks, BAR probe sequence, command register readiness, and extended capability walks.
- Warn-only posture in this contract profile unless consumer explicitly promotes.

## Canonical

- Required source: [`PCIE5_CONFIG_SPACE.md`](../../../PCIE5_CONFIG_SPACE.md)
- Mapping entry: [`PCIE5_SPEC_TO_CONTRACT_MAPPING.md` Slice 6](../../../PCIE5_SPEC_TO_CONTRACT_MAPPING.md)
- Rule IDs: `PCIE5-CFG-001` .. `PCIE5-CFG-005`

## Key fields to inspect

- `vidpid_read_observed`
- `vidpid_value`
- `bar_sizing_observed`
- `enumeration_sequence_complete`
- `link_control_read_before_write`
- `bus_master_enabled`

## Validation

- Fixture suite: `pcie-cfgspace`
- Run command: `python scripts/run_fixture_smoke.py --suite pcie-cfgspace --format json`
- Regression path: `python scripts/run_regression_smoke.py --suite advisory --format json`

## Decision guidance

- Advisory-only boundary here: use for consumer diagnostics, not for required-gate closure.
- Incomplete enumeration evidence means hard caution even if other required slices are nominal.

## Advisory evidence checks

### Pass condition

- VID/PID and BAR discovery fields are present.
- Enumeration sequence is complete and deterministic.
- Register read/write ordering matches expected sequence in command fields.

### Fail condition

- Read-only path has no completion markers.
- BAR readiness not established before link-up dependent operations.
- Enumeration sequence incomplete while required fixtures are nominal.

### Failure pattern examples

| Pattern | Detection field | Meaning | Suggested action |
| --- | --- | --- | --- |
| Missing enumeration sequence | `enumeration_sequence_complete` | CFG path incomplete | Add fixture trace and rerun |
| BAR not ready | `bar_sizing_observed` | Device exposure risk | Validate BAR probing order |
| Read-before-write skip | `link_control_read_before_write` | Hidden mis-sequencing | Keep advisory warning and inspect logs |


## Advisory failure playbook
- Use the shared triage policy and payload format: [Advisory Failure Playbook](../spec-advisory-failure-playbook.md)

## Consumer response template

```markdown
--8<-- "../snippets/advisory-decision-response-template.txt"
```

```json
{
  "slice": "pcie-cfgspace",
  "claim_level": "advisory_expansion",
  "result": "review_only",
  "required_fields": [
    "vidpid_read_observed",
    "bar_sizing_observed",
    "enumeration_sequence_complete",
    "link_control_read_before_write"
  ],
  "usage": "cfg_sequence_investigation"
}
```
