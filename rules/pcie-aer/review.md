# PCIe AER / Error Handling Rule Pack

Rule pack: `pcie-aer`

## Rule basis

- Require AER evidence when error events (Surprise Down, Malformed TLP, unexpected Completion)
  are present in the capture.
- Treat Malformed TLP and Unexpected Completion as hard-stop violations requiring explanation.
- Require Surprise Down to produce a visible AER Uncorrectable Error log.
- Treat absence of AER log after Surprise Down as incomplete evidence (warn).
- Do not approve error recovery paths that skip AER status register clearing.

## Hard-stop rules

- `PCIE5-AER-001`: Malformed TLP detected in capture must have a corresponding AER Uncorrectable
  Error record. Malformed TLP without AER evidence is a hard stop.
- `PCIE5-AER-002`: Unexpected Completion (CplD or Cpl with UR/CA status) must be explained.
  Unexplained Unexpected Completion is a hard stop.
- `PCIE5-AER-003`: If `surprise_down_observed = true` and `aer_surprise_down_logged = false`,
  this is a hard stop: Surprise Down must produce an AER record to be debuggable.

## Warn rules

- `PCIE5-AER-004` (warn): Correctable errors (REPLAY_NUM rollover, LCRC error, Bad TLP) are
  warn-grade. Count > 10 in a single capture warrants review.
- `PCIE5-AER-005` (warn): AER status registers (Reg=0x104 Uncorrectable, Reg=0x110 Correctable)
  must be read and cleared by the OS after Surprise Down recovery. Absence of this read sequence
  after a Surprise Down event warrants a warning.
- `PCIE5-AER-006` (warn): Completion Timeout (device did not return a completion) without a
  corresponding AER log or retry is warn-grade.

## Review prompts

- Was a Surprise Down event observed, and was it logged in AER Uncorrectable Error Status?
- Were AER registers read and cleared during the recovery sequence?
- Were any Malformed TLPs or Unexpected Completions present?
- Was the correctable error count within acceptable bounds?
- Was Completion Timeout observed, and was it handled?
