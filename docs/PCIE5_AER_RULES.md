# PCIe AER and Error Handling Rules

This contract slice makes error event visibility and AER log consistency reviewer-enforced.

## Background

PCIe Advanced Error Reporting (AER) is an extended capability (base offset 0x100+) that
provides machine-readable error logging. Key concepts for debug:

- **Surprise Down**: When a device disappears without a proper Hot-Plug removal sequence.
  Produces an AER Uncorrectable Error (Fatal or Non-Fatal). In the GL9767/SD7 MUX scenario,
  SD7 removal triggers a Surprise Down on the host downstream port.
- **Correctable vs. Uncorrectable errors**: Correctable errors (LCRC, REPLAY_NUM) can be
  recovered by the DLL replay mechanism. Uncorrectable errors (Malformed TLP, Surprise Down,
  Poisoned TLP) require OS intervention.
- **WHEA_UNCORRECTABLE_ERROR (BugCheck 0x124)**: Windows BSOD triggered when an uncorrectable
  AER error propagates to the OS without being handled. Relevant to this project's BSOD scenario.

## Required evidence fields (`checks.pcie_aer_report`)

- `surprise_down_observed`: boolean — was a Surprise Link Down event seen in the capture?
- `aer_surprise_down_logged`: boolean — was the AER Uncorrectable Error Status register
  (Reg=0x104) read after Surprise Down, confirming the error was logged?
- `aer_registers_cleared`: boolean — was AER status cleared (CfgWr with write-1-to-clear
  pattern) after the Surprise Down recovery?
- `malformed_tlp_observed`: boolean — was a Malformed TLP seen in the capture?
- `unexpected_completion_observed`: boolean — was an Unexpected Completion (UR/CA status) seen?
- `correctable_error_count`: integer — total correctable error events (LCRC, REPLAY_NUM rollover)
- `completion_timeout_observed`: boolean — was a Completion Timeout observed?

## Conditionally required fields

- `aer_uncorrectable_error_value`: string (hex) — value read from AER Uncorrectable Error Status
  (required when `aer_surprise_down_logged = true`)
- `aer_source_id`: string — Error Source ID from Root Error Status (required when AER fatal reported)
- `correctable_error_types`: array of strings — types of correctable errors observed
- `completion_timeout_requester_id`: string — RequesterID of the TLP that timed out
- `notes`: array of strings

## Contract rules

- `PCIE5-AER-001`: If `malformed_tlp_observed = true` and `aer_surprise_down_logged = false`
  (no AER logging evidence), this is a hard stop. Malformed TLP must produce an AER record.
- `PCIE5-AER-002`: If `unexpected_completion_observed = true` without explanation in notes,
  this is a hard stop. Every Unexpected Completion needs a traceable cause.
- `PCIE5-AER-003`: If `surprise_down_observed = true` and `aer_surprise_down_logged = false`,
  this is a hard stop. Surprise Down must be logged to be diagnosable.
- `PCIE5-AER-004` (warn): If `correctable_error_count > 10`, warn for potential signal integrity
  or protocol stability issue.
- `PCIE5-AER-005` (warn): If `surprise_down_observed = true` and `aer_registers_cleared = false`,
  warn that AER status was not cleaned up; stale error bits will affect next session.
- `PCIE5-AER-006` (warn): If `completion_timeout_observed = true` without a corresponding
  recovery or retry sequence, warn.

## Key AER config space offsets (reference)

| Offset | Register | Notes |
|--------|----------|-------|
| 0x100 | AER Enhanced Cap Header | Cap ID = 0x0001 |
| 0x104 | Uncorrectable Error Status | Bit20 = Surprise Down, Bit15 = Malformed TLP |
| 0x108 | Uncorrectable Error Mask | Mask bits for uncorrectable errors |
| 0x10C | Uncorrectable Error Severity | Fatal vs. Non-Fatal |
| 0x110 | Correctable Error Status | Bit0 = Receiver Error, Bit6 = REPLAY_NUM Rollover |
| 0x114 | Correctable Error Mask | |
| 0x118 | AER Capabilities and Control | ECRC generation/check enable |
| 0x11C–0x12B | TLP Prefix Log | First failing TLP header |

## Reviewer prompts

- Was a Surprise Down observed, and was it logged in AER Uncorrectable Error Status?
- Was AER status register cleared after recovery?
- Were Malformed TLPs or Unexpected Completions present? What was the cause?
- Was the correctable error count within bounds (< 10 per session)?
- Was a Completion Timeout observed? Which requester timed out?
- Could the observed BSOD (if any) be WHEA_UNCORRECTABLE_ERROR (0x124) from an unhandled
  AER fatal, or DRIVER_POWER_STATE_FAILURE (0x9F) from a CfgRd timeout during PM L1?
