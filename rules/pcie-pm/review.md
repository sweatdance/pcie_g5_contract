# PCIe Power Management Rule Pack

Rule pack: `pcie-pm`

## Rule basis

- Require explicit PM state evidence for any power management claim.
- Treat PM L1 entry before enumeration completes as a hard-stop violation.
- Require ASPM configuration evidence showing both sides agreed before L1 entry.
- Treat PM_Active_State_Request_L1 without a prior successful VID/DID read as a violation.
- Do not infer safe L1 entry from PM_Request_Ack alone when enumeration state is unknown.

## Hard-stop rules

- `PCIE5-PM-001`: PM_Active_State_Request_L1 must not occur before enumeration is confirmed
  complete (CfgRd 0x000 VID/DID acknowledged by the host). If PM L1 is observed without
  a prior VID/DID read, this is a hard stop.
- `PCIE5-PM-002`: ASPM L1 bits in Link Control (offset 0x090h bits[1:0]) must be explicitly
  written by the host before GL9767 can initiate L1. If ASPM was never enabled by CfgWr and
  PM_Active_State_Request_L1 is still present, this is a hard stop (unexpected L1 trigger path).
- `PCIE5-PM-003`: PM_Request_Ack sent by downstream port while the link is in the enumeration
  window (between first Link Up and first successful CfgRd 0x000) is a hard stop.

## Warn rules

- `PCIE5-PM-004`: L1.1 / L1.2 entry path (CLKREQ# de-assertion) requires explicit CLKREQ#
  evidence; absence of scope data makes L1.2 classification inconclusive (warn only).
- `PCIE5-PM-005`: Multiple consecutive PM L1 cycles (>3 in <100ms) after enumeration completes
  may indicate excessive idle timer sensitivity; warn for review.
- `PCIE5-PM-006`: CfgWr to Link Control (Reg=0x090) with ASPM bits enabled must be preceded
  by a CfgRd to the same register (read-modify-write pattern); bare write without prior read
  risks overwriting other fields (warn only).

## Review prompts

- Was VID/DID read (CfgRd 0x000) confirmed before the first PM_Active_State_Request_L1?
- What was the value written to Link Control (Reg=0x090) that enabled ASPM?
- Was PM_Request_Ack sent by the downstream port during the enumeration window?
- Did the host downstream port ASPM state match the device ASPM state at L1 entry time?
- Is L1.2 (CLKREQ#-based) a possibility given the observed PM L1 behavior?
