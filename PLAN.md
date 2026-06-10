> **Last Updated**: 2026-06-10
> **Owner**: PCIe Architecture
> **Freshness**: Sprint (7d)

## Objective
Build a reusable external domain contract for PCIe Gen5 LTSSM and link training in RTL projects.

## Current Sprint
- Establish contract structure
- Define JSON evidence schema
- Validate loader and runtime smoke

## Boundaries
- Keep scope limited to LTSSM and link training
- Do not broaden to full protocol or compliance automation in v0.1.0
- Phase 1 scope declaration is: LTSSM/link-training hard-stop slices are contractually bounded; PM/AER/DLL/TLP/Hot-Plug/CFG remain protocol-expansion evidence with advisory completion status.
- Record claim ceiling explicitly as: only LTSSM + link-training completion claims are currently complete; all other slices are not a completed contract scope yet.
