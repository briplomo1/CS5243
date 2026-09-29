"""Student implementations for A2. Do not add dependencies or bypass required work."""

from __future__ import annotations

from collections.abc import Sequence
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
import cv2

borders = ['reflect', 'edge', 'constant']

def convolve2d_manual(image: np.ndarray, kernel: np.ndarray, border_mode: str = "reflect") -> np.ndarray:
    """Convolve a 2-D or HxWxC image with an odd 2-D kernel; return float32.

    Apply true mathematical convolution, including spatial reversal of the kernel.
    Support ``reflect``, ``edge``, and ``constant`` borders. Do not delegate the
    core operation to a library convolution, correlation, or neural-network layer.
    """

    if kernel.ndim != 2:
        raise ValueError(f"kernel must be 2-dimensional, got {kernel.shape}")
    kernel_h, kernel_w = kernel.shape
    if kernel_h % 2 == 0 or kernel_w % 2 == 0:
        raise ValueError(f"kernel must be odd, got {kernel.shape}")
    if border_mode not in borders:
        raise ValueError(f"border mode must be one of {borders}", borders)
    pad_h, pad_w = kernel_h // 2, kernel_w // 2
    H, W = image.shape[:2]
    pad = ((pad_h, pad_h), (pad_w, pad_w))
    if image.ndim == 3:
        pad = pad + ((0, 0),)
    if border_mode == "constant":
        padded = np.pad(image, pad, mode="constant", constant_values=0.0)
    else:
        if border_mode == "reflect" and (pad_h >= H or pad_w >= W):
            raise ValueError(f"Relfect border requires kernel half-size to be less than {H}x{W}")
        padded = np.pad(image, pad, mode=border_mode)

    kernel_rev = kernel[::-1, ::-1]
    conv = np.zeros_like(image)
    for u in range(kernel_h):
        for v in range(kernel_w):
            w = kernel_rev[u, v]
            if w!= 0.0:
                conv += w * padded[u:u + H, v:v + W]
    return conv.astype(np.float32)

def gaussian_kernel(size: int, sigma: float) -> np.ndarray:
    """Return a nonnegative, symmetric, normalized float32 square Gaussian kernel."""
    if size % 2 == 0:
        raise ValueError(f"size must be odd, got {size}")

    ax = np.arange(size) - size//2
    xx, yy = np.meshgrid(ax, ax)
    kernel = np.exp(-(xx**2 + yy**2) / (2 * sigma**2))
    kernel = kernel / kernel.sum()
    return kernel.astype(np.float32)


def sharpen_image(image: np.ndarray, amount: float, sigma: float) -> np.ndarray:
    """Return unclipped float32 unsharp masking; require amount >= 0 and sigma > 0.
    Compute ``image + amount * (image - blur)`` for a Gaussian blur of ``sigma``,
    so ``amount = 0`` returns the input unchanged. Choose the Gaussian support
    yourself and state your choice; see the A2 README.
    """
    if sigma <= 0.0:
        raise ValueError(f"sigma must be positive, got {sigma}")
    if amount < 0:
        raise ValueError(f"amount must be positive, got {amount}")
    radius = int(np.ceil(3*sigma))
    size = 2 * radius + 1
    kernel = gaussian_kernel(size, sigma)
    blur = convolve2d_manual(image, kernel, border_mode="constant")
    sharp = image + amount * (image - blur)
    return sharp.astype(np.float32)


def add_gaussian_noise(image: np.ndarray, sigma: float, rng: np.random.Generator) -> np.ndarray:
    """Add supplied-RNG Gaussian noise to float [0,1]; require sigma >= 0 and clip."""
    if sigma < 0.0:
        raise ValueError(f"sigma must be positive, got {sigma}")
    noise = rng.normal(loc=0.0, scale=sigma, size=image.shape)
    out = image + noise.astype(image.dtype, copy=False)
    return np.clip(out, 0.0, 1.0)


def add_impulse_noise(image: np.ndarray, probability: float, rng: np.random.Generator) -> np.ndarray:
    """Apply equiprobable salt or pepper to independently selected spatial pixels.

    Select each pixel with ``probability`` using only ``rng``. Set every channel of
    a selected color pixel to the same value, either 0 or 1 with equal probability.
    """
    if not 0.0 <= probability <= 1.0:
        raise ValueError(f"probability must be between 0 and 1, got {probability}")

    img_shape = image.shape[:2] if image.ndim == 3 else image.shape

    hit = rng.random(img_shape) < probability
    salt = rng.random(img_shape) < 0.5
    values = salt.astype(image.dtype)

    out = image.copy()
    if image.ndim == 3:
        out[hit] = values[hit][:, None]
    else:
        out[hit] = values[hit]
    return out



def median_filter_manual(image: np.ndarray, kernel_size: int, border_mode: str = "reflect") -> np.ndarray:
    """Median-filter 2-D or HxWxC data with an odd window; do not delegate filtering."""
    if kernel_size % 2 == 0:
        raise ValueError(f"kernel_size must be odd, got {kernel_size}")
    if border_mode not in borders:
        raise ValueError(f"border mode must be one of {borders}", borders)

    img = np.asarray(image, dtype=np.float64)
    if img.ndim not in  (2, 3):
        raise ValueError(f"image must be 2-dimensional, got {img.ndim}")

    radius = kernel_size // 2
    H, W = img.shape[:2]

    if border_mode == "reflect" and (radius >= H or radius >= W):
        raise ValueError("Reflect border requires kernel half-size < image size")
    pad_width = [(radius,radius), (radius, radius)]
    if img.ndim == 3:
        pad_width.append((0, 0))

    if border_mode == "constant":
        padded = np.pad(img, pad_width=pad_width, mode="constant", constant_values=0.0)
    elif border_mode == "edge":
        padded = np.pad(img, pad_width=pad_width, mode="edge")
    else:
        padded = np.pad(img, pad_width=pad_width, mode="reflect")

    def median2d(plane: np.ndarray) -> np.ndarray:
        windows = sliding_window_view(plane, (kernel_size, kernel_size))
        return np.median(windows, axis=(-2, -1))

    if img.ndim == 2:
        out = median2d(padded)
    else:
        channels = [median2d(padded[..., chan]) for chan in range(img.shape[2])]
        out = np.stack(channels, axis=-1)
    return out.astype(np.float32)


def normalize_contrast(image: np.ndarray, low_percentile: float, high_percentile: float) -> np.ndarray:
    """Globally stretch all image values between two valid percentiles to [0,1].

    Use one pair of percentile values jointly across all channels, apply one affine
    mapping, and clip. Raise ``ValueError`` for invalid or equal computed bounds.
    """
    if not (0.0 <= low_percentile <= 100.0):
        raise ValueError(f"low_percentile must be between 0 and 100, got {low_percentile}")
    if not (0.0 <= high_percentile <= 100.0):
        raise ValueError(f"high_percentile must be between 0 and 100, got {high_percentile}")
    if low_percentile >= high_percentile:
        raise ValueError(f"low percentile must be less than high percentile, got {low_percentile}")

    img = np.asarray(image, dtype=np.float64)
    lo, hi = np.percentile(img, (low_percentile, high_percentile))

    if hi <= lo:
        raise ValueError(f"high percentile must be less than low percentile, got {hi}")

    out = (img-lo) / (hi-lo)
    out = np.clip(out, 0.0, 1.0)
    return out.astype(np.float32)


def histogram_equalize_gray(image: np.ndarray) -> np.ndarray:
    """Equalize a 2-D uint8 image with a 256-bin CDF; return 2-D uint8.

    Subtract the first nonzero CDF value, map to the full uint8 range with
    deterministic nearest-integer rounding, and return constant images unchanged.
    """
    if image.ndim != 2:
        raise ValueError(f"image must be 2-dimensional, got {image.ndim}")
    if image.dtype != np.uint8:
        raise ValueError(f"image must be uint8, got {image.dtype}")
    hist, _ = np.histogram(image, bins=256)
    cdf = np.cumsum(hist)
    tot = image.size

    cdf_gt0 = cdf[cdf > 0]
    cdf_min = cdf_gt0[0]
    denom = tot-cdf_min
    if denom == 0:
        return image.copy()
    table = np.rint((cdf.astype(np.float64) - cdf_min) / denom*255)
    table = table.astype(np.uint8)
    # Get each pixel as lookup into table
    return table[image]

def apply_gamma(image: np.ndarray, gamma: float) -> np.ndarray:
    """Return ``image ** gamma`` for float [0,1] input as float32 [0,1].

    Positive gamma below 1 brightens; gamma above 1 darkens.
    """
    if gamma <= 0:
        raise ValueError(f"gamma must be > 0, got {gamma}")

    img = np.asarray(image, dtype=np.float64)
    out = img ** gamma
    return out.astype(np.float32)



def gaussian_pyramid(image: np.ndarray, levels: int) -> list[np.ndarray]:
    if levels < 1:
        raise ValueError(f"levels must be positive, got {levels}")

    img = np.asarray(image, dtype=np.float32)
    if img.ndim not in (2, 3):
        raise ValueError(f"image must be 2-dimensional, got {img.ndim}")

    pyramid = [img]
    current = img
    for _ in range(levels -1):
        H, W = current.shape[:2]
        reduced = cv2.pyrDown(current)
        pyramid.append(reduced.astype(np.float32))
        current = reduced
    return pyramid

def expand(level: np.ndarray, target_shape: tuple[int, int]) -> np.ndarray:
    target_H, target_W = target_shape[:2]
    h, w = level.shape[:2]
    if target_H < h or target_W < w:
        raise ValueError(f"target shape {(target_H, target_W)}must be >= source shape {(h, w)}")
    expanded = cv2.pyrUp(level, dstsize=(target_W, target_H))
    return expanded.astype(np.float32)

def laplacian_pyramid(image: np.ndarray, levels: int) -> list[np.ndarray]:
    """Return fine-to-coarse Laplacian levels with the coarsest Gaussian last."""
    gauss = gaussian_pyramid(image, levels)
    laplacian = []
    for i in range(levels - 1):
        expanded = expand(gauss[i+1], gauss[i].shape[:2])
        laplacian.append((gauss[i] - expanded).astype(np.float32))
    laplacian.append(gauss[-1])
    return laplacian

def reconstruct_laplacian_pyramid(pyramid: Sequence[np.ndarray]) -> np.ndarray:
    """Reconstruct a float32 image, including pyramids with odd spatial dimensions."""
    if len(pyramid) == 0:
        raise ValueError(f"empty pyramid sequence, cannot reconstruct laplacian")

    reconstructed = np.asarray(pyramid[-1], dtype=np.float32)
    for level in reversed(pyramid[:-1]):
        t_shape = level.shape[:2]
        reconstructed = expand(reconstructed, t_shape) + np.asarray(level, dtype=np.float32)
    return reconstructed.astype(np.float32)


def laplacian_pyramid_blend(image_a: np.ndarray, image_b: np.ndarray, mask: np.ndarray, levels: int) -> np.ndarray:
    """Laplacian pyramid blend of equal-size float [0,1] images with a float [0,1] spatial mask.

    Mask 0 selects ``image_a``; mask 1 selects ``image_b``; intermediate values blend.
    """
    lap_a = laplacian_pyramid(image_a, levels)
    lap_b = laplacian_pyramid(image_b, levels)
    mask_pyr = gaussian_pyramid(mask.astype(np.float32), levels)

    blended = []
    for la, lb, m in zip(lap_a, lap_b, mask_pyr):
        if la.ndim == 3:
            m = m[..., None]
        level = la * (1.0 - m) + lb * m
        blended.append(level.astype(np.float32))

    result = reconstruct_laplacian_pyramid(blended)
    return np.clip(result, 0.0, 1.0)
