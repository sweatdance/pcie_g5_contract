# PCIe Gen5 Speed And Width Negotiation

This contract slice tracks target-versus-negotiated outcomes and prevents silent downtraining or degraded-width approval.

## Required evidence fields

- `target_speed_gtps`
- `negotiated_speed_gtps`
- `target_width`
- `negotiated_width`
- `downtrained`

## Conditionally required evidence fields

- `degraded_width_expected`
- `degraded_width_reason`
- `fallback_reason`

## Contract rules

- A nominal Gen5 success claim requires negotiated speed to match target speed.
- Width mismatch is warning-grade only when it is explicitly expected and justified.
- A downtrained result must not be presented as a nominal Gen5 success.

## Reviewer prompts

- Is the target speed really what the test intended to validate?
- If the link width degraded, was that expected before the run?
- Is fallback behavior visible and tied to a reason rather than left implicit?
