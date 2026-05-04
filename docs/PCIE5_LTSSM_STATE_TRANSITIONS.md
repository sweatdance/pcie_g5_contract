# PCIe Gen5 LTSSM State Transition Guidance

This contract slice focuses on reviewer-visible evidence that LTSSM progression was legal for the scenario under review.

## Required evidence fields

- `ltssm_final_state`
- `ltssm_trace_summary.visited_states`
- `ltssm_trace_summary.illegal_transition_count`
- `ltssm_trace_summary.reached_recovery`

## Contract rules

- Nominal success claims require final state `L0`.
- Nominal success claims require `illegal_transition_count = 0`.
- The visited-state summary must be explicit enough to distinguish a short partial trace from a converged training path.
- A path that reaches recovery is review-visible even if the final state is `L0`.

## Reviewer prompts

- Did the trace progress through the expected training path for the scenario?
- Is recovery visible, and if so, was it expected?
- Is the report proving stable convergence or only partial progression?
