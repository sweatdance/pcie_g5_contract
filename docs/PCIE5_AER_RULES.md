# PCIe AER and Error Handling Rules

This contract slice makes error event visibility, AER log consistency, and error register
configuration reviewer-enforced for both endpoint and Root Complex perspectives.

## Background

PCIe Advanced Error Reporting (AER) is an Extended Capability (Cap ID = 0x0001, base offset
0x100+) that provides machine-readable error logging on PCIe Endpoints and Root Ports.

- **Surprise Down**: Device disappears without Hot-Plug removal. Produces AER Uncorrectable
  Error (bit20). In the GL9767/SD7 MUX scenario, SD7 removal triggers Surprise Down on the
  host downstream port.
- **Correctable vs Uncorrectable**: Correctable errors (LCRC, REPLAY_NUM rollover) are recovered
  by the DLL replay mechanism. Uncorrectable errors require OS intervention.
- **WHEA_UNCORRECTABLE_ERROR (BugCheck 0x124)**: Windows BSOD when AER fatal error propagates
  to OS without being handled. Distinct from 0x9F/0xA0 (PM timeout).
- **Advisory Non-Fatal**: Uncorrectable error with Severity=Non-Fatal; OS may not crash but must
  log the error. Only valid if explicitly configured in Uncorrectable Error Severity register.

---

## AER Uncorrectable Error Status Register (Reg = 0x104)

Bits are write-1-to-clear. Default severity per PCIe Base Spec shown; may be overridden by
Uncorrectable Error Severity register (0x10C).

| Bit | Name | Default Severity | Notes |
|-----|------|-----------------|-------|
| 4 | Data Link Protocol Error | Fatal | DL CRC/sequence error unrecoverable |
| 5 | Surprise Down Error | Fatal | Device removed without warning |
| 12 | Poisoned TLP Received | Non-Fatal | EP bit set in received TLP |
| 13 | Flow Control Protocol Error | Fatal | FC credit accounting violation |
| 14 | Completion Timeout | Non-Fatal | Non-posted request never completed |
| 15 | Completer Abort | Non-Fatal | Completer sent CA status |
| 16 | Unexpected Completion | Non-Fatal | Completion to unknown requester |
| 17 | Receiver Overflow | Fatal | Overflow of receiver buffer |
| 18 | Malformed TLP | Fatal | TLP length/field inconsistency |
| 19 | ECRC Error | Non-Fatal | End-to-End CRC mismatch |
| 20 | Unsupported Request Error | Non-Fatal | UR status returned |
| 21 | ACS Violation | Non-Fatal | ACS check failed |
| 22 | Internal Error | Fatal | Device-internal fatal error |
| 23 | MC Blocked TLP | Non-Fatal | Multicast blocked |
| 24 | AtomicOp Egress Blocked | Non-Fatal | AtomicOp blocked at ingress |
| 25 | TLP Prefix Blocked Error | Non-Fatal | TLP Prefix blocked |
| 26 | Poisoned TLP Egress Blocked | Non-Fatal | Poisoned TLP blocked at ingress |

**Critical for GL9767 / SD7 BSOD debug**:
- bit5 (Surprise Down): triggered when SD7 is removed during MUX switch
- bit18 (Malformed TLP): triggered on format/length violations
- bit13 (Flow Control Protocol Error): always fatal; triggers WHEA 0x124

---

## AER Uncorrectable Error Mask Register (Reg = 0x108)

Bit=1 masks (suppresses) the corresponding error from being reported. Default all-zero
(no masking). Advisory NFE configurations may mask specific bits for known-good errors.

**Warning**: Masking bit20 (Surprise Down) prevents WHEA reporting but does not fix the
underlying hot-plug race condition. Do not mask Surprise Down as a permanent fix.

---

## AER Uncorrectable Error Severity Register (Reg = 0x10C)

Bit=1 = Fatal; Bit=0 = Non-Fatal. Overrides the default severity per bit in Uncorrectable
Error Status. Used to demote Fatal errors to Non-Fatal (Advisory NFE mechanism).

| Common customization | Bit | Notes |
|----------------------|-----|-------|
| Demote Surprise Down from Fatal | bit5=0 | Makes Surprise Down Non-Fatal; OS logs but may not BSOD |
| Keep Poisoned TLP as Non-Fatal | bit12=0 | Default; driver-recoverable |
| Promote Completion Timeout to Fatal | bit14=1 | Aggressive; causes BSOD on any CTO |

---

## AER Correctable Error Status Register (Reg = 0x110)

Bits are write-1-to-clear. All correctable errors are recoverable by the DLL.

| Bit | Name | Common Cause |
|-----|------|--------------|
| 0 | Receiver Error | Physical layer noise |
| 6 | Bad TLP | LCRC error in received TLP |
| 7 | Bad DLLP | CRC error in received DLLP |
| 8 | REPLAY_NUM Rollover | 4 consecutive TLP replays without ACK; link likely degraded |
| 12 | Replay Timer Timeout | Replay timer expired; sender retransmits oldest unACK'd TLP |
| 13 | Advisory Non-Fatal Error | Non-Fatal Uncorrectable error occurred; see Uncorrectable Status |
| 14 | Corrected Internal Error | Internal ECC or parity corrected |
| 15 | Header Log Overflow | More errors logged than Header Log can hold |

**Frequency threshold for investigation**: > 10 correctable errors per session, or any burst
of > 5 of the same type within 60ms = signal integrity concern.

---

## AER Capabilities and Control Register (Reg = 0x118)

| Bit | Name | Description |
|-----|------|-------------|
| [4:0] | First Error Pointer | Bit number of first uncorrectable error logged (must match lowest bit in Reg=0x104) |
| 5 | ECRC Generation Capable | 1 = endpoint can generate ECRC on outgoing TLPs |
| 6 | ECRC Generation Enable | 1 = endpoint generates ECRC; must match receiver Check Enable |
| 7 | ECRC Check Capable | 1 = endpoint can verify ECRC on incoming TLPs |
| 8 | ECRC Check Enable | 1 = endpoint verifies ECRC; must match sender Generation Enable |
| 9 | Multiple Header Recording Capable | 1 = can log up to 3 TLP headers |
| 10 | Multiple Header Recording Enable | 1 = log multiple failing TLP headers |

**ECRC rule**: Generation Enable and Check Enable must be consistent between sender and receiver.
Asymmetric ECRC (sender generates, receiver does not check, or vice versa) is valid for
compatibility but means ECRC is effectively non-functional.

---

## TLP Header Log (Reg = 0x11C–0x12B)

Four 32-bit DWORDs capturing the header of the first failing TLP. Used for forensic analysis.
Valid only when a new error is logged (after clearing and before re-clearing).

| Offset | Content |
|--------|---------|
| 0x11C | TLP Header DW0 (Fmt, Type, TC, Length) |
| 0x120 | TLP Header DW1 (RequesterID, Tag, BE) |
| 0x124 | TLP Header DW2 (Address[63:32] or CompleterID/Length) |
| 0x128 | TLP Header DW3 (Address[31:0]) |

---

## Root Error Command Register (Reg = 0x12C) — Root Port only

| Bit | Name | Description |
|-----|------|-------------|
| 0 | Correctable Error Reporting Enable | 1 = generate interrupt on correctable AER event |
| 1 | Non-Fatal Error Reporting Enable | 1 = generate interrupt on non-fatal AER event |
| 2 | Fatal Error Reporting Enable | 1 = generate interrupt on fatal AER event |

OS must set these bits to enable AER interrupt delivery (NMI/MSI path to WHEA).

---

## Root Error Status Register (Reg = 0x130) — Root Port only

| Bit | Name | Description |
|-----|------|-------------|
| 0 | ERR_COR Received | 1 = correctable error received from downstream device |
| 1 | Multiple ERR_COR Received | 1 = >1 correctable error; only first source ID logged |
| 2 | ERR_FATAL/NONFATAL Received | 1 = non-fatal or fatal error received |
| 3 | Multiple ERR_FATAL/NONFATAL Received | 1 = >1 error; first source ID in Reg=0x134 bits[15:0] |
| 4 | First Uncorrectable Fatal | 1 = first error was fatal |
| 5 | Non-Fatal Error Messages Received | |
| 6 | Fatal Error Messages Received | |
| [31:7] | Advanced Error Interrupt Message Number | MSI/MSI-X vector for AER interrupt |

---

## Error Source ID Register (Reg = 0x134) — Root Port only

| Bits | Content |
|------|---------|
| [15:0] | ERR_COR Source ID: Bus[7:0], Device[4:0], Function[2:0] of first correctable error source |
| [31:16] | ERR_FATAL/NONFATAL Source ID: same format for first non-fatal/fatal error source |

---

## Windows BSOD Code Mapping

| AER Error | Windows BugCheck | Notes |
|-----------|-----------------|-------|
| Surprise Down (bit5) | 0x9F, 0xA0, 0x124 | 0x124 if fatal propagates to WHEA; 0x9F/0xA0 if PM timeout races |
| Flow Control Protocol Error (bit13) | 0x124 | Always fatal → WHEA |
| Malformed TLP (bit18) | 0x124 | Fatal → WHEA |
| Completion Timeout (bit14, if promoted to Fatal) | 0x9F / 0xA0 | 0x9F = PoFx timeout; 0xA0 = ACPI wait for S0 |
| ECRC Error (bit19) | 0x124 | If severity=Fatal |
| Correctable burst (no single fatal) | None / silent degradation | DLL recovers; driver may not see it |

---

## Required Evidence Fields (`checks.pcie_aer_report`)

```yaml
# Mandatory
surprise_down_observed: boolean
aer_surprise_down_logged: boolean
aer_registers_cleared: boolean
malformed_tlp_observed: boolean
unexpected_completion_observed: boolean
correctable_error_count: integer
completion_timeout_observed: boolean

# Uncorrectable error detail
aer_uncorrectable_error_value: string    # hex, e.g. "0x00100020" (bit5+bit18)
aer_uncorrectable_mask_value: string     # hex value of Reg=0x108
aer_severity_value: string              # hex value of Reg=0x10C
first_error_pointer: integer            # bits[4:0] of Reg=0x118

# ECRC
ecrc_generation_enable: boolean
ecrc_check_enable: boolean

# Root Complex (if capturing Root Port perspective)
root_error_status_value: string         # hex value of Reg=0x130
aer_source_id: string                   # hex, "BBDDFF" format

# Correctable error detail
correctable_error_types: array[string]  # e.g. ["REPLAY_NUM_ROLLOVER", "RECEIVER_ERROR"]
aer_correctable_status_value: string    # hex value of Reg=0x110

# BSOD correlation
bsod_code: string                       # e.g. "0xA0", "0x124", "0x9F"

notes: array[string]
```

---

## Reviewer Prompts

**Error events**
- Was Surprise Down observed? Was bit5 of Reg=0x104 set?
- Was Malformed TLP (bit18) or Flow Control Protocol Error (bit13) logged?
- Were AER registers cleared (write-1-to-clear) before new device enumeration?

**AER register configuration**
- What bits are set in Uncorrectable Error Mask (Reg=0x108)? Any non-default masking?
- Does First Error Pointer (bits[4:0] of Reg=0x118) match the lowest error bit in Reg=0x104?
- Is ECRC Generation Enable consistent with ECRC Check Enable (receiver)?
- Was Root Error Status read to identify the Error Source ID?

**BSOD correlation**
- What was the Windows BugCheck code? 0x9F/0xA0 = PM timeout; 0x124 = WHEA fatal AER
- Did the AER fatal error propagate to Root Complex before the BSOD?
- Was Surprise Down severity configured as Fatal (default) or demoted to Non-Fatal?

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
