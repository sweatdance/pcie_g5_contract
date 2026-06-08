# PCIe Power Management Rules

This contract slice enforces reviewer-visible evidence for PCIe power state transitions,
ASPM configuration, and PM L1 entry/exit sequencing.

## Background

PCIe ASPM (Active State Power Management) allows a device to request entry into L0s or L1
low-power states when the link is idle. The key properties that affect debug:

- **GL9767 HW default**: ASPM = DISABLED at reset. ASPM activates only after the host writes
  the Link Control register (config space offset 0x090h, bits[1:0]) with ASPM enable bits.
- **L1 negotiation**: GL9767 sends `PM_Active_State_Request_L1` upstream. The host downstream
  port must ACK with `PM_Request_Ack` for L1 entry to proceed. If the host port has ASPM
  disabled, it will not ACK and the link stays in L0.
- **Enumeration dependency**: A device cannot be safely power-managed before the OS has
  completed enumeration (identified VID/DID via CfgRd 0x000). L1 entry before enumeration
  is complete causes device loss.

## Required evidence fields (`checks.pcie_pm_report`)

- `enumeration_complete`: boolean — was CfgRd 0x000 (VID/DID) acknowledged before PM L1?
- `pm_l1_observed`: boolean — was PM_Active_State_Request_L1 seen in the capture?
- `aspm_enabled_by_cfgwr`: boolean — was CfgWr to Link Control (Reg=0x090) with ASPM bits
  set observed before the PM L1 request?
- `link_control_aspm_value`: string (hex) — the data value written to Reg=0x090 (e.g. "0x00000042")
- `pm_request_ack_in_enum_window`: boolean — was PM_Request_Ack sent during the enumeration
  window (before first successful CfgRd 0x000)?

## Conditionally required fields

- `aspm_enable_timestamp`: string — timestamp of the CfgWr that enabled ASPM (required when
  `aspm_enabled_by_cfgwr = true`)
- `pm_l1_timestamp`: string — timestamp of first PM_Active_State_Request_L1 (required when
  `pm_l1_observed = true`)
- `vidpid_read_timestamp`: string — timestamp of first CfgRd 0x000 completion (required when
  `enumeration_complete = true`)
- `l1_cycle_count`: integer — number of PM L1 cycles observed in the capture
- `clkreq_evidence`: string — CLKREQ# scope data if available; "not_captured" if absent

## Contract rules

- `PCIE5-PM-001`: If `pm_l1_observed = true` and `enumeration_complete = false`, this is a
  hard-stop violation. PM L1 must not interrupt enumeration.
- `PCIE5-PM-002`: If `pm_l1_observed = true` and `aspm_enabled_by_cfgwr = false`, this is a
  hard-stop violation. An unexpected PM L1 trigger path must be identified.
- `PCIE5-PM-003`: If `pm_request_ack_in_enum_window = true`, this is a hard-stop violation.
  The host downstream port ACKed L1 while enumeration was in progress.
- `PCIE5-PM-004` (warn): If `l1_cycle_count > 3` within 100ms after enumeration completes,
  warn for excessive idle timer sensitivity review.
- `PCIE5-PM-005` (warn): If CfgWr to Reg=0x090 enabling ASPM was not preceded by a CfgRd
  to the same register, warn for missing read-modify-write pattern.

## Reviewer prompts

- Was VID/DID (CfgRd 0x000) confirmed before the first PM L1 request?
- What value was written to Link Control Reg=0x090 and when?
  - Data=0x00000040: Clock PM on, ASPM disabled (safe)
  - Data=0x00000042: ASPM L1 enabled (bit1=1, activates GL9767 HW idle timer)
- Did the host downstream port ASPM state match device ASPM capability at L1 entry?
- Is L1.2 (CLKREQ# path) also active? This cannot be determined from CATC alone without
  scope evidence on the CLKREQ# pin.
- How many PM L1 cycles occurred, and was this after or before enumeration completed?

## Example compliant JSON report

```json
{
  "schema_version": "1.0",
  "enumeration_complete": true,
  "pm_l1_observed": true,
  "aspm_enabled_by_cfgwr": true,
  "link_control_aspm_value": "0x00000042",
  "pm_request_ack_in_enum_window": false,
  "aspm_enable_timestamp": "0011.006736s",
  "pm_l1_timestamp": "0011.100188s",
  "vidpid_read_timestamp": "0009.919538s",
  "l1_cycle_count": 6,
  "clkreq_evidence": "not_captured",
  "notes": ["PM L1 occurs 93ms after ASPM enabled; enumeration was complete"]
}
```

## Example violation JSON report

```json
{
  "schema_version": "1.0",
  "enumeration_complete": false,
  "pm_l1_observed": true,
  "aspm_enabled_by_cfgwr": true,
  "link_control_aspm_value": "0x00000042",
  "pm_request_ack_in_enum_window": true,
  "notes": ["PM L1 during enumeration window - host ACKed before VID/DID was read"]
}
```
