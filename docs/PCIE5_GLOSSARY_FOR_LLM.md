# PCIe Gen5 Contract Glossary (LLM Edition)

## claim_level

How this contract describes confidence level.

- `complete`: in current contract ceiling for this repo and usable for completed-scope claims.
- `advisory`: visible review evidence exists, but not a completed compliance claim yet.

## hard_stop

A rule result that must fail completion claims in required scope. Usually used for
enumeration safety, invalid ordering, or clear protocol violations.

## warn

Visibility-level result that should be reported and reviewed but does not automatically
convert advisory slice into completed-compliance scope.

## required scope

The contract surface that is explicitly allowed to produce completed success claims:
`pcie-ltssm`, `pcie-eq`, `pcie-link-negotiation` (plus recovery/fallback evidence).

## advisory scope

Protocol expansion slices with rule coverage but not full-completion claims:
`pcie-pm`, `pcie-aer`, `pcie-dll`, `pcie-tlp`, `pcie-hotplug`, `pcie-cfgspace`.

## required evidence

Fields and artifacts needed to support a success claim in a required scope.

- Final state
- State transitions / legality summary
- equalization completion and phase summary
- negotiated and target speed/width
- recovery/fallback visibility when triggered
- explicit assumptions

## non_claim

Any assertion that expands contract scope beyond this repo's current `claim_ceiling`.
Do not escalate it as protocol-complete.
