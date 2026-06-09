# PCIe Data Link Layer Rules

This contract slice enforces Data Link layer initialization, flow control sequencing,
ACK/NAK replay protocol, PM DLLP ordering, and sequence number management.

## Background

The PCIe Data Link Layer (DLL) sits between the Physical layer and Transaction layer. Its
responsibilities relevant to debug:

- **Flow Control (FC) initialization**: Before any TLPs can flow, both sides must complete
  the InitFC handshake. Only after InitFC1 + InitFC2 exchange does the DLL transition to
  DL_Active and TLP flow is allowed.
- **ACK/NAK protocol**: Every TLP is acknowledged by an ACK DLLP (or NAK if corrupted).
  NAK triggers replay from the sender. Replay timer controls the maximum wait for ACK.
- **REPLAY_NUM**: 2-bit counter incremented per replay attempt. Rolling over from 11b to
  00b (4 consecutive replays) forces the LTSSM into Recovery state.
- **UpdateFC**: After initial FC credit exchange, UpdateFC DLLPs are sent periodically to
  refresh credit availability to the remote transmitter.
- **PM DLLPs**: Power Management DLLPs (PM_Active_State_Request_L1, PM_Request_Ack,
  PM_Enter_L1, PM_Enter_L23, PM_Turn_Off, PME_TO_Ack) must only appear after DL_Active.

---

## DLLP Type Reference

All DLLPs are 8 bytes: Type (1B) + Payload (4B) + CRC16 (2B) + End (1B).

| DLLP Type Code | Name | Direction | Notes |
|----------------|------|-----------|-------|
| 0x00 | ACK | Either | Acknowledges TLPs up to AckNak_Seq_Num |
| 0x10 | NAK | Either | Requests replay from TLP with sequence = AckNak_Seq_Num+1 |
| 0x20–0x23 | InitFC1 (P/NP/Cpl/VC) | Either | Initial FC credit advertisement |
| 0x40–0x43 | InitFC2 (P/NP/Cpl/VC) | Either | Echo of InitFC1; confirms mutual agreement |
| 0x30–0x33 | UpdateFC (P/NP/Cpl/VC) | Either | Periodic credit refresh |
| 0x02 | PM_Enter_L1 | DS→US | Downstream port requests L1 entry |
| 0x03 | PM_Enter_L23 | DS→US | Downstream port requests L2/L3 (power removal) |
| 0x04 | PM_Active_State_Request_L1 | US→DS | Upstream (device) requests ASPM L1 |
| 0x05 | PM_Request_Ack | DS→US | Downstream ACKs ASPM L1 request |
| 0x06 | PM_Turn_Off | DS→US | Root Complex signals power removal (S3/S5) |
| 0x07 | PME_TO_Ack | US→DS | Device acknowledges PM_Turn_Off |
| 0x30 | Vendor Defined Type 0 | — | Vendor-specific DLLP |

### ACK / NAK DLLP Format

| Byte(s) | Field | Notes |
|---------|-------|-------|
| 0 | Type | 0x00=ACK, 0x10=NAK |
| 1–2 | Reserved | Must be zero |
| 3–4 | AckNak_Seq_Num[11:0] | 12-bit sequence number; ACK confirms all TLPs ≤ this seq |
| 5–6 | CRC16 | Polynomial: 0x100B |
| 7 | End | 0xAA (end of DLLP) |

### UpdateFC DLLP Format

| Byte(s) | Field | Notes |
|---------|-------|-------|
| 0 | Type | 0x30 (Posted), 0x31 (Non-Posted), 0x32 (Completion), 0x33 (VC1+) |
| 1 | HdrFC[7:0] | Header credits available (infinite = 0x7F) |
| 2 | HdrFC[1:0] + DataFC[11:6] | |
| 3 | DataFC[5:0] | Data credits available (infinite = 0xFFF) |
| 4–5 | CRC16 | |
| 6 | End | |

---

## FC Credit Types and Initialization States

Three FC credit types, each tracked independently:

| FC Type | TLP Types Covered | Infinite Credit Value |
|---------|-------------------|----------------------|
| Posted (P) | MWr, Message | HdrFC=0x7F, DataFC=0xFFF |
| Non-Posted (NP) | MRd, CfgRd, CfgWr, IO | HdrFC=0x7F, DataFC=0 (NP has no data) |
| Completion (Cpl) | CplD, Cpl | HdrFC=0x7F, DataFC=0xFFF |

**Initialization sequence**:
```
SDS (Start of Data Stream symbol — Physical Layer up)
  ↓
InitFC1 (both directions) — advertise available credits
  ↓
InitFC2 (both directions) — echo/confirm InitFC1 values
  ↓
DL_Active: TLP flow permitted for each type where both sides completed InitFC
  ↓
UpdateFC (periodic) — credit refresh
```

**IMPORTANT**: InitFC2 with infinite credit values (0x7F HdrFC) means the *advertising* side
accepts unlimited credits of that type from the *other* side. This does NOT mean the sender
has unlimited credits; it means the receiver can accept unlimited TLPs of that type.

---

## ACK/NAK and Replay Buffer Mechanism

### Sequence Number Space

- 12-bit sequence number: 0x000 to 0xFFF (wrap at 0xFFF → 0x000)
- Each new TLP (CfgRd, CfgWr, MRd, MWr, etc.) is assigned the next sequence number
- Receiver ACKs by sending ACK DLLP with AckNak_Seq_Num = highest in-order received TLP

### Replay Buffer Window

- Maximum 2048 unacknowledged TLPs outstanding at once (REPLAY_BUFFER_MAX = 2048)
- If ACK not received before REPLAY_TIMER expires, sender replays oldest unacknowledged TLP
- REPLAY_TIMER: configurable; typically 200µs for Gen1, 100µs for Gen2, 50µs for Gen3

### REPLAY_NUM Counter

| REPLAY_NUM | State |
|-----------|-------|
| 00 | First attempt (no replay yet) |
| 01 | First replay |
| 10 | Second replay |
| 11 | Third replay |
| Rollover (11→00) | **Recovery state**: LTSSM must enter Recovery |

**REPLAY_NUM rollover** triggers the Physical Layer to initiate link Recovery. After
successful Recovery, REPLAY_NUM resets to 00 and replay restarts from the beginning.
Failure to enter Recovery after REPLAY_NUM rollover = DLL protocol violation.

---

## PM DLLP Ordering Rules

PM DLLPs must occur only after DL_Active (InitFC complete in both directions):

```
DL_Active established
  ↓
Device → PM_Active_State_Request_L1 [ASPM: device requests L1 entry]
  ↓  (host may reject by sending PM DLLP NAK or ignoring)
Host → PM_Request_Ack [host agrees to L1; link enters L1]
  ↓
... link in L1 ...
  ↓
Exit L1: either side drives FTS (Fast Training Sequence) to request L0
```

PM DLLP before DL_Active (before InitFC complete) = ordering violation.
PM_Active_State_Request_L1 during enumeration window (before VID/DID CfgRd complete)
= root cause of GL9767 BSOD (covered by pcie-pm hard-stop rules).

---

## DLLP CRC16 Error

DLLP CRC polynomial: x^16 + x^12 + x^5 + 1 (same as USB CRC16).
CRC error in a DLLP causes the receiver to discard the DLLP (not generate NAK for DLLP
errors, unlike TLP NAK). Multiple DLLP CRC errors indicate physical layer signal degradation.

---

## Required Evidence Fields (`checks.pcie_dll_report`)

```yaml
# Mandatory
initfc_complete: boolean
dl_up_confirmed: boolean
nak_observed: boolean
nak_followed_by_replay: boolean
updatefc_observed: boolean
capture_duration_ms: number

# FC initialization detail
initfc_direction_evidence: string         # "both_directions" | "upstream_only" | "downstream_only"
initfc_credit_type_all_initialized: boolean  # Were P/NP/Cpl all initialized?

# ACK/NAK detail
nak_count: integer
replay_timer_timeout_count: integer
replay_num_rollover_observed: boolean     # REPLAY_NUM reached 11b→00b
replay_num_rollover_recovery_confirmed: boolean  # Link entered Recovery after rollover

# Sequence numbers
sequence_number_wrap_observed: boolean    # 12-bit seq num wrapped 0xFFF→0x000
ack_seq_progression_consistent: boolean  # Monotonically increasing ACK seq nums

# PM DLLP ordering
pm_dllp_before_dl_up: boolean             # PM DLLP observed before InitFC complete
pm_active_state_request_count: integer

# DLLP CRC errors
dllp_crc_error_count: integer
repeated_initfc2_count: integer           # CATC artifact: repeated identical InitFC2

notes: array[string]
```

---

## Reviewer Prompts

**FC initialization**
- Were InitFC1 and InitFC2 observed in both Downstream and Upstream directions?
- Were Posted, Non-Posted, and Completion credits all initialized before their TLP types?
- Was the first TLP observed after InitFC2 completion?

**Replay and sequence numbers**
- Were NAK DLLPs present? Was each followed by a replay?
- Did REPLAY_NUM roll over? Did the link enter Recovery?
- Did the 12-bit sequence number wrap? Was the replay buffer drained first?

**PM DLLP ordering**
- Were PM DLLPs only sent after DL_Active?
- How many PM_Active_State_Request_L1 DLLPs were observed? Before or after VID/DID read?

**CATC artifacts**
- Are repeated InitFC2 values (identical VC/FC) consistent with CATC frequency-lock artifacts
  at link build-up? (Not real FC errors; common with CATC analyzers on Gen1/Gen2 links)

## Background

The PCIe Data Link Layer (DLL) sits between the Physical layer and Transaction layer. Its
responsibilities relevant to debug:

- **Flow Control (FC) initialization**: Before any TLPs can flow, both sides must complete
  the InitFC handshake (InitFC1 → InitFC2 exchange in both directions). Only after this
  handshake does the DLL transition to DL_Up and TLP flow is allowed.
- **ACK/NAK protocol**: Every TLP is acknowledged by an ACK DLLP (or NAK if corrupted).
  A NAK triggers a replay from the sender. Excessive NAKs indicate signal integrity issues.
- **UpdateFC**: After initial FC credit exchange, UpdateFC DLLPs are sent periodically to
  refresh credit availability. Absence of UpdateFC in a long capture may indicate filtering
  or starvation.
- **CATC artifact warning**: Repeated InitFC2 with identical values is a known CATC
  frequency-lock artifact during initial training and should not be treated as real FC errors
  without further evidence.

## Required evidence fields (`checks.pcie_dll_report`)

- `initfc_complete`: boolean — were InitFC1 + InitFC2 DLLPs observed in both directions?
- `dl_up_confirmed`: boolean — was DL_Up (post-SDS + InitFC) confirmed before first TLP?
- `nak_observed`: boolean — was any NAK DLLP observed in the capture?
- `nak_followed_by_replay`: boolean — if NAK observed, was a subsequent replay sequence seen?
- `updatefc_observed`: boolean — were UpdateFC DLLPs present in the capture?
- `capture_duration_ms`: number — duration of the capture in milliseconds (for UpdateFC context)

## Conditionally required fields

- `initfc_direction_evidence`: string — description of which directions InitFC was seen
  ("upstream_only", "downstream_only", "both_directions")
- `nak_count`: integer — number of NAK DLLPs observed (required when `nak_observed = true`)
- `repeated_initfc2_count`: integer — number of InitFC2 repetitions with identical values
  (required when > 3 repetitions detected)
- `notes`: array of strings

## Contract rules

- `PCIE5-DLL-001`: If `dl_up_confirmed = false` but TLPs are present, this is a hard stop.
  TLPs cannot appear before DL layer is active.
- `PCIE5-DLL-002`: If `nak_observed = true` and `nak_followed_by_replay = false`, this is
  a hard stop. NAK without replay violates the DL retransmission protocol.
- `PCIE5-DLL-003` (warn): If `updatefc_observed = false` and `capture_duration_ms > 200`,
  warn for possible FC starvation or capture filtering.
- `PCIE5-DLL-004` (warn): If `repeated_initfc2_count > 3`, warn. These may be CATC
  frequency-lock artifacts (see CATC Tip #2); do not treat as definitive FC errors.
- `PCIE5-DLL-005` (warn): If `nak_count > 5` in a single capture, warn for signal integrity
  review.

## InitFC sequence reference

```
Physical Link Up (SDS)
    ↓
InitFC1 (DS→US): VC0 Posted/Non-Posted/Completion credit advertisement
InitFC1 (US→DS): VC0 credit advertisement
    ↓
InitFC2 (DS→US): Echo of InitFC1 values
InitFC2 (US→DS): Echo
    ↓
DL_Up: TLP flow now permitted
    ↓
UpdateFC (periodic): Credit refresh
```

## Reviewer prompts

- Were InitFC1 and InitFC2 seen in both Downstream and Upstream directions?
- Was the first TLP (CfgRd/MRd) observed after InitFC completion?
- Were there NAK DLLPs, and was each followed by a replay?
- Are repeated InitFC2 values likely CATC artifacts (check if they appeared at link build-up)?
- Was UpdateFC observed in the capture duration?
