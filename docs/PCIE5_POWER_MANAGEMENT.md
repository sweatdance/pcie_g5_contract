# PCIe Power Management Rules

This contract slice enforces reviewer-visible evidence for PCIe power state transitions,
D-state management, ASPM configuration, L1 PM Substates, and PME event sequencing.

## Background

PCIe power management has three orthogonal mechanisms:

1. **D-states** (Device Power States): Controlled by writing the PMCSR register in the
   PM Capability structure. D0=fully on, D3hot=main power off but config space accessible,
   D3cold=all power removed. These are software-initiated transitions.

2. **ASPM** (Active State Power Management): Hardware-controlled link idle states.
   L0s=partial idle, L1=deep idle. Initiated by the device after the host writes
   Link Control [ASPM bits]. No OS intervention for individual L1 cycles.

3. **L1 PM Substates** (L1.1 / L1.2): Extension of ASPM L1 that uses CLKREQ# deassertion
   to gate the reference clock. Configured via L1 PM Substates Extended Capability.
   L1.2 requires both sides to de-assert CLKREQ# and removes the reference clock.

**GL9767 HW default**: ASPM = DISABLED at reset. ASPM activates only after the host writes
Link Control (offset 0x090h, bits[1:0]) with ASPM enable bits.

---

## D-State Reference

### D0 — Fully Operational

- Device fully powered and functional
- All registers accessible; memory and I/O transactions supported
- No restrictions on operation

### D1 — Low Power (if supported)

- Most context preserved; power reduced
- Config space accessible; memory and I/O transactions not required to work
- PME supported if PME_Support bit3=1 in PM Capabilities
- Recovery time: Tpme_restore ≤ 1ms typical

### D2 — Lower Power (if supported, rare)

- More context may be lost than D1
- Config space accessible; device may not respond to memory transactions
- Recovery time: Tpme_restore ≤ 4ms typical

### D3hot — Deepest Software-Accessible State

- Main power removed but Vaux/Vcca still present
- Config space accessible (mandatory by spec)
- Memory and I/O transactions not supported
- Transactions Pending (Device Status bit5) must be 0 before writing D3hot
- No_Soft_Reset bit in PMCSR: if 0, device resets all state; if 1, device retains config state
- PME supported if PME_Support bit4=1 in PM Capabilities
- **Recovery**: After writing PMCSR PowerState=00b (D0), device needs Trst before use
  - Trst range: 1ms minimum (spec); many devices require 10–100ms
  - Monitor Transactions Pending before re-use

### D3cold — Power Removed

- All power removed (including Vaux)
- No config space access possible
- Requires full hardware power cycle and OS re-enumeration on return to D0
- PME supported only via dedicated wake signal (PME#/WAKE# pin)
- PME_En cannot be meaningfully set while in D3cold (register not writable)

---

## Power Management Capability Registers

### PM Capabilities Register (at PM cap base + 2)

| Bit | Field | Meaning |
|-----|-------|---------|
| [2:0] | Version | 011b = PM spec 1.2 (required for PCIe) |
| 3 | PME Clock | 1 = device requires clock for PME (uncommon for PCIe) |
| 5 | DSI | Device-Specific Initialization required |
| [8:6] | Aux_Current | Vaux current required (0=0mA, 1=55mA, …) |
| 9 | D1_Support | 1 = D1 state supported |
| 10 | D2_Support | 1 = D2 state supported |
| [15:11] | PME_Support | Bit per D-state: bit11=D0, 12=D1, 13=D2, 14=D3hot, 15=D3cold |

### PMCSR — PM Control / Status Register (at PM cap base + 4)

| Bit | Field | Description |
|-----|-------|-------------|
| [1:0] | PowerState | 00=D0, 01=D1, 10=D2, 11=D3hot |
| 3 | No_Soft_Reset | 1 = no internal reset on D3hot→D0 |
| 8 | PME_En | 1 = enable PME assertion from current D-state |
| [12:9] | Data_Select | Selects PM data source |
| [14:13] | Data_Scale | Scaling factor for Data |
| 15 | PME_Status | 1 = PME was asserted; write 1 to clear |

**Write sequence for D-state transition**:
1. Read PMCSR (confirm current state)
2. Verify Transactions Pending = 0 (Device Status bit5)
3. Write PMCSR PowerState = target state
4. For D3hot→D0: wait Trst, then confirm link re-training complete

---

## ASPM L0s

- Entry: device de-asserts TX idle, sends EIEOS (Electrical Idle Exit Ordered Set)
- Both sides must support L0s (Link Capabilities bit10)
- L0s can be enabled independently of L1 via Link Control bits[1:0] = 01b
- Exit latency: sub-µs to few µs; lower than L1
- Not applicable to GL9767 by default (ASPM disabled at reset; L0s less common)

---

## ASPM L1 (Background)

- Entry: device sends PM_Active_State_Request_L1; host must ACK with PM_Request_Ack
- Host controls via Link Control 0x090 bits[1:0]: 10b=L1 only, 11b=L0s+L1
- Exit: either side requests L0 via FTS (Fast Training Sequences)
- GL9767 ASPM default: disabled at reset; activated only after CfgWr to 0x090

---

## L1 PM Substates (L1.1 / L1.2)

Extends ASPM L1 with CLKREQ# hardware gating.

### L1.1

- CLKREQ# de-asserted but reference clock still active in platform
- Vcc1.8 maintained; common mode reference clock maintained
- Exit latency: ~5–10µs
- Configured via L1 PM Substates Control 1 bits: ASPM L1.1 Enable (bit3)

### L1.2

- CLKREQ# de-asserted AND reference clock removed by platform
- Vcc1.8 removed; deepest L1 substate (maximum power savings)
- Exit requires: clock restore + common mode restore + link training
- Exit latency: hundreds of µs to ms
- Configured via L1 PM Substates Control 1 bits: ASPM L1.2 Enable (bit2)
- Requires: Enable Clock PM in Link Control (bit8=1) on both sides
- **CATC note**: L1.2 entry/exit NOT directly visible in CATC; requires CLKREQ# scope

### L1 PM Substates Capability Register (at extended cap base + 4)

| Bit | Field | Meaning |
|-----|-------|---------|
| 0 | PCI-PM L1.2 Supported | PMCSR-triggered L1.2 |
| 1 | PCI-PM L1.1 Supported | PMCSR-triggered L1.1 |
| 2 | ASPM L1.2 Supported | CLKREQ#-based ASPM L1.2 |
| 3 | ASPM L1.1 Supported | CLKREQ#-based ASPM L1.1 |
| 4 | L1 PM Substates Supported | Summary bit |
| [15:8] | Port Common Mode Restore Time | µs for Vcc/clock stabilization |
| [19:16] | Port T_POWER_ON Scale | 0=2µs/unit, 1=10µs/unit, 2=100µs/unit |
| [24:20] | Port T_POWER_ON Value | Value × Scale = total T_POWER_ON time |

### L1 PM Substates Control 1 (at extended cap base + 8)

| Bit | Field | Description |
|-----|-------|-------------|
| 0 | PCI-PM L1.2 Enable | Enable PCI-PM L1.2 |
| 1 | PCI-PM L1.1 Enable | Enable PCI-PM L1.1 |
| 2 | ASPM L1.2 Enable | Enable ASPM L1.2 |
| 3 | ASPM L1.1 Enable | Enable ASPM L1.1 |
| [15:8] | Common Mode Restore Time | Must ≥ Port Common Mode Restore Time in Cap |
| [25:16] | LTR L1.2 Threshold | Encoded LTR threshold for gating L1.2 entry |

### L1 PM Substates Control 2 (at extended cap base + C)

| Bit | Field | Description |
|-----|-------|-------------|
| [1:0] | T_POWER_ON Scale | Must ≥ Port T_POWER_ON Scale in Capabilities |
| [6:2] | T_POWER_ON Value | Must ≥ Port T_POWER_ON Value in Capabilities |

---

## PME Event Flow

1. Device detects wakeup condition (internal or external)
2. Device sends **PM_PME TLP** upstream (if PME_En = 1 and D-state supports PME)
3. Root Complex asserts PME interrupt to OS (Root Status PME_Status bit)
4. OS reads device PME_Status in PMCSR
5. OS writes 1 to PME_Status to clear (write-1-to-clear)
6. OS transitions device from D3hot → D0 to resume operation

---

## PME_Turn_Off / PME_TO_Ack (System Power-Down)

Used during S3/S5 system sleep transition:

1. Root Complex sends **PME_Turn_Off** message downstream
2. Device completes all pending transactions
3. Device sends **PME_TO_Ack** message upstream (must be within 10ms per spec)
4. Root Complex de-asserts PCIe clock (device enters D3cold)

**Timeout**: RC must wait at most 10ms for PME_TO_Ack. If not received, RC may power down anyway.

---

## Required Evidence Fields (`checks.pcie_pm_report`)

```yaml
# ASPM evidence (existing fields)
enumeration_complete: boolean
pm_l1_observed: boolean
aspm_enabled_by_cfgwr: boolean
link_control_aspm_value: string     # hex value written to 0x090
pm_request_ack_in_enum_window: boolean
l1_cycle_count: integer
clkreq_evidence: string             # "not_captured" | "L1.1_confirmed" | "L1.2_confirmed"

# D-state evidence (new fields)
d_state_transition_observed: boolean
d_state_from: string                # "D0" | "D1" | "D2" | "D3hot"
d_state_to: string
pmcsr_written: boolean
pmcsr_value: string                 # hex; e.g. "0x0003" = D3hot
transactions_pending_zero: boolean  # Device Status bit5=0 before D3hot write
d3hot_to_d0_trst_observed: boolean

# PME evidence
pme_en_set: boolean
pme_status_cleared: boolean
pme_to_ack_observed: boolean

# L1 PM Substates evidence
l1_substate_mode: string            # "none" | "L1.1" | "L1.2" | "L1.1_and_L1.2"
l1pm_substates_configured: boolean
l1pm_control1_value: string         # hex
l1pm_control2_value: string         # hex
ltr_l1_2_threshold_nonzero: boolean
common_mode_restore_time_sufficient: boolean
t_power_on_programmed_correctly: boolean

# Optional
notes: array[string]
```

---

## Contract Rules Summary

| Rule ID | Type | Summary |
|---------|------|---------|
| PM-001 | Hard Stop | PM L1 before enumeration complete |
| PM-002 | Hard Stop | PM L1 without ASPM CfgWr |
| PM-003 | Hard Stop | PM_Request_Ack during enumeration window |
| PM-004 | Warn | L1.2 without CLKREQ# scope evidence |
| PM-005 | Warn | >3 L1 cycles in <100ms after enumeration |
| PM-006 | Warn | Link Control write without prior read |
| PM-007 | Hard Stop | D-state write to unsupported D1/D2 |
| PM-008 | Hard Stop | D3hot write with Transactions Pending ≠ 0 |
| PM-009 | Warn | L0s without exit latency verification |
| PM-010 | Warn | D3hot→D0 without Trst delay |
| PM-011 | Warn | PME_Status not cleared after PME event |
| PM-012 | Warn | PME_En set from unsupported D-state |
| PM-013 | Warn | ASPM L1.2 Enable without capability confirmation |
| PM-014 | Warn | T_POWER_ON under-programmed vs device cap |
| PM-015 | Warn | LTR_L1.2_Threshold = 0 (unconditional L1.2) |
| PM-016 | Warn | Common_Mode_Restore_Time < device requirement |
| PM-017 | Warn | PME_TO_Ack not observed within 10ms |

---

## Reviewer Prompts

**ASPM**
- Was VID/DID CfgRd confirmed before the first PM_Active_State_Request_L1?
- What was written to Link Control 0x090? (0x42 = ASPM L1 enabled)
- Was PM_Request_Ack sent during the enumeration window?

**D-states**
- Were D1/D2 states claimed while PM Capabilities shows they are not supported?
- Was Transactions Pending = 0 confirmed before D3hot write?
- Was Trst delay observed after D3hot→D0 before link re-use?
- Was PME_Status cleared after PME processing?

**L1 PM Substates**
- Were L1 PM Substates Capabilities read from both sides before enabling?
- Was T_POWER_ON programmed to at least the device's required value?
- Was LTR_L1.2_Threshold non-zero (intentional gate for L1.2)?
- Was Common_Mode_Restore_Time consistent with device capability?
- Was Enable Clock PM (Link Control bit8) set before ASPM L1.2 enable?

---

## Example Compliant JSON Report

```json
{
  "schema_version": "1.0",
  "enumeration_complete": true,
  "pm_l1_observed": true,
  "aspm_enabled_by_cfgwr": true,
  "link_control_aspm_value": "0x00000042",
  "pm_request_ack_in_enum_window": false,
  "l1_cycle_count": 6,
  "clkreq_evidence": "not_captured",
  "d_state_transition_observed": false,
  "l1_substate_mode": "none",
  "l1pm_substates_configured": false,
  "notes": ["PM L1 occurs 93ms after ASPM enabled; enumeration complete before L1"]
}
```

## Example Violation JSON Report

```json
{
  "schema_version": "1.0",
  "enumeration_complete": false,
  "pm_l1_observed": true,
  "aspm_enabled_by_cfgwr": true,
  "link_control_aspm_value": "0x00000042",
  "pm_request_ack_in_enum_window": true,
  "d_state_transition_observed": false,
  "notes": ["FAIL: PM L1 during enumeration window - host ACKed before VID/DID was read"]
}
```

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
