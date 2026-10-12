"""Deterministic Apple HDR input discovery without decoding images."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

SUPPORTED_EXTENSIONS = frozenset({".heic", ".heif", ".jpg", ".jpeg"})


class BatchInputError(ValueError):
    """Invalid batch input or ambiguous output mapping."""


@dataclass(frozen=True)
class BatchItem:
    source: Path
    output_name: str


def discover(inputs: Iterable[Path], *, recursive: bool = False) -> list[BatchItem]:
    """Discover supported files, deduplicate paths, and reject output-name collisions.

    Directory traversal is shallow unless recursive=True. Unsupported files inside
    directories are ignored; explicit unsupported files fail immediately.
    """
    sources: dict[Path, None] = {}
    for raw in inputs:
        path = raw.expanduser()
        if path.is_file():
            if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                raise BatchInputError(f"Unsupported explicit input: {path}")
            sources[path.resolve()] = None
        elif path.is_dir():
            iterator = path.rglob("*") if recursive else path.iterdir()
            for candidate in iterator:
                if candidate.is_file() and candidate.suffix.lower() in SUPPORTED_EXTENSIONS:
                    sources[candidate.resolve()] = None
        else:
            raise BatchInputError(f"Input does not exist: {path}")
    if not sources:
        raise BatchInputError("No supported HEIC/JPEG files found")
    ordered = sorted(sources, key=lambda path: str(path).casefold())
    # Keep the extension to distinguish IMG_1234.HEIC and IMG_1234.JPG.
    # Refuse duplicate names from separate directories rather than silently overwrite.
    names: dict[str, Path] = {}
    items = []
    for source in ordered:
        name = source.name
        key = name.casefold()
        if key in names:
            raise BatchInputError(
                f"Output collision for {name}: {names[key]} and {source}. "
                "Use separate batches or rename inputs."
            )
        names[key] = source
        items.append(BatchItem(source=source, output_name=name))
    return items
