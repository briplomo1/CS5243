"""Portable video frame I/O through imageio."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path

import imageio.v3 as iio
import numpy as np


def read_frames(path: str | Path) -> Iterator[np.ndarray]:
    yield from iio.imiter(path, plugin="FFMPEG")


def write_frames(path: str | Path, frames: Iterable[np.ndarray], fps: float = 30.0) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    iio.imwrite(target, list(frames), plugin="FFMPEG", fps=fps)
    return target

