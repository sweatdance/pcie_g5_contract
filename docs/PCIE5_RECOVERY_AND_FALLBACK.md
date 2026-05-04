# PCIe Gen5 Recovery And Fallback Visibility

This contract slice keeps retrain, recovery, and fallback behavior visible to reviewers.

## Required evidence fields

- `retry_count`
- `recovery_triggered`
- `downtrained`

## Conditionally required evidence fields

- `fallback_reason`
- `recovery_reason`

## Contract rules

- Recovery or retrain behavior must be visible in the report when it occurred.
- Retry counts greater than zero require context.
- Downtraining without a fallback reason is incomplete evidence.

## Reviewer prompts

- Did the run converge only after recovery or retrain?
- Is the fallback reason explicit and reviewable?
- Is the result still being described as nominal success despite recovery dependence?
