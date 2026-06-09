# Long-Term Memory

## Memory Authority
<!-- memory_type: structural_long_term -->
<!-- promotion_status: authoritative -->
<!-- promoted_by: governance-baseline / 2026-06-09 -->
<!-- promoted_at: 2026-06-09 -->
<!-- source_anchor: governance/MEMORY_PROTOCOL.md -->

- Repo-local `memory/` is the only cross-agent memory authority for this contract repo.
- Canonical long-term memory lives in `memory/00_long_term.md`.
- Canonical daily session memory lives in `memory/YYYY-MM-DD.md`.
- New session-derived daily entries should be written with `E:\BackUp\Git_EE\ai-governance-framework\governance_tools\memory_record.py`.
- External ad hoc notes are not governance authority until distilled into this repo-local `memory/` directory.

## Contract Boundary
<!-- memory_type: structural_long_term -->
<!-- promotion_status: authoritative -->
<!-- promoted_by: repo-governance-import / 2026-06-09 -->
<!-- promoted_at: 2026-06-09 -->
<!-- source_anchor: contract.yaml -->

- Completion claims are limited to PCIe Gen5 LTSSM and link-training evidence only.
- Protocol-expansion slices (`pm`, `aer`, `cfgspace`, `dll`, `tlp`, `hotplug`) are advisory evidence surfaces, not complete-scope claims.
- Review conclusions should prefer JSON evidence and validator output over prose-only assertions.

## Validation Baseline
<!-- memory_type: structural_long_term -->
<!-- promotion_status: authoritative -->
<!-- promoted_by: repo-governance-import / 2026-06-09 -->
<!-- promoted_at: 2026-06-09 -->
<!-- source_anchor: .github/workflows/contract-regression.yml -->

- The required gate is the LTSSM and link-training fixture/regression suite.
- Advisory suites are non-blocking until real PCIe JSON evidence is present for those slices.
- Governance drift should be checked against the external `ai-governance-framework` checkout, not an in-repo placeholder path.
