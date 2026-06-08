# PCIe Hot-Plug Lifecycle Rule Pack

Rule pack: `pcie-hotplug`

## Rule basis

- Require evidence that the OS Surprise Remove sequence completed before a new device
  is expected to enumerate on the same slot.
- Treat PM_Active_State_Request_L1 during the enumeration window as a hard stop.
- Require a minimum observable gap between Surprise Down and the new device's first CfgRd.
- Require ASPM state to be clean (disabled) on the slot before new device enumeration.
- Require Hot-Plug Controller (HPC) register sequences to follow PCIe spec ordering.
- Require CommandCompleted to be polled before issuing subsequent Slot Control writes.
- Treat MUX-based hot-plug scenarios as requiring explicit timing and TS1 rate evidence.

## Hard-stop rules

- `PCIE5-HP-001`: PM_Active_State_Request_L1 observed before first CfgRd 0x000 (VID/DID)
  of the new device is a hard stop.
- `PCIE5-HP-002`: PM_Request_Ack sent by the host downstream port while the new device has
  not yet been enumerated (no CfgRd 0x000 seen) is a hard stop.
- `PCIE5-HP-003`: New device CfgRd observed while the previous device's AER status was not
  cleared (stale AER error bits) is a hard stop.
- `PCIE5-HP-010` (hard stop): Slot Control Power Controller Control bit cleared (power off)
  must not be issued while PresenceDetectState=1 AND Data Link Layer Link Active=1. Pulling
  power from an active device without PERST# assertion first is a hard stop.
- `PCIE5-HP-011` (hard stop): A second Slot Control write must not be issued before
  CommandCompleted=1 in Slot Status (or Command Completed interrupt received). Issuing
  back-to-back Slot Control writes without CommandCompleted is a hard stop.

## Warn rules — timing and state cleanliness

- `PCIE5-HP-004` (warn): If `time_surprise_down_to_first_cfgrd_ms < 500`, warn. OS hot-plug
  remove sequence typically requires 500ms–2s to complete.
- `PCIE5-HP-005` (warn): If `slot_aspm_disabled_at_new_link_up` cannot be confirmed, warn.
- `PCIE5-HP-006` (warn): MUX scenario: if Upstream TS1 advertises speeds above new device
  maximum, warn for residual signal or incomplete MUX switch.
- `PCIE5-HP-007` (warn): More than 5 link cycles with duration < 10ms warns for MUX or SI issue.

## Warn rules — HPC register sequence

- `PCIE5-HP-008` (warn): Slot Control must set Power Indicator to Blink before initiating
  power-up sequence. Omitting Blink state deviates from PCIe spec hot-plug state machine.
- `PCIE5-HP-009` (warn): PERST# must remain asserted for at least Tpvperl (100ms) after slot
  power is stable before being de-asserted. De-assertion before power stable period warns.
- `PCIE5-HP-012` (warn): After new link comes up (DLLSC=1 in Slot Status), the OS must read
  Slot Status to clear DLLSC before starting enumeration. Stale DLLSC bit warns.
- `PCIE5-HP-013` (warn): PresenceDetectChanged interrupt must result in a Slot Status read
  within 100ms. Extended delay in handling PDC interrupt warns.
- `PCIE5-HP-014` (warn): Attention Indicator must be set to OFF after successful device
  enumeration. Attention Indicator left ON after successful hot-add warns.
- `PCIE5-HP-015` (warn): If MRL Sensor is implemented, MRL Sensor State must be CLOSED
  before power-up sequence can proceed. Power-up with MRL OPEN warns.
- `PCIE5-HP-016` (warn): Slot Power Limit value in Slot Capabilities must not be exceeded
  by the device's power consumption as reported in Device Capabilities. Over-limit warns.

## MUX switch scenario specifics

- Upstream TS1 [2.5 GT/s, 5.0 GT/s] only = GL9767 (max Gen2/5G)
- Upstream TS1 [8.0 GT/s+] = SD7 or other Gen3+ device
- MUX switch time ≥ 500ms recommended for OS remove sequence completion

## Review prompts — OS timing

- Was there ≥ 500ms between Surprise Down and the new device's first CfgRd?
- Was slot ASPM confirmed disabled before the new device appeared?
- Were stale AER bits cleared before new enumeration started?
- Was PM L1 observed during the enumeration window?

## Review prompts — HPC register sequence

- Was CommandCompleted polled before each subsequent Slot Control write?
- Was Power Indicator set to Blink before power-up?
- Was PERST# held for ≥ 100ms after power stable?
- Was DLLSC read and cleared after new link came up?
- Was PresenceDetectChanged handled within 100ms?
- Was Attention Indicator set to OFF after successful enumeration?
- Is MRL Sensor present and was it CLOSED before power-up?
- Was Slot Power Limit consistent with device power requirements?
