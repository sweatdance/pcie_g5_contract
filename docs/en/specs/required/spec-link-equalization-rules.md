---
title: Equalization Rules
description: Required-scope equalization completion and link-training evidence
---

# Equalization Rules

## Status

- Contract surface: `pcie-eq`
- Claim level: `required_gate_ready`
- Source completeness: **required page**

## Scope

- Keeps equalization completion and phase status reviewer-safe.
- Required for nominal gen-up claims in this repository.

## Canonical

- Required source: [`PCIE5_LINK_EQUALIZATION_RULES.md`](../../../PCIE5_LINK_EQUALIZATION_RULES.md)
- Mapping entry: [`PCIE5_SPEC_TO_CONTRACT_MAPPING.md` Slice 2](../../../PCIE5_SPEC_TO_CONTRACT_MAPPING.md)
- Related required speed context: [`spec-speed-width-negotiation.md`](spec-speed-width-negotiation.md)

## Evidence fields

- `equalization_complete`
- `equalization_phase_summary.completed_phases`
- `equalization_phase_summary.failed_phases`
- `lane_failures`

## Validation

- Fixture suite: `pcie-eq`
- Run command: `python scripts/run_fixture_smoke.py --suite pcie-eq --format json`
- Required smoke: `python scripts/run_regression_smoke.py --suite required --format json`

## Decision guardrails

- Equalization failure must be explicit even if recovery still produces an L0 state.
- Unresolved lane failure summaries prevent hard required-gate completion.
- Use advisory review if phase-level evidence is partial.

## Decision guidance

- This page is required-gate relevant only when equalization is expected for the negotiated link path.
- Do not treat `equalization_complete = true` as final success if any failed phase remains unexplained.
- Route unresolved equalization issues to advisory-only notes and block required-gate closure until rationale is present.

## Required evidence checks

### Pass condition

- `equalization_complete` is present.
- `equalization_phase_summary.completed_phases` contains required stages.
- `lane_failures` is empty or explained by explicit downtraining rationale.

### Fail condition

- Incomplete or missing equalization completion marker.
- Failed phase not reconciled in `lane_failures`.
- Unknown downtraining reasons with `equalization_complete = true`.

### Failure pattern examples

| Pattern | Detection field | Meaning | Suggested action |
| --- | --- | --- | --- |
| Empty failure list with downtrained | `lane_failures` | Partial signal quality acceptance | Require explicit fallback reason |
| Missing phase summary | `equalization_phase_summary` | Coverage blind spot | Re-run fixture in EQ-observed mode |
| Equalization pass with warning counters | `equalization_phase_summary.failed_phases` | Incomplete negotiation | Keep required-gate as blocked |

## Consumer response template
```markdown
--8<-- "../snippets/required-decision-response-template.txt"
```

```json
{
  "slice": "pcie-eq",
  "claim_level": "required_gate_ready",
  "result": "satisfied|blocked",
  "required_fields": [
    "equalization_complete",
    "equalization_phase_summary.completed_phases",
    "lane_failures"
  ]
}
```
