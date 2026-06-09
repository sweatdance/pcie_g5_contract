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