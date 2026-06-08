# Changelog

## v0.9.0 - 2026-06-08

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