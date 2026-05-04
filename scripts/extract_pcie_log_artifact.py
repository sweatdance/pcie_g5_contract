from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


TRANSITION_RE = re.compile(r"^\s*(\d+)\s+ns\s+: LTSSM transition: (.+) -> (.+)$")
ERROR_RE = re.compile(r"(?i)(?:^|[^A-Za-z])(error|fail|timeout|fatal|unsupported)(?:[^A-Za-z]|$)")


def parse_log(log_path: Path) -> dict:
    transitions = []
    error_messages = []

    for line_number, raw_line in enumerate(log_path.read_text(encoding="utf-8").splitlines(), start=1):
        transition_match = TRANSITION_RE.match(raw_line)
        if transition_match:
            transitions.append(
                {
                    "timestamp_ns": int(transition_match.group(1)),
                    "from": transition_match.group(2).strip(),
                    "to": transition_match.group(3).strip(),
                }
            )
            continue

        if line_number > 30 and ERROR_RE.search(raw_line):
            error_messages.append(raw_line.strip())

    final_state = transitions[-1]["to"] if transitions else None

    return {
        "test_name": log_path.stem,
        "final_state": final_state,
        "ltssm_transitions": transitions,
        "error_messages": error_messages,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract LTSSM artifacts from PCIe packet monitor logs.")
    parser.add_argument("logs", nargs="+", type=Path, help="Packet monitor log files to parse.")
    parser.add_argument("--output", required=True, type=Path, help="Path to the JSON artifact to write.")
    args = parser.parse_args()

    artifact = {"tests": [parse_log(log_path) for log_path in args.logs]}
    args.output.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())