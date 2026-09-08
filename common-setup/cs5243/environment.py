"""Environment inspection without imposing a compute-device policy."""

from __future__ import annotations

import importlib
import platform
import random
import sys
from importlib import metadata

import numpy as np

ENVIRONMENT_VERSION = "2026.1"
PYTHON_SPEC = (3, 11)


def package_version(distribution: str) -> str | None:
    """Return an installed distribution version, or ``None``."""
    try:
        return metadata.version(distribution)
    except metadata.PackageNotFoundError:
        return None


def environment_report() -> dict[str, object]:
    """Return portable runtime facts useful in validation reports."""
    packages = ["numpy", "scipy", "pandas", "matplotlib", "Pillow", "opencv-python",
                "scikit-image", "scikit-learn", "imageio", "torch", "torchvision"]
    return {
        "environment_version": ENVIRONMENT_VERSION,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "packages": {name: package_version(name) for name in packages},
    }


def verify_environment() -> list[str]:
    """Return problems found in the active course environment."""
    problems: list[str] = []
    if sys.version_info[:2] != PYTHON_SPEC:
        problems.append(f"Python 3.11 required; found {platform.python_version()}")
    for module in ("numpy", "scipy", "pandas", "matplotlib", "PIL", "cv2", "skimage",
                   "sklearn", "imageio", "tqdm", "torch", "torchvision", "yaml"):
        try:
            importlib.import_module(module)
        except Exception as exc:  # imports can fail from binary incompatibility
            problems.append(f"Cannot import {module}: {exc}")
    return problems


def set_deterministic_seed(seed: int = 5243) -> None:
    """Seed standard random generators without imposing device behavior."""
    random.seed(seed)
    np.random.seed(seed)
    try:
        torch = importlib.import_module("torch")
        torch.manual_seed(seed)
    except ImportError:
        pass
