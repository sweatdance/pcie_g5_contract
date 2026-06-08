# PCIe Transaction Layer Rule Pack

Rule pack: `pcie-tlp`

## Rule basis

- Require Completion Status evidence for all outstanding requests that expect completions.
- Treat non-Successful-Completion (non-SC) status without explanation as a hard stop.
- Treat Poisoned TLPs as a hard stop requiring AER correspondence.
- Require CfgRd without a matching CplD to be flagged as a timeout event.
- Treat Memory requests to unassigned BAR space as a hard stop.

## Hard-stop rules

- `PCIE5-TLP-001`: Completion with non-SC status (UR, CA, CRS) must be explicitly explained.
  An unexplained UR/CA Completion is a hard stop.
- `PCIE5-TLP-002`: Poisoned TLP (EP bit set in TLP header) must have a corresponding AER
  Uncorrectable Error record. Poisoned TLP without AER evidence is a hard stop.
- `PCIE5-TLP-003`: Memory request (MRd or MWr) to an address range that was not assigned
  via BAR sizing is a hard stop (rogue access or software bug).

## Warn rules

- `PCIE5-TLP-004` (warn): CfgRd without a corresponding CplD within the capture window
  suggests a Completion Timeout; warn and check AER Completion Timeout status.
- `PCIE5-TLP-005` (warn): Completion RetryStatus (CRS) observed more than once suggests the
  device is not ready; warn if device was expected to be functional at that point.
- `PCIE5-TLP-006` (warn): TLP Length field inconsistent with the actual payload size
  (detectable via CATC decode error) warrants warn for protocol compliance review.

## Review prompts

- Were any non-SC Completions (UR, CA, CRS) observed? What were the causes?
- Were Poisoned TLPs present? Was there a corresponding AER record?
- Did any CfgRd or MRd lack a matching Completion within the capture?
- Were all Memory requests confined to the assigned BAR address ranges?
- Was CRS observed, and was device readiness confirmed afterward?
