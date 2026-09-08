#!/usr/bin/env python3
"""Validate one assignment directory and write its JSON report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cs5243.validation import load_config, report, validate_submission


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assignment", default="A1", help="Assignment identifier (default: A1)")
    parser.add_argument("--config", type=Path, help="Default: WORKSPACE/ASSIGNMENT/config/ASSIGNMENT.yml")
    parser.add_argument("--submission", type=Path, help="Default: WORKSPACE/ASSIGNMENT")
    parser.add_argument("--report", type=Path, help="Default: SUBMISSION/validation-report.json")
    parser.add_argument("--preflight", action="store_true", help="Check setup, assets, signatures, and metadata without requiring completed work")
    args = parser.parse_args()

    config_path = (
        args.config or REPOSITORY_ROOT.parent / args.assignment / "config" / f"{args.assignment}.yml"
    ).resolve()
    submission = (args.submission or REPOSITORY_ROOT.parent / args.assignment).resolve()
    config = load_config(config_path)
    findings, identity = validate_submission(submission, config, preflight=args.preflight)
    result = report(config, findings, identity, preflight=args.preflight)
    default_name = "preflight-report.json" if args.preflight else "validation-report.json"
    output = (args.report or submission / default_name).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    print(f"Validation report: {output}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
