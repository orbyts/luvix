"""Batch manifest pairing, safe rebuilding, and validation tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from luvix.batch.rebuild import (
    BatchPairingError,
    discover_pairs,
    rebuild_many,
    validate_many,
)
from luvix.cli import app


def setup_pair(tmp_path: Path, name: str = "image.JPG") -> tuple[Path, Path]:
    extracted = tmp_path / "extracted"
    components = extracted / name
    components.mkdir(parents=True)
    (components / "manifest.json").write_text(json.dumps({"source_name": name}))
    (components / "base.png").touch()
    (components / "gainmap.png").touch()
    sources = tmp_path / "sources"
    sources.mkdir()
    (sources / name).touch()
    return extracted, sources


def test_pairing_and_rebuild(tmp_path: Path) -> None:
    extracted, sources = setup_pair(tmp_path)
    pairs = discover_pairs(extracted, sources)
    assert len(pairs) == 1
    calls = []

    def backend(*args):
        calls.append(args)
        Path(args[-1]).parent.mkdir(exist_ok=True)
        Path(args[-1]).touch()
        return "ok"

    report = rebuild_many(pairs, tmp_path / "out", backend=backend)
    assert report["succeeded"] == 1
    assert calls[0][0] == "rebuild"
    assert calls[0][2].endswith("base.png")
    assert (
        validate_many(pairs, tmp_path / "out", backend=lambda *_: '{"valid":true}')["succeeded"]
        == 1
    )


def test_no_overwrite_and_validation_failure(tmp_path: Path) -> None:
    extracted, sources = setup_pair(tmp_path)
    pairs = discover_pairs(extracted, sources)
    output = tmp_path / "out"
    output.mkdir()
    (output / "image.JPG").touch()
    report = rebuild_many(pairs, output, backend=lambda *_: pytest.fail("overwritten"))
    assert report["failed"] == 1
    assert validate_many(pairs, output, backend=lambda *_: '{"valid":false}')["failed"] == 1


def test_manifest_mismatch_rejected(tmp_path: Path) -> None:
    extracted, sources = setup_pair(tmp_path)
    (extracted / "image.JPG" / "manifest.json").write_text('{"source_name":"different.JPG"}')
    with pytest.raises(BatchPairingError):
        discover_pairs(extracted, sources)


def test_ambiguous_source_rejected(tmp_path: Path) -> None:
    extracted, sources = setup_pair(tmp_path)
    nested = sources / "nested"
    nested.mkdir()
    (nested / "image.JPG").touch()
    with pytest.raises(BatchPairingError, match="exactly one"):
        discover_pairs(extracted, sources, recursive=True)


def test_cli_rebuild_and_validate(tmp_path: Path, monkeypatch) -> None:
    extracted, sources = setup_pair(tmp_path)
    output = tmp_path / "out"

    def backend(*args):
        if args[0] == "rebuild":
            output.mkdir(exist_ok=True)
            (output / "image.JPG").touch()
            return "ok"
        return '{"valid":true}'

    monkeypatch.setattr("luvix.cli.run_backend", backend)
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "batch",
            "rebuild",
            str(extracted),
            "--sources",
            str(sources),
            "-o",
            str(output),
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["succeeded"] == 1
    result = runner.invoke(
        app,
        [
            "batch",
            "validate",
            str(output),
            "--sources",
            str(sources),
            "--extracted",
            str(extracted),
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["succeeded"] == 1


def test_batch_rebuild_creates_output_directory(tmp_path):
    """Rebuild creates a missing nested output directory."""
    from luvix.batch.rebuild import rebuild_many

    source_file = tmp_path / "original.HEIC"
    source_file.write_bytes(b"source")

    base = tmp_path / "base.png"
    gainmap = tmp_path / "gainmap.png"
    base.write_bytes(b"base")
    gainmap.write_bytes(b"gainmap")

    output = tmp_path / "new" / "nested" / "rebuilt"

    assert not output.exists()

    def fake_backend(*args):
        assert args[0] == "rebuild"
        destination = Path(args[-1])
        assert destination.parent.is_dir()
        destination.write_bytes(b"rebuilt")
        return ""

    pairs = [
        {
            "source": source_file,
            "base": base,
            "gainmap": gainmap,
        }
    ]

    report = rebuild_many(
        pairs,
        output,
        backend=fake_backend,
    )

    assert output.is_dir()
    assert (output / "original.HEIC").read_bytes() == b"rebuilt"
    assert report["succeeded"] == 1
    assert report["failed"] == 0


def test_batch_rebuild_refuses_overwrite(tmp_path):
    """Existing rebuilt files must never be overwritten."""
    from luvix.batch.rebuild import rebuild_many

    source_file = tmp_path / "original.HEIC"
    source_file.write_bytes(b"source")

    output = tmp_path / "rebuilt"
    output.mkdir()

    destination = output / source_file.name
    destination.write_bytes(b"existing")

    def forbidden_backend(*args):
        raise AssertionError("Backend must not run for existing output")

    report = rebuild_many(
        [
            {
                "source": source_file,
                "base": tmp_path / "base.png",
                "gainmap": tmp_path / "gainmap.png",
            }
        ],
        output,
        backend=forbidden_backend,
    )

    assert destination.read_bytes() == b"existing"
    assert report["succeeded"] == 0
    assert report["failed"] == 1
    assert report["results"][0]["error"] == "Output already exists"
