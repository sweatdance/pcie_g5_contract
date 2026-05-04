# PCIe Equalization Rule Pack

Rule pack: `pcie-eq`

## Rule basis

- Require explicit equalization evidence for Gen5 success claims.
- Treat failed phases and lane-level anomalies as review-visible.
- Do not infer equalization success from a final `L0` state alone.

## Review prompts

- Which equalization phases completed?
- Were any phases retried or failed?
- Are lane-level anomalies explicitly summarized?
