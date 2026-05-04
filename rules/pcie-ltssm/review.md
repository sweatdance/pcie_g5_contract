# PCIe LTSSM Rule Pack

Rule pack: `pcie-ltssm`

## Rule basis

- Require machine-readable JSON evidence for LTSSM and link training claims.
- Keep review scope aligned to RTL link training behavior.
- Require explicit final-state, speed, width, and equalization evidence.
- Require LTSSM trace evidence with an illegal-transition summary.
- Treat degraded-width or downtrained outcomes as review-visible, not implied success.
- Treat recovery-visible convergence as distinct from a clean nominal path.

## Review prompts

- What evidence proves the design reached `L0`?
- What evidence proves the state progression was legal?
- Was Gen5 speed actually negotiated, or only targeted?
- Did the link width degrade, and if so, was that intentional?
- Was equalization completed without unresolved lane failures?
- Did the path depend on recovery or retrain?
- Which assumptions about link partner or topology remain outside this slice?
