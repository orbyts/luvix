"""Container dispatch and optional native integration regression coverage."""

from __future__ import annotations

import json
import os
import platform
from pathlib import Path

import pytest
from typer.testing import CliRunner

from luvix.cli import app

runner = CliRunner()


@pytest.mark.parametrize("suffix", [".HEIC", ".JPG", ".jpeg"])
def test_rebuild_dispatch_accepts_source_extension(monkeypatch, suffix):
    calls = []
    monkeypatch.setattr("luvix.cli.run_backend", lambda *args: calls.append(args) or "ok")
    result = runner.invoke(
        app,
        [
            "rebuild",
            "--source",
            f"photo{suffix}",
            "--gainmap",
            "map.png",
            "--output",
            f"rebuilt{suffix}",
        ],
    )
    assert result.exit_code == 0
    assert calls[0] == ("rebuild", f"photo{suffix}", "-", "map.png", f"rebuilt{suffix}")


@pytest.mark.skipif(platform.system() != "Darwin", reason="ImageIO integration requires macOS")
def test_native_jpeg_rebuild(tmp_path):
    """Opt-in private/public fixture integration; never requires fixtures in CI."""
    fixture = os.environ.get("LUVIX_JPEG_FIXTURE")
    source = (
        Path(fixture)
        if fixture
        else Path(__file__).parent / "fixtures" / "apple" / "iphone_hdr_jpeg.jpg"
    )
    if not source.is_file():
        pytest.skip("Apple HDR JPEG fixture unavailable")
    from luvix.backends.apple.bridge import run_backend

    extracted = tmp_path / "components"
    run_backend("extract", str(source), str(extracted))

    manifest = json.loads((extracted / "manifest.json").read_text())
    assert manifest["source_orientation"] == 6
    assert manifest["editing_orientation"] == 1
    assert (manifest["editing_base_width"], manifest["editing_base_height"]) == (4284, 5712)
    assert (manifest["editing_gain_width"], manifest["editing_gain_height"]) == (2142, 2856)

    output = tmp_path / "rebuilt.jpg"
    run_backend(
        "rebuild",
        str(source),
        str(extracted / "base.png"),
        str(extracted / "gainmap.png"),
        str(output),
    )
    assert output.read_bytes()[:3] == b"\xff\xd8\xff"
    before = json.loads(run_backend("inspect", str(source)))
    after = json.loads(run_backend("inspect", str(output)))
    for key in (
        "base_width",
        "base_height",
        "gain_width",
        "gain_height",
        "gain_format",
        "color_space",
        "orientation",
        "has_gainmap_metadata",
    ):
        assert before[key] == after[key], key
    assert json.loads(run_backend("validate", str(source), str(output)))["valid"]
    # Semantic edits are intentionally not policed. Geometry is the rebuild gate.
