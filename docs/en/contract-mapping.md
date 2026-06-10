---
title: Contract Mapping
description: Surface-to-spec mapping and evidence-routing index
---

# Contract Mapping

| Surface | Slice | Contract surface | Evidence source |
| --- | --- | --- | --- |
| LTSSM state transitions | LTSSM | `pcie-ltssm` | `PCIE5_LTSSM_STATE_TRANSITIONS.md` |
| LTSSM checklist | LTSSM | `pcie-ltssm` | `PCIE5_LTSSM_CHECKLIST.md` |
| Link equalization | EQ | `pcie-eq` | `PCIE5_LINK_EQUALIZATION_RULES.md` |
| Speed/width negotiation | Link negotiation | `pcie-link-negotiation` | `PCIE5_SPEED_WIDTH_NEGOTIATION.md` |
| Recovery and fallback | LTSSM | `pcie-ltssm` | `PCIE5_RECOVERY_AND_FALLBACK.md` |
| Power management | PM | `pcie-pm` | `PCIE5_POWER_MANAGEMENT.md` |
| AER rules | AER | `pcie-aer` | `PCIE5_AER_RULES.md` |
| DLL rules | DLL | `pcie-dll` | `PCIE5_DLL_RULES.md` |
| TLP rules | TLP | `pcie-tlp` | `PCIE5_TLP_RULES.md` |
| Hot-plug rules | Hot-Plug | `pcie-hotplug` | `PCIE5_HOTPLUG_RULES.md` |
| Config-space | CFG | `pcie-cfgspace` | `PCIE5_CONFIG_SPACE.md` |

## Mapping usage pattern

- For implementation questions, resolve first to the corresponding contract surface and then to the mapped source.
- For evidence questions, map to fixture suite (`pcie-ltssm`, `pcie-eq`, `pcie-link-negotiation`, etc.) and run matching smoke.
- For required-gate queries, restrict to `LTSSM`, `EQ`, and `Link negotiation` surfaces only.

## Required-gate routing table

| Gate class | Allowed surfaces | Validation expectation | Typical question |
| --- | --- | --- | --- |
| Hard gate | LTSSM, EQ, Link negotiation | fixture smoke pass + explicit status update | "Can this repo be promoted as a required contract input?" |
| Advisory review | PM, AER, DLL, TLP, Hot-Plug, CFG | evidence exists, not enforced as required | "Why did this case fail?" |
| Contextual | Source docs and artifacts | traceability for rationale and glossary clarity | "Where is this clause defined?" |

## What to do when evidence is missing

- Keep claim labels (`required`, `advisory`, `not claimed`) intact.
- Add a `memory/` note and rerun the nearest smoke scope.
- Do not move surface to required-gate while smoke or contract routing is unverified.
