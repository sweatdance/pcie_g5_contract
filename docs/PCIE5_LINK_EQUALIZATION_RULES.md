# PCIe Gen5 Link Equalization Rules

This contract slice makes equalization reviewer-visible without embedding full spec prose.

## Required evidence fields

- `equalization_complete`
- `equalization_phase_summary.completed_phases`
- `equalization_phase_summary.failed_phases`
- `lane_failures`

## Contract rules

- Nominal Gen5 success claims require `equalization_complete = true`.
- Failed equalization phases must be explicit, even when the run later recovers.
- Non-empty lane failure summaries require reviewer attention and explanation.

## Reviewer prompts

- Which phases completed, and which failed?
- Are lane failures transient, expected, or unexplained?
- Is the report claiming Gen5 success despite incomplete equalization evidence?
