# PCIe Data Link Layer Rule Pack

Rule pack: `pcie-dll`

## Rule basis

- Require InitFC1/InitFC2 exchange evidence before claiming Data Link layer is active (DL_Up).
- Treat TLPs observed before DL_Up as hard-stop violations.
- Require NAK DLLPs to be followed by replay evidence.
- Warn when UpdateFC DLLPs are absent in captures long enough to expect them.
- Do not treat SDS alone as proof of Data Link layer readiness.

## Hard-stop rules

- `PCIE5-DLL-001`: TLPs (CfgRd, CfgWr, MRd, MWr, Cpl) must not appear before InitFC
  exchange completion (both InitFC1 and InitFC2 observed in both directions). TLP before
  DL_Up is a hard stop.
- `PCIE5-DLL-002`: NAK DLLP must be followed by a replay sequence. NAK without subsequent
  replay is a hard stop (indicates DL protocol violation or capture truncation).

## Warn rules

- `PCIE5-DLL-003` (warn): UpdateFC DLLPs absent in captures longer than 200ms after DL_Up
  may indicate FC credit starvation or capture filtering. Warn for review.
- `PCIE5-DLL-004` (warn): InitFC1 or InitFC2 with identical VC/FC values repeated more than
  3 times is consistent with DL re-init or CATC frequency-lock decode artifact; warn.
- `PCIE5-DLL-005` (warn): If DLLP ACK sequence number is not monotonically increasing,
  warn for possible DL replay storm.

## Review prompts

- Were InitFC1 and InitFC2 DLLPs observed in both directions before the first TLP?
- Was a NAK observed, and was it followed by a replay?
- Was UpdateFC present in captures long enough to expect it?
- Were there repeated InitFC2 values that could be CATC decode artifacts?
- Is the DL sequence number progression consistent with no DL-layer errors?
