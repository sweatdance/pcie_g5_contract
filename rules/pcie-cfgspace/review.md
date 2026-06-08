# PCIe Configuration Space Rule Pack

Rule pack: `pcie-cfgspace`

## Rule basis

- Require evidence that enumeration reached at least VID/DID (CfgRd 0x000) before claiming
  a device was successfully identified.
- Require BAR sizing to follow the probe-then-assign sequence.
- Require Link Control access to follow a read-modify-write pattern.
- Warn when the PCIe capability chain was not traversed before driver load.

## Warn rules (all configuration space violations are warn-grade unless enumeration is incomplete)

- `PCIE5-CFG-001` (hard stop when enumeration_complete=false): VID/DID read (CfgRd 0x000
  yielding a valid non-FFFF value) must be present in any capture claiming device enumeration.
- `PCIE5-CFG-002` (warn): BAR sizing must follow the sequence: CfgWr FFFFFFFF →
  CfgRd same offset → CfgWr actual address. Out-of-order or missing steps warn.
- `PCIE5-CFG-003` (warn): PCIe Capability pointer (CfgRd 0x034) must be read before
  any extended capability (offset ≥ 0x100) is accessed.
- `PCIE5-CFG-004` (warn): Link Control (Reg=0x090) write must be preceded by a CfgRd to
  the same offset. Bare write without prior read risks overwriting reserved or functional bits.
- `PCIE5-CFG-005` (warn): Command register (Reg=0x004) Bus Master Enable bit (bit2) must be
  set before any Memory or I/O transactions are accepted by the device.

## Review prompts

- Was CfgRd 0x000 (VID/DID) observed and did it return a non-FFFF vendor ID?
- Did BAR sizing follow probe-then-assign for all BARs?
- Was the PCIe capability chain traversed before extended capabilities were accessed?
- Was Link Control written without a preceding read (risky overwrite)?
- Was Bus Master Enable set before the first MRd/MWr to device memory space?
