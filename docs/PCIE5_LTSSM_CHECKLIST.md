# PCIe Gen5 LTSSM Review Checklist

Use this checklist for RTL-scoped review of PCIe Gen5 LTSSM and link training changes.

## Required evidence

- A JSON training report is attached or referenced.
- The target link speed is explicit.
- The negotiated link speed is explicit.
- The target link width is explicit.
- The negotiated link width is explicit.
- Final LTSSM state is explicit.
- LTSSM visited-state summary is explicit.
- Illegal transition count is explicit.
- Equalization completion or phase outcome is explicit.
- Equalization phase summary is explicit.
- Lane-level failure summary is explicit, even when empty.
- Recovery or retrain visibility is explicit when triggered.
- Downtrain or degraded-width expectation is explicit when applicable.

## Reviewer checks

- The change scope is limited to LTSSM or link training logic.
- The evidence shows the design reaches `L0` for the intended scenario.
- The evidence does not rely on an illegal LTSSM transition summary.
- Negotiated speed matches the intended Gen5 target for the scenario under review.
- Negotiated width does not silently degrade without explanation.
- Equalization does not terminate with an unresolved failure condition.
- Recovery or fallback behavior is described when training does not converge.
- Recovery-triggered convergence is not described as a clean nominal path without qualification.
- Any lane degradation, downtrain, or retry behavior is called out explicitly.
- Assumptions about topology, partner capability, presets, or lane masking are stated.

## Safety boundaries

- Do not approve changes based only on prose claims when the JSON report is missing.
- Do not treat partial LTSSM traces as proof of stable `L0` entry.
- Do not infer Gen5 success from lower-speed convergence.
- Do not infer legal LTSSM progression when the report omits transition evidence.
- Do not broaden this contract to DLL, TLP, retimer, or compliance coverage without a versioned contract change.
