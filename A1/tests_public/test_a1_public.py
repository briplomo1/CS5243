"""Small public sanity tests for A1; additional edge cases are not included here."""

from __future__ import annotations

import sys
import os
import importlib.util
from pathlib import Path

import numpy as np
import pytest


A1_ROOT = Path(__file__).resolve().parents[1]
SRC = A1_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import a1_tools  # noqa: E402
implementation = os.environ.get("CS5243_A1_IMPLEMENTATION")
if implementation:
    spec = importlib.util.spec_from_file_location("a1_candidate", implementation)
    assert spec is not None and spec.loader is not None
    sc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sc)
else:
    import student_code as sc  # noqa: E402


FUNCTIONS = [
    "image_summary", "crop_image", "flip_horizontal", "extract_channel", "bgr_to_rgb",
    "replace_region", "contact_sheet", "brighten_loop", "brighten_vectorized", "to_float01",
    "to_uint8_safe", "grayscale_mean", "grayscale_luminance", "hsv_rule", "transform_frame",
]


def implemented(function, *args, **kwargs):
    try:
        return function(*args, **kwargs)
    except NotImplementedError:
        pytest.skip(f"{function.__name__} is still a starter placeholder")


def test_imports_and_signatures():
    assert all(callable(getattr(sc, name, None)) for name in FUNCTIONS)


def test_repository_and_assets_are_discoverable():
    root = a1_tools.find_repository_root(A1_ROOT)
    assert (root / "environment.yml").is_file()
    assert (a1_tools.asset_root(root) / "images" / "channel_order.png").is_file()
    assert a1_tools.verify_asset_checksums() == []


def test_basic_spatial_operations():
    image = np.arange(4 * 5 * 3, dtype=np.uint8).reshape(4, 5, 3)
    crop = implemented(sc.crop_image, image, 1, 2, 2, 2)
    assert crop.shape == (2, 2, 3)
    assert np.array_equal(implemented(sc.flip_horizontal, image), image[:, ::-1])
    assert implemented(sc.extract_channel, image, 1).shape == (4, 5)


def test_brightness_implementations_agree():
    image = np.array([[0, 10, 250]], dtype=np.uint8)
    loop = implemented(sc.brighten_loop, image, 20)
    vector = implemented(sc.brighten_vectorized, image, 20)
    assert loop.dtype == vector.dtype == np.uint8
    assert np.array_equal(loop, vector)
    assert vector.tolist() == [[20, 30, 255]]


def test_safe_round_trip():
    image = np.array([0, 1, 127, 255], dtype=np.uint8)
    floating = implemented(sc.to_float01, image)
    restored = implemented(sc.to_uint8_safe, floating)
    assert floating.dtype == np.float32
    assert np.array_equal(restored, image)


def test_video_probe_and_readback():
    root = a1_tools.find_repository_root(A1_ROOT)
    path = a1_tools.asset_root(root) / "video" / "moving_shapes.mp4"
    metadata = a1_tools.probe_video(path)
    assert metadata["width"] == 320 and metadata["height"] == 240
    assert metadata["frame_count"] == 48 and metadata["fps"] == pytest.approx(12.0, abs=0.2)
