"""Batch discovery, collision and extraction behavior (no macOS required)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from luvix.batch.discovery import BatchInputError, discover
from luvix.batch.extract import extract_many
from luvix.cli import app


def test_discovery_filters_and_sorts(tmp_path: Path) -> None:
    (tmp_path / "z.JPG").touch()
    (tmp_path / "a.HEIC").touch()
    (tmp_path / "ignored.txt").touch()
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "deep.jpeg").touch()
    assert [i.output_name for i in discover([tmp_path])] == ["a.HEIC", "z.JPG"]
    assert len(discover([tmp_path], recursive=True)) == 3


def test_explicit_invalid_input(tmp_path: Path) -> None:
    file = tmp_path / "image.png"
    file.touch()
    with pytest.raises(BatchInputError, match="Unsupported"):
        discover([file])


def test_duplicate_output_name_fails(tmp_path: Path) -> None:
    for name in ("first", "second"):
        folder = tmp_path / name
        folder.mkdir()
        (folder / "same.HEIC").touch()
    with pytest.raises(BatchInputError, match="collision"):
        discover([tmp_path], recursive=True)


def test_same_stem_different_extension_is_safe(tmp_path: Path) -> None:
    (tmp_path / "a.JPG").touch()
    (tmp_path / "a.HEIC").touch()
    assert len(discover([tmp_path])) == 2


def test_extract_failures_are_isolated(tmp_path: Path) -> None:
    for name in ("a.jpg", "b.heic"):
        (tmp_path / name).touch()
    items = discover([tmp_path])

    def backend(_command: str, source: str, destination: str) -> str:
        if source.endswith("a.jpg"):
            raise RuntimeError("bad gain map")
        Path(destination).mkdir(parents=True)
        return "ok"

    report = extract_many(items, tmp_path / "out", backend=backend)
    assert report["failed"] == 1
    assert report["succeeded"] == 1


def test_existing_output_not_overwritten(tmp_path: Path) -> None:
    source = tmp_path / "a.JPG"
    source.touch()
    output = tmp_path / "out"
    (output / source.name).mkdir(parents=True)
    report = extract_many(discover([source]), output, backend=lambda *_: "ok")
    assert report["failed"] == 1
    assert "already exists" in report["results"][0]["error"]


def test_cli_batch_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = tmp_path / "a.HEIC"
    source.touch()

    def fake_backend(_command: str, _source: str, destination: str) -> str:
        Path(destination).mkdir(parents=True)
        return "ok"

    monkeypatch.setattr("luvix.cli.run_backend", fake_backend)
    result = CliRunner().invoke(
        app, ["batch", "extract", str(source), "-o", str(tmp_path / "out"), "--json"]
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["succeeded"] == 1
