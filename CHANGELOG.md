# Changelog

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