---
title: Glossary and Source Mapping
description: Term map and link graph for governed contract entry points
---

# Glossary and Source Mapping

This page is the practical bridge between spec-domain terms and the contract surfaces.

## Glossary seeds

- **LTSSM**: Link Training and Status State Machine
- **EQ**: Link equalization state and coefficient validation
- **Recovery/Fallback**: Retain visibility for retrain and fallback behavior
- **Required slice**: Must be complete before downstream CI gating decisions
- **Advisory slice**: Useful for reviewer context, not a required gate

## Source map to contract surfaces

- `docs/PCIE5_GLOSSARY_FOR_LLM.md`
- `docs/PCIE5_SPEC_TO_CONTRACT_MAPPING.md`
- `docs/PCIE5_LTSSM_STATE_TRANSITIONS.md`
- `docs/PCIE5_LINK_EQUALIZATION_RULES.md`
- `docs/PCIE5_SPEED_WIDTH_NEGOTIATION.md`
- `docs/PCIE5_RECOVERY_AND_FALLBACK.md`
- `docs/PCIE5_AER_RULES.md`
- `docs/PCIE5_CONFIG_SPACE.md`
- `docs/PCIE5_POWER_MANAGEMENT.md`
- `docs/PCIE5_DLL_RULES.md`
- `docs/PCIE5_TLP_RULES.md`
- `docs/PCIE5_HOTPLUG_RULES.md`

## Rule of use

- For governance decisions, use **surface mapping first**, then check the corresponding fixture scope.
- For implementation help, use this repo as a boundary-aware index and stay within the required scope when making completion claims.
