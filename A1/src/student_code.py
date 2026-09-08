"""Student implementations for A1. Do not add dependencies or use bypass libraries."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np


def image_summary(image: np.ndarray) -> dict[str, object]:
    """Return shape, height, width, channels, dtype, range, mean, and nbytes."""
    row = {
            'shape': image.shape,
            'height': image.shape[0],
            'width': image.shape[1],
            'channels': image.shape[2] if image.ndim == 3 else 1,
            'dtype': image.dtype,
            'range': (image.min(), image.max()),
            'mean': image.mean(),
            'nbytes': image.nbytes
        }
    return row


def crop_image(image: np.ndarray, top: int, left: int, height: int, width: int) -> np.ndarray:
    """Return an independent NumPy crop; reject nonpositive or out-of-bounds rectangles."""
    raise NotImplementedError


def flip_horizontal(image: np.ndarray) -> np.ndarray:
    """Return a horizontally flipped view or copy using array operations."""
    raise NotImplementedError


def extract_channel(image: np.ndarray, channel: int) -> np.ndarray:
    """Return one 2-D channel without changing its values."""
    raise NotImplementedError


def bgr_to_rgb(image: np.ndarray) -> np.ndarray:
    """Reorder a three-channel BGR array to RGB using NumPy."""
    raise NotImplementedError


def replace_region(image: np.ndarray, top: int, left: int, height: int, width: int,
                   value: int | Sequence[int]) -> np.ndarray:
    """Return a copy with a positive, in-bounds rectangle replaced."""
    raise NotImplementedError


def contact_sheet(images: Sequence[np.ndarray], columns: int, fill_value: int = 0) -> np.ndarray:
    """Top-left-align all-grayscale or all-RGB uint8 images with an 8-pixel border/gutter."""
    raise NotImplementedError


def brighten_loop(image: np.ndarray, offset: float) -> np.ndarray:
    """Brighten uint8 values with loops, nearest-even rounding, and clipping to [0, 255]."""
    raise NotImplementedError


def brighten_vectorized(image: np.ndarray, offset: float) -> np.ndarray:
    """Brighten uint8 values vectorially, nearest-even rounding, and clipping to [0, 255]."""
    raise NotImplementedError


def to_float01(image: np.ndarray) -> np.ndarray:
    """Convert uint8 or uint16 values to float32 in [0, 1]."""
    raise NotImplementedError


def to_uint8_safe(image: np.ndarray) -> np.ndarray:
    """Convert floating [0, 1] values to uint8 with clipping and rounding."""
    raise NotImplementedError


def grayscale_mean(image_rgb: np.ndarray) -> np.ndarray:
    """Return the unweighted channel mean as float32."""
    raise NotImplementedError


def grayscale_luminance(image_rgb: np.ndarray) -> np.ndarray:
    """Return 0.299R + 0.587G + 0.114B as float32."""
    raise NotImplementedError


def hsv_rule(hsv_image: np.ndarray, lower: Sequence[int], upper: Sequence[int]) -> np.ndarray:
    """Return a boolean mask for inclusive OpenCV-HSV bounds, including wrapped hue ranges."""
    raise NotImplementedError


def transform_frame(frame_rgb: np.ndarray) -> np.ndarray:
    """Flip RGB horizontally and multiply red by 0.65, preserving HxWx3 uint8."""
    raise NotImplementedError
