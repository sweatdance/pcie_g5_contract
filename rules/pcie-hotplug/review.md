# PCIe Hot-Plug Lifecycle Rule Pack

Rule pack: `pcie-hotplug`

## Rule basis

- Require evidence that the OS Surprise Remove sequence completed before a new device
  is expected to enumerate on the same slot.
- Treat PM_Active_State_Request_L1 during the enumeration window as a hard stop.
- Require a minimum observable gap between Surprise Down and the new device's first CfgRd.
- Require ASPM state to be clean (disabled) on the slot before new device enumeration.
- Treat MUX-based hot-plug scenarios (where a different device appears on the same physical
  link after a MUX switch) as requiring explicit timing evidence.

## Hard-stop rules

- `PCIE5-HP-001`: PM_Active_State_Request_L1 observed before first CfgRd 0x000 (VID/DID) of
  the new device is a hard stop. PM L1 must not interrupt enumeration.
- `PCIE5-HP-002`: PM_Request_Ack sent by the host downstream port while the new device has
  not yet been enumerated (no CfgRd 0x000 seen) is a hard stop. The host ACKed L1 during
  the critical enumeration window.
- `PCIE5-HP-003`: New device CfgRd observed while the previous device's AER status was not
  cleared (stale AER error bits) is a hard stop. Error state from previous device must be
  cleared before new device enumeration.

## Warn rules

- `PCIE5-HP-004` (warn): If `time_surprise_down_to_first_cfgrd_ms < 500`, warn. The OS
  hot-plug remove sequence typically requires 500ms–2s to complete. Enumeration starting
  earlier than 500ms after Surprise Down suggests the OS did not finish cleanup.
- `PCIE5-HP-005` (warn): If `slot_aspm_disabled_at_new_link_up` cannot be confirmed (no
  CfgRd to host downstream port Link Control before new device Link Up), warn. ASPM state
  of the host port is unconfirmed.
- `PCIE5-HP-006` (warn): In MUX scenarios, if the new device (GL9767) link-up shows TS1
  advertising a speed higher than the new device's maximum (e.g., >5G for GL9767), warn
  for possible residual SD7 signal or MUX switching artifact.
- `PCIE5-HP-007` (warn): If link cycling (repeated Link Up/Down with duration < 10ms each)
  occurs more than 5 times before stable link, warn for MUX switch timing or SI issue.

## MUX switch scenario specifics

For MUX-based hot-plug (where the same physical PCIe port switches between two devices):

- The "old" device (SD7) must have completed Surprise Down and the OS remove sequence
  before the "new" device (GL9767) appears.
- The MUX switch propagation time must be large enough for OS cleanup (≥ 500ms recommended).
- TS1/TS2 rate advertisement identifies the active link partner:
  - Upstream TS1 advertising [2.5 GT/s, 5.0 GT/s] only = GL9767 (max Gen2)
  - Upstream TS1 advertising [8.0 GT/s] or higher = SD7 card (Gen3+)

## Review prompts

- Was PM L1 observed before the first VID/DID read of the new device?
- Did the host downstream port ACK PM L1 while the new device was not yet enumerated?
- What was the time gap between Surprise Down (old device) and first CfgRd (new device)?
- Was ASPM disabled on the host slot before the new device appeared?
- In MUX scenarios: what TS1 rate did the Upstream link advertise at first Link Up?
  [2.5/5.0 only] = GL9767; [8.0+] = SD7 still active or MUX not yet switched.
- Were stale AER error bits from the previous device cleared before new device enumeration?
