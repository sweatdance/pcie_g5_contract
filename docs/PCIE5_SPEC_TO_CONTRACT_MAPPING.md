# PCIe Gen5 Spec To Contract Mapping

This file maps internal PCIe 5.0 spec study slices into reusable contract surfaces.
It is intentionally normalized and does not reproduce spec text.

## Slice 1: LTSSM states and transitions

- Contract surface: LTSSM state evidence and transition legality summary
- Rule ids: `PCIE5-LTSSM-STATE-001`, `PCIE5-LTSSM-STATE-002`
- Required evidence:
  - final LTSSM state
  - visited states or summarized path
  - illegal transition count
- Validator feasibility: high
- Decision impact: block nominal success claims when illegal transitions are present

## Slice 2: Link training and equalization

- Contract surface: equalization completion and phase summary
- Rule ids: `PCIE5-EQ-001`, `PCIE5-EQ-002`
- Required evidence:
  - equalization completion flag
  - equalization phase summary
  - lane failure summary
- Validator feasibility: high
- Decision impact: block nominal Gen5 success claims when equalization is incomplete

## Slice 3: Speed and width negotiation

- Contract surface: target versus negotiated speed and width
- Rule ids: `PCIE5-LINK-NEG-001`, `PCIE5-LINK-NEG-002`
- Required evidence:
  - target speed and negotiated speed
  - target width and negotiated width
  - degraded-width expectation and reason when applicable
- Validator feasibility: high
- Decision impact: block silent mismatch; warn on explicit degraded-width cases

## Slice 4: Recovery and fallback

- Contract surface: retrain, recovery, fallback visibility
- Rule ids: `PCIE5-RECOVERY-001`
- Required evidence:
  - recovery triggered flag
  - retry count
  - fallback or downtrain explanation when present
- Validator feasibility: medium
- Decision impact: warn or block depending on whether a nominal success claim is made

## Non-scope for v0.2

- Data Link Layer semantics
- TLP rules
- retimer-specific coverage
- compliance certification procedures
- lane margining breadth beyond summary evidence
