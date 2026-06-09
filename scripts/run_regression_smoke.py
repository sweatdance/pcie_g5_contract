#!/usr/bin/env python3
"""Run the contract's full regression smoke suite."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _default_framework_root(contract_root: Path) -> Path:
    return (contract_root.parent / "ai-governance-framework").resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run full regression smoke checks for the contract repo.")
    parser.add_argument("--framework-root", help="Path to ai-governance-framework")
    parser.add_argument("--contract-root", default=".", help="Path to the contract repository root")
    parser.add_argument(
        "--suite",
        choices=("all", "required", "advisory"),
        default="all",
        help="Run only required or advisory fixture suites.",
    )
    parser.add_argument("--format", choices=("human", "json"), default="human")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    contract_root = Path(args.contract_root).resolve()
    framework_root = Path(args.framework_root).resolve() if args.framework_root else _default_framework_root(contract_root)
    if not framework_root.exists():
        print(f"ERROR: framework root not found: {framework_root}", file=sys.stderr)
        return 1

    sys.path.insert(0, str(contract_root / "scripts"))
    sys.path.insert(0, str(framework_root))

    from governance_tools.external_repo_smoke import format_human as format_external_human
    from governance_tools.external_repo_smoke import run_external_repo_smoke
    from run_fixture_smoke import format_human as format_fixture_human
    from run_fixture_smoke import run_fixture_smoke

    fixture_payload = run_fixture_smoke(contract_root, framework_root, suite=args.suite)
    external_result = run_external_repo_smoke(contract_root, contract_file=contract_root / "contract.yaml")
    overall_ok = fixture_payload["ok"] and external_result.ok

    if args.format == "json":
        print(
            json.dumps(
                {
                    "ok": overall_ok,
                    "fixture_smoke": fixture_payload,
                    "external_repo_smoke": {
                        "ok": external_result.ok,
                        "repo_root": external_result.repo_root,
                        "plan_path": external_result.plan_path,
                        "contract_path": external_result.contract_path,
                        "rules": external_result.rules,
                        "pre_task_ok": external_result.pre_task_ok,
                        "session_start_ok": external_result.session_start_ok,
                        "post_task_ok": external_result.post_task_ok,
                        "warnings": external_result.warnings,
                        "errors": external_result.errors,
                    },
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0 if overall_ok else 1

    print("[contract_regression_smoke]")
    print(f"ok={overall_ok}")
    print("[fixture_smoke]")
    print(format_fixture_human(fixture_payload))
    print("[external_repo_smoke]")
    print(format_external_human(external_result))
    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
