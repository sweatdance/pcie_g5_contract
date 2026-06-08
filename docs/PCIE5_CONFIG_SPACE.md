# PCIe Configuration Space Rules

This contract slice makes enumeration completeness and configuration space access patterns
reviewer-visible.

## Background

PCIe device enumeration consists of the OS reading and writing configuration space to:
1. Identify the device (CfgRd 0x000 → VID/DID)
2. Discover capabilities (CfgRd 0x034 → capability pointer, traverse chain)
3. Size and assign BARs (CfgWr FFFFFFFF → CfgRd → CfgWr address)
4. Configure Link Control (CfgRd/CfgWr 0x090 for ASPM, speed settings)
5. Enable Bus Master (CfgWr 0x004 bit2=1)

A device cannot function correctly if any of these steps are skipped or out of order.

## Required evidence fields (`checks.pcie_cfgspace_report`)

- `vidpid_read_observed`: boolean — was CfgRd 0x000 observed in the capture?
- `vidpid_value`: string (hex) — the VID/DID value returned (e.g. "17A0:9767"); "FFFF/FFFF" = device not present
- `enumeration_sequence_complete`: boolean — did the full probe sequence complete (VID/DID + caps + BARs + enable)?
- `bar_sizing_observed`: boolean — was the CfgWr FFFFFFFF → CfgRd → CfgWr assign sequence observed for at least one BAR?
- `link_control_read_before_write`: boolean — was CfgRd 0x090 observed before any CfgWr 0x090?
- `bus_master_enabled`: boolean — was CfgWr 0x004 with bit2=1 observed?

## Conditionally required fields

- `vidpid_read_timestamp`: string — timestamp of first CfgRd 0x000 (required when `vidpid_read_observed = true`)
- `first_cfgwr_timestamp`: string — timestamp of first CfgWr to any register (required when `enumeration_sequence_complete = true`)
- `capability_chain_traversed`: boolean — was CfgRd 0x034 + capability walk observed?
- `bar_count_probed`: integer — number of BARs where sizing was observed
- `notes`: array of strings

## Contract rules

- `PCIE5-CFG-001`: If `vidpid_read_observed = false`, enumeration did not start; this is a
  hard stop when `enumeration_sequence_complete = true` is claimed (contradictory evidence).
- `PCIE5-CFG-002` (warn): If `bar_sizing_observed = false` but `enumeration_sequence_complete = true`,
  warn that BAR probe evidence is missing.
- `PCIE5-CFG-003` (warn): If `capability_chain_traversed = false` but extended capabilities
  were accessed (offset ≥ 0x100), warn for out-of-order capability access.
- `PCIE5-CFG-004` (warn): If `link_control_read_before_write = false`, warn for potential
  read-modify-write violation on Link Control register.
- `PCIE5-CFG-005` (warn): If `bus_master_enabled = false` but MRd/MWr TLPs to device BAR
  space are observed, warn for Bus Master Enable race condition.

## Key config space offsets (reference)

| Offset | Register | Notes |
|--------|----------|-------|
| 0x000 | VID / DID | Device identity; must be non-FFFF |
| 0x004 | Command / Status | bit2 = Bus Master Enable |
| 0x008 | Class Code / Rev | Device class |
| 0x010–0x024 | BAR[0]–BAR[5] | Base Address Registers |
| 0x030 | Expansion ROM BAR | |
| 0x034 | Capability Pointer | Points to first capability structure |
| 0x070 | PCIe Capability (PCI Express Cap) | Standard PCIe cap block |
| 0x080 | PCIe Device Control/Status | MaxPayloadSize, MaxReadReqSize |
| 0x088 | PCIe Link Capabilities | MaxLinkSpeed, MaxLinkWidth |
| 0x090 | PCIe Link Control/Status | ASPM bits[1:0], speed/width status |
| 0x0A8 | PCIe Device Control 2 | Completion timeout, OBFF, LTR |
| 0x0B0 | PCIe Link Control 2 | Target link speed |
| 0x100+ | Extended Capabilities | AER, LTR, L1 PM Substates, etc. |

## Reviewer prompts

- Was CfgRd 0x000 observed and did it return a valid (non-FFFF) VID/DID?
- Was BAR sizing (FFFFFFFF probe) observed for all implemented BARs?
- Was the capability chain walked before extended capabilities at 0x100+ were accessed?
- Was Link Control (0x090) read before it was written?
- Was Bus Master Enable set before device MMIO transactions began?
