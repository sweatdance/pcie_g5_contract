# PCIe Gen5 LTSSM Contract Notes

<!-- governance:key=repo_profile -->
- Repository: pcie_g5_contract
- Domain: PCIe Gen5 LTSSM contract for RTL
- Scope: external repository onboarding and contract validation workflow

<!-- governance:key=workflow -->
- Read contract.yaml first.
- Keep changes scoped to LTSSM contract for RTL only; do not generalize to full PCIe stack.
- Prefer evidence from generated JSON training report over prose claims.
- Validate with:
  - `governance_tools/external_repo_readiness.py --repo . --format json`
  - `python -X utf8 governance_tools/external_repo_readiness.py --repo . --format json`
- When making changes, update `governance/framework.lock.json`, hooks, and `.github/copilot-instructions.md` in onboarding slice.

<!-- governance:key=rails_and_boundaries -->
- Do not quote or invent PCIe 5.0 spec language from memory.
- Do not relax governance checks to satisfy tests; only fix real violations.
- Escalate if a repo-local path or command can affect closeout evidence generation.

<!-- governance:key=signals -->
- command: git status --short
- path: contract.yaml
- path: AGENTS.md
- path: governance/framework.lock.json
- path: .git/hooks/pre-commit
- path: .git/hooks/pre-push
- path: .github/copilot-instructions.md

<!-- governance:key=f7_update_boundary -->
- F-7 updates must preserve existing repo-specific AGENTS.md rules.
- Validate F-7 state with `python -X utf8 -m governance_tools.f7_full_update --repo . --format json` from the framework environment.
- Required external contract surfaces: contract.yaml, governance/framework.lock.json, .git/hooks/pre-commit, .git/hooks/pre-push, .github/copilot-instructions.md.


<!-- governance:key=memory_workflow -->
- Before claiming completion for any change touching `memory/**`, run `python -m governance_tools.memory_workflow --check --repo .`.
- For memory completion claims, run `python -m governance_tools.memory_workflow --check --repo . --run-guard` and report blockers before claiming DONE.
- Use the canonical memory writer for session-derived memory; do not edit memory records as ordinary markdown.
