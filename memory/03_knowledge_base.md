# Knowledge Base

## Gotchas

- External ad hoc memory notes are not canonical for this repo. Distill anything durable into repo-local `memory/` before using it as governance truth.
- The repo allows `02_tech_stack.md` as an alias memory file, but it still requires canonical `memory/00_long_term.md` and `memory/YYYY-MM-DD.md`.
- A passing governance drift check does not prove the workflow path is runnable in CI; this repo previously pointed at a non-existent `governance/governance_tools/governance_drift_checker.py`.
- Advisory PCIe slices currently fail positive fixtures in no-evidence mode because the fixtures do not yet provide the required advisory JSON report shape. This is expected to remain non-blocking until those evidence surfaces are filled in.
- Required LTSSM and link-training validation is the real claim boundary. Do not upgrade advisory slice status from fixture presence alone.
- Root cause of the earlier memory mistake: external Codex memory formatting was applied before checking repo-local governance rules. For this repo, `memory/` inside the repo outranks external ad hoc notes, and daily memory after the canonical-writer cutoff should be written in session-derived canonical format.
