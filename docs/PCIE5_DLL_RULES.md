# PCIe Data Link Layer Rules

This contract slice enforces Data Link layer initialization and flow control visibility.

## Background

The PCIe Data Link Layer (DLL) sits between the Physical layer and Transaction layer. Its
responsibilities relevant to debug:

- **Flow Control (FC) initialization**: Before any TLPs can flow, both sides must complete
  the InitFC handshake (InitFC1 → InitFC2 exchange in both directions). Only after this
  handshake does the DLL transition to DL_Up and TLP flow is allowed.
- **ACK/NAK protocol**: Every TLP is acknowledged by an ACK DLLP (or NAK if corrupted).
  A NAK triggers a replay from the sender. Excessive NAKs indicate signal integrity issues.
- **UpdateFC**: After initial FC credit exchange, UpdateFC DLLPs are sent periodically to
  refresh credit availability. Absence of UpdateFC in a long capture may indicate filtering
  or starvation.
- **CATC artifact warning**: Repeated InitFC2 with identical values is a known CATC
  frequency-lock artifact during initial training and should not be treated as real FC errors
  without further evidence.

## Required evidence fields (`checks.pcie_dll_report`)

- `initfc_complete`: boolean — were InitFC1 + InitFC2 DLLPs observed in both directions?
- `dl_up_confirmed`: boolean — was DL_Up (post-SDS + InitFC) confirmed before first TLP?
- `nak_observed`: boolean — was any NAK DLLP observed in the capture?
- `nak_followed_by_replay`: boolean — if NAK observed, was a subsequent replay sequence seen?
- `updatefc_observed`: boolean — were UpdateFC DLLPs present in the capture?
- `capture_duration_ms`: number — duration of the capture in milliseconds (for UpdateFC context)

## Conditionally required fields

- `initfc_direction_evidence`: string — description of which directions InitFC was seen
  ("upstream_only", "downstream_only", "both_directions")
- `nak_count`: integer — number of NAK DLLPs observed (required when `nak_observed = true`)
- `repeated_initfc2_count`: integer — number of InitFC2 repetitions with identical values
  (required when > 3 repetitions detected)
- `notes`: array of strings

## Contract rules

- `PCIE5-DLL-001`: If `dl_up_confirmed = false` but TLPs are present, this is a hard stop.
  TLPs cannot appear before DL layer is active.
- `PCIE5-DLL-002`: If `nak_observed = true` and `nak_followed_by_replay = false`, this is
  a hard stop. NAK without replay violates the DL retransmission protocol.
- `PCIE5-DLL-003` (warn): If `updatefc_observed = false` and `capture_duration_ms > 200`,
  warn for possible FC starvation or capture filtering.
- `PCIE5-DLL-004` (warn): If `repeated_initfc2_count > 3`, warn. These may be CATC
  frequency-lock artifacts (see CATC Tip #2); do not treat as definitive FC errors.
- `PCIE5-DLL-005` (warn): If `nak_count > 5` in a single capture, warn for signal integrity
  review.

## InitFC sequence reference

```
Physical Link Up (SDS)
    ↓
InitFC1 (DS→US): VC0 Posted/Non-Posted/Completion credit advertisement
InitFC1 (US→DS): VC0 credit advertisement
    ↓
InitFC2 (DS→US): Echo of InitFC1 values
InitFC2 (US→DS): Echo
    ↓
DL_Up: TLP flow now permitted
    ↓
UpdateFC (periodic): Credit refresh
```

## Reviewer prompts

- Were InitFC1 and InitFC2 seen in both Downstream and Upstream directions?
- Was the first TLP (CfgRd/MRd) observed after InitFC completion?
- Were there NAK DLLPs, and was each followed by a replay?
- Are repeated InitFC2 values likely CATC artifacts (check if they appeared at link build-up)?
- Was UpdateFC observed in the capture duration?
