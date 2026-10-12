"""Compare HDR rasters in the same linear-light RGB working space.

This module intentionally does not change image decoding or color management.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import numpy as np

from luvix.backends.apple.hdr_raster import render_hdr_raster


class FidelityError(ValueError):
    """Inputs are not comparable without additional transforms."""


def compare_linear_rgb(
    reference: np.ndarray,
    candidate: np.ndarray,
    *,
    threshold: float = 0.01,
    reference_white: float = 1.0,
) -> dict[str, float | int | None]:
    """Calculate channel-wise errors, with highlights selected from reference pixels."""
    a = np.asarray(reference)
    b = np.asarray(candidate)
    if a.ndim != 3 or a.shape[-1] != 3 or a.shape != b.shape or not a.size:
        raise FidelityError("Expected matching, nonempty HxWx3 linear RGB rasters")
    if not np.issubdtype(a.dtype, np.number) or not np.issubdtype(b.dtype, np.number):
        raise FidelityError("Raster channels must be numeric")
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise FidelityError("Raster contains non-finite values")
    if not np.isfinite(threshold) or threshold < 0:
        raise FidelityError("threshold must be finite and nonnegative")
    if not np.isfinite(reference_white) or reference_white <= 0:
        raise FidelityError("reference_white must be finite and positive")

    delta = np.asarray(a, dtype=np.float64) - np.asarray(b, dtype=np.float64)
    absolute = np.abs(delta)
    highlights = np.any(a > reference_white, axis=2)
    highlight_error = absolute[highlights]
    changed = np.any(absolute > threshold, axis=2)
    return {
        "width": int(a.shape[1]),
        "height": int(a.shape[0]),
        "mae": float(np.mean(absolute)),
        "rmse": float(np.sqrt(np.mean(np.square(delta)))),
        "p99_absolute_error": float(np.percentile(absolute, 99)),
        "max_absolute_error": float(np.max(absolute)),
        "highlight_pixel_count": int(np.count_nonzero(highlights)),
        "highlight_mae": float(np.mean(highlight_error)) if highlight_error.size else None,
        "changed_pixel_fraction": float(np.mean(changed)),
        "threshold": float(threshold),
    }


def compare_apple_hdr(
    reference: Path, candidate: Path, *, threshold: float = 0.01
) -> dict[str, object]:
    """Decode both sources via Apple's existing HDR renderer and compare raw raster axes."""
    with tempfile.TemporaryDirectory(prefix="luvix-fidelity-") as directory:
        root = Path(directory)
        results = []
        for name, path in (("reference", reference), ("candidate", candidate)):
            if not path.is_file():
                raise FileNotFoundError(path)
            prefix = root / name
            render_hdr_raster(path, prefix)
            info = json.loads(prefix.with_suffix(".json").read_text())
            results.append((prefix, info))
        (ref_prefix, ref_info), (test_prefix, test_info) = results
        for key in ("width", "height", "orientation", "color_space", "source_primaries"):
            if ref_info.get(key) != test_info.get(key):
                raise FidelityError(f"Cannot compare: {key} differs")
        h, w = int(ref_info["height"]), int(ref_info["width"])
        ref = np.memmap(ref_prefix.with_suffix(".rgba32f"), dtype="<f4", mode="r", shape=(h, w, 4))
        test = np.memmap(
            test_prefix.with_suffix(".rgba32f"), dtype="<f4", mode="r", shape=(h, w, 4)
        )
        metrics = compare_linear_rgb(ref[..., :3], test[..., :3], threshold=threshold)
        return {
            "reference": str(reference),
            "candidate": str(candidate),
            "working_space": ref_info["color_space"],
            "source_primaries": ref_info["source_primaries"],
            "orientation": ref_info["orientation"],
            "metrics": metrics,
        }
