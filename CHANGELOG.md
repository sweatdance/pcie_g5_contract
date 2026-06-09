# Changelog

## v0.11.0 - 2026-06-09

- **pcie-aer expanded to 90%+ coverage** (was ~40%):
  - Rules expanded from 6 to 13 (AER-001 through AER-013), now covering:
    - Malformed TLP / Unexpected Completion / Surprise Down hard stops (existing)
    - Flow Control Protocol Error (bit13) — always fatal, new hard stop (AER-008)
    - First Error Pointer consistency (AER-011) — hard stop if mismatch
    - Non-default AER Mask (AER-009) — masked bits must be documented
    - Advisory Non-Fatal classification (AER-010) — undocumented Severity override
    - Asymmetric ECRC configuration (AER-007) — warn for non-functional ECRC
    - Root Error Status without Source ID (AER-012) — forensic analysis impossible
    - Correctable error burst pattern (AER-013) — >5 same type within 60ms
  - doc `PCIE5_AER_RULES.md` completely rewritten: Uncorrectable Error Status all 27 bits,
    Correctable Error Status all 16 bits, Root Error Command, Root Error Status, Error Source ID,
    AER Capabilities and Control (ECRC bits, First Error Pointer), TLP Header Log, WHEA mapping table
  - New validator `pcie_aer_json_validator.py`
  - New fixtures: `smoke_aer_compliant.checks.json`, `smoke_aer_noncompliant_surprise_not_logged.checks.json`

- **pcie-dll expanded to 90%+ coverage** (was ~50%):
  - Rules expanded from 5 to 11 (DLL-001 through DLL-011), now covering:
    - TLP before DL_Up / NAK without replay (existing hard stops)
    - REPLAY_NUM rollover without Recovery (DLL-007) — new hard stop
    - FC credit types not all initialized before TLP flow (DLL-009)
    - DLLP CRC16 error without DL re-sync (DLL-008)
    - PM DLLP before DL_Up (DLL-011)
    - 12-bit sequence number wrap (DLL-010)
    - ACK sequence number out-of-window (DLL-006)
  - doc `PCIE5_DLL_RULES.md` completely rewritten: full DLLP type table, ACK/NAK/UpdateFC
    format tables, FC credit type reference, REPLAY_NUM state machine, InitFC sequence diagram,
    PM DLLP ordering rules, DLLP CRC16 description, evidence field YAML schema
  - New validator `pcie_dll_json_validator.py`
  - New fixture: `smoke_dll_compliant.checks.json`

- **pcie-tlp expanded to 90%+ coverage** (was ~50%):
  - Rules expanded from 6 to 13 (TLP-001 through TLP-013), now covering:
    - Non-SC Completion / Poisoned TLP / BAR violation (existing hard stops)
    - Tag reuse before Completion (TLP-008) — new hard stop
    - TLP Length mismatch (TLP-013) — new hard stop (Malformed TLP)
    - Invalid Last DW BE for multi-DWORD requests (TLP-007)
    - Message TLP routing type mismatch (TLP-009)
    - TC out of established VC range (TLP-010)
    - Type 1 Config Request from wrong port type (TLP-011)
    - Extended Tag used without Enable bit (TLP-012)
  - doc `PCIE5_TLP_RULES.md` completely rewritten: Fmt/Type encoding table, TLP DW0 fields,
    First/Last DW BE rules, Completion Status encoding table, Completion header fields, Tag
    management (5/8/10-bit), Message TLP type table with routing subtypes, AtomicOp TLPs,
    Traffic Class/VC mapping, TLP ordering rules, evidence field YAML schema
  - New validator `pcie_tlp_json_validator.py`
  - New fixture: `smoke_tlp_compliant.checks.json`

- Updated `contract.yaml`: version 0.11.0, added `pcie_aer_json_validator.py`,
  `pcie_dll_json_validator.py`, `pcie_tlp_json_validator.py`
- Updated `fixtures/fixture_manifest.json`: added 4 new fixture entries



- **pcie-cfgspace expanded to 90%+ coverage** (was ~14%):
  - Rules expanded from 5 to 26 (CFG-001 through CFG-026), now covering:
    - All Type 0 Header registers (VID/DID, Command all 11 bits, Status, Class Code,
      Subsystem VID/ID, Header Type, Interrupt Pin)
    - Power Management Capability (D-state support, PMCSR D3hot/D0 access rules)
    - MSI Capability (Enable, address validity, INTx Disable consistency)
    - MSI-X Capability (Table BIR validity, Function Mask, Enable)
    - Full PCIe Express Capability (Device Control all bits, Link Control all bits,
      Device Control 2 including Completion Timeout, LTR Enable, OBFF Enable)
    - LTR Extended Capability (LTR Enable before LTR message warn)
    - L1 PM Substates Extended Capability (T_POWER_ON, LTR threshold, Common Mode Restore)
  - doc `PCIE5_CONFIG_SPACE.md` completely rewritten: all register tables with bit
    definitions, L1 PM Substates register details, evidence field YAML schema
  - New validator `pcie_cfgspace_json_validator.py` enforcing CFG-001, CFG-006, CFG-013
    (hard stops) and CFG-002 through CFG-026 (warns)
  - New fixtures: `smoke_cfgspace_compliant.checks.json`,
    `smoke_cfgspace_noncompliant_no_vidpid.checks.json`

- **pcie-pm expanded to 90%+ coverage** (was ~40%):
  - Rules expanded from 6 to 17 (PM-001 through PM-017), now covering:
    - D-states: D0/D1/D2/D3hot/D3cold definitions, transition rules, Trst delay
    - PMCSR write sequence (Transactions Pending=0 gate, No_Soft_Reset)
    - PM_PME message flow, PME_Status clearing, PME_En from unsupported D-state
    - L0s entry (EIEOS sequence, latency requirements)
    - L1.1 / L1.2 substates: L1 PM Substates Capabilities all bits, Control 1 all bits,
      Control 2 all bits, T_POWER_ON programming requirement
    - PME_Turn_Off / PME_TO_Ack sequence (10ms timeout)
  - doc `PCIE5_POWER_MANAGEMENT.md` expanded with D-state reference, PM Capability
    register tables, L0s/L1 description, L1 PM Substates register tables, PME flow,
    PME_Turn_Off sequence, evidence field YAML schema
  - `pcie_pm_json_validator.py` extended with PM-007 through PM-016 rule enforcement
  - New fixture: `smoke_pm_compliant_d3hot.checks.json`

- **pcie-hotplug expanded to 90%+ coverage** (was ~60%):
  - Rules expanded from 7 to 16 (HP-001 through HP-016), now covering:
    - Slot Capabilities all bits (Hot-Plug Capable, Hot-Plug Surprise, Power Controller,
      MRL Sensor, Attention Indicator, Power Indicator, EMI, Slot Power Limit)
    - Slot Control all bits (Attention/Power Indicator Control encoding, Power Controller
      Control, DLLSC Enable, CommandCompleted Interrupt Enable)
    - Slot Status all bits (PDC, CommandCompleted, MRL Sensor State, Presence Detect State,
      DLLSC)
    - Hot-add command sequence (Blink → Power On → poll CommandCompleted → T_Power_Up →
      PERST# de-assert → wait DLLSC → enumerate → Power Indicator On → Attn Indicator Off)
    - Hot-remove sequence (Power Indicator Off → Power Controller Off → poll CommandCompleted)
    - Timing requirements table (T_Power_Up 100ms, T_Reset 100µs, T_Cmd 1s poll)
    - HP-010 (hard stop): power removed without PERST# assertion
    - HP-011 (hard stop): second SlotCtl write before CommandCompleted
  - doc `PCIE5_HOTPLUG_RULES.md` expanded with full HPC register tables (SlotCap,
    SlotCtl, SlotSts bit definitions), hot-add/remove command sequence pseudocode,
    timing requirements table
  - `pcie_hotplug_json_validator.py` extended with HP-008 through HP-016 enforcement
  - New fixture: `smoke_hotplug_noncompliant_cmd_without_completed.checks.json`

- Updated `contract.yaml`: version 0.10.0, added `pcie_cfgspace_json_validator.py`
- Updated `fixtures/fixture_manifest.json`: added 4 new fixture entries



- Expanded contract from Physical Layer only to full PCIe protocol coverage.
- Added Power Management slice (pcie-pm): ASPM enable sequencing, PM L1 before enumeration
  detection, PM_Request_Ack in enumeration window detection.
- Added Configuration Space slice (pcie-cfgspace, warn-grade): VID/DID read confirmation,
  BAR sizing sequence, Link Control read-modify-write pattern, Bus Master Enable.
- Added AER / Error Handling slice (pcie-aer): Surprise Down logging, Malformed TLP,
  Unexpected Completion, AER register clearing after hot-plug.
- Added Data Link Layer slice (pcie-dll): InitFC1/InitFC2 sequence, NAK replay enforcement,
  UpdateFC absence warning, repeated InitFC2 artifact warning.
- Added Transaction Layer slice (pcie-tlp): non-SC Completion explanation requirement,
  Poisoned TLP AER correspondence, unassigned BAR access detection, CfgRd timeout warning.
- Added Hot-Plug Lifecycle slice (pcie-hotplug): MUX switch timing enforcement (≥500ms gap),
  ASPM state cleanliness, stale AER clearing, TS1 rate-based device identification.
- Added validators: pcie_pm_json_validator.py, pcie_hotplug_json_validator.py.
- Added fixtures for PM and Hot-Plug slices (compliant and noncompliant).
- Updated contract.yaml: name changed to pcie-gen5-full-protocol, version 0.9.0,
  added hard_stop_rules for pcie-pm/aer/dll/tlp/hotplug, warn_rules for pcie-cfgspace.
- Physical Layer slices (LTSSM, equalization, speed/width, recovery) unchanged from v0.3.0.

## v0.3.0 - 2026-05-04

- Expanded the PCIe Gen5 LTSSM contract from a minimal slice into a reusable validation pack for LTSSM state transitions, equalization, speed and width negotiation, and recovery visibility.
- Added contract documentation for spec-to-contract mapping, LTSSM transition evidence, equalization review requirements, negotiation expectations, and recovery or fallback handling.
- Strengthened `pcie_ltssm_json_validator.py` to enforce report structure, field types, schema versioning, and cross-field failure-mode consistency.
- Added positive and negative smoke fixtures plus regression scripts for contract validation.
- Added a GitHub Actions workflow for regression smoke execution in CI.

## v0.2.0 - 2026-05-04

- Added richer JSON evidence schema coverage for LTSSM traces, equalization summaries, degraded-width handling, and recovery visibility.
- Introduced rule packs for LTSSM, equalization, and link-negotiation review slices.

## v0.1.0 - 2026-05-04

- Initial external PCIe Gen5 LTSSM link-training contract scaffold.
- Added machine-readable `contract.yaml`, reviewer guidance, baseline docs, validator entrypoint, and smoke fixtures.

- Expanded the PCIe Gen5 LTSSM contract from a minimal slice into a reusable validation pack for LTSSM state transitions, equalization, speed and width negotiation, and recovery visibility.
- Added contract documentation for spec-to-contract mapping, LTSSM transition evidence, equalization review requirements, negotiation expectations, and recovery or fallback handling.
- Strengthened `pcie_ltssm_json_validator.py` to enforce report structure, field types, schema versioning, and cross-field failure-mode consistency.
- Added positive and negative smoke fixtures plus regression scripts for contract validation.
- Added a GitHub Actions workflow for regression smoke execution in CI.

## v0.2.0 - 2026-05-04

- Added richer JSON evidence schema coverage for LTSSM traces, equalization summaries, degraded-width handling, and recovery visibility.
- Introduced rule packs for LTSSM, equalization, and link-negotiation review slices.

## v0.1.0 - 2026-05-04

- Initial external PCIe Gen5 LTSSM link-training contract scaffold.
- Added machine-readable `contract.yaml`, reviewer guidance, baseline docs, validator entrypoint, and smoke fixtures.