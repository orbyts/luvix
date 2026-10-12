"""Deterministic numerical tests for the internal HDR fidelity metrics."""

import numpy as np
import pytest

from luvix.hdr.fidelity import FidelityError, compare_linear_rgb


def test_identical_rasters_have_zero_error():
    image = np.array([[[0.0, 1.0, 2.0], [0.5, 0.3, 0.1]]], dtype=np.float32)
    result = compare_linear_rgb(image, image)
    assert result["mae"] == 0
    assert result["rmse"] == 0
    assert result["highlight_pixel_count"] == 1
    assert result["changed_pixel_fraction"] == 0


def test_known_error_and_highlight_mask():
    a = np.array([[[2, 0, 0], [0, 0, 0]]], dtype=np.float32)
    b = np.array([[[1, 0, 0], [0, 0, 0]]], dtype=np.float32)
    result = compare_linear_rgb(a, b, threshold=0.5)
    assert result["mae"] == pytest.approx(1 / 6)
    assert result["rmse"] == pytest.approx((1 / 6) ** 0.5)
    assert result["highlight_mae"] == pytest.approx(1 / 3)
    assert result["changed_pixel_fraction"] == pytest.approx(0.5)


def test_rejects_mismatch_and_nan():
    a = np.zeros((2, 2, 3), dtype=np.float32)
    with pytest.raises(FidelityError, match="matching"):
        compare_linear_rgb(a, np.zeros((3, 2, 3), dtype=np.float32))
    a[0, 0, 0] = np.nan
    with pytest.raises(FidelityError, match="non-finite"):
        compare_linear_rgb(a, a)


def test_no_highlights_returns_null():
    a = np.zeros((1, 1, 3), dtype=np.float32)
    assert compare_linear_rgb(a, a)["highlight_mae"] is None
