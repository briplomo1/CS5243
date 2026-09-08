#!/usr/bin/env python3
"""Create a validated, Canvas-ready assignment ZIP."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
import unicodedata
import zipfile
from pathlib import Path, PurePosixPath

from cs5243.validation import load_config, matches, report, validate_submission


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def canvas_name(first_name: str, last_name: str, assignment: str) -> str:
    """Return the required ``LastName_FirstName_A#`` folder name."""
    def clean(value: str) -> str:
        ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
        return re.sub(r"[^A-Za-z0-9'-]+", "", ascii_value)
    return f"{clean(last_name)}_{clean(first_name)}_{assignment}"


def package_submission(submission: Path, config: dict, output: Path | None = None) -> tuple[Path | None, dict]:
    """Validate and atomically build a ZIP; return ``None`` on errors."""
    submission = submission.expanduser().resolve()
    findings, identity = validate_submission(submission, config)
    result = report(config, findings, identity)
    if not result["valid"]:
        return None, result

    folder = canvas_name(identity["first_name"], identity["last_name"], config["assignment"])
    destination = (output or submission.parent / f"{folder}.zip").expanduser().resolve()
    include_patterns = config.get("package", {}).get("include_patterns", [])
    prohibited = config.get("prohibited_patterns", []) + config.get("warning_patterns", [])
    included: list[tuple[Path, str]] = []
    for path in submission.rglob("*"):
        if not path.is_file():
            continue
        name = path.relative_to(submission).as_posix()
        if any(part.startswith(".") for part in PurePosixPath(name).parts):
            continue
        if name == "validation-report.json":
            continue
        if matches(name, include_patterns) and not matches(name, prohibited):
            included.append((path, name))

    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent) as temp_dir:
        temporary_zip = Path(temp_dir) / destination.name
        with zipfile.ZipFile(temporary_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path, name in sorted(included, key=lambda item: item[1]):
                archive.write(path, f"{folder}/{name}")
            archive.writestr(f"{folder}/validation-report.json", json.dumps(result, indent=2) + "\n")
        temporary_zip.replace(destination)
    return destination, result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assignment", default="A1", help="Assignment identifier (default: A1)")
    parser.add_argument("--config", type=Path, help="Default: WORKSPACE/ASSIGNMENT/config/ASSIGNMENT.yml")
    parser.add_argument("--submission", type=Path, help="Default: WORKSPACE/ASSIGNMENT")
    parser.add_argument("--output", type=Path, help="Default: LastName_FirstName_A#.zip beside the assignment directory")
    args = parser.parse_args()

    config_path = (
        args.config or REPOSITORY_ROOT.parent / args.assignment / "config" / f"{args.assignment}.yml"
    ).resolve()
    submission = (args.submission or REPOSITORY_ROOT.parent / args.assignment).resolve()
    config = load_config(config_path)
    output, result = package_submission(submission, config, args.output)
    if output is None:
        print(json.dumps(result, indent=2))
        print("Packaging stopped because validation found errors.")
        return 1
    print(f"Created: {output}")
    print(f"Warnings to review: {result['summary']['warnings']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
