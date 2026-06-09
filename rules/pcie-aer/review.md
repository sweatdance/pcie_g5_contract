# PCIe AER / Error Handling Rule Pack

Rule pack: `pcie-aer`

## Rule basis

- Require AER evidence when error events (Surprise Down, Malformed TLP, Unexpected Completion,
  Poisoned TLP, Flow Control Protocol Error) are present in the capture.
- Treat Malformed TLP, Unexpected Completion, and Flow Control Protocol Error as hard stops.
- Require Surprise Down to produce a visible AER Uncorrectable Error log.
- Require AER status registers to be cleared before new device enumeration begins.
- Require all masked errors to be documented (unmasked = default for Surprise Down).
- Require ECRC generation/checking to be consistent on both sides when capability exists.

## Hard-stop rules

- `PCIE5-AER-001`: Malformed TLP detected in capture must have a corresponding AER
  Uncorrectable Error record (bit15 of Reg=0x104). Malformed TLP without AER evidence is a hard stop.
- `PCIE5-AER-002`: Unexpected Completion (CplD or Cpl with UR/CA status, or completion to an
  unknown requester) must be explained in notes. Unexplained Unexpected Completion is a hard stop.
- `PCIE5-AER-003`: If `surprise_down_observed = true` and `aer_surprise_down_logged = false`,
  this is a hard stop. Surprise Down must produce a Surprise Down Error (bit20 of Reg=0x104).
- `PCIE5-AER-008` (hard stop): Flow Control Protocol Error (bit13 of Uncorrectable Error Status)
  in the AER log is always fatal. Any observation must trigger immediate link health investigation.
- `PCIE5-AER-011` (hard stop): First Error Pointer (AER Capabilities and Control bits[4:0]) must
  match the lowest-numbered bit set in Uncorrectable Error Status. Mismatch indicates corrupted
  AER state and cannot be trusted for root-cause analysis.

## Warn rules — correctable errors

- `PCIE5-AER-004` (warn): Correctable errors total > 10 in a single capture warrants signal
  integrity review (LCRC, REPLAY_NUM rollover, Receiver Error, Bad DLLP, Bad TLP).
- `PCIE5-AER-013` (warn): More than 5 correctable errors of the same type within 60ms is a
  burst pattern that suggests SI degradation, not transient noise.

## Warn rules — AER register management

- `PCIE5-AER-005` (warn): AER status registers (Reg=0x104 Uncorrectable, Reg=0x110 Correctable)
  must be read and cleared by the OS after Surprise Down recovery. Absence warns for stale state.
- `PCIE5-AER-006` (warn): Completion Timeout (bit14 of Uncorrectable Error Status) without a
  corresponding AER log or retry sequence warns for hidden timeout.
- `PCIE5-AER-009` (warn): Any bit set in Uncorrectable Error Mask (Reg=0x108) suppresses that
  error from reporting. Masked errors must be documented with reason; unexpected masking warns.
- `PCIE5-AER-010` (warn): Advisory Non-Fatal classification: if Uncorrectable Error Severity
  (Reg=0x10C) has a bit cleared (severity=Non-Fatal) for an error that normally requires
  fatal handling, document the design intent. Undocumented Advisory NFE configuration warns.

## Warn rules — ECRC

- `PCIE5-AER-007` (warn): ECRC Generation Enable and ECRC Check Enable (AER Capabilities and
  Control register bits) must match on both endpoints. Asymmetric ECRC configuration causes
  silent data corruption (checking side discards TLPs that the sending side did not protect).

## Warn rules — Root Complex AER

- `PCIE5-AER-012` (warn): Root Error Status (Reg=0x130) ERR_FATAL or ERR_NONFATAL bit set
  without a traceable Error Source ID (Reg=0x134 bits[15:0]) means the error source cannot
  be identified for forensic analysis. Source ID must be captured.

## Review prompts — error events

- Was a Surprise Down observed, and was it logged in AER Uncorrectable Error Status bit20?
- Were AER registers read and cleared during recovery?
- Were Malformed TLPs or Unexpected Completions present? What was the root cause?
- Was a Flow Control Protocol Error (bit13) present? This is always fatal.

## Review prompts — AER register configuration

- What bits are set in Uncorrectable Error Mask (Reg=0x108)? Any non-default masking?
- What is the First Error Pointer (bits[4:0] of AER Cap/Control)? Does it match the error?
- Is ECRC Generation Enable consistent between endpoint and root port?
- Does Root Error Status have a valid Error Source ID?

## Review prompts — Windows BSOD correlation

- If BSOD occurred, which bugcheck code: 0x9F / 0xA0 (PM timeout), 0xFE (DPC timeout),
  0x124 (WHEA_UNCORRECTABLE_ERROR from AER fatal), or 0x7E / 0x50 (driver fault)?
- Did the AER fatal error propagate to Root Complex before the BSOD?
