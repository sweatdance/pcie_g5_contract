#!/usr/bin/env python3
"""Run positive and negative post-task fixture checks for the PCIe LTSSM contract."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from datetime import timezone
from pathlib import Path


def _classify_suite(expected_rule_ids: list[str] | None) -> str:
    rules = {str(rule_id).strip().lower() for rule_id in (expected_rule_ids or [])}
    if {"pcie-ltssm", "pcie-eq", "pcie-link-negotiation"}.intersection(rules):
        return "required"
    return "advisory"


def _inject_rules(response_text: str, rules: list[str]) -> str:
    rules_value = ",".join(rules)
    lines = response_text.splitlines()
    replaced = False
    target_prefix = "RULES = "
    for idx, line in enumerate(lines):
        if line.startswith(target_prefix):
            lines[idx] = f"{target_prefix}{rules_value}"
            replaced = True
            break
    if not replaced:
        lines.append(f"{target_prefix}{rules_value}")
    return "\n".join(lines) + "\n"


def _write_receipt(payload: dict, receipt_path: Path) -> None:
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_payload = {
        "schema_version": "1.0",
        "artifact_type": "fixture_smoke_receipt",
        "created_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        **payload,
    }
    receipt_path.write_text(json.dumps(receipt_payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _default_framework_root(contract_root: Path) -> Path:
    candidate = contract_root.parent / "ai-governance-framework"
    return candidate.resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run contract fixture smoke checks.")
    parser.add_argument("--framework-root", help="Path to ai-governance-framework")
    parser.add_argument("--contract-root", default=".", help="Path to the contract repository root")
    parser.add_argument("--format", choices=("human", "json"), default="human")
    parser.add_argument(
        "--suite",
        choices=("all", "required", "advisory"),
        default="all",
        help="Run only required or advisory fixture suites.",
    )
    parser.add_argument(
        "--receipt-path",
        default=str((Path(".") / "artifacts" / "validation" / "fixture-smoke-receipt.json").as_posix()),
        help="Path to write machine-readable fixture smoke receipt.",
    )
    return parser


def run_fixture_smoke(contract_root: Path, framework_root: Path, suite: str = "all") -> dict:
    if not framework_root.exists():
        raise FileNotFoundError(f"framework root not found: {framework_root}")

    sys.path.insert(0, str(framework_root))
    from runtime_hooks.core.post_task_check import run_post_task_check

    fixtures_root = contract_root / "fixtures"
    manifest_path = fixtures_root / "fixture_manifest.json"
    response_path = fixtures_root / "post_task_response.txt"
    contract_path = contract_root / "contract.yaml"

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    response_text = response_path.read_text(encoding="utf-8")

    results = []
    selected_files = []
    overall_ok = True
    for fixture in manifest.get("fixtures", []):
        fixture_suite = _classify_suite(fixture.get("expected_rule_ids") if isinstance(fixture.get("expected_rule_ids"), list) else [])
        if suite != "all" and fixture_suite != suite:
            continue
        selected_files.append(fixture.get("file"))
        rule_ids = fixture.get("expected_rule_ids")
        if not isinstance(rule_ids, list) or not rule_ids:
            if not isinstance(rule_ids, list):
                warnings = [f"fixture '{fixture.get('file')}' missing expected_rule_ids; using default response rules"]
            else:
                warnings = [f"fixture '{fixture.get('file')}' expected_rule_ids empty; using default response rules"]
            current_response_text = response_text
        else:
            warnings = []
            current_response_text = _inject_rules(response_text, [str(rule_id) for rule_id in rule_ids])
        checks_path = fixtures_root / fixture["file"]
        checks = json.loads(checks_path.read_text(encoding="utf-8"))
        result = run_post_task_check(
            response_text=current_response_text,
            risk="medium",
            oversight="review-required",
            memory_mode="candidate",
            create_snapshot=False,
            checks=checks,
            contract_file=contract_path,
            project_root=contract_root,
            evidence_paths=[response_path.resolve(), checks_path.resolve()],
        )
        matched = bool(result["ok"]) is bool(fixture["expected_ok"])
        overall_ok = overall_ok and matched
        results.append(
            {
                "file": fixture["file"],
                "description": fixture.get("description", ""),
                "expected_rule_ids": rule_ids if isinstance(rule_ids, list) else None,
                "expected_ok": fixture["expected_ok"],
                "actual_ok": result["ok"],
                "matched_expectation": matched,
                "domain_validator_count": len(result.get("domain_validator_results") or []),
                "warnings": (warnings or []) + (result.get("warnings") or []),
                "errors": result.get("errors") or [],
            }
        )
    return {
        "suite": suite,
        "ok": overall_ok,
        "contract_root": str(contract_root),
        "framework_root": str(framework_root),
        "fixture_count": len(results),
        "selected_fixture_count": len(selected_files),
        "results": results,
        "selected_fixtures": selected_files,
    }


def format_human(payload: dict) -> str:
    lines = [
        "[contract_fixture_smoke]",
        f"ok={payload['ok']}",
        f"contract_root={payload['contract_root']}",
        f"framework_root={payload['framework_root']}",
    ]
    for item in payload["results"]:
        lines.append(
            " | ".join(
                [
                    item["file"],
                    f"expected_ok={item['expected_ok']}",
                    f"actual_ok={item['actual_ok']}",
                    f"matched={item['matched_expectation']}",
                    f"domain_validators={item['domain_validator_count']}",
                ]
            )
        )
        for warning in item["warnings"]:
            lines.append(f"  warning: {warning}")
        for error in item["errors"]:
            lines.append(f"  error: {error}")
    return "\n".join(lines)


def main() -> int:
    args = build_parser().parse_args()
    contract_root = Path(args.contract_root).resolve()
    framework_root = Path(args.framework_root).resolve() if args.framework_root else _default_framework_root(contract_root)
    try:
        payload = run_fixture_smoke(contract_root, framework_root, suite=args.suite)
        _write_receipt(payload, Path(args.receipt_path))
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload["ok"] else 1

    print(format_human(payload))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
