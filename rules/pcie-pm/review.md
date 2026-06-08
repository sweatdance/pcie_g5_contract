# PCIe Power Management Rule Pack

Rule pack: `pcie-pm`

## Rule basis

- Require explicit PM state evidence for any power management claim.
- Treat PM L1 entry before enumeration completes as a hard-stop violation.
- Require ASPM configuration evidence showing both sides agreed before L1 entry.
- Require D-state transitions to be consistent with PM Capability constraints.
- Require L1 PM Substates (L1.1/L1.2) configuration to be verified before substate entry.
- Require PME events to have a traceable source and OS-visible PME_Status clearing.
- Treat PM_Active_State_Request_L1 without a prior successful VID/DID read as a violation.

## Hard-stop rules

- `PCIE5-PM-001`: PM_Active_State_Request_L1 must not occur before enumeration is confirmed
  complete (CfgRd 0x000 VID/DID acknowledged by the host). PM L1 before enumeration = hard stop.
- `PCIE5-PM-002`: ASPM L1 bits in Link Control (0x090h bits[1:0]) must be explicitly written
  by the host before GL9767 can initiate L1. Unexpected PM L1 with no CfgWr to 0x090 = hard stop.
- `PCIE5-PM-003`: PM_Request_Ack sent by downstream port during the enumeration window
  (between first Link Up and first VID/DID CfgRd) = hard stop.
- `PCIE5-PM-007` (hard stop): D-state write (CfgWr PMCSR) requesting D1 or D2 when the
  device's PM Capabilities register shows D1/D2 are not supported is a hard stop.
- `PCIE5-PM-008` (hard stop): PMCSR write targeting D3hot (PowerState=11b) while a
  non-zero Transactions Pending bit (Device Status) is observed = hard stop. The device
  must complete or abort all transactions before entering D3hot.

## Warn rules — ASPM (L0s / L1)

- `PCIE5-PM-004` (warn): L1.1 / L1.2 entry path (CLKREQ# de-assertion) requires explicit
  CLKREQ# scope evidence. Absence makes L1.2 classification inconclusive.
- `PCIE5-PM-005` (warn): More than 3 PM L1 cycles within 100ms after enumeration completes
  may indicate excessive ASPM idle timer sensitivity.
- `PCIE5-PM-006` (warn): CfgWr to Link Control 0x090 with ASPM bits set must be preceded by
  a CfgRd to the same register (read-modify-write). Bare write risks overwriting reserved bits.
- `PCIE5-PM-009` (warn): L0s entry (via EIEOS) requires both ports to have L0s Acceptable
  Latency values compatible with their respective FC and Replay Timer limits. L0s enabled
  without latency verification warns.

## Warn rules — D-state transitions

- `PCIE5-PM-010` (warn): D3hot→D0 transition must be followed by a reset recovery period
  (Trst ≥ 1ms, implementation-dependent up to 100ms) before link training begins.
  CfgRd immediately following D0 write without observed link re-training warns.
- `PCIE5-PM-011` (warn): PME_Status bit in PMCSR must be cleared (CfgWr write-1-to-clear)
  by the OS after a PME event is processed. Stale PME_Status blocks subsequent PME delivery.
- `PCIE5-PM-012` (warn): PME_En bit must only be set while the device is in D0, D1, D2,
  or D3hot, and only when PME_Support in PM Capabilities confirms PME from that D-state.
  PME_En set while in an unsupported D-state warns.

## Warn rules — L1 PM Substates (L1.1 / L1.2)

- `PCIE5-PM-013` (warn): ASPM L1.2 Enable in L1 PM Substates Control 1 must only be set
  when both sides confirm ASPM L1.2 Supported in their L1 PM Substates Capabilities.
  Asymmetric or unchecked L1.2 Enable warns.
- `PCIE5-PM-014` (warn): T_POWER_ON in L1 PM Substates Control 2 must be programmed to
  at least the device's Port T_POWER_ON from its L1 PM Substates Capabilities.
  Under-programming causes L1.2 exit failures (link cannot restore in time).
- `PCIE5-PM-015` (warn): LTR_L1.2_Threshold in L1 PM Substates Control 1 must be set to
  a non-zero value unless the system design intentionally allows unconditional L1.2 entry
  regardless of service latency requirements.
- `PCIE5-PM-016` (warn): Common_Mode_Restore_Time in L1 PM Substates Control 1 must match
  the endpoint's reported Port Common Mode Restore Time in Capabilities. Mismatch causes
  L1.1 exit failures.

## Warn rules — PME_Turn_Off sequence

- `PCIE5-PM-017` (warn): PME_Turn_Off message (Root Complex to device) must be acknowledged
  by PME_TO_Ack (device to Root Complex) before the RC powers down the slot. Missing
  PME_TO_Ack in a planned power-down capture warns.

## Review prompts — ASPM

- Was VID/DID CfgRd confirmed before the first PM_Active_State_Request_L1?
- What was written to Link Control 0x090 to enable ASPM?
  - 0x00000040: Clock PM on, ASPM disabled (safe initial state)
  - 0x00000042: ASPM L1 enabled (bit1=1, activates HW idle timer)
- Was PM_Request_Ack sent during the enumeration window?

## Review prompts — D-states

- Were D1/D2 states claimed while PM Capabilities shows they are not supported?
- Was a D3hot→D0 transition observed, and was sufficient delay present before link re-use?
- Was PME_Status cleared after PME processing?
- Was PME_En set from a D-state where PME delivery is not supported?

## Review prompts — L1 PM Substates

- Were L1 PM Substates Capabilities read from both sides before L1.1/L1.2 was enabled?
- Was T_POWER_ON programmed to at least the device's required value?
- Was LTR_L1.2_Threshold set to a meaningful non-zero value?
- Was Common_Mode_Restore_Time consistent with the endpoint's capability?
