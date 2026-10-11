from __future__ import annotations

from luvix.doctor import _cloudinary_credentials_configured, _swift_toolchain_status


def test_partial_cloudinary_credentials_are_not_configured(monkeypatch) -> None:
    monkeypatch.delenv("CLOUDINARY_URL", raising=False)
    monkeypatch.setenv("CLOUDINARY_CLOUD_NAME", "cloud")
    monkeypatch.setenv("CLOUDINARY_API_KEY", "key")
    monkeypatch.delenv("CLOUDINARY_API_SECRET", raising=False)

    assert _cloudinary_credentials_configured() is False


def test_cloudinary_url_counts_as_configured(monkeypatch) -> None:
    monkeypatch.setenv("CLOUDINARY_URL", "cloudinary://key:secret@example")

    assert _cloudinary_credentials_configured() is True


def test_swift_toolchain_reports_ready(monkeypatch) -> None:
    class Result:
        returncode = 0
        stdout = "Apple Swift version 6"
        stderr = ""

    monkeypatch.setattr("luvix.doctor.shutil.which", lambda name: "/usr/bin/swiftc")
    monkeypatch.setattr("luvix.doctor.subprocess.run", lambda *args, **kwargs: Result())
    status = _swift_toolchain_status()
    assert status["ready"] is True
    assert status["toolchain_status"] == "ready"


def test_swift_toolchain_detects_xcode_license(monkeypatch) -> None:
    class Result:
        returncode = 69
        stdout = ""
        stderr = "You have not agreed to the Xcode license agreements."

    monkeypatch.setattr("luvix.doctor.shutil.which", lambda name: "/usr/bin/swiftc")
    monkeypatch.setattr("luvix.doctor.subprocess.run", lambda *args, **kwargs: Result())
    status = _swift_toolchain_status()
    assert status["ready"] is False
    assert status["toolchain_status"] == "Xcode license not accepted"
