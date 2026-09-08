"""Common image I/O and representation conversions."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image


def load_image(path: str | Path, mode: str = "RGB") -> np.ndarray:
    with Image.open(path) as image:
        return np.asarray(image.convert(mode))


def save_image(path: str | Path, array: np.ndarray) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(to_uint8(array)).save(target)
    return target


def to_float01(array: np.ndarray) -> np.ndarray:
    values = np.asarray(array)
    if values.dtype == np.uint8:
        return values.astype(np.float32) / 255.0
    result = values.astype(np.float32)
    if result.size and (result.min() < 0 or result.max() > 1):
        raise ValueError("Floating-point image values must lie in [0, 1]")
    return result


def to_uint8(array: np.ndarray) -> np.ndarray:
    values = np.asarray(array)
    if values.dtype == np.uint8:
        return values
    return np.round(np.clip(values, 0, 1) * 255).astype(np.uint8)

