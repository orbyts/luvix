from __future__ import annotations

from typer.testing import CliRunner

from luvix.cli import app

runner = CliRunner()


def test_inspect_dispatch_pretty_json(monkeypatch):
    monkeypatch.setattr("luvix.cli.run_backend", lambda *args: '{"gain_format":"L008"}')
    result = runner.invoke(app, ["inspect", "test.HEIC"])
    assert result.exit_code == 0
    assert result.stdout == '{\n  "gain_format": "L008"\n}\n'


def test_inspect_compact_json(monkeypatch):
    monkeypatch.setattr("luvix.cli.run_backend", lambda *args: '{"gain_format":"L008"}')
    result = runner.invoke(app, ["inspect", "test.HEIC", "--compact"])
    assert result.exit_code == 0
    assert result.stdout == '{"gain_format":"L008"}\n'


def test_extract_dispatch(monkeypatch):
    calls = []
    monkeypatch.setattr("luvix.cli.run_backend", lambda *args: calls.append(args) or "ok")
    result = runner.invoke(app, ["extract", "test.HEIC", "--output", "out"])
    assert result.exit_code == 0
    assert calls[0][0] == "extract"


def test_rebuild_requires_edit():
    result = runner.invoke(app, ["rebuild", "--source", "a.HEIC", "--output", "b.HEIC"])
    assert result.exit_code == 2


def test_rebuild_dispatch(monkeypatch):
    calls = []
    monkeypatch.setattr("luvix.cli.run_backend", lambda *args: calls.append(args) or "ok")
    result = runner.invoke(
        app, ["rebuild", "--source", "a.HEIC", "--gainmap", "map.png", "--output", "b.HEIC"]
    )
    assert result.exit_code == 0
    assert calls[0][3] == "map.png"


def test_validate_dispatch(monkeypatch):
    monkeypatch.setattr("luvix.cli.run_backend", lambda *args: '{"valid":true}')
    result = runner.invoke(app, ["validate", "--source", "a.HEIC", "--output", "b.HEIC"])
    assert result.exit_code == 0
