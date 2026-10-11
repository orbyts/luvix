from __future__ import annotations

import json

from typer.testing import CliRunner

from luvix.cli import app

runner = CliRunner()


def test_inspect_hdr_dispatch(monkeypatch):
    calls = []

    def fake_probe(source, samples):
        calls.append((source, samples))
        return json.dumps({"hdr": {"max_rgb": [2.0, 1.5, 1.2]}})

    monkeypatch.setattr("luvix.backends.apple.hdr_probe.run_hdr_probe", fake_probe)
    result = runner.invoke(app, ["inspect-hdr", "example.HEIC", "--samples", "8"])
    assert result.exit_code == 0, result.output
    assert calls[0][1] == 8
    assert json.loads(result.output)["hdr"]["max_rgb"] == [2.0, 1.5, 1.2]


def test_inspect_hdr_rejects_zero_samples():
    result = runner.invoke(app, ["inspect-hdr", "example.HEIC", "--samples", "0"])
    assert result.exit_code != 0


def test_inspect_hdr_compact(monkeypatch):
    monkeypatch.setattr(
        "luvix.backends.apple.hdr_probe.run_hdr_probe",
        lambda source, samples: json.dumps({"hdr": {"max_rgb": [2.0]}}),
    )
    result = runner.invoke(app, ["inspect-hdr", "example.HEIC", "--compact"])
    assert result.exit_code == 0
    assert result.stdout == '{"hdr":{"max_rgb":[2.0]}}\n'
