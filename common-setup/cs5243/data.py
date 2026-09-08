"""Safe, small data-path helpers; assignment datasets remain external."""

from __future__ import annotations

import hashlib
from pathlib import Path


REPOSITORY_MARKERS = ("environment.yml", "pyproject.toml", "config")


def find_repository_root(start: str | Path | None = None) -> Path:
    """Find the ``common-setup/`` environment/infrastructure root from a file or
    directory, independent of ``cwd``.

    This is the folder produced by extracting ``cs5243-common-setup.zip`` (or,
    in the instructor repo, the ``common-setup/`` directory itself) — it
    contains ``environment.yml``, ``pyproject.toml``, and ``config``. It is
    *not* the outer workspace folder that also holds the per-assignment
    ``A1/`` .. ``A5/`` siblings; use :func:`find_course_root` for that.

    ``start`` may live either inside ``common-setup/`` itself (e.g. the
    ``cs5243`` package or the release scripts) or inside a sibling ``A#/``
    assignment folder (e.g. ``A1/src/a1_tools.py``) — ``common-setup/`` is not
    an ancestor of ``A#/``, so each directory walked upward is checked both as
    a possible ``common-setup/`` itself and, failing that, for a
    ``common-setup`` child that satisfies the markers.
    """
    current = Path(start or __file__).expanduser().resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if all((candidate / marker).exists() for marker in REPOSITORY_MARKERS):
            return candidate
        nested = candidate / "common-setup"
        if nested.is_dir() and all((nested / marker).exists() for marker in REPOSITORY_MARKERS):
            return nested
    raise FileNotFoundError(f"Could not locate the CS 5243 repository above {current}")


def find_course_root(start: str | Path | None = None) -> Path:
    """Find the outer workspace folder that contains ``common-setup/`` and each
    per-assignment ``A#/`` folder as direct siblings.

    Students assemble this folder themselves (any name they like) by
    extracting ``cs5243-common-setup.zip`` and each assignment's zip directly
    into it. This function simply returns the parent of whatever
    :func:`find_repository_root` resolves to.
    """
    return find_repository_root(start).parent


def require_file(path: str | Path) -> Path:
    resolved = Path(path).expanduser().resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"Required file not found: {resolved}")
    return resolved


def sha256(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with require_file(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def list_files(root: str | Path, suffixes: tuple[str, ...] | None = None) -> list[Path]:
    base = Path(root)
    files = (path for path in base.rglob("*") if path.is_file())
    if suffixes:
        wanted = tuple(s.lower() for s in suffixes)
        files = (path for path in files if path.suffix.lower() in wanted)
    return sorted(files)
