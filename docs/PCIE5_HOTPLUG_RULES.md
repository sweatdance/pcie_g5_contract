# PCIe Hot-Plug Lifecycle Rules

This contract slice enforces timing, state-cleanliness, and ASPM-safety for PCIe hot-plug
and MUX-switch scenarios.

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
