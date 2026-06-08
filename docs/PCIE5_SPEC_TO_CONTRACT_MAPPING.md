# PCIe Gen5 Spec To Contract Mapping

This file maps internal PCIe 5.0 spec study slices into reusable contract surfaces.
It is intentionally normalized and does not reproduce spec text.

## Slice 1: LTSSM states and transitions

- Contract surface: LTSSM state evidence and transition legality summary
- Rule ids: `PCIE5-LTSSM-STATE-001`, `PCIE5-LTSSM-STATE-002`
- Required evidence:
  - final LTSSM state
  - visited states or summarized path
  - illegal transition count
- Validator feasibility: high
- Decision impact: block nominal success claims when illegal transitions are present

## Slice 2: Link training and equalization

- Contract surface: equalization completion and phase summary
- Rule ids: `PCIE5-EQ-001`, `PCIE5-EQ-002`
- Required evidence:
  - equalization completion flag
  - equalization phase summary
  - lane failure summary
- Validator feasibility: high
- Decision impact: block nominal Gen5 success claims when equalization is incomplete

## Slice 3: Speed and width negotiation

- Contract surface: target versus negotiated speed and width
- Rule ids: `PCIE5-LINK-NEG-001`, `PCIE5-LINK-NEG-002`
- Required evidence:
  - target speed and negotiated speed
  - target width and negotiated width
  - degraded-width expectation and reason when applicable
- Validator feasibility: high
- Decision impact: block silent mismatch; warn on explicit degraded-width cases

## Slice 4: Recovery and fallback

- Contract surface: retrain, recovery, fallback visibility
- Rule ids: `PCIE5-RECOVERY-001`
- Required evidence:
  - recovery triggered flag
  - retry count
  - fallback or downtrain explanation when present
- Validator feasibility: medium
- Decision impact: warn or block depending on whether a nominal success claim is made

## Slice 5: Power Management and ASPM

- Contract surface: PM L1 entry/exit sequencing and ASPM configuration safety
- Rule ids: `PCIE5-PM-001`, `PCIE5-PM-002`, `PCIE5-PM-003`, `PCIE5-PM-004`, `PCIE5-PM-005`
- Required evidence:
  - enumeration_complete flag before PM L1 observation
  - aspm_enabled_by_cfgwr and link_control_aspm_value
  - pm_request_ack_in_enum_window flag
- Validator feasibility: high
- Decision impact: hard stop when PM L1 interrupts enumeration; warn on ASPM config gaps

## Slice 6: Configuration Space Access

- Contract surface: enumeration completeness and config space access pattern correctness
- Rule ids: `PCIE5-CFG-001` through `PCIE5-CFG-005`
- Required evidence:
  - vidpid_read_observed and vidpid_value
  - bar_sizing_observed and link_control_read_before_write
  - bus_master_enabled
- Validator feasibility: high
- Decision impact: warn-grade; hard stop only when enumeration claimed but VID/DID absent

## Slice 7: AER and Error Handling

- Contract surface: error event logging and AER register management
- Rule ids: `PCIE5-AER-001` through `PCIE5-AER-006`
- Required evidence:
  - surprise_down_observed and aer_surprise_down_logged
  - malformed_tlp_observed and unexpected_completion_observed
  - aer_registers_cleared
- Validator feasibility: high
- Decision impact: hard stop on Malformed TLP / Unexpected Completion without AER; warn on correctable errors

## Slice 8: Data Link Layer

- Contract surface: InitFC handshake completion and NAK/replay protocol visibility
- Rule ids: `PCIE5-DLL-001` through `PCIE5-DLL-005`
- Required evidence:
  - initfc_complete and dl_up_confirmed
  - nak_observed and nak_followed_by_replay
  - updatefc_observed and capture_duration_ms
- Validator feasibility: high
- Decision impact: hard stop on TLP before DL_Up; hard stop on NAK without replay

## Slice 9: Transaction Layer

- Contract surface: Completion Status visibility and address boundary correctness
- Rule ids: `PCIE5-TLP-001` through `PCIE5-TLP-006`
- Required evidence:
  - non_sc_completion_observed and explanation
  - poisoned_tlp_observed and poisoned_tlp_aer_logged
  - memory_access_to_unassigned_bar
- Validator feasibility: high
- Decision impact: hard stop on unexplained UR/CA/Poisoned TLP; warn on CfgRd timeout

## Slice 10: Hot-Plug Lifecycle

- Contract surface: MUX switch timing, ASPM cleanliness, AER state before new enumeration
- Rule ids: `PCIE5-HP-001` through `PCIE5-HP-007`
- Required evidence:
  - pm_l1_before_enum_complete and pm_request_ack_in_enum_window
  - time_surprise_down_to_first_cfgrd_ms
  - aer_cleared_before_new_enum
  - upstream_ts1_rate_at_first_linkup (for MUX device identification)
- Validator feasibility: high
- Decision impact: hard stop on PM L1 during enumeration window; warn on short MUX timing gaps

## Non-scope for v0.2 (now covered in v0.9.0)

The following were previously listed as non-scope. All are now covered:

- Data Link Layer semantics → Slice 8 (pcie-dll)
- TLP rules → Slice 9 (pcie-tlp)
- Power Management / ASPM → Slice 5 (pcie-pm)
- Configuration Space → Slice 6 (pcie-cfgspace, warn-grade)
- AER / Error Handling → Slice 7 (pcie-aer)
- Hot-Plug Lifecycle → Slice 10 (pcie-hotplug)

Still outside scope:

- retimer-specific coverage
- compliance certification procedures
- lane margining breadth beyond summary evidence
- Vendor-Defined Messages / vendor extensions
