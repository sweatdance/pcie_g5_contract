# memory/ README

This directory is the shared memory channel for this repository.

## Canonical Files

- `00_long_term.md`: curated long-term memory for main sessions
- `YYYY-MM-DD.md`: daily session logs and post-push entries

## Supporting Files

- `01_active_task.md`: current task state and next safe step
- `02_tech_stack.md`: repo facts, toolchain facts, and accepted workflow aliases
- `03_knowledge_base.md`: troubleshooting notes, anti-patterns, and durable lessons
- `04_review_log.md`: review summaries and validation history

## Cross-Agent Rule

- Treat files in this `memory/` directory as the only cross-agent memory authority for this repo.
- Do not use external or private agent memory files as governance truth for this repo.
- If useful context exists only outside the repo, copy a concise, auditable summary into this directory before relying on it.
