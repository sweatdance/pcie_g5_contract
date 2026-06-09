# Verification Status (LLM-Facing)

> This page is a visibility summary, not an automatically regenerated truth source.
> The governed source is `contract.yaml`, `fixtures/fixture_manifest.json`, and validator scripts.

## 1) Current verification summary

- Total fixture entries: **24**
- Expected passing fixtures: **10**
- Expected failing fixtures: **14**
- Scope mode:
  - Required scope: LTSSM + link-training completion paths
  - Advisory scope: PM/AER/DLL/TLP/Hot-Plug/CFG visibility

## 2) Coverage by slice

| Slice | Fixtures | Pass | Fail | Claim level |
| --- | ---: | ---: | ---: | --- |
| pcie-ltssm | 12 | 3 | 9 | Complete |
| pcie-eq | 12 | 3 | 9 | Complete |
| pcie-link-negotiation | 12 | 3 | 9 | Complete |
| pcie-pm | 3 | 2 | 1 | Advisory |
| pcie-hotplug | 3 | 2 | 1 | Advisory |
| pcie-aer | 2 | 1 | 1 | Advisory |
| pcie-cfgspace | 2 | 1 | 1 | Advisory |
| pcie-dll | 1 | 1 | 0 | Advisory |
| pcie-tlp | 1 | 1 | 0 | Advisory |

Note: `pcie-ltssm`, `pcie-eq`, and `pcie-link-negotiation` are the same required evidence slice
set with different rule labels, so counts overlap by design.

Note: pcie-eq and pcie-link-negotiation are part of the completed LTSSM/link-training
claim surface and are used together with LTSSM required slices.

## 3) Maturity meanings

- **Complete**: accepted for completed claims in current contract ceiling.
- **Advisory**: review-visible, rule-checked, useful for design feedback, but not
  a full-compliance contract claim in this version.

## 4) Update rule for this page

- Update only when `fixtures/fixture_manifest.json`, `contract.yaml`, or rule pack
  coverage shape changes.
- Do not infer missing entries as completed unless fixture manifest and claim ceiling
  are updated together.

## 5) Evidence source locations

- `fixtures/fixture_manifest.json`
- `contract.yaml`
- `docs/*_rules.md`
- `rules/pcie-*/review.md`
- `scripts/run_*_smoke.py`
