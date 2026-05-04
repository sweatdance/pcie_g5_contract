# Release Notes v0.3.0

## Summary

`v0.3.0` is the first contract release intended for reuse across private RTL projects using the AI Governance Framework.

This release stabilizes the PCIe Gen5 LTSSM link-training slice around four review-visible themes:

- LTSSM transition evidence
- equalization completion and failure reporting
- speed and width negotiation consistency
- recovery, retrain, and fallback visibility

## Included in this release

- Reusable external contract entrypoint in `contract.yaml`
- Domain guidance in `AGENTS.md`
- Spec-aligned evidence guidance in `docs/`
- Review rule packs in `rules/`
- Enforcing JSON validator in `validators/pcie_ltssm_json_validator.py`
- Positive and negative smoke fixtures in `fixtures/`
- Regression helpers in `scripts/`
- GitHub Actions regression workflow in `.github/workflows/contract-regression.yml`

## Validation highlights

- The validator now checks required fields, field types, supported schema version, and nested report structure.
- The validator now enforces cross-field consistency for:
  - `ltssm_trace_summary.reached_recovery`
  - `recovery_triggered`, `recovery_reason`, and `retry_count`
  - `downtrained` and `fallback_reason`
  - `equalization_complete` against completed and failed phase evidence
  - degraded-width expectation versus negotiated width

## Regression coverage

The fixture suite covers:

- nominal training success
- illegal LTSSM transition summary
- missing LTSSM trace summary
- incomplete equalization evidence
- missing downtraining reason
- unexpected width mismatch
- unsupported schema version
- retry count without recovery trigger
- equalization marked complete with missing nominal phases

## Upgrade notes

- Reports should continue to use `schema_version: "1.0"`.
- Producers must populate `recovery_triggered` and `retry_count` consistently with the LTSSM trace.
- Producers claiming nominal equalization success must report all four phases in `completed_phases` and leave `failed_phases` empty.