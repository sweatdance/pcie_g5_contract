# PCIe Configuration Space Rules

This contract slice makes enumeration completeness, configuration space register semantics,
capability structure coverage, and extended capability access patterns reviewer-visible.

## Background

PCIe device enumeration consists of the OS reading and writing configuration space to:
1. Identify the device (CfgRd 0x000 → VID/DID, Class Code, Subsystem ID)
2. Discover capabilities (CfgRd 0x034 → capability pointer, traverse chain)
3. Size and assign BARs (CfgWr FFFFFFFF → CfgRd → CfgWr address)
4. Configure interrupts (MSI or MSI-X enable in capability structure)
5. Configure PCIe Express Capability (Device Control, Link Control, Device Control 2)
6. Enable Bus Master (CfgWr 0x004 bit2=1)
7. Configure Extended Capabilities (LTR, L1 PM Substates, Completion Timeout)

A device cannot function correctly if any of these steps are skipped or out of order.

---

## Type 0 Configuration Header (0x000–0x03F)

### 0x000 — Vendor ID / Device ID

| Field | Bits | Notes |
|-------|------|-------|
| Vendor ID | [15:0] | PCI-SIG assigned. 0xFFFF = device absent / link down |
| Device ID | [31:16] | Vendor-defined device model number |

**GL9767 example**: VID=0x17A0, DID=0x9767.
CfgRd returning 0xFFFFFFFF indicates device is not accessible (CRS/CA/UR or link down).

### 0x004 — Command Register / Status Register

#### Command Register [15:0]

| Bit | Name | Meaning when set |
|-----|------|-----------------|
| 0 | I/O Space Enable | Allow I/O BAR transactions |
| 1 | Memory Space Enable | Allow Memory BAR read/write |
| 2 | Bus Master Enable | Allow device to initiate MRd/MWr DMA |
| 3 | Special Cycles | Enable Special Cycle snooping |
| 4 | Memory Write and Invalidate | Allow MWI transactions (legacy) |
| 5 | VGA Palette Snoop | Enable VGA palette snoop (graphics only) |
| 6 | Parity Error Response | Enable PERR# assertion on parity error |
| 8 | SERR# Enable | Enable SERR# signalling on fatal errors |
| 9 | Fast Back-to-Back | Allow fast back-to-back transactions (legacy) |
| 10 | INTx Disable | Mask legacy INTx interrupt. Must be 1 when MSI/MSI-X is enabled |

**Critical bits for debug**:
- bit1 (Memory Space Enable): must be 1 before any CfgWr/CfgRd to BAR addresses
- bit2 (Bus Master Enable): must be 1 before any DMA from device
- bit10 (INTx Disable): must be 1 when MSI or MSI-X is enabled to prevent dual-delivery

#### Status Register [31:16]

| Bit | Name | Meaning when set |
|-----|------|-----------------|
| 16 (reg bit0) | INTx Status | INTx interrupt is pending (asserted) |
| 20 (reg bit4) | Capabilities List | Device implements capability chain (must be 1 for PCIe) |
| 23 (reg bit7) | Fast Back-to-Back Capable | Device supports fast B2B (legacy) |
| 24 (reg bit8) | Master Data Parity Error | Bus master parity error occurred |
| 27:25 | DEVSEL Timing | 00=fast, 01=medium, 10=slow (PCIe always fast) |
| 28 | Signaled Target Abort | Device issued Target Abort |
| 29 | Received Target Abort | Master received Target Abort |
| 30 | Received Master Abort | Master received Master Abort (no target responded) |
| 31 | Signaled System Error | Device signaled SERR# |

### 0x008 — Revision ID / Class Code

| Field | Bytes | Meaning |
|-------|-------|---------|
| Revision ID | 0x008 | Silicon revision; vendor-defined |
| Programming Interface | 0x009 | Sub-class qualifier |
| Sub-class | 0x00A | Refines device function |
| Base Class | 0x00B | High-level device category |

**Common Base Class values**:
- 0x01: Mass Storage Controller (SD Host → sub-class 0x05)
- 0x04: Multimedia Controller
- 0x05: Memory Controller
- 0x0C: Serial Bus Controller (USB etc.)
- 0xFF: Unclassified

**GL9767**: Base Class 0x01, Sub-class 0x05 (SD Host Controller).

### 0x00C–0x00F — Miscellaneous Header Fields

| Offset | Field | Notes |
|--------|-------|-------|
| 0x00C | Cache Line Size | System cache line in 32-bit DWORDs; must match system value for MWI |
| 0x00E | Header Type | bit7=Multi-function; bits[6:0]: 0x00=Type 0, 0x01=Type 1 (bridge) |
| 0x00F | BIST | bit7=BIST Capable; bit6=Start BIST; bits[3:0]=Completion Code |

### 0x010–0x024 — Base Address Registers (BAR[0]–BAR[5])

BAR type determined by reading the low bits after a FFFFFFFF write:

| BAR bits[2:0] | Type | Alignment granularity |
|---------------|------|-----------------------|
| 000 | 32-bit Memory | Write FFFFFFFF → read → low bits give size |
| 010 | Reserved (Type 10 is not valid) | — |
| 100 | 64-bit Memory (uses two consecutive BARs) | — |
| xx1 | I/O BAR | bits[1:0]=01, address is I/O space |

**Sizing sequence** (mandatory per PCI spec):
1. Save original value
2. CfgWr 0xFFFFFFFF → BAR offset
3. CfgRd BAR offset (size mask returned)
4. CfgWr assigned base address → BAR offset
5. Repeat for 64-bit upper DWORD if applicable

### 0x02C–0x02F — Subsystem Vendor ID / Subsystem Device ID

System-level device identification. Read during enumeration by `SetupDiGetDeviceRegistryProperty`.
Used by INF files to select the correct driver. Must be read to confirm platform-specific identity.

### 0x030–0x033 — Expansion ROM Base Address

bit0 = ROM Enable. Address aligned to ROM size. Write FFFFFFFF to size, then assign address.
For PCIe devices without Option ROM, this register is typically read-only zero.

### 0x034 — Capabilities Pointer

Points to first byte of the first capability structure in the range 0x040–0xFF.
Must be read before traversing the capability chain. Value must be 4-byte aligned (bits[1:0]=00).

### 0x03C–0x03F — Interrupt and Timing

| Offset | Field | Notes |
|--------|-------|-------|
| 0x03C | Interrupt Line | BIOS-assigned IRQ routing (OS may override) |
| 0x03D | Interrupt Pin | 0x00=No INTx; 0x01=INTA#; 0x02=INTB#; 0x03=INTC#; 0x04=INTD# |
| 0x03E | Min_Gnt | PCI legacy; 0 for PCIe |
| 0x03F | Max_Lat | PCI legacy; 0 for PCIe |

---

## Power Management Capability (Cap ID = 0x01)

Typically at offset 0x040–0x060 depending on capability ordering.

### PM Capabilities Register

| Bit | Name | Meaning |
|-----|------|---------|
| [2:0] | Version | 0x03 = PCI PM spec 1.2 (required for PCIe) |
| 3 | PME Clock | 1 = device requires PCIe clock for PME (uncommon on PCIe) |
| 5 | DSI | Device-Specific Initialization required before use |
| [8:6] | Aux_Current | Auxiliary power drawn from Vaux |
| 9 | D1 Support | 1 = device supports D1 state |
| 10 | D2 Support | 1 = device supports D2 state |
| [15:11] | PME_Support | Bit per D-state (D0..D3hot, D3cold) from which PME can be asserted |

### PM Control/Status Register (PMCSR)

| Bit | Name | Description |
|-----|------|-------------|
| [1:0] | PowerState | 00=D0, 01=D1, 10=D2, 11=D3hot |
| 3 | No_Soft_Reset | 1 = no internal reset on D3hot→D0; device retains registers |
| 8 | PME_En | 1 = enable PME# assertion from this device |
| [12:9] | Data_Select | Selects PM data reported in Data register |
| [14:13] | Data_Scale | Scaling factor for Data register |
| 15 | PME_Status | 1 = PME was asserted; write 1 to clear |

**D-state transition rules**:
- D0 ↔ D1 ↔ D2: allowed with brief transition time (<1ms for D1, <4ms for D2)
- D0/D1/D2 → D3hot: device config space still accessible; full state loss
- D3hot → D0: requires Trst ≥ 1ms (device may require up to 100ms; check No_Soft_Reset bit)
- D3cold → D0: requires power re-application; full re-enumeration required

---

## MSI Capability (Cap ID = 0x05)

### MSI Message Control Register

| Bit | Name | Description |
|-----|------|-------------|
| 0 | MSI Enable | 1 = MSI enabled; INTx Disable should also be set |
| [3:1] | Multiple Message Capable | Log2 of number of interrupt vectors device can use |
| [6:4] | Multiple Message Enable | Log2 of enabled vectors (≤ Multiple Message Capable) |
| 7 | 64-bit Capable | 1 = device can use 64-bit MSI addresses |
| 8 | Per-Vector Masking Capable | 1 = supports individual vector mask/pending |

### MSI Address and Data

| Offset from Cap | Field | Description |
|-----------------|-------|-------------|
| +4 | Message Address Low | Target address for MSI write; typically 0xFEEXXXXX (x86 APIC) |
| +8 | Message Address High | Upper 32 bits (64-bit MSI only) |
| +C (or +8) | Message Data | Data written to Message Address on interrupt |
| +10 (if per-vector) | Mask Bits | Bit-per-vector mask; 1 = masked |
| +14 (if per-vector) | Pending Bits | Bit-per-vector pending status (RO) |

---

## MSI-X Capability (Cap ID = 0x11)

### MSI-X Message Control Register

| Bit | Name | Description |
|-----|------|-------------|
| [10:0] | Table Size | Number of MSI-X table entries minus 1 |
| 14 | Function Mask | 1 = all vectors masked (global mask) |
| 15 | MSI-X Enable | 1 = MSI-X enabled; INTx Disable must also be set |

### MSI-X Table and PBA

| Field | Description |
|-------|-------------|
| Table Offset / BIR | bits[2:0] = BAR Index (BIR), bits[31:3] = offset within BAR to MSI-X table |
| PBA Offset / BIR | Same format; points to Pending Bit Array (one bit per vector) |

Each MSI-X table entry is 16 bytes: Message Address (64-bit), Message Data (32-bit), Vector Control (32-bit, bit0=Mask).

---

## PCIe Express Capability (Cap ID = 0x10)

This is the primary PCIe-specific capability. Location varies by device (typically 0x060–0x0E0).

### PCIe Capabilities Register (offset +2 from cap header)

| Bit | Name | Notes |
|-----|------|-------|
| [3:0] | Capability Version | 0x2 = PCIe Gen1; common value is 0x2 for all Gen devices |
| [7:4] | Device/Port Type | 0x0=PCI Express EP, 0x1=Legacy EP, 0x4=Root Port, 0x6=Downstream Port, 0x7=Upstream Port |
| 8 | Slot Implemented | 1 = physical slot exists (relevant for hot-plug root ports) |
| [13:9] | Interrupt Message Number | MSI/MSI-X vector for this capability |

### Device Capabilities Register (offset +4)

| Bit | Name | Notes |
|-----|------|-------|
| [2:0] | MaxPayloadSize Supported | 000=128B, 001=256B, 010=512B, 011=1KB, 100=2KB, 101=4KB |
| [4:3] | Phantom Functions Supported | 0=not supported |
| 5 | Extended Tag Field Supported | 1 = 8-bit tags supported |
| [8:6] | Endpoint L0s Acceptable Latency | 0=<64ns, 1=64–128ns, … 7=no limit |
| [11:9] | Endpoint L1 Acceptable Latency | 0=<1µs, 1=1–2µs, … 7=no limit |
| 15 | Role-Based Error Reporting | 1 = RBER; required for PCIe Gen2+ |
| [25:18] | Captured Slot Power Limit Value | Encoded slot power limit |
| [27:26] | Captured Slot Power Limit Scale | 0=1.0x, 1=0.1x, 2=0.01x, 3=0.001x |

### Device Control Register (offset +8)

| Bit | Name | Description |
|-----|------|-------------|
| 0 | Correctable Error Reporting Enable | Enable AER correctable interrupt to RC |
| 1 | Non-Fatal Error Reporting Enable | Enable non-fatal error interrupt |
| 2 | Fatal Error Reporting Enable | Enable fatal error interrupt |
| 3 | Unsupported Request Reporting Enable | Enable UR reporting |
| 4 | Enable Relaxed Ordering | Permit RO bit in TLP headers |
| [7:5] | MaxPayloadSize | 000=128B, …must ≤ MaxPayloadSize Supported |
| 8 | Extended Tag Field Enable | Enable 8-bit tags (requires bit5=1 in DevCap) |
| 9 | Phantom Functions Enable | Enable Phantom Function use (rarely needed) |
| 10 | Aux Power PM Enable | Allow device to draw Vaux in D3cold |
| 11 | Enable No Snoop | Permit No Snoop bit in TLPs (cache bypass) |
| [14:12] | MaxReadReqSize | 000=128B, 001=256B, 010=512B, 011=1KB, 100=2KB, 101=4KB |
| 15 | BCR / FLR | Write 1 to initiate Function-Level Reset (FLR) |

### Device Status Register (offset +10)

| Bit | Name | Description (write-1-to-clear) |
|-----|------|-------------------------------|
| 0 | Correctable Error Detected | Latched; clear with write-1 |
| 1 | Non-Fatal Error Detected | Latched |
| 2 | Fatal Error Detected | Latched |
| 3 | Unsupported Request Detected | Latched |
| 4 | Aux Power Detected | Device drawing Vaux |
| 5 | Transactions Pending | 1 = device has pending completions; must be 0 before D3hot |

### Link Capabilities Register (offset +12)

| Bit | Name | Notes |
|-----|------|-------|
| [3:0] | MaxLinkSpeed | 0x1=2.5GT/s, 0x2=5GT/s, 0x3=8GT/s, 0x4=16GT/s, 0x5=32GT/s |
| [9:4] | MaxLinkWidth | 0x01=x1, 0x02=x2, 0x04=x4, 0x08=x8, 0x10=x16 |
| [11:10] | ASPM Support | bit10=L0s, bit11=L1 support |
| [14:12] | L0s Exit Latency | 0=<64ns … 7=≥4µs |
| [17:15] | L1 Exit Latency | 0=<1µs … 7=≥32µs |
| 18 | Clock Power Management Capable | 1 = CLKREQ# can be used |
| 19 | Surprise Down Error Reporting Capable | 1 = can detect sudden link loss |
| 20 | Data Link Layer Link Active Reporting Capable | 1 = DLLA bit in Link Status valid |
| 21 | Link BW Notification Capability | 1 = BW change interrupts available |
| 22 | ASPM Optionality Compliance | 1 = ASPM is optional per board design |
| [31:24] | Port Number | Unique port number assigned by firmware |

### Link Control Register (offset +16 = 0x090 for typical EP layout)

| Bit | Name | Description |
|-----|------|-------------|
| [1:0] | ASPM Control | 00=Disabled, 01=L0s only, 10=L1 only, 11=L0s+L1 |
| 3 | Read Completion Boundary (RCB) | 0=64B, 1=128B |
| 4 | Link Disable | Write 1 to disable the link (downstream port only) |
| 5 | Retrain Link | Write 1 to initiate link retraining |
| 6 | Common Clock Configuration | 1 = both sides use common reference clock (spread-spectrum safe) |
| 7 | Extended Synch | 1 = increase FTS count for better link stability |
| 8 | Enable Clock PM | 1 = allow CLKREQ# to gate reference clock (L1.2 prerequisite) |
| 9 | HW Autonomous Width Disable | 1 = disable automatic width downgrade |
| 10 | Link BW Management Interrupt Enable | Enable interrupt on link BW change |
| 11 | Link Autonomous BW Interrupt Enable | Enable interrupt on autonomous BW change |

### Link Status Register (offset +18)

| Bit | Name | Notes |
|-----|------|-------|
| [3:0] | Current Link Speed | Same encoding as MaxLinkSpeed |
| [9:4] | Negotiated Link Width | Active link width |
| 11 | Link Training | 1 = LTSSM is in Training or Recovery |
| 12 | Slot Clock Config | 1 = device uses slot reference clock |
| 13 | Data Link Layer Link Active | 1 = DL layer is in DL_Active (link fully up) |
| 14 | Link BW Management Status | 1 = link degraded below negotiated width/speed |
| 15 | Link Autonomous BW Status | 1 = link changed speed/width autonomously |

### Device Capabilities 2 Register (offset +24)

| Bit | Name | Notes |
|-----|------|-------|
| [3:0] | Completion Timeout Ranges Supported | Bitmap: A=bit0, B=bit1, C=bit2, D=bit3 |
| 4 | Completion Timeout Disable Supported | 1 = software can disable timeout |
| 5 | ARI Forwarding Supported | For MFD (multi-function) devices behind switch |
| [11:9] | LTR Mechanism Supported | 1 = LTR extended cap implemented |
| [13:12] | OBFF Supported | 0=not supported, 1=WAKE#, 2=WAKE#+CLKREQ# variant |

### Device Control 2 Register (offset +40 = 0x0A8 for typical EP)

| Bit | Name | Description |
|-----|------|-------------|
| [3:0] | Completion Timeout Value | 0000=range A (50µs–50ms default); see spec Table 7-31 |
| 4 | Completion Timeout Disable | 1 = disable completion timeout (if DevCap2 bit4=1) |
| 5 | ARI Forwarding Enable | Enable ARI (alternate routing ID) for MFD |
| 6 | Atomic Op Requester Enable | Enable AtomicOp TLPs (rare) |
| 10 | LTR Mechanism Enable | 1 = enable LTR message sending |
| [13:12] | OBFF Enable | 0=disabled, 1=WAKE# signaling enabled, 2=CLKREQ variant |

### Link Capabilities 2 Register (offset +44)

| Bit | Name | Notes |
|-----|------|-------|
| [7:1] | Supported Link Speeds Vector | bit1=2.5GT/s, bit2=5GT/s, bit3=8GT/s, bit4=16GT/s, bit5=32GT/s |
| 8 | Crosslink Supported | 1 = supports crosslink (rare, test only) |

### Link Control 2 Register (offset +48 = 0x0B0 for typical EP)

| Bit | Name | Description |
|-----|------|-------------|
| [3:0] | Target Link Speed | Speed to transition to after retraining: 1=2.5GT/s, 2=5GT/s, 3=8GT/s, 4=16GT/s |
| 4 | Enter Compliance | Force link into compliance mode |
| 5 | HW Autonomous Speed Disable | 1 = disable hardware-initiated speed change |
| [9:7] | Transmit Margin | Test mode; should be 000 in normal operation |
| 10 | Enter Modified Compliance | Test mode |
| 12 | Compliance SOS | Send SKP OS Sequence instead of compliance pattern |
| [15:12] | Compliance Preset/De-emphasis | Test mode |

### Link Status 2 Register (offset +50)

| Bit | Name | Description |
|-----|------|-------------|
| 0 | Current De-emphasis Level | 0 = -6dB, 1 = -3.5dB |
| 1 | Equalization Complete | 1 = EQ done (Gen3+) |
| 2 | Equalization Phase 1 Successful | |
| 3 | Equalization Phase 2 Successful | |
| 4 | Equalization Phase 3 Successful | |
| 5 | Link Equalization Request | 1 = EQ re-run requested |

### Slot Capabilities (if Slot Implemented=1, offset +20)

See `PCIE5_HOTPLUG_RULES.md` for full Slot Cap / Slot Control / Slot Status coverage.

---

## LTR Extended Capability (Cap ID = 0x0018, Extended Cap)

Located at 0x100+ in extended config space.

| Offset | Field | Description |
|--------|-------|-------------|
| +4 | Max Snoop Latency | bits[9:0]=value; bits[12:10]=scale (0=1ns, 1=32ns, 2=1µs, 3=32µs, 4=1ms, 5=32ms) |
| +6 | Max No-Snoop Latency | Same encoding as Max Snoop Latency |

**Usage**: Device sends LTR messages with these maximum latency values. Platform uses them to decide when it can enter low-power states. A value of 0 in both fields = device has no latency requirement (allows platform to sleep freely).

---

## L1 PM Substates Extended Capability (Cap ID = 0x001E, Extended Cap)

Located at 0x100+ in extended config space.

### L1 PM Substates Capabilities Register

| Bit | Name | Description |
|-----|------|-------------|
| 0 | PCI-PM L1.2 Supported | 1 = device supports PCI-PM-based L1.2 |
| 1 | PCI-PM L1.1 Supported | 1 = device supports PCI-PM-based L1.1 |
| 2 | ASPM L1.2 Supported | 1 = device supports ASPM-based L1.2 (requires CLKREQ#) |
| 3 | ASPM L1.1 Supported | 1 = device supports ASPM-based L1.1 |
| 4 | L1 PM Substates Supported | 1 = any L1 substate supported (summary bit) |
| [15:8] | Port Common Mode Restore Time | Time in µs for Vcc stabilization after L1.1/L1.2 exit |
| [19:16] | Port T_POWER_ON Scale | Multiplier for T_POWER_ON: 0=2µs, 1=10µs, 2=100µs |
| [24:20] | Port T_POWER_ON Value | Multiplied by scale gives total T_POWER_ON time |

### L1 PM Substates Control 1 Register

| Bit | Name | Description |
|-----|------|-------------|
| 0 | PCI-PM L1.2 Enable | 1 = enable PCI-PM L1.2 |
| 1 | PCI-PM L1.1 Enable | 1 = enable PCI-PM L1.1 |
| 2 | ASPM L1.2 Enable | 1 = enable ASPM L1.2 (requires Enable Clock PM in Link Control) |
| 3 | ASPM L1.1 Enable | 1 = enable ASPM L1.1 |
| [15:8] | Common Mode Restore Time | Must ≥ Port Common Mode Restore Time from Capabilities |
| [25:16] | LTR L1.2 Threshold Scale+Value | Encoded LTR threshold for L1.2 entry; 0 = always enter L1.2 |

### L1 PM Substates Control 2 Register

| Bit | Name | Description |
|-----|------|-------------|
| [1:0] | T_POWER_ON Scale | 0=2µs, 1=10µs, 2=100µs — must ≥ Port T_POWER_ON Scale in Capabilities |
| [6:2] | T_POWER_ON Value | Multiplied by scale; must ≥ Port T_POWER_ON Value in Capabilities |

---

## Required Evidence Fields (`checks.pcie_cfgspace_report`)

```yaml
# Mandatory
vidpid_read_observed: boolean
vidpid_value: string            # "17A0:9767"; "FFFF:FFFF" = absent
class_code_value: string        # hex, e.g. "010500"
subsystem_vidpid_read: boolean
enumeration_sequence_complete: boolean
bar_sizing_observed: boolean
bar_count_probed: integer
capability_chain_traversed: boolean

# Command / Status
command_register_value: string  # hex, e.g. "0x0007"
memory_space_enabled: boolean   # Command bit1
bus_master_enabled: boolean     # Command bit2
intx_disable: boolean           # Command bit10

# Interrupt configuration
msi_or_msix_enabled: boolean
msi_type: string                # "msi" | "msix" | "intx" | "none"
msi_address_valid: boolean      # non-zero and not all-F

# PCIe Express Capability
link_control_read_before_write: boolean
link_control_aspm_value: string # hex value at 0x090
device_control_value: string    # hex, Device Control register
device_control2_value: string   # hex, Device Control 2 register
max_payload_size_set: integer   # bytes (128, 256, 512, ...)
max_read_req_size_set: integer
completion_timeout_value: string

# Extended Capabilities
ltr_enabled: boolean
ltr_message_sent: boolean
l1pm_substates_configured: boolean
l1pm_control1_value: string     # hex
l1pm_control2_value: string     # hex

# Optional
notes: array[string]
```

---

## Key Config Space Offset Reference

| Offset | Register | Critical bits |
|--------|----------|---------------|
| 0x000 | VID / DID | non-FFFF confirms device present |
| 0x004 | Command | bit0=MemSpc, bit1=IOSpc, bit2=BusMaster, bit10=INTxDis |
| 0x006 | Status | bit4=CapsList, bit5=Txns Pending (legacy), bit8=MstParErr |
| 0x008 | Revision ID / Class Code | Class 010500 = SD Host |
| 0x00E | Header Type | bit7=MFD; bits[6:0]=0=Type0 endpoint |
| 0x010–0x024 | BAR[0]–[5] | 64-bit BAR uses two consecutive slots |
| 0x02C | Subsystem VID/ID | Platform-level device identity |
| 0x034 | Capabilities Pointer | Start of standard capability chain |
| 0x03D | Interrupt Pin | 0=none; 1=INTA# |
| cap+0x08 | Device Control | bits[7:5]=MPS, bits[14:12]=MRRS, bit11=NoSnoop |
| cap+0x10 | Device Status | bit5=Transactions Pending (must=0 before D3hot) |
| cap+0x0C | Link Capabilities | bits[3:0]=MaxSpeed, bits[9:4]=MaxWidth, bits[11:10]=ASPM |
| cap+0x10 | Link Control (0x090) | bits[1:0]=ASPM, bit8=ClockPM |
| cap+0x12 | Link Status | bits[3:0]=CurrSpeed, bits[9:4]=NegWidth |
| cap+0x28 | Device Control 2 | bits[3:0]=CTO, bit10=LTR Enable |
| cap+0x30 | Link Control 2 (0x0B0) | bits[3:0]=TargetSpeed |
| 0x100+ | Extended Caps | AER (0x001), LTR (0x018), L1PM (0x01E) |

---

## Reviewer Prompts

**Identification**
- Was CfgRd 0x000 (VID/DID) observed with non-FFFF Vendor ID?
- Was Class Code consistent with the expected device type?
- Was Subsystem VID/ID read for platform identification?

**BAR and access control**
- Was BAR sizing (FFFFFFFF probe) observed for all implemented BARs?
- Was Memory Space Enable (Command bit1) set before any MRd/MWr to BAR?
- Was Bus Master Enable (Command bit2) set before DMA?

**Interrupt configuration**
- Is MSI Enable or MSI-X Enable set? Is INTx Disable consistent?
- Is MSI Message Address a valid APIC address?
- If MSI-X: is Table BIR pointing to an assigned BAR?

**PCIe Express Capability**
- Was Link Control (0x090) read before it was written?
- Were MaxPayloadSize and MaxReadReqSize within device capability?
- Was Completion Timeout configured for the device's response latency?
- Was Target Link Speed (0x0B0) consistent with the negotiated speed?

**Power management and substates**
- Was LTR Enable set only after LTR message was transmitted?
- Were L1 PM Substates registers (L1.1/L1.2 Enable, T_POWER_ON) configured correctly?
- Is Transactions Pending (Device Status bit5) 0 before D3hot write?

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
