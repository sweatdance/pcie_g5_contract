# PCIe Configuration Space Rule Pack

Rule pack: `pcie-cfgspace`

## Rule basis

- Require complete enumeration evidence: VID/DID, Class Code, Subsystem ID, all BARs, capabilities.
- Require all configuration space accesses to follow the correct sequence and field semantics.
- Require MSI or MSI-X to be configured before driver interrupt operation is claimed functional.
- Require PCIe Express Capability to be fully configured (Device Control, Link Control,
  Device Control 2, Device Capabilities consistency).
- Require Extended Capabilities (LTR, L1 PM Substates, Completion Timeout) to be consistent
  with observed device behavior.
- Require D-state transitions to follow Power Management Capability constraints.
- Warn when any mandatory enumeration step is missing, incomplete, or out of order.

## Hard-stop rules

- `PCIE5-CFG-001` (hard stop when `enumeration_complete = true` claimed but absent):
  VID/DID CfgRd 0x000 returning a non-FFFF Vendor ID must be present. Contradictory
  evidence (enumeration claimed without VID/DID read) is a hard stop.
- `PCIE5-CFG-006` (hard stop): Memory Space Enable (Command Reg 0x004 bit0) must be set
  before any MRd/MWr to device BAR space. Memory access before this bit is set is a hard stop.
- `PCIE5-CFG-013` (hard stop): If Class Code (CfgRd 0x008) returns an unexpected device
  class that cannot be reconciled with the claimed device identity, this is a hard stop.

## Warn rules

### Header (0x000–0x03F)

- `PCIE5-CFG-002` (warn): BAR sizing must follow: CfgWr FFFFFFFF → CfgRd same offset →
  CfgWr actual address. Missing or out-of-order steps warn. All implemented BARs must be probed.
- `PCIE5-CFG-003` (warn): Capability pointer (CfgRd 0x034) must be read before accessing
  any standard capability or extended capability (offset ≥ 0x100).
- `PCIE5-CFG-005` (warn): Bus Master Enable (Command bit2) must be set before DMA
  (MRd/MWr initiated by the device) is expected.
- `PCIE5-CFG-012` (warn): Subsystem Vendor ID / Subsystem ID (CfgRd 0x02C) must be read
  during enumeration for system-level device identification.
- `PCIE5-CFG-014` (warn): Interrupt Pin (CfgRd 0x03D) must be read to determine if the
  device uses legacy INTx before any interrupt-related driver configuration.
- `PCIE5-CFG-016` (warn): INTx Disable (Command bit10) must be set when MSI or MSI-X is
  enabled. Simultaneous INTx active and MSI/MSI-X enabled is a protocol violation.

### Power Management Capability

- `PCIE5-CFG-015` (warn): Power Management Capability (Cap ID=0x01) must be read before
  writing PMCSR to change D-state. Bare PMCSR write without prior PM Capabilities read warns.
- `PCIE5-CFG-017` (warn): D3hot→D0 transition must be followed by a Trst delay (minimum
  10ms) before any configuration access. CfgRd immediately after D3hot→D0 warns.
- `PCIE5-CFG-018` (warn): PME_En bit in PMCSR must not be set if the device's PM Capabilities
  register shows PME is not supported from the current D-state.

### MSI / MSI-X Capability

- `PCIE5-CFG-007` (warn): MSI Enable (MSI Control bit0) or MSI-X Enable (MSI-X Control bit15)
  must be set before driver interrupt delivery is claimed active. Neither set with INTx Disable
  set leaves the device with no interrupt path.
- `PCIE5-CFG-019` (warn): MSI Message Address must be a valid APIC memory-mapped address
  (system-dependent, typically 0xFEEXXXXX on x86). Zero or all-F address warns.
- `PCIE5-CFG-020` (warn): MSI-X Table BIR must reference a valid BAR. If the referenced BAR
  is not assigned (value 0x00000000 or FFFFFFFF), MSI-X cannot function.

### PCIe Express Capability (Device Control / Device Control 2)

- `PCIE5-CFG-004` (warn): Link Control (Reg=0x090) write must be preceded by CfgRd to the
  same offset (read-modify-write). Bare write risks overwriting ASPM, speed, or width fields.
- `PCIE5-CFG-008` (warn): MaxPayloadSize (Device Control bits[7:5]) must not exceed the
  device's MaxPayloadSize Supported (Device Capabilities bits[2:0]). Mismatch warns.
- `PCIE5-CFG-009` (warn): MaxReadReqSize (Device Control bits[14:12]) set above 512 bytes
  on a path with a switch warns unless the switch's MPS and RRS settings are confirmed compatible.
- `PCIE5-CFG-021` (warn): Completion Timeout Value (Device Control 2 bits[3:0]) must be
  within a range appropriate for the downstream device's response latency requirements.
  Value 0000b (default, 50us–50ms range A) is typically safe; shorter values may cause
  spurious timeouts on devices with slow config-space access.
- `PCIE5-CFG-022` (warn): Enable No Snoop (Device Control bit11) must only be set when the
  system coherency model permits it. Incorrect No Snoop setting can cause cache coherency issues.
- `PCIE5-CFG-023` (warn): Link Control 2 Target Link Speed (CfgWr 0x0B0 bits[3:0]) must
  match the intended operating speed. Mismatch between Target Link Speed and negotiated speed warns.

### LTR Extended Capability

- `PCIE5-CFG-010` (warn): LTR Enable (Device Control 2 bit10) must only be set after the
  device has sent at least one LTR message establishing its latency requirements. Setting
  LTR Enable without a prior LTR message warns.
- `PCIE5-CFG-024` (warn): LTR Max Snoop Latency and Max No-Snoop Latency values must be
  non-zero when LTR is active. Zero-value LTR reports maximum platform latency tolerance
  (may prevent platform from entering low-power states).

### L1 PM Substates Extended Capability

- `PCIE5-CFG-011` (warn): L1 PM Substates Control 1 (ASPM L1.1 Enable, ASPM L1.2 Enable)
  must only be set when both port and device indicate support in their L1 PM Substates
  Capabilities registers. Setting L1.2 without CLKREQ# hardware support warns.
- `PCIE5-CFG-025` (warn): LTR_L1.2_Threshold in L1 PM Substates Control 1 must be set to
  a value consistent with the platform's LTR requirements. Zero threshold means L1.2 entry
  is never gated by LTR, which may cause excessive L1.2 transitions.
- `PCIE5-CFG-026` (warn): T_POWER_ON in L1 PM Substates Control 2 must be within the
  device's Port T_POWER_ON value from L1 PM Substates Capabilities. Under-programming this
  field causes L1.2 exit failures.

## Review prompts — enumeration completeness

- Was CfgRd 0x000 (VID/DID) observed with non-FFFF Vendor ID?
- Was Class Code (CfgRd 0x008) read and does it match the expected device type?
- Was Subsystem VID/ID (CfgRd 0x02C) read?
- Was BAR sizing (FFFFFFFF probe) observed for all implemented BARs?
- Was Memory Space Enable (Command bit0) set before MRd/MWr to BAR space?
- Was Bus Master Enable (Command bit2) set before DMA?

## Review prompts — interrupt configuration

- Is MSI Enable or MSI-X Enable set? Is INTx Disable set consistently?
- Is MSI Message Address a valid APIC address?
- Is MSI-X Table BIR pointing to an assigned BAR?

## Review prompts — PCIe Express Capability

- Was Link Control (0x090) read before it was written (read-modify-write)?
- Were MaxPayloadSize and MaxReadReqSize within device and system limits?
- Was Completion Timeout configured appropriately?
- Was Target Link Speed in Link Control 2 consistent with the negotiated speed?

## Review prompts — power management and substates

- Was PM Capability read before PMCSR D-state write?
- Was a Trst delay observed after D3hot→D0 transition?
- Was LTR Enable set only after an LTR message was sent?
- Were L1 PM Substates registers (L1.1 Enable, L1.2 Enable, T_POWER_ON) configured
  before L1.1/L1.2 entry was expected?
