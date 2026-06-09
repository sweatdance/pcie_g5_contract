# PCIe Data Link Layer Rule Pack

Rule pack: `pcie-dll`

## Rule basis

- Require InitFC1/InitFC2 exchange evidence before claiming Data Link layer is active (DL_Up).
- Treat TLPs observed before DL_Up as hard-stop violations.
- Require NAK DLLPs to be followed by replay evidence.
- Require REPLAY_NUM rollover to be followed by link Recovery state.
- Require PM DLLPs (PM_Active_State_Request_L1) to appear only after DL_Up.
- Warn when UpdateFC DLLPs are absent in captures long enough to expect them.
- Warn when DLLP CRC errors appear without DL re-synchronization.
- Treat REPLAY_NUM rollover without subsequent Recovery as a hard stop.

## Hard-stop rules

- `PCIE5-DLL-001`: TLPs (CfgRd, CfgWr, MRd, MWr, Cpl) must not appear before InitFC exchange
  completion (both InitFC1 and InitFC2 observed in both directions). TLP before DL_Up = hard stop.
- `PCIE5-DLL-002`: NAK DLLP must be followed by a replay sequence (retransmission of the
  NACK'd TLP). NAK without subsequent replay is a hard stop.
- `PCIE5-DLL-007` (hard stop): REPLAY_NUM reaching 3 (rollover from 11b to 00b) causes the
  LTSSM to enter Recovery. If REPLAY_NUM overflow is observed and link does not enter Recovery,
  the DL layer state machine is in violation.

## Warn rules — FC initialization and UpdateFC

- `PCIE5-DLL-003` (warn): UpdateFC DLLPs absent in captures longer than 200ms after DL_Up
  may indicate FC credit starvation or capture filtering.
- `PCIE5-DLL-004` (warn): InitFC1 or InitFC2 with identical VC/FC values repeated more than
  3 times is consistent with DL re-init or CATC frequency-lock decode artifact.
- `PCIE5-DLL-009` (warn): FC credit type not yet at FI (Infinite) credit state before the
  first TLP of that type flows. Posted, Non-Posted, and Completion credits must each be
  initialized before the corresponding TLP type can flow.

## Warn rules — ACK/NAK and sequence numbers

- `PCIE5-DLL-005` (warn): NAK count > 5 in a single capture warns for signal integrity review.
- `PCIE5-DLL-006` (warn): ACK DLLP sequence number must be within the valid Replay Buffer
  Window (up to 2048 unacknowledged TLPs). Out-of-window ACK (AckNak_Seq_Num below the
  oldest unacknowledged TLP seq) warns for DL protocol state confusion.
- `PCIE5-DLL-010` (warn): Sequence number 12-bit wrap (0xFFF → 0x000) during active TLP flow
  without observable replay buffer drain event warns for potential TLP sequence tracking loss.

## Warn rules — DLLP CRC and PM DLLPs

- `PCIE5-DLL-008` (warn): DLLP CRC16 error (detected by receiver) without subsequent
  DL re-synchronization (ACK retransmit or link recovery) warns for signal integrity.
- `PCIE5-DLL-011` (warn): PM DLLP (PM_Active_State_Request_L1 or PM_Enter_L1) observed before
  DL_Up is confirmed (before InitFC complete) is a PM sequence ordering violation.

## Review prompts — FC initialization

- Were InitFC1 and InitFC2 observed in both Downstream and Upstream directions?
- Was the first TLP observed after InitFC completion?
- Were Posted, Non-Posted, and Completion credits all initialized before their TLP types flowed?

## Review prompts — Replay and sequence numbers

- Were there NAK DLLPs? Was each followed by a replay?
- Did REPLAY_NUM reach 3 (rollover)? Did the link enter Recovery?
- Did the 12-bit sequence number wrap, and was there evidence of correct replay buffer drain?
- Were ACK sequence numbers monotonically increasing within the replay window?

## Review prompts — DLLP types and PM ordering

- Were PM DLLPs (PM_Active_State_Request_L1) observed only after DL_Up?
- Were DLLP CRC errors present? Were they recovered without link reset?
- Are repeated InitFC2 values likely CATC artifacts (appeared at link build-up)?
