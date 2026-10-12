"""Regression checks for the native Apple orientation-normalized component contract."""

from __future__ import annotations

from importlib.resources import files


def _swift_source() -> str:
    return files("luvix.backends.apple").joinpath("imageio.swift").read_text()


def test_orientation_inverse_table_covers_quarter_turns() -> None:
    source = _swift_source()
    assert "case 6: return 8" in source
    assert "case 8: return 6" in source
    assert "default: return orientation" in source


def test_orientation_swaps_dimensions_for_transposed_orientations() -> None:
    source = _swift_source()
    assert "case 5, 6, 7, 8: return (height, width)" in source


def test_extract_records_editing_geometry() -> None:
    source = _swift_source()
    for field in (
        "source_orientation",
        "editing_orientation",
        "editing_base_width",
        "editing_base_height",
        "editing_gain_width",
        "editing_gain_height",
    ):
        assert field in source
