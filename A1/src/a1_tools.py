"""Provided A1 infrastructure helpers. Graded array operations are not implemented here."""

from __future__ import annotations

import hashlib
import math
from collections.abc import Iterable, Iterator, Sequence
from pathlib import Path

import imageio.v2 as iio
import imageio.v3 as iio3
import matplotlib.pyplot as plt
import numpy as np

from cs5243.data import find_course_root, find_repository_root


def assignment_paths() -> dict[str, Path]:
    root = find_repository_root(__file__)
    assignment = find_course_root(__file__) / "A1"
    return {"root": root, "assignment": assignment, "assets": assignment / "data",
            "figures": assignment / "outputs" / "figures", "tables": assignment / "outputs" / "tables",
            "videos": assignment / "outputs" / "videos", "extension": assignment / "outputs" / "extension"}


def ensure_output_directories() -> dict[str, Path]:
    paths = assignment_paths()
    for key in ("figures", "tables", "videos", "extension"):
        paths[key].mkdir(parents=True, exist_ok=True)
    return paths


def discover_images() -> list[Path]:
    return sorted((assignment_paths()["assets"] / "images").glob("*.*"))


def verify_asset_hashes() -> list[str]:
    assets = assignment_paths()["assets"]
    problems: list[str] = []
    for line in (assets / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        expected, relative = line.split(maxsplit=1)
        path = assets / relative.strip()
        if not path.is_file():
            problems.append(f"Missing asset: {relative}")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            problems.append(f"Checksum mismatch: {relative}")
    return problems


# Descriptive alias used in the public tests and notebook prose.
verify_asset_checksums = verify_asset_hashes


def asset_root(root: str | Path | None = None) -> Path:
    """Return the A1 asset directory, optionally beneath an explicit environment
    (``common-setup/``) root. ``root`` is the environment root, not the
    workspace root, so its parent (the workspace folder containing ``A1/`` as
    a sibling of ``common-setup/``) is used to locate ``A1/data``."""
    env_root = Path(root) if root is not None else assignment_paths()["root"]
    return env_root.parent / "A1" / "data"


def format_bytes(count: int) -> str:
    for unit in ("B", "KiB", "MiB", "GiB"):
        if count < 1024 or unit == "GiB":
            return f"{count:.1f} {unit}" if unit != "B" else f"{count} B"
        count /= 1024
    raise AssertionError("unreachable")


def axes_grid(rows: int, columns: int, *, scale: float = 3.2):
    return plt.subplots(rows, columns, figsize=(scale * columns, scale * rows), squeeze=False)


def probe_video(path: str | Path) -> dict[str, float | int | str]:
    source = Path(path)
    metadata = iio3.immeta(source, plugin="FFMPEG")
    fps = float(metadata.get("fps", 0.0))
    raw_frames = metadata.get("nframes", 0) or 0
    frames = int(raw_frames) if isinstance(raw_frames, (int, float)) and math.isfinite(raw_frames) else 0
    if frames <= 0 or frames > 10_000_000:
        frames = sum(1 for _ in iio3.imiter(source, plugin="FFMPEG"))
    size = metadata.get("size", (0, 0))
    return {"path": source.name, "width": int(size[0]), "height": int(size[1]), "fps": fps,
            "frame_count": frames, "duration_seconds": frames / fps if fps else 0.0,
            "codec": str(metadata.get("codec", "unknown"))}


def iter_video_frames(path: str | Path) -> Iterator[np.ndarray]:
    yield from iio3.imiter(path, plugin="FFMPEG")


def sample_video_frames(path: str | Path, times_seconds: Sequence[float]) -> list[np.ndarray]:
    metadata = probe_video(path)
    wanted = [max(0, round(time * float(metadata["fps"]))) for time in times_seconds]
    lookup = set(wanted)
    found: dict[int, np.ndarray] = {}
    for index, frame in enumerate(iter_video_frames(path)):
        if index in lookup:
            found[index] = frame
        if len(found) == len(lookup):
            break
    if not found:
        raise ValueError(f"No readable frames in {path}")
    return [found[index] if index in found else found[max(found)] for index in wanted]


def write_mp4(path: str | Path, frames: Iterable[np.ndarray], *, fps: float) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with iio.get_writer(target, fps=fps, codec="libx264", pixelformat="yuv420p", macro_block_size=16,
                        ffmpeg_log_level="error", quality=7) as writer:
        count = 0
        for frame in frames:
            values = np.asarray(frame)
            if values.dtype != np.uint8 or values.ndim != 3 or values.shape[2] != 3:
                raise ValueError("Video frames must be HxWx3 uint8 RGB arrays")
            writer.append_data(values)
            count += 1
    if count == 0:
        raise ValueError("At least one video frame is required")
    return target


def verify_video_round_trip(path: str | Path, *, expected_width: int, expected_height: int,
                            expected_fps: float, expected_frames: int) -> dict[str, object]:
    actual = probe_video(path)
    checks = {"resolution": (actual["width"], actual["height"]) == (expected_width, expected_height),
              "fps": abs(float(actual["fps"]) - expected_fps) <= max(0.1, expected_fps * 0.05),
              "frame_count": abs(int(actual["frame_count"]) - expected_frames) <= 1}
    return {"metadata": actual, "checks": checks, "valid": all(checks.values())}
