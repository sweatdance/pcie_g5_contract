# Verification Status (LLM-Facing)

> This page is a visibility summary, not an automatically regenerated truth source.
> The governed source is `contract.yaml`, `fixtures/fixture_manifest.json`, and validator scripts.

## 1) Current verification summary

- Last verified run: `python -X utf8 scripts/run_regression_smoke.py --suite advisory --format json`
  and `python -X utf8 scripts/run_regression_smoke.py --suite required --format json`
- Total fixture entries: **24**
- Expected passing fixtures: **10**
- Expected failing fixtures: **14**
- Scope mode:
  - Required scope: `pcie-ltssm` / `pcie-eq` / `pcie-link-negotiation`
  - Advisory scope: `pcie-pm` / `pcie-aer` / `pcie-dll` / `pcie-tlp` / `pcie-hotplug` / `pcie-cfgspace`
- Overall outcome (this run):
  - Fixture smoke matched expectations: **23 / 24**
  - Regression smoke (`run_regression_smoke.py`) overall: **FAILED** because fixture mismatch exists in advisory slices
- External repo smoke (`run_external_repo_smoke`) returned: **ok**
- External warning of note: advisory routing no longer uses no-evidence mode; one remaining noncompliant advisory fixture mismatch is `smoke_cfgspace_noncompliant_no_vidpid` which currently does not emit hard-stop errors under existing `pcie_cfgspace_json_validator` semantics.

## 2) Coverage by slice

| Slice | Fixtures | Pass | Fail | Claim level |
| --- | ---: | ---: | ---: | --- |
| pcie-ltssm | 12 | 3 | 9 | required_gate_ready |
| pcie-eq | 12 | 3 | 9 | required_gate_ready |
| pcie-link-negotiation | 12 | 3 | 9 | required_gate_ready |
| pcie-pm | 3 | 3 | 0 | advisory_expansion |
| pcie-hotplug | 3 | 3 | 0 | advisory_expansion |
| pcie-aer | 2 | 2 | 0 | advisory_expansion |
| pcie-cfgspace | 2 | 1 | 1 | advisory_expansion |
| pcie-dll | 1 | 1 | 0 | advisory_expansion |
| pcie-tlp | 1 | 1 | 0 | advisory_expansion |

Notes:
- `pcie-ltssm`, `pcie-eq`, and `pcie-link-negotiation` are the same required evidence slice set
  with different rule labels, so counts overlap by design.
- Required-scope fixtures are all expectation-matching (**12/12**) and remain the only set suitable for CI gate boundary.
- Advisory slice status: PM/AER/Hot-Plug/DLL/TLP non-compliant fixtures now fail as expected and emit policy errors; CFG-space non-compliant fixture remains non-blocking (`matched_expectation = false`) and needs validator severity mapping review.

Note: pcie-eq and pcie-link-negotiation are part of the completed LTSSM/link-training
claim surface and are used together with LTSSM required slices.

## 3) Maturity meanings

- **required_gate_ready**: evidence slice is in contract scope and matched fixture expectations; acceptable for required CI gates.
- **advisory_expansion**: review-visible, rule-checked output exists, but routing is not yet proven as hard gate evidence.
- **not_claimed**: not part of this contract's proven completion boundary.

## 4) Update rule for this page

- Update only when `fixtures/fixture_manifest.json`, `contract.yaml`, or rule pack
  coverage shape changes.
- Do not infer missing entries as completed unless fixture manifest and claim ceiling
  are updated together.
- Required-gate status must be recalculated from latest `run_regression_smoke.py` and `run_fixture_smoke.py` JSON output.
- Do not promote advisory-expansion fixtures to required-gate status until they produce matched
  expectation under routed JSON evidence for those rule domains.

## 5) Evidence source locations

- `fixtures/fixture_manifest.json`
- `contract.yaml`
- `docs/*_rules.md`
- `rules/pcie-*/review.md`
- `scripts/run_*_smoke.py`
