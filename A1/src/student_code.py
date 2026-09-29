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


def _check_rect(image: np.ndarray, top: int, left: int, height: int, width: int) -> None:
    if height <= 0 or width <= 0:
        raise ValueError("Rectangle dimensions must be positive")
    if top < 0 or left < 0 or top + height > image.shape[0] or left + width > image.shape[1]:
        raise ValueError("Rectangle must lie inside the image")


def crop_image(image: np.ndarray, top: int, left: int, height: int, width: int) -> np.ndarray:
    """Return an independent NumPy crop; reject nonpositive or out-of-bounds rectangles."""
    _check_rect(image, top, left, height, width)
    return image[top:top + height, left:left + width].copy()


def flip_horizontal(image: np.ndarray) -> np.ndarray:
    """Return a horizontally flipped view or copy using array operations."""
    return image[:, ::-1].copy()


def extract_channel(image: np.ndarray, channel: int) -> np.ndarray:
    """Return one 2-D channel without changing its values."""
    if image.ndim != 3 or not 0 <= channel < image.shape[2]:
        raise ValueError("Invalid channel for image")
    return image[..., channel].copy()


def bgr_to_rgb(image: np.ndarray) -> np.ndarray:
    """Reorder a three-channel BGR array to RGB using NumPy."""
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("Expected a three-channel image")
    return image[..., ::-1].copy()


def replace_region(image: np.ndarray, top: int, left: int, height: int, width: int,
                   value: int | Sequence[int]) -> np.ndarray:
    """Return a copy with a positive, in-bounds rectangle replaced."""
    _check_rect(image, top, left, height, width)
    out = image.copy()
    out[top:top + height, left:left + width] = value
    return out


def contact_sheet(images: Sequence[np.ndarray], columns: int, fill_value: int = 0) -> np.ndarray:
    """Top-left-align all-grayscale or all-RGB uint8 images with an 8-pixel border/gutter."""
    if columns < 1 or len(images) == 0:
        raise ValueError("Need at least one image and one column")
    ndim = images[0].ndim
    for img in images:
        if img.dtype != np.uint8 or img.ndim != ndim or ndim not in (2, 3) or (ndim == 3 and img.shape[2] != 3):
            raise ValueError("Images must be all 2-D or all HxWx3 uint8")
    cell_h = max(img.shape[0] for img in images)
    cell_w = max(img.shape[1] for img in images)
    rows = -(-len(images) // columns)
    shape = (8 + rows * (cell_h + 8), 8 + columns * (cell_w + 8)) + ((3,) if ndim == 3 else ())
    sheet = np.full(shape, fill_value, dtype=np.uint8)
    for i, img in enumerate(images):
        r, c = divmod(i, columns)
        y, x = 8 + r * (cell_h + 8), 8 + c * (cell_w + 8)
        sheet[y:y + img.shape[0], x:x + img.shape[1]] = img
    return sheet


def brighten_loop(image: np.ndarray, offset: float) -> np.ndarray:
    """Brighten uint8 values with loops, nearest-even rounding, and clipping to [0, 255]."""
    out = np.empty_like(image, dtype=np.uint8)
    for index in np.ndindex(image.shape):
        out[index] = min(max(np.rint(float(image[index]) + offset), 0), 255)
    return out


def brighten_vectorized(image: np.ndarray, offset: float) -> np.ndarray:
    """Brighten uint8 values vectorially, nearest-even rounding, and clipping to [0, 255]."""
    return np.clip(np.rint(image.astype(np.float64) + offset), 0, 255).astype(np.uint8)


def to_float01(image: np.ndarray) -> np.ndarray:
    """Convert uint8 or uint16 values to float32 in [0, 1]."""
    if image.dtype == np.uint8:
        return image.astype(np.float32) / np.float32(255)
    if image.dtype == np.uint16:
        return image.astype(np.float32) / np.float32(65535)
    raise ValueError("Expected uint8 or uint16")


def to_uint8_safe(image: np.ndarray) -> np.ndarray:
    """Convert floating [0, 1] values to uint8 with clipping and rounding."""
    return np.clip(np.rint(np.asarray(image, dtype=np.float64) * 255), 0, 255).astype(np.uint8)


def grayscale_mean(image_rgb: np.ndarray) -> np.ndarray:
    """Return the unweighted channel mean as float32."""
    return image_rgb.astype(np.float32).mean(axis=-1).astype(np.float32)


def grayscale_luminance(image_rgb: np.ndarray) -> np.ndarray:
    """Return 0.299R + 0.587G + 0.114B as float32."""
    weights = np.array([0.299, 0.587, 0.114], dtype=np.float32)
    return (image_rgb.astype(np.float32) @ weights).astype(np.float32)


def hsv_rule(hsv_image: np.ndarray, lower: Sequence[int], upper: Sequence[int]) -> np.ndarray:
    """Return a boolean mask for inclusive OpenCV-HSV bounds, including wrapped hue ranges."""
    hsv = hsv_image.astype(np.int16)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    if lower[0] <= upper[0]:
        hue = (h >= lower[0]) & (h <= upper[0])
    else:
        hue = (h >= lower[0]) | (h <= upper[0])
    return hue & (s >= lower[1]) & (s <= upper[1]) & (v >= lower[2]) & (v <= upper[2])


def transform_frame(frame_rgb: np.ndarray) -> np.ndarray:
    """Flip RGB horizontally and multiply red by 0.65, preserving HxWx3 uint8."""
    out = frame_rgb[:, ::-1].astype(np.float32)
    out[..., 0] *= 0.65
    return np.clip(np.rint(out), 0, 255).astype(np.uint8)
