"""YAML-driven, non-executing assignment submission validation."""

from __future__ import annotations

import ast
import csv
import fnmatch
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any

import yaml
import numpy as np
from PIL import Image, UnidentifiedImageError

from .data import find_course_root
from .notebook import is_executed, load_notebook, markdown_headings, student_information


@dataclass(frozen=True)
class Finding:
    """One actionable validation result."""

    level: str
    code: str
    message: str
    path: str | None = None


def load_config(path: str | Path) -> dict[str, Any]:
    """Load and minimally validate an assignment contract."""
    with Path(path).open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    required = {"assignment", "assignment_version", "environment_version", "individual"}
    if not isinstance(config, dict):
        raise ValueError("Validation YAML must contain a mapping")
    missing = required.difference(config)
    if missing:
        raise ValueError(f"Validation YAML is missing required keys: {sorted(missing)}")
    if config["individual"] is not True:
        raise ValueError("A1-A5 validation contracts must set individual: true")
    return config


def matches(path: str, patterns: list[str]) -> bool:
    """Match portable POSIX paths using shell-style patterns."""
    candidate = PurePosixPath(path)
    return any(fnmatch.fnmatch(path, pattern) or candidate.match(pattern) for pattern in patterns)


def _finding(level: str, code: str, message: str, path: str | None = None) -> Finding:
    return Finding(level, code, message, path)


def _validate_identity(notebook: dict, config: dict[str, Any], path: str, *, preflight: bool = False) -> tuple[list[Finding], dict[str, str]]:
    findings: list[Finding] = []
    info = student_information(notebook)
    identity = config.get("identity", {})
    first_name = info.get("firstname", "").strip()
    last_name = info.get("lastname", "").strip()
    name = " ".join(part for part in (first_name, last_name) if part)
    abc123 = info.get("abc123", "").strip()
    resources = info.get("externalresourcesandgenerativeaiassistance", "").strip()
    component_pattern = identity.get("name_component_pattern", r"[^\s]+(?:[ '\-][^\s]+)*")
    if (not first_name or not last_name or re.search(r"replace|todo|your name", name, re.IGNORECASE)
            or not re.fullmatch(component_pattern, first_name) or not re.fullmatch(component_pattern, last_name)):
        findings.append(_finding("warning" if preflight else "error", "student-name", "Replace the first-name and last-name placeholders.", path))
    if not abc123 or not re.fullmatch(identity.get("abc123_pattern", r"[A-Za-z]{3}[0-9]{3}"), abc123):
        findings.append(_finding("warning" if preflight else "error", "abc123", "Enter a valid UTSA ABC123 identifier (three letters and three digits).", path))
    if not resources or re.search(r"replace|todo|list each", resources, re.IGNORECASE):
        findings.append(_finding("warning" if preflight else "error", "resource-declaration", "Declare external resources and generative-AI assistance, or write None.", path))
    return findings, {"name": name, "first_name": first_name, "last_name": last_name, "abc123": abc123.lower()}


def _validate_notebook(path: Path, relative: str, config: dict[str, Any], *, preflight: bool = False) -> tuple[list[Finding], dict[str, str]]:
    findings: list[Finding] = []
    identity: dict[str, str] = {}
    try:
        notebook = load_notebook(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [_finding("error", "invalid-notebook", str(exc), relative)], identity

    notebook_config = config.get("notebook", {})
    if not preflight and notebook_config.get("executed", True) and not is_executed(notebook):
        findings.append(_finding("error", "not-executed", "Run every nonempty code cell and save the notebook.", relative))
    if any(output.get("output_type") == "error" for cell in notebook["cells"] for output in cell.get("outputs", [])):
        findings.append(_finding("error", "execution-error", "Notebook contains a saved execution error.", relative))
    headings = markdown_headings(notebook)
    for heading in notebook_config.get("required_sections", []):
        if heading not in headings:
            findings.append(_finding("error", "missing-section", f"Missing notebook section: {heading}", relative))

    metadata = notebook.get("metadata", {}).get("cs5243", {})
    expected = {
        "assignment": str(config["assignment"]),
        "assignment_version": str(config["assignment_version"]),
        "environment_version": str(config["environment_version"]),
    }
    for key, expected_value in expected.items():
        if str(metadata.get(key, "")) != expected_value:
            findings.append(_finding("error", f"{key.replace('_', '-')}-mismatch",
                                     f"Notebook {key} must be {expected_value!r}.", relative))

    identity_findings, identity = _validate_identity(notebook, config, relative, preflight=preflight)
    findings.extend(identity_findings)

    text = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])
    if re.search(r"\b(?:TODO|REPLACE ME|YOUR RESPONSE)\b", text, re.IGNORECASE):
        findings.append(_finding("warning", "placeholder-text", "Review unresolved placeholder text before submission.", relative))
    if notebook_config.get("warn_absolute_paths", True) and has_machine_specific_path(text):
        findings.append(_finding("warning", "absolute-path", "Notebook contains a machine-specific absolute path; use pathlib and repository-relative paths.", relative))
    return findings, identity


def has_machine_specific_path(text: str) -> bool:
    """Detect common user- or drive-specific paths without flagging URLs."""
    return bool(re.search(r"(?<![\w:/])(?:[A-Za-z]:[\\/]|/(?:Users|home|mnt|private|tmp)/)", text))


def _validate_preflight(base: Path, config: dict[str, Any]) -> list[Finding]:
    """Check immutable assets and starter signatures without importing student code."""
    findings: list[Finding] = []
    settings = config.get("preflight", {})
    manifest_name = settings.get("asset_manifest")
    if manifest_name:
        try:
            repository = find_course_root(base)
        except FileNotFoundError as exc:
            return [_finding("error", "repository-access", str(exc))]
        manifest = repository / manifest_name
        if not manifest.is_file():
            findings.append(_finding("error", "asset-manifest", "Asset checksum manifest is missing.", manifest_name))
        else:
            asset_root = manifest.parent
            for line_number, line in enumerate(manifest.read_text(encoding="utf-8").splitlines(), 1):
                if not line.strip():
                    continue
                try:
                    expected, relative = line.split(maxsplit=1)
                except ValueError:
                    findings.append(_finding("error", "asset-manifest", f"Invalid checksum line {line_number}.", manifest_name))
                    continue
                asset = asset_root / relative.strip()
                if not asset.is_file():
                    findings.append(_finding("error", "missing-asset", "Required assignment asset is missing.", asset.relative_to(repository).as_posix()))
                elif hashlib.sha256(asset.read_bytes()).hexdigest() != expected:
                    findings.append(_finding("error", "asset-checksum", "Assignment asset checksum does not match.", asset.relative_to(repository).as_posix()))

    functions = settings.get("required_functions", {})
    source_name = functions.get("path")
    if source_name:
        source_path = base / source_name
        if source_path.is_file():
            try:
                tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
                defined = {node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
                for name in functions.get("names", []):
                    if name not in defined:
                        findings.append(_finding("error", "missing-function", f"Required starter function is missing: {name}", source_name))
            except (SyntaxError, UnicodeDecodeError) as exc:
                findings.append(_finding("error", "invalid-source", f"Cannot inspect starter source: {exc}", source_name))
    return findings


def _nested_key_exists(value: Any, dotted_key: str) -> bool:
    current = value
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            return False
        current = current[part]
    return True


def _validate_artifact_schemas(base: Path, config: dict[str, Any]) -> list[Finding]:
    """Validate configured CSV headers and JSON key structure without executing code."""
    findings: list[Finding] = []
    schemas = config.get("artifact_schemas", {})
    for relative, required_columns in schemas.get("csv", {}).items():
        path = base / relative
        if not path.is_file():
            continue
        try:
            with path.open(newline="", encoding="utf-8") as handle:
                columns = next(csv.reader(handle), [])
        except (OSError, UnicodeDecodeError, csv.Error) as exc:
            findings.append(_finding("error", "artifact-schema", f"Cannot read CSV header: {exc}", relative))
            continue
        missing = [column for column in required_columns if column not in columns]
        if missing:
            findings.append(_finding("error", "artifact-schema", f"CSV is missing required columns: {missing}", relative))
    for relative, required_keys in schemas.get("json", {}).items():
        path = base / relative
        if not path.is_file():
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            findings.append(_finding("error", "artifact-schema", f"Cannot read JSON artifact: {exc}", relative))
            continue
        missing = [key for key in required_keys if not _nested_key_exists(value, key)]
        if missing:
            findings.append(_finding("error", "artifact-schema", f"JSON is missing required keys: {missing}", relative))
    return findings


def _validate_image_artifacts(base: Path, config: dict[str, Any]) -> list[Finding]:
    """Validate optional readable-image and minimum-dimension requirements."""
    findings: list[Finding] = []
    for relative, requirements in config.get("image_artifacts", {}).items():
        path = base / relative
        if not path.is_file():
            continue
        try:
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                width, height = image.size
        except (OSError, UnidentifiedImageError) as exc:
            findings.append(_finding("error", "invalid-image", f"Cannot read image artifact: {exc}", relative))
            continue
        minimum_width = int(requirements.get("min_width", 1))
        minimum_height = int(requirements.get("min_height", 1))
        if width < minimum_width or height < minimum_height:
            findings.append(_finding("error", "image-dimensions",
                                     f"Image must be at least {minimum_width}x{minimum_height} pixels; found {width}x{height}.", relative))
    return findings


def _validate_numeric_artifacts(base: Path, config: dict[str, Any]) -> list[Finding]:
    """Validate optional NumPy-array shape and finite-value requirements."""
    findings: list[Finding] = []
    for relative, requirements in config.get("numeric_artifacts", {}).items():
        path = base / relative
        if not path.is_file():
            continue
        try:
            value = np.load(path, allow_pickle=False)
        except (OSError, ValueError) as exc:
            findings.append(_finding("error", "invalid-array", f"Cannot read NumPy artifact: {exc}", relative))
            continue
        if isinstance(value, np.lib.npyio.NpzFile):
            value.close()
            findings.append(_finding("error", "invalid-array", "Expected one .npy array, not an NPZ archive.", relative))
            continue
        expected_ndim = requirements.get("ndim")
        if expected_ndim is not None and value.ndim != int(expected_ndim):
            findings.append(_finding("error", "array-shape", f"Array must have {expected_ndim} dimensions; found {value.ndim}.", relative))
        minimum_shape = requirements.get("min_shape", [])
        if minimum_shape and (len(minimum_shape) != value.ndim or any(size < int(minimum) for size, minimum in zip(value.shape, minimum_shape))):
            findings.append(_finding("error", "array-shape", f"Array shape {value.shape} is smaller than required {tuple(minimum_shape)}.", relative))
        if requirements.get("finite", False) and not np.isfinite(value).all():
            findings.append(_finding("error", "array-values", "Array must contain only finite values.", relative))
    return findings


def _validate_ply_artifacts(base: Path, config: dict[str, Any]) -> list[Finding]:
    """Validate the structure and declared vertex count of ASCII PLY artifacts."""
    findings: list[Finding] = []
    for relative, requirements in config.get("ply_artifacts", {}).items():
        path = base / relative
        if not path.is_file():
            continue
        try:
            lines = path.read_text(encoding="ascii").splitlines()
            end = lines.index("end_header")
            if not lines or lines[0] != "ply" or "format ascii 1.0" not in lines[:end]:
                raise ValueError("expected an ASCII PLY header")
            vertex_line = next(line for line in lines[:end] if line.startswith("element vertex "))
            count = int(vertex_line.split()[-1])
            if count < int(requirements.get("min_vertices", 1)):
                raise ValueError(f"expected at least {requirements.get('min_vertices', 1)} vertices")
            rows = [line for line in lines[end + 1:] if line.strip()]
            if len(rows) < count or any(len(row.split()) < 3 for row in rows[:count]):
                raise ValueError("vertex rows do not match the declared count")
            for row in rows[:count]:
                float(row.split()[0]); float(row.split()[1]); float(row.split()[2])
        except (OSError, UnicodeError, ValueError, StopIteration) as exc:
            findings.append(_finding("error", "invalid-ply", f"Cannot parse PLY artifact: {exc}", relative))
    return findings


def validate_submission(root: str | Path, config: dict[str, Any], *, preflight: bool = False) -> tuple[list[Finding], dict[str, str]]:
    """Validate one assignment directory without executing student code."""
    base = Path(root).expanduser().resolve()
    findings: list[Finding] = []
    identity: dict[str, str] = {}
    if not base.is_dir():
        return [_finding("error", "missing-root", f"Submission directory not found: {base}")], identity

    files = sorted(path for path in base.rglob("*") if path.is_file())
    relative = [path.relative_to(base).as_posix() for path in files]
    directories = [path.relative_to(base).as_posix() for path in base.rglob("*") if path.is_dir()]

    prohibited = config.get("prohibited_patterns", [])
    excluded = config.get("warning_patterns", [])
    excluded_names: set[str] = set()
    prohibited_names: set[str] = set()
    all_paths = sorted(set(relative + directories), key=lambda name: (len(PurePosixPath(name).parts), name))
    for name in all_paths:
        parents = {parent.as_posix() for parent in PurePosixPath(name).parents if parent.as_posix() != "."}
        if matches(name, prohibited):
            prohibited_names.add(name)
            if not parents.intersection(prohibited_names):
                findings.append(_finding("error", "prohibited-path", "Remove prohibited dataset, environment, checkpoint, or model content.", name))
        elif matches(name, excluded):
            excluded_names.add(name)
            if not parents.intersection(excluded_names):
                findings.append(_finding("warning", "excluded-path", "This cache or temporary path will not be packaged.", name))
        elif any(part.startswith(".") and part != ".gitkeep" for part in PurePosixPath(name).parts):
            excluded_names.add(name)
            if not parents.intersection(excluded_names):
                findings.append(_finding("warning", "hidden-path", "Hidden content will not be packaged.", name))

    requirements = config.get("preflight", {}).get("required_artifacts", []) if preflight else config.get("required_artifacts", [])
    for requirement in requirements:
        pattern = requirement["pattern"]
        matched = [name for name in relative if matches(name, [pattern]) and not any(part.startswith(".") for part in PurePosixPath(name).parts)]
        if len(matched) < int(requirement.get("minimum", 1)):
            label = requirement.get("label", pattern)
            findings.append(_finding("error", "missing-artifact", f"Required artifact missing: {label} ({pattern})"))

    allowed_extensions = {extension.lower() for extension in config.get("allowed_extensions", [])}
    max_bytes = float(config.get("max_file_size_mb", 25)) * 1024 * 1024
    warning_bytes = float(config.get("warn_file_size_mb", 10)) * 1024 * 1024
    for path, name in zip(files, relative):
        size = path.stat().st_size
        if name in excluded_names or any(part.startswith(".") for part in PurePosixPath(name).parts):
            continue
        if allowed_extensions and path.suffix.lower() not in allowed_extensions:
            findings.append(_finding("error", "file-type", f"File type {path.suffix or '<none>'!r} is not allowed.", name))
        if size == 0 and not path.name.startswith("."):
            findings.append(_finding("error", "empty-file", "Remove or regenerate this empty file.", name))
        if size > max_bytes:
            findings.append(_finding("error", "large-file", f"File exceeds {config.get('max_file_size_mb', 25)} MB.", name))
        elif size > warning_bytes:
            findings.append(_finding("warning", "large-file-warning", f"Review this file because it exceeds {config.get('warn_file_size_mb', 10)} MB.", name))
        if path.suffix.lower() in {".py", ".md", ".txt"}:
            try:
                if has_machine_specific_path(path.read_text(encoding="utf-8")):
                    findings.append(_finding("warning", "absolute-path", "File contains a machine-specific absolute path.", name))
            except UnicodeDecodeError:
                findings.append(_finding("error", "invalid-text", "Expected a UTF-8 text file.", name))

    expected_notebook = config.get("notebook", {}).get("filename", f"{config['assignment']}.ipynb")
    notebook_path = base / expected_notebook
    if not notebook_path.is_file():
        findings.append(_finding("error", "missing-notebook", f"Required notebook not found: {expected_notebook}"))
    else:
        notebook_findings, identity = _validate_notebook(notebook_path, expected_notebook, config, preflight=preflight)
        findings.extend(notebook_findings)

    html_name = config.get("notebook", {}).get("html_filename", f"{config['assignment']}.html")
    html_path = base / html_name
    if not preflight and html_path.is_file():
        try:
            html = html_path.read_text(encoding="utf-8")
            if "<html" not in html.lower():
                findings.append(_finding("error", "invalid-html", "Rendered HTML does not contain an HTML document.", html_name))
            markers = list(config.get("notebook", {}).get("required_html_markers", []))
            if identity.get("name") and not re.search(r"replace|todo", identity["name"], re.IGNORECASE):
                markers.extend([identity.get("first_name", ""), identity.get("last_name", ""), identity.get("abc123", "")])
            for marker in filter(None, markers):
                if marker.lower() not in html.lower():
                    findings.append(_finding("error", "stale-html", f"Rendered HTML is missing expected content: {marker!r}.", html_name))
        except UnicodeDecodeError:
            findings.append(_finding("error", "invalid-html", "Rendered HTML must be UTF-8 text.", html_name))

    if preflight:
        findings.extend(_validate_preflight(base, config))
    else:
        findings.extend(_validate_artifact_schemas(base, config))
        findings.extend(_validate_image_artifacts(base, config))
        findings.extend(_validate_numeric_artifacts(base, config))
        findings.extend(_validate_ply_artifacts(base, config))
    findings.sort(key=lambda item: (item.level != "error", item.code, item.path or ""))
    return findings, identity


def report(config: dict[str, Any], findings: list[Finding], identity: dict[str, str], *, preflight: bool = False) -> dict[str, Any]:
    """Build the stable JSON validation-report format."""
    errors = sum(item.level == "error" for item in findings)
    warnings = sum(item.level == "warning" for item in findings)
    return {
        "assignment": config["assignment"],
        "assignment_version": str(config["assignment_version"]),
        "environment_version": str(config["environment_version"]),
        "mode": "preflight" if preflight else "full",
        "student": identity,
        "valid": errors == 0,
        "summary": {"errors": errors, "warnings": warnings},
        "findings": [asdict(item) for item in findings],
    }
