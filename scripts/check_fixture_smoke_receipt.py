#!/usr/bin/env python3
"""Fixture smoke receipt freshness / drift check.

Verifies that the committed `artifacts/validation/fixture-smoke-receipt.json`
is structurally consistent with the current `fixtures/fixture_manifest.json`
and that all required-gate evidence invariants hold.

Exit codes:
  0  all checks passed
  1  one or more checks failed (details printed to stdout)

Usage::

    python scripts/check_fixture_smoke_receipt.py

    # or with explicit paths:
    python scripts/check_fixture_smoke_receipt.py \\
        --receipt  artifacts/validation/fixture-smoke-receipt.json \\
        --manifest fixtures/fixture_manifest.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Required fields that every result entry must carry
# ---------------------------------------------------------------------------
_RESULT_REQUIRED_FIELDS = {
    "file",
    "maturity_tier",
    "routing_ok",
    "matched_expectation",
    "actual_validators",
}

# Maturity tiers that belong to the required-gate surface
_REQUIRED_GATE_TIERS = {"required_gate.trigger_verified", "required_gate.routing_verified"}

# Maturity tiers that belong to the advisory surface
_ADVISORY_TIERS = {"advisory_expansion.routing_verified"}


def _load_json(path: Path) -> dict | list:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def check(receipt_path: Path, manifest_path: Path) -> list[str]:  # noqa: PLR0912
    """Run all drift checks; return a list of failure messages (empty = pass)."""
    failures: list[str] = []

    # ------------------------------------------------------------------
    # 1. Files must exist
    # ------------------------------------------------------------------
    for p in (receipt_path, manifest_path):
        if not p.exists():
            failures.append(f"File not found: {p}")

    if failures:
        return failures  # can't continue without files

    receipt: dict = _load_json(receipt_path)  # type: ignore[assignment]
    manifest: dict = _load_json(manifest_path)  # type: ignore[assignment]

    # ------------------------------------------------------------------
    # 2. Top-level receipt structure
    # ------------------------------------------------------------------
    if receipt.get("artifact_type") != "fixture_smoke_receipt":
        failures.append(
            f"receipt.artifact_type is '{receipt.get('artifact_type')}', "
            f"expected 'fixture_smoke_receipt'"
        )

    if receipt.get("ok") is not True:
        failures.append(
            f"receipt.ok={receipt.get('ok')!r} — last recorded smoke run did not pass overall"
        )

    # ------------------------------------------------------------------
    # 3. Fixture count must match manifest
    # ------------------------------------------------------------------
    manifest_fixtures: list = manifest.get("fixtures", [])
    manifest_count = len(manifest_fixtures)
    receipt_fixture_count: int = receipt.get("fixture_count", -1)
    receipt_results: list = receipt.get("results", [])

    if receipt_fixture_count != manifest_count:
        failures.append(
            f"receipt.fixture_count={receipt_fixture_count} "
            f"!= manifest fixture count={manifest_count} — "
            f"receipt may be stale (manifest changed without re-running smoke)"
        )

    if len(receipt_results) != manifest_count:
        failures.append(
            f"len(receipt.results)={len(receipt_results)} "
            f"!= manifest fixture count={manifest_count} — "
            f"results array length drift"
        )

    # Build a set of fixture filenames from manifest for cross-reference
    manifest_files = {f["file"] for f in manifest_fixtures}
    receipt_files = {r.get("file") for r in receipt_results}

    missing_from_receipt = manifest_files - receipt_files
    if missing_from_receipt:
        for fname in sorted(missing_from_receipt):
            failures.append(
                f"Fixture '{fname}' is in manifest but has no result entry in receipt"
            )

    extra_in_receipt = receipt_files - manifest_files
    if extra_in_receipt:
        for fname in sorted(extra_in_receipt):
            failures.append(
                f"Receipt result '{fname}' has no matching entry in manifest (stale entry)"
            )

    # ------------------------------------------------------------------
    # 4. Per-result structural invariants
    # ------------------------------------------------------------------
    for result in receipt_results:
        fname = result.get("file", "<unknown>")
        prefix = f"[{fname}]"

        # 4a. Required fields present
        for field in sorted(_RESULT_REQUIRED_FIELDS):
            if field not in result:
                failures.append(f"{prefix} missing required field '{field}'")

        tier: str = result.get("maturity_tier", "")

        # 4b. routing_ok must be True for any tier in our known sets
        if tier in (_REQUIRED_GATE_TIERS | _ADVISORY_TIERS):
            if result.get("routing_ok") is not True:
                failures.append(
                    f"{prefix} tier='{tier}' but routing_ok={result.get('routing_ok')!r} "
                    f"(tier name implies routing was verified)"
                )

        # 4c. matched_expectation must be True for the receipt to be valid evidence
        if result.get("matched_expectation") is not True:
            failures.append(
                f"{prefix} matched_expectation={result.get('matched_expectation')!r} "
                f"— fixture expectation mismatch in committed receipt"
            )

        # 4d. required_gate.trigger_verified invariants
        if tier == "required_gate.trigger_verified":
            keywords = result.get("expected_trigger_keywords")
            if not keywords:
                failures.append(
                    f"{prefix} tier='required_gate.trigger_verified' "
                    f"but expected_trigger_keywords is empty/null "
                    f"(tier requires keyword evidence)"
                )
            if result.get("violation_keyword_ok") is not True:
                failures.append(
                    f"{prefix} tier='required_gate.trigger_verified' "
                    f"but violation_keyword_ok={result.get('violation_keyword_ok')!r} "
                    f"(trigger keywords must be present in violations)"
                )

        # 4e. Advisory fixtures must not carry required-gate tiers
        # Detect advisory fixtures by expected_rule_ids containing only advisory slices
        _ADVISORY_SLICES = {
            "pcie-pm", "pcie-aer", "pcie-dll", "pcie-tlp",
            "pcie-hotplug", "pcie-cfgspace",
        }
        _REQUIRED_SLICES = {"pcie-ltssm", "pcie-eq", "pcie-link-negotiation"}

        expected_rule_ids: list = result.get("expected_rule_ids") or []
        pcie_slices_in_fixture = {r for r in expected_rule_ids if r.startswith("pcie-")}

        if (
            pcie_slices_in_fixture
            and pcie_slices_in_fixture.issubset(_ADVISORY_SLICES)
            and tier in _REQUIRED_GATE_TIERS
        ):
            failures.append(
                f"{prefix} advisory fixture (slices={sorted(pcie_slices_in_fixture)}) "
                f"is labeled with required-gate tier='{tier}' — "
                f"advisory fixtures must not be elevated to required-gate"
            )

    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--receipt",
        default="artifacts/validation/fixture-smoke-receipt.json",
        help="Path to fixture smoke receipt JSON (default: artifacts/validation/fixture-smoke-receipt.json)",
    )
    parser.add_argument(
        "--manifest",
        default="fixtures/fixture_manifest.json",
        help="Path to fixture manifest JSON (default: fixtures/fixture_manifest.json)",
    )
    args = parser.parse_args(argv)

    project_root = Path(__file__).parent.parent
    receipt_path = project_root / args.receipt
    manifest_path = project_root / args.manifest

    failures = check(receipt_path, manifest_path)

    if not failures:
        print("receipt freshness check: PASSED")
        print(f"  receipt : {receipt_path.relative_to(project_root)}")
        print(f"  manifest: {manifest_path.relative_to(project_root)}")
        return 0

    print("receipt freshness check: FAILED")
    print(f"  {len(failures)} issue(s) found:\n")
    for i, msg in enumerate(failures, 1):
        print(f"  {i:2d}. {msg}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
