"""Consistent lightweight plotting helpers."""

from __future__ import annotations

import math
from collections.abc import Sequence

import matplotlib.pyplot as plt
import numpy as np


def show_images(images: Sequence[np.ndarray], titles: Sequence[str] | None = None,
                columns: int = 3, figsize: tuple[float, float] | None = None):
    if not images:
        raise ValueError("At least one image is required")
    rows = math.ceil(len(images) / columns)
    fig, axes = plt.subplots(rows, columns, figsize=figsize or (4 * columns, 4 * rows), squeeze=False)
    for index, axis in enumerate(axes.flat):
        axis.axis("off")
        if index < len(images):
            image = images[index]
            axis.imshow(image, cmap="gray" if np.asarray(image).ndim == 2 else None)
            if titles and index < len(titles):
                axis.set_title(titles[index])
    fig.tight_layout()
    return fig, axes

