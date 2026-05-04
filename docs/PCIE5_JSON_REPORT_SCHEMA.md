# PCIe Gen5 LTSSM JSON Report Schema

This contract expects post-task evidence in a JSON object under `checks.pcie_ltssm_report`.

## Required keys

- `schema_version`: string
- `target_speed_gtps`: number
- `negotiated_speed_gtps`: number
- `target_width`: integer
- `negotiated_width`: integer
- `ltssm_final_state`: string
- `ltssm_trace_summary`: object
- `equalization_complete`: boolean
- `equalization_phase_summary`: object
- `lane_failures`: array
- `downtrained`: boolean
- `recovery_triggered`: boolean

## Optional keys

- `scenario`: string
- `topology`: string
- `retry_count`: integer
- `fallback_reason`: string
- `recovery_reason`: string
- `degraded_width_expected`: boolean
- `degraded_width_reason`: string
- `notes`: array of strings

## Required nested keys

- `ltssm_trace_summary.visited_states`: array of strings
- `ltssm_trace_summary.illegal_transition_count`: integer
- `ltssm_trace_summary.reached_recovery`: boolean
- `equalization_phase_summary.completed_phases`: array of strings
- `equalization_phase_summary.failed_phases`: array of strings

## Example

```json
{
  "schema_version": "1.0",
  "scenario": "x16_root_complex_to_endpoint_nominal",
  "target_speed_gtps": 32.0,
  "negotiated_speed_gtps": 32.0,
  "target_width": 16,
  "negotiated_width": 16,
  "ltssm_final_state": "L0",
  "ltssm_trace_summary": {
    "visited_states": ["Detect", "Polling", "Configuration", "Recovery", "L0"],
    "illegal_transition_count": 0,
    "reached_recovery": true
  },
  "equalization_complete": true,
  "equalization_phase_summary": {
    "completed_phases": ["phase0", "phase1", "phase2", "phase3"],
    "failed_phases": []
  },
  "retry_count": 0,
  "downtrained": false,
  "recovery_triggered": false,
  "degraded_width_expected": false,
  "lane_failures": [],
  "notes": ["nominal training path"]
}
```

## Interpretation rules

- `ltssm_final_state` must be `L0` for a passing nominal training result.
- `ltssm_trace_summary.illegal_transition_count` must be `0` for a passing nominal training result.
- `negotiated_speed_gtps` must match `target_speed_gtps` for nominal Gen5 success.
- `negotiated_width` must match `target_width` unless the report explicitly marks an expected degraded-width scenario.
- `downtrained = true` requires fallback context and must not be presented as a clean nominal Gen5 result.
- `recovery_triggered = true` is review-visible even when the final state is `L0`.
- Non-empty `lane_failures` requires explanation even if the overall run is not blocked.
