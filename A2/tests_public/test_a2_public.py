"""Limited public sanity checks for A2."""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import a2_tools  # noqa: E402

candidate = os.environ.get("CS5243_A2_IMPLEMENTATION")
if candidate:
    spec = importlib.util.spec_from_file_location("a2_candidate", candidate)
    assert spec is not None and spec.loader is not None
    sc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sc)
else:
    import student_code as sc  # noqa: E402


NAMES = [
    "convolve2d_manual", "gaussian_kernel", "sharpen_image", "add_gaussian_noise",
    "add_impulse_noise", "median_filter_manual", "normalize_contrast",
    "histogram_equalize_gray", "apply_gamma", "gaussian_pyramid",
    "laplacian_pyramid", "reconstruct_laplacian_pyramid", "laplacian_pyramid_blend",
]


def run(function, *args, **kwargs):
    try:
        return function(*args, **kwargs)
    except NotImplementedError:
        pytest.skip(f"{function.__name__} remains a starter placeholder")


def test_imports_and_assets():
    assert all(callable(getattr(sc, name, None)) for name in NAMES)
    assert a2_tools.verify_asset_hashes() == []


def test_gaussian_and_true_convolution():
    kernel = run(sc.gaussian_kernel, 5, 1.2)
    assert kernel.shape == (5, 5) and kernel.dtype == np.float32
    assert np.all(kernel >= 0) and kernel.sum() == pytest.approx(1, abs=1e-6)
    assert np.allclose(kernel, kernel[::-1, ::-1])

    image = np.zeros((5, 5), np.float32)
    image[2, 2] = 1
    asymmetric = np.array([[0, 1, 2], [0, 0, 3], [0, 0, 0]], np.float32)
    result = run(sc.convolve2d_manual, image, asymmetric, "constant")
    assert np.array_equal(result[1:4, 1:4], asymmetric)


def test_sharpen_is_unsharp_masking():
    image = np.linspace(0, 1, 9 * 11, dtype=np.float32).reshape(9, 11)
    assert np.allclose(run(sc.sharpen_image, image, 0.0, 1.2), image, atol=1e-6)

    edge = np.zeros((9, 11), np.float32)
    edge[:, 5:] = 1.0
    assert np.max(run(sc.sharpen_image, edge, 3.0, 1.2)) > 1.0


def test_noise_is_deterministic_and_spatial():
    image = np.full((12, 13, 3), 0.5, np.float32)
    first = run(sc.add_gaussian_noise, image, 0.1, np.random.default_rng(4))
    second = run(sc.add_gaussian_noise, image, 0.1, np.random.default_rng(4))
    assert np.array_equal(first, second)

    impulse = run(sc.add_impulse_noise, image, 1.0, np.random.default_rng(5))
    assert set(np.unique(impulse)) == {0.0, 1.0}
    assert np.array_equal(impulse[..., 0], impulse[..., 1])
    assert np.array_equal(impulse[..., 1], impulse[..., 2])


def test_gamma_contrast_and_pyramid_round_trip():
    image = np.linspace(0, 1, 7 * 9, dtype=np.float32).reshape(7, 9)
    assert np.allclose(run(sc.apply_gamma, image, 1), image)
    assert np.all(run(sc.apply_gamma, image, 0.5) >= image)
    assert np.all(run(sc.apply_gamma, image, 2.0) <= image)

    pyramid = run(sc.laplacian_pyramid, image, 3)
    reconstructed = run(sc.reconstruct_laplacian_pyramid, pyramid)
    assert len(pyramid) == 3 and reconstructed.shape == image.shape
    assert np.max(np.abs(reconstructed - image)) < 1e-5


def test_blend_contracts():
    image_a = np.zeros((9, 11, 3), np.float32)
    image_b = np.ones_like(image_a)
    zeros = np.zeros((9, 11), np.float32)
    ones = np.ones((9, 11), np.float32)
    assert np.max(np.abs(run(sc.laplacian_pyramid_blend, image_a, image_b, zeros, 3) - image_a)) < 1e-5
    assert np.max(np.abs(run(sc.laplacian_pyramid_blend, image_a, image_b, ones, 3) - image_b)) < 1e-5
