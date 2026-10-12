"""Safe batch pairing and native rebuild/validation orchestration."""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from pathlib import Path

from luvix.batch.discovery import SUPPORTED_EXTENSIONS


class BatchPairingError(ValueError):
    """Ambiguous or invalid extracted-component pairing."""


def discover_pairs(extracted: Path, sources: Path, *, recursive: bool = False) -> list[dict]:
    """Match extraction manifests to source files by exact source_name.

    Source paths must resolve inside the supplied source directory. Ambiguous
    names are rejected rather than guessing. No user edits are inspected.
    """
    extracted = extracted.expanduser().resolve()
    sources = sources.expanduser().resolve()
    if not extracted.is_dir() or not sources.is_dir():
        raise BatchPairingError("Extraction and source paths must be directories")
    manifests = sorted(
        extracted.rglob("manifest.json") if recursive else extracted.glob("*/manifest.json"),
        key=lambda p: str(p).casefold(),
    )
    if not manifests:
        raise BatchPairingError("No extraction manifests found")
    candidates = sources.rglob("*") if recursive else sources.iterdir()
    index: dict[str, list[Path]] = {}
    for path in candidates:
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            index.setdefault(path.name.casefold(), []).append(path.resolve())
    pairs = []
    used_sources: set[Path] = set()
    for manifest in manifests:
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            name = data["source_name"]
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise BatchPairingError(f"Invalid manifest {manifest}: {exc}") from exc
        if not isinstance(name, str) or Path(name).name != name or name in {".", ".."}:
            raise BatchPairingError(f"Unsafe source_name in {manifest}")
        matches = index.get(name.casefold(), [])
        if len(matches) != 1:
            raise BatchPairingError(f"Expected exactly one source for {name}; found {len(matches)}")
        source = matches[0]
        if source in used_sources:
            raise BatchPairingError(f"Source paired more than once: {source}")
        used_sources.add(source)
        if manifest.parent.name.casefold() != name.casefold():
            raise BatchPairingError(f"Directory/manifest source mismatch: {manifest.parent}")
        base = manifest.parent / "base.png"
        gainmap = manifest.parent / "gainmap.png"
        if not base.is_file() or not gainmap.is_file():
            raise BatchPairingError(f"Missing component PNG in {manifest.parent}")
        pairs.append({"source": source, "base": base, "gainmap": gainmap})
    return pairs


def rebuild_many(
    pairs: Sequence[dict],
    output: Path,
    *,
    backend: Callable[..., str],
    continue_on_error: bool = True,
) -> dict:
    """Rebuild paired sources; delegate geometry checks to the native backend."""
    results = []
    output.mkdir(parents=True, exist_ok=True)

    for pair in pairs:
        source = pair["source"]
        destination = output / source.name
        row = {"source": str(source), "output": str(destination)}
        if destination.exists():
            row.update(status="failed", error="Output already exists")
        else:
            try:
                backend(
                    "rebuild",
                    str(source),
                    str(pair["base"]),
                    str(pair["gainmap"]),
                    str(destination),
                )
                row["status"] = "ok"
            except Exception as exc:
                row.update(status="failed", error=str(exc))
        results.append(row)
        if row["status"] == "failed" and not continue_on_error:
            break
    return _report("rebuild", len(pairs), results)


def validate_many(
    pairs: Sequence[dict],
    rebuilt: Path,
    *,
    backend: Callable[..., str],
    continue_on_error: bool = True,
) -> dict:
    """Validate each rebuilt file against its original source."""
    results = []
    for pair in pairs:
        source = pair["source"]
        destination = rebuilt / source.name
        row = {"source": str(source), "output": str(destination)}
        try:
            if not destination.is_file():
                raise ValueError("Rebuilt output is missing")
            raw = backend("validate", str(source), str(destination))
            payload = json.loads(raw)
            if payload.get("valid") is not True:
                raise ValueError(f"Structural validation failed: {payload}")
            row["status"] = "ok"
        except Exception as exc:
            row.update(status="failed", error=str(exc))
        results.append(row)
        if row["status"] == "failed" and not continue_on_error:
            break
    return _report("validate", len(pairs), results)


def _report(operation: str, total: int, results: list[dict]) -> dict:
    succeeded = sum(row["status"] == "ok" for row in results)
    return {
        "operation": operation,
        "total": total,
        "processed": len(results),
        "succeeded": succeeded,
        "failed": len(results) - succeeded,
        "results": results,
    }
