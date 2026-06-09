# PCIe Transaction Layer Rules

This contract slice enforces TLP completeness, Completion Status visibility, TLP header
format correctness, access boundary validation, and Tag/TC management.

## Background

PCIe Transaction Layer Packets (TLPs) carry configuration, memory, I/O, and message traffic.
Key concepts for debug:

- **UR (Unsupported Request)**: Target does not support the operation. Common cause: accessing
  a non-existent register offset, or sending MRd before Memory Space Enable is set.
- **CA (Completer Abort)**: Target encountered a fatal error processing the request.
- **CRS (Configuration Retry Status)**: Device not yet ready; requester should retry (≤1s).
- **Poisoned TLP**: EP (Error Poisoning) bit set; data is corrupt. Must produce AER event.
- **Completion Timeout**: Non-Posted request without Completion → Windows BSOD (0x9F or 0xA0).
- **Tag**: Identifies a Non-Posted request uniquely. Reuse before completion causes routing ambiguity.
- **Traffic Class (TC)**: TLP priority class; must be mapped to an established Virtual Channel.

---

## TLP Format Overview

### Fmt[2:0] and Type[4:0] Encoding

Fmt and Type together occupy bits[6:0] of TLP DW0.

| Fmt | DW Count | Has Data | Use |
|-----|----------|----------|-----|
| 000 | 3 | No | MRd, CfgRd0/1, IO Read (non-data requests) |
| 001 | 4 | No | MRd 64-bit |
| 010 | 3 | Yes | MWr 32-bit, IO Write, CplD 32-bit |
| 011 | 4 | Yes | MWr 64-bit, CplD 64-bit |
| 100 | 1 | No | TLP Prefix |

### Common TLP Type Codes (Type field bits[4:0])

| Type | Name | Fmt | Description |
|------|------|-----|-------------|
| 00000 | MRd | 000/001 | Memory Read Request |
| 00001 | MRdLk | 000/001 | Memory Read Lock (legacy) |
| 00100 | MWr | 010/011 | Memory Write Request |
| 00101 | IO Read | 000 | I/O Read (legacy PCIe / PCI compat) |
| 00110 | IO Write | 010 | I/O Write |
| 00100 | CfgRd0 | 000 | Configuration Read Type 0 (direct) |
| 00101 | CfgWr0 | 010 | Configuration Write Type 0 |
| 00110 | CfgRd1 | 000 | Configuration Read Type 1 (routed via bridge) |
| 00111 | CfgWr1 | 010 | Configuration Write Type 1 |
| 01010 | Cpl | 000 | Completion without Data |
| 01011 | CplD | 010/011 | Completion with Data |
| 01100 | CplLk | 000 | Completion Locked (legacy) |
| 01101 | CplDLk | 010 | Completion Locked with Data |
| 10000–1xxxx | Msg | 001 | Message Request (various subtypes) |
| 11000–1xxxx | MsgD | 011 | Message Request with Data |
| 01001 | FetchAdd | 010/011 | AtomicOp Fetch and Add |
| 01101 | Swap | 010/011 | AtomicOp Unconditional Swap |
| 01110 | CAS | 010/011 | AtomicOp Compare and Swap |

### TLP DW0 Common Fields

| Bits | Field | Description |
|------|-------|-------------|
| [31:29] | Fmt[2:0] | Header format and data presence |
| [28:24] | Type[4:0] | TLP type |
| 23 | T9 | Extended Tag bit9 (10-bit tags) |
| [22:20] | TC[2:0] | Traffic Class (0–7) |
| 19 | T8 | Extended Tag bit8 (8-bit tags) |
| 18 | Attr[2] | ID-based ordering (rare) |
| 17 | LN | Lightweight Notification (LN TLPs) |
| 16 | TH | TLP Hints present |
| 15 | TD | TLP Digest present (ECRC in TLP suffix) |
| 14 | EP | Error Poisoned bit — if 1, payload data is corrupt |
| [13:12] | Attr[1:0] | Relaxed Ordering (bit1), No Snoop (bit0) |
| [11:10] | AT[1:0] | Address Type (for ATS) |
| [9:0] | Length[9:0] | Payload length in DWORDs; 0 = 1024 DW |

---

## First DW / Last DW Byte Enable Rules

Present in bits [7:0] of DW1 for MRd, MWr, CfgRd, CfgWr, IO requests.

| Field | Bits | Description |
|-------|------|-------------|
| Last DW BE | [7:4] | Byte enables for last DWORD of payload |
| First DW BE | [3:0] | Byte enables for first DWORD of payload |

**Encoding**: 1 = byte enabled, 0 = byte disabled (masked). Example: 0xF = all 4 bytes enabled.

**Rules**:
- For Length=1 DWORD: Last DW BE must be 0x0 (only First DW BE is used)
- For Length>1 DWORD: Last DW BE must be non-zero (0x0 is invalid → Malformed TLP)
- For CfgRd/CfgWr of 32-bit registers: First DW BE=0xF is standard
- MRd/MWr with First DW BE=0x0 and Last DW BE=0x0 = zero-length request (only valid for flush)

---

## Completion Status Encoding

| Status | Code | TLP Type | Meaning |
|--------|------|----------|---------|
| SC | 000b | Cpl / CplD | Successful Completion |
| UR | 001b | Cpl | Unsupported Request |
| CRS | 010b | Cpl | Configuration Retry Status (device not ready) |
| CA | 100b | Cpl | Completer Abort (fatal at target) |

### Completion Header Fields

| Bits | Field | Notes |
|------|-------|-------|
| [31:16] of DW1 | Completer ID | BDF of the completer |
| [15:13] | Cpl Status[2:0] | SC/UR/CRS/CA encoding |
| 12 | BCM | Byte Count Modified (for I/O) |
| [11:0] | Byte Count | Total bytes remaining to complete the request |
| [31:16] of DW2 | Requester ID | BDF of the original requester |
| [15:8] | Tag | Must match the Tag from the original Non-Posted request |
| [6:0] | Lower Address | Byte offset within first DWORD of data |

---

## Tag Field Management

### Tag Bit Widths

| Mode | Tag Width | Enable |
|------|-----------|--------|
| Default | 5-bit (32 tags) | Always |
| Extended Tag (8-bit) | 8-bit (256 tags) | Device Control bit8=1 AND completer supports it |
| 10-bit Extended Tag | 10-bit (1024 tags) | PCIe Gen4+ with T8/T9 bits in DW0 header |

**Key rule**: All outstanding Non-Posted requests (MRd, CfgRd, IO Read) at a given requester
must have unique Tags. Tag reuse before receiving the Completion for the original request
causes the Completion to be routed to the wrong requester context → hard stop.

**CRS handling by Windows**: On first CfgRd to a device (during enumeration), if CRS is
received, Windows re-issues the CfgRd up to a configurable number of times (typically 5×,
1s total). If all retries return CRS, device is considered non-functional.

---

## Message TLP Reference

Message TLPs (Fmt=001 for no data, Fmt=011 for with-data) carry platform-level events.

### Message Routing Subtype (bits[2:0] of Type field)

| Bits[2:0] | Routing | Use |
|-----------|---------|-----|
| 000 | Routed to Root Complex | PME, Error messages from device |
| 001 | Broadcast from Root Complex | PM_Turn_Off from RC to all downstream |
| 010 | Routed by Address | — |
| 011 | Routed by ID (B/D/F) | Targeted messages |
| 100 | Implicit: Local terminate | Vendor messages |
| 101 | Gather & route to RC | MCTP/VDM variants |

### Common Message Codes

| Message Code (byte at DW1[31:24]) | Name | Direction |
|-----------------------------------|------|-----------|
| 0x10 | ERR_COR | Device → RC (correctable AER) |
| 0x11 | ERR_NONFATAL | Device → RC (non-fatal AER) |
| 0x13 | ERR_FATAL | Device → RC (fatal AER) |
| 0x14 | PM_Active_State_Nak | RC → Device (ASPM NAK) |
| 0x18 | PME_Turn_Off | RC → Device (power removal) |
| 0x19 | PME_TO_Ack | Device → RC (PME_Turn_Off ack) |
| 0x24 | Unlock (legacy) | — |
| 0x30 | Set_Slot_Power_Limit | RC → Device (after hot-plug) |
| 0x7E | Vendor Defined Type 1 | Vendor-specific |
| 0x7F | Vendor Defined Type 2 | Vendor-specific |

---

## AtomicOp TLPs

AtomicOp TLPs (FetchAdd, Swap, CAS) require:
- AtomicOp Requester Enable set in Device Control 2 (bit6)
- AtomicOp Completer capability in Device Capabilities 2 of the target
- AtomicOp Routing Enabled in switches on the path

Payload:
- FetchAdd/Swap: 1 or 2 DWORDs (32-bit or 64-bit operand)
- CAS: 2 or 4 DWORDs (compare value + swap value)

---

## Traffic Class and Virtual Channel Mapping

| TC | Description | Default VC mapping |
|----|-------------|-------------------|
| TC0 | Best-effort (default, always supported) | VC0 |
| TC1–TC7 | Higher priority, optional | VC1–VC7 (if VC Extended Cap present) |

**Rule**: TLPs with TC > 0 must have a corresponding VC extended capability entry mapping
that TC to a VC. Without an established VC mapping, switches drop TLPs with unrecognized TC.

---

## TLP Ordering Rules

| Rule | Description |
|------|-------------|
| Strong ordering (default) | Posted MWr before Non-Posted MRd (from same requester) |
| Relaxed Ordering | Attr bit1=1: Non-Posted can pass Posted from same requester |
| No Snoop | Attr bit0=1: Completer may return data without cache check |

**Note for GL9767 (SD Host)**:
- Relaxed Ordering should be disabled (bit1=0) unless explicitly verified as safe for
  the platform coherency model
- No Snoop setting depends on whether CPU cache coherency is required for SD data buffers

---

## Required Evidence Fields (`checks.pcie_tlp_report`)

```yaml
# Mandatory
non_sc_completion_observed: boolean
poisoned_tlp_observed: boolean
cfgrd_without_cpld_observed: boolean
memory_access_to_unassigned_bar: boolean
total_tlp_count: integer

# Non-SC Completion detail
non_sc_completion_types: array[string]    # ["UR", "CRS", "CA"] as observed
non_sc_completion_explanation: string

# Poisoned TLP detail
poisoned_tlp_aer_logged: boolean

# Tag management
tag_reuse_observed: boolean               # Same Tag reused before Completion returned
max_tag_value_seen: integer               # Highest Tag value observed (5-bit=31, 8-bit=255)
extended_tag_enabled: boolean             # Device Control bit8

# Byte Enable
invalid_last_dw_be_observed: boolean      # Last DW BE=0x0 for Length>1 TLP

# Message TLPs
message_tlp_types_observed: array[string] # e.g. ["ERR_COR", "PME_TO_Ack"]

# Traffic Class
tc_out_of_vc_range_observed: boolean      # TC > 0 without VC mapping

# Completion Timeout
completion_timeout_requester_ids: array[string]

notes: array[string]
```

---

## Reviewer Prompts

**Completion status**
- Were non-SC Completions (UR, CA, CRS) present? What is the explanation per request?
- Was Poisoned TLP (EP=1) present? Was AER Uncorrectable Error logged?
- Which CfgRd/MRd had no matching CplD? What register/address was being accessed?

**TLP format and access boundaries**
- Were all MRd/MWr addresses within assigned BAR ranges?
- Were any Length mismatches detected (CATC Malformed TLP decode error)?
- Were Last DW BE values valid for multi-DWORD requests?

**Tag management**
- Was any Tag reused before its Completion was returned? (Tag collision)
- Was Extended Tag enabled? Did the completer support it?

**Routing and ordering**
- Were all Traffic Class values within an established VC range?
- Were Message TLPs (PME_TO_Ack, ERR_FATAL, etc.) correctly routed?
- Were Type 1 Config Requests only generated by Root Port or upstream switches?
- Was Relaxed Ordering appropriate for the platform coherency model?

## Background

PCIe Transaction Layer Packets (TLPs) carry configuration, memory, I/O, and message traffic.
Key error conditions relevant to debug:

- **UR (Unsupported Request)**: The target device does not support the requested operation.
  Common cause: accessing a register offset that does not exist in the device.
- **CA (Completer Abort)**: The target device encountered a fatal error processing the request.
- **CRS (Configuration Retry Status)**: The device is not yet ready; the requester should retry.
  Windows uses CRS for device readiness polling during enumeration.
- **Poisoned TLP**: The EP (Error Poisoning) bit is set, indicating the data payload is corrupt.
  Propagates through switches; must produce AER error.
- **Completion Timeout**: The requester sent a Non-Posted request but never received a
  Completion. Windows detects this as a device hang and may trigger BSOD (0x9F or 0xA0).

## Required evidence fields (`checks.pcie_tlp_report`)

- `non_sc_completion_observed`: boolean — was any Completion with UR/CA/CRS status seen?
- `poisoned_tlp_observed`: boolean — was any Poisoned TLP (EP=1) seen?
- `cfgrd_without_cpld_observed`: boolean — was any CfgRd with no corresponding CplD seen?
- `memory_access_to_unassigned_bar`: boolean — were MRd/MWr to un-BAR-assigned ranges seen?
- `total_tlp_count`: integer — total TLPs observed in capture

## Conditionally required fields

- `non_sc_completion_types`: array of strings — types observed (e.g. ["UR", "CRS"])
  (required when `non_sc_completion_observed = true`)
- `non_sc_completion_explanation`: string — explanation of each non-SC status
  (required when `non_sc_completion_observed = true`)
- `poisoned_tlp_aer_logged`: boolean — was AER Uncorrectable Error logged for the Poisoned TLP?
  (required when `poisoned_tlp_observed = true`)
- `completion_timeout_requester_ids`: array of strings — IDs of timed-out requesters
  (required when `cfgrd_without_cpld_observed = true`)
- `notes`: array of strings

## Contract rules

- `PCIE5-TLP-001`: If `non_sc_completion_observed = true` and `non_sc_completion_explanation`
  is absent or empty, this is a hard stop.
- `PCIE5-TLP-002`: If `poisoned_tlp_observed = true` and `poisoned_tlp_aer_logged = false`,
  this is a hard stop.
- `PCIE5-TLP-003`: If `memory_access_to_unassigned_bar = true`, this is a hard stop.
- `PCIE5-TLP-004` (warn): If `cfgrd_without_cpld_observed = true`, warn for potential
  Completion Timeout; check device BSOD code (0x9F / 0xA0 = power management timeout,
  0xA = IRQL fault if the Completion arrived late).
- `PCIE5-TLP-005` (warn): If CRS appears in `non_sc_completion_types` more than once,
  warn for device readiness issue.

## Completion Status reference

| Status | Code | Meaning |
|--------|------|---------|
| SC | 000b | Successful Completion — normal |
| UR | 001b | Unsupported Request — target does not support the operation |
| CRS | 010b | Configuration Retry Status — device not yet ready |
| CA | 100b | Completer Abort — fatal error at target |

## Reviewer prompts

- Were non-SC Completions present? UR suggests bad register access; CA suggests device error.
- Was Poisoned TLP propagated through a switch? Did AER catch it?
- Which CfgRd requests had no corresponding CplD? What address/register was being read?
- Were all MRd/MWr addresses within BAR-assigned ranges?
- If Completion Timeout is suspected, what BSOD code was generated by Windows?
