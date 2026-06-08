# PCIe Hot-Plug Lifecycle Rules

This contract slice enforces timing, state-cleanliness, ASPM-safety, and Hot-Plug Controller
(HPC) register sequencing for PCIe hot-plug and MUX-switch scenarios.

## Background

PCIe hot-plug involves two phases on the same physical port:

**Phase 1: Surprise Removal (old device)**
- Device is removed without a graceful power-down
- Host sees Link Down → generates AER Surprise Down error
- OS executes: IRP_MN_SURPRISE_REMOVAL → IRP_MN_REMOVE_DEVICE → resource cleanup
- Typical OS cleanup time: 500ms to several seconds depending on driver complexity

**Phase 2: Hot-Add (new device)**
- New device brings up the link
- OS hot-plug handler detects DLLSC (Data Link Layer State Changed) event
- OS must wait for the slot state to be READY before starting enumeration
- OS executes: CfgRd 0x000 (VID/DID) → full enumeration sequence

**Critical race condition (this project's root cause)**:
If Phase 2 begins before Phase 1 completes, the host slot ASPM state, AER error registers,
and bus number assignments may still be in the "removing" state. This causes:
- ASPM-enabled slot → GL9767 gets PM L1 before enumeration completes → device lost → BSOD
- Stale AER error bits → new device's errors may be misattributed

---

## Hot-Plug Controller (HPC) Register Reference

HPC registers are in the PCIe Express Capability at the Root Port or Downstream Port.
Relevant only when Slot Implemented bit is set in PCIe Capabilities register.

### Slot Capabilities Register (PCIe Cap offset +20)

| Bit | Name | Description |
|-----|------|-------------|
| 0 | Attention Button Present | 1 = physical Attention Button on slot |
| 1 | Power Controller Present | 1 = slot has power controller (can control power) |
| 2 | MRL Sensor Present | 1 = Manually-operated Retention Latch sensor exists |
| 3 | Attention Indicator Present | 1 = Attention Indicator LED present |
| 4 | Power Indicator Present | 1 = Power Indicator LED present |
| 5 | Hot-Plug Surprise | 1 = device can be removed without prior software notification |
| 6 | Hot-Plug Capable | 1 = slot supports hot-plug (presence detect, power control, etc.) |
| [14:7] | Slot Power Limit Value | Combined with Scale: max slot power limit |
| [16:15] | Slot Power Limit Scale | 0=1.0×, 1=0.1×, 2=0.01×, 3=0.001× (multiplied by Value) |
| 17 | Electromechanical Interlock Present | 1 = EMI (solenoid lock) on slot |
| 18 | No Command Completed Support | 1 = CommandCompleted is not signaled (fast path) |
| [31:19] | Physical Slot Number | Unique slot identifier |

### Slot Control Register (PCIe Cap offset +24)

| Bit | Name | Description |
|-----|------|-------------|
| 0 | Attention Button Pressed Enable | 1 = enable interrupt on Attention Button press |
| 1 | Power Fault Detected Enable | 1 = enable interrupt on power fault |
| 2 | MRL Sensor Changed Enable | 1 = enable interrupt on MRL state change |
| 3 | Presence Detect Changed Enable | 1 = enable interrupt on Presence Detect change |
| 4 | Command Completed Interrupt Enable | 1 = enable interrupt when Command Completed |
| 5 | Hot-Plug Interrupt Enable | 1 = master enable for hot-plug interrupts |
| [7:6] | Attention Indicator Control | 00=Reserved, 01=On, 10=Blink, 11=Off |
| [9:8] | Power Indicator Control | 00=Reserved, 01=On, 10=Blink, 11=Off |
| 10 | Power Controller Control | 0=Power On, 1=Power Off |
| 11 | Electromechanical Interlock Control | 0=Disengage, 1=Engage EMI |
| 12 | Data Link Layer State Changed Enable | 1 = enable DLLSC interrupt |

**Power Indicator Control encoding**:
- 01b = On (device powered and operational)
- 10b = Blink (power-up sequence in progress)
- 11b = Off (slot powered down)

**Attention Indicator Control encoding**:
- 01b = On (attention required or error condition)
- 10b = Blink (user should locate this slot)
- 11b = Off (no error condition)

### Slot Status Register (PCIe Cap offset +26)

| Bit | Name | Description |
|-----|------|-------------|
| 0 | Attention Button Pressed | Latched; 1 = Attention Button was pressed; write-1-to-clear |
| 1 | Power Fault Detected | Latched; 1 = power fault detected; write-1-to-clear |
| 2 | MRL Sensor Changed | Latched; write-1-to-clear |
| 3 | Presence Detect Changed (PDC) | Latched; 1 = presence state changed; write-1-to-clear |
| 4 | Command Completed | 1 = previous Slot Control command completed; write-1-to-clear |
| 5 | MRL Sensor State | 0 = MRL Closed (latch in); 1 = MRL Open (latch out) |
| 6 | Presence Detect State (PDS) | 0 = Slot Empty; 1 = Card Present (in-band Presence Detect) |
| 7 | Electromechanical Interlock Engaged | 1 = EMI is currently engaged |
| 8 | Data Link Layer State Changed (DLLSC) | Latched; 1 = DLLA state changed; write-1-to-clear |

---

## Required Hot-Plug Command Sequence (IEEE Spec Compliant)

### Hot-Add Sequence (Device Insertion)

```
1. INTERRUPT: Presence Detect Changed (PDC) interrupt fired
2. OS reads Slot Status → PDC=1 (and possibly DLLSC=1)
3. OS clears PDC: write-1 to Slot Status bit3
4. OS reads Presence Detect State (Slot Status bit6)
   → If PDS=0: card removed, go to Hot-Remove sequence
   → If PDS=1: card inserted, continue

5. OS sets Attention Indicator → Blink (Slot Control bits[7:6]=10b)
6. OS sets Power Indicator → Blink (Slot Control bits[9:8]=10b)
   → Write Slot Control, then POLL: wait CommandCompleted=1 (or timeout 1s)

7. OS turns Power Controller → On (Slot Control bit10=0)
   → Poll CommandCompleted=1 before next Slot Control write

8. OS waits T_Power_Up (≥100ms): slot power stabilizes

9. PERST# de-asserted (by HW or via platform mechanism)

10. Wait for DLLSC=1 in Slot Status (Data Link Layer Link Active=1)
    → This confirms the link is up and device is responding

11. OS clears DLLSC: write-1 to Slot Status bit8

12. OS starts enumeration: CfgRd 0x000 (VID/DID)

13. After successful enumeration:
    OS sets Power Indicator → On (Slot Control bits[9:8]=01b)
    OS sets Attention Indicator → Off (Slot Control bits[7:6]=11b)
    → Poll CommandCompleted after each Slot Control write
```

### Hot-Remove Sequence (Device Removal)

```
1. INTERRUPT: DLLSC=1 (link went down) and/or PDC=1 (presence lost)
2. OS reads Slot Status
3. OS initiates surprise removal handling (IRP_MN_SURPRISE_REMOVAL)

4. OS sets Power Indicator → Off (Slot Control bits[9:8]=11b)
5. OS turns Power Controller → Off (Slot Control bit10=1)
   → Poll CommandCompleted=1 before next operation

6. OS sets Attention Indicator → Off (bits[7:6]=11b)
7. OS clears stale Slot Status bits (DLLSC, PDC)
8. OS clears stale AER error registers
9. Slot is now ready for next hot-add
```

---

## Hot-Plug Timing Requirements

| Timing | Value | Source | Notes |
|--------|-------|--------|-------|
| T_Power_Up | ≥ 100ms | PCIe Base Spec | Slot power stable before PERST# release |
| T_pcie_reset | ≥ 100µs | PCIe Electrical Spec | PERST# assertion minimum duration |
| T_cmd_timeout | ≤ 1s | OS policy | Max wait for CommandCompleted |
| T_dllsc_wait | device-dependent | — | Wait for DLLSC=1 after PERST# release |
| T_surprise_remove_recovery | ≥ 500ms | Windows HCK | Gap before new enum after Surprise Down |

---

## MUX Switch Scenario Specifics

For MUX-based hot-plug (same physical PCIe port switches between two devices):

- The "old" device (SD7) must have completed Surprise Down and OS remove sequence
  before the "new" device (GL9767) appears.
- MUX switch propagation time must be large enough for OS cleanup (≥ 500ms recommended).
- TS1/TS2 rate advertisement identifies the active link partner:

| Upstream TS1 Advertised Rates | Interpretation |
|-------------------------------|----------------|
| [2.5 GT/s, 5.0 GT/s] only | GL9767 (max Gen2 = 5GT/s) |
| [2.5 GT/s, 5.0 GT/s, 8.0 GT/s] | Gen3-capable device (may be SD7) |
| [8.0 GT/s, 16.0 GT/s, …] | SD7 card or Gen4/Gen5 device |

---

## Required Evidence Fields (`checks.pcie_hotplug_report`)

```yaml
# Timing
surprise_down_timestamp: string
new_device_first_linkup_timestamp: string
new_device_first_cfgrd_timestamp: string
time_surprise_down_to_first_cfgrd_ms: number
pm_l1_before_enum_complete: boolean
pm_request_ack_in_enum_window: boolean
slot_aspm_disabled_at_new_link_up: boolean  # null if unknown
aer_cleared_before_new_enum: boolean
upstream_ts1_rate_at_first_linkup: string

# HPC register sequence (new fields)
slot_capabilities_value: string             # hex (full SlotCap register)
slot_control_sequence: array[string]        # list of SlotCtl writes observed
slot_status_events: array[string]           # list of status events (PDC, DLLSC, CmdCmpl)
command_completed_before_next_cmd: boolean
presence_detect_state_before_powerup: boolean
dllsc_triggered_enumeration: boolean
power_indicator_blink_observed: boolean
t_power_up_ms: number                       # measured ms from PwrCtrl ON to PERST# release
attention_indicator_cleared_after_enum: boolean

# MUX scenario
link_cycling_count: integer
mux_scenario: boolean
mux_switch_time_ms: number
new_device_max_speed_gtps: number

notes: array[string]
```

---

## Contract Rules Summary

| Rule ID | Type | Summary |
|---------|------|---------|
| HP-001 | Hard Stop | PM L1 before enumeration |
| HP-002 | Hard Stop | PM_Request_Ack during enum window |
| HP-003 | Hard Stop | Stale AER before new enum |
| HP-004 | Warn | <500ms from Surprise Down to CfgRd |
| HP-005 | Warn | Slot ASPM state unknown |
| HP-006 | Warn | TS1 speed > new device max |
| HP-007 | Warn | Link cycling > 5 cycles |
| HP-008 | Warn | Power Indicator not Blink during power-up |
| HP-009 | Warn | PERST# de-assert before 100ms T_Power_Up |
| HP-010 | Hard Stop | Power removed while device active without PERST# |
| HP-011 | Hard Stop | Second SlotCtl write before CommandCompleted |
| HP-012 | Warn | DLLSC not cleared after new link up |
| HP-013 | Warn | PDC interrupt not handled within 100ms |
| HP-014 | Warn | Attention Indicator left On after successful enum |
| HP-015 | Warn | Power-up with MRL Open |
| HP-016 | Warn | Device power > Slot Power Limit |

---

## Example Compliant JSON Report

```json
{
  "schema_version": "1.0",
  "surprise_down_timestamp": "0001.202577s",
  "new_device_first_linkup_timestamp": "0009.919346s",
  "new_device_first_cfgrd_timestamp": "0009.919538s",
  "time_surprise_down_to_first_cfgrd_ms": 8716.9,
  "pm_l1_before_enum_complete": false,
  "pm_request_ack_in_enum_window": false,
  "slot_aspm_disabled_at_new_link_up": true,
  "aer_cleared_before_new_enum": true,
  "upstream_ts1_rate_at_first_linkup": "2.5 GT/s, 5.0 GT/s",
  "command_completed_before_next_cmd": true,
  "presence_detect_state_before_powerup": true,
  "dllsc_triggered_enumeration": true,
  "power_indicator_blink_observed": true,
  "t_power_up_ms": 105,
  "attention_indicator_cleared_after_enum": true,
  "mux_scenario": true,
  "mux_switch_time_ms": 8716.7,
  "new_device_max_speed_gtps": 5.0,
  "notes": ["PASS: 8.7s gap; ASPM disabled; CommandCompleted polled; T_Power_Up 105ms"]
}
```

## Example Violation JSON Report

```json
{
  "schema_version": "1.0",
  "surprise_down_timestamp": "0005.448703s",
  "new_device_first_linkup_timestamp": "0005.448709s",
  "new_device_first_cfgrd_timestamp": null,
  "time_surprise_down_to_first_cfgrd_ms": null,
  "pm_l1_before_enum_complete": true,
  "pm_request_ack_in_enum_window": true,
  "slot_aspm_disabled_at_new_link_up": false,
  "aer_cleared_before_new_enum": false,
  "upstream_ts1_rate_at_first_linkup": "8.0 GT/s, 16.0 GT/s",
  "command_completed_before_next_cmd": false,
  "dllsc_triggered_enumeration": false,
  "mux_scenario": true,
  "mux_switch_time_ms": 0.006,
  "new_device_max_speed_gtps": 5.0,
  "notes": ["FAIL: MUX switched in 6us; OS not ready; ASPM enabled; PM L1 during enum; BSOD"]
}
```

## Background

PCIe hot-plug involves two phases on the same physical port:

**Phase 1: Surprise Removal (old device)**
- SD7 card or other device is removed without a graceful power-down
- Host sees Link Down → generates AER Surprise Down error
- OS executes: IRP_MN_SURPRISE_REMOVAL → IRP_MN_REMOVE_DEVICE → resource cleanup
- Typical OS cleanup time: 500ms to several seconds depending on driver complexity

**Phase 2: Hot-Add (new device)**
- New device (e.g., GL9767 after MUX switch) brings up the link
- OS hot-plug handler detects Link Up + Presence Detect Changed
- OS must wait for the slot state to be READY before starting enumeration
- OS executes: CfgRd 0x000 (VID/DID) → full enumeration sequence

**Critical race condition (this project's root cause):**
If Phase 2 begins before Phase 1 completes, the host slot ASPM state, AER error registers,
and bus number assignments may still be in the "removing" state. This causes:
- ASPM-enabled slot → GL9767 gets PM L1 before enumeration completes → device lost → BSOD
- Stale AER error bits → new device's errors may be misattributed

## Required evidence fields (`checks.pcie_hotplug_report`)

- `surprise_down_timestamp`: string — timestamp of Surprise Down event (old device)
- `new_device_first_linkup_timestamp`: string — timestamp of first Link Up for new device
- `new_device_first_cfgrd_timestamp`: string — timestamp of first CfgRd 0x000 for new device
- `time_surprise_down_to_first_cfgrd_ms`: number — gap in ms between Surprise Down and first CfgRd
- `pm_l1_before_enum_complete`: boolean — was PM L1 observed before first CfgRd 0x000?
- `pm_request_ack_in_enum_window`: boolean — was PM_Request_Ack sent before first CfgRd 0x000?
- `slot_aspm_disabled_at_new_link_up`: boolean — was host slot ASPM confirmed disabled before
  new device Link Up? (null if unknown/not captured)
- `aer_cleared_before_new_enum`: boolean — was AER status cleared before new device enumeration?
- `upstream_ts1_rate_at_first_linkup`: string — TS1 Data Rate field from Upstream at first Link Up
  (e.g. "2.5 GT/s, 5.0 GT/s" = GL9767; "8.0 GT/s, 16.0 GT/s" = SD7)

## Conditionally required fields

- `link_cycling_count`: integer — number of Link Up/Down cycles with duration < 10ms
  (required when > 5 cycles detected)
- `mux_scenario`: boolean — is this a MUX-based hot-plug scenario?
- `mux_switch_time_ms`: number — time from old device Link Down to new device first TS1
  (required when `mux_scenario = true`)
- `new_device_max_speed_gtps`: number — new device maximum supported speed
  (required when `mux_scenario = true`, used to validate TS1 rate)
- `notes`: array of strings

## Contract rules

- `PCIE5-HP-001`: If `pm_l1_before_enum_complete = true`, this is a hard stop.
- `PCIE5-HP-002`: If `pm_request_ack_in_enum_window = true`, this is a hard stop.
- `PCIE5-HP-003`: If `aer_cleared_before_new_enum = false`, this is a hard stop.
- `PCIE5-HP-004` (warn): If `time_surprise_down_to_first_cfgrd_ms < 500`, warn.
- `PCIE5-HP-005` (warn): If `slot_aspm_disabled_at_new_link_up` is null (unknown), warn.
- `PCIE5-HP-006` (warn): In MUX scenario, if `upstream_ts1_rate_at_first_linkup` contains
  speeds higher than `new_device_max_speed_gtps`, warn for possible MUX switching artifact.
- `PCIE5-HP-007` (warn): If `link_cycling_count > 5`, warn.

## TS1 rate identification reference (MUX scenarios)

| Upstream TS1 Advertised Rates | Interpretation |
|-------------------------------|----------------|
| [2.5 GT/s, 5.0 GT/s] only | GL9767 is the link partner (max Gen2 = 5G) |
| [2.5 GT/s, 5.0 GT/s, 8.0 GT/s] | Gen3-capable device (could be SD7 or other) |
| [8.0 GT/s, 16.0 GT/s, ...] | SD7 card or Gen4/Gen5 device |

## Example compliant JSON report

```json
{
  "schema_version": "1.0",
  "surprise_down_timestamp": "0001.202577s",
  "new_device_first_linkup_timestamp": "0009.919346s",
  "new_device_first_cfgrd_timestamp": "0009.919538s",
  "time_surprise_down_to_first_cfgrd_ms": 8716.9,
  "pm_l1_before_enum_complete": false,
  "pm_request_ack_in_enum_window": false,
  "slot_aspm_disabled_at_new_link_up": true,
  "aer_cleared_before_new_enum": true,
  "upstream_ts1_rate_at_first_linkup": "2.5 GT/s, 5.0 GT/s",
  "mux_scenario": true,
  "mux_switch_time_ms": 8716.7,
  "new_device_max_speed_gtps": 5.0,
  "notes": ["PASS scenario: 8.7s gap allowed OS cleanup; ASPM disabled by hot-plug handler"]
}
```

## Example violation JSON report

```json
{
  "schema_version": "1.0",
  "surprise_down_timestamp": "0005.448703s",
  "new_device_first_linkup_timestamp": "0005.448709s",
  "new_device_first_cfgrd_timestamp": null,
  "time_surprise_down_to_first_cfgrd_ms": null,
  "pm_l1_before_enum_complete": true,
  "pm_request_ack_in_enum_window": true,
  "slot_aspm_disabled_at_new_link_up": false,
  "aer_cleared_before_new_enum": false,
  "upstream_ts1_rate_at_first_linkup": "8.0 GT/s, 16.0 GT/s",
  "mux_scenario": true,
  "mux_switch_time_ms": 0.006,
  "new_device_max_speed_gtps": 5.0,
  "notes": ["FAIL scenario: MUX switched in 6us; OS had no time to clean up; ASPM enabled; BSOD"]
}
```
