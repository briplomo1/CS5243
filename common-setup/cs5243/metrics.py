"""Small, dependency-light metrics shared across assignments."""

from __future__ import annotations

import numpy as np


def mean_squared_error(reference: np.ndarray, estimate: np.ndarray) -> float:
    a, b = np.asarray(reference, dtype=np.float64), np.asarray(estimate, dtype=np.float64)
    if a.shape != b.shape:
        raise ValueError(f"Shape mismatch: {a.shape} != {b.shape}")
    return float(np.mean(np.square(a - b)))


def accuracy(reference: np.ndarray, prediction: np.ndarray) -> float:
    a, b = np.asarray(reference), np.asarray(prediction)
    if a.shape != b.shape:
        raise ValueError(f"Shape mismatch: {a.shape} != {b.shape}")
    if a.size == 0:
        raise ValueError("Accuracy is undefined for empty arrays")
    return float(np.mean(a == b))

