"""Batch extraction using the same native operation as single-file extraction."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path

from luvix.batch.discovery import BatchItem


def extract_many(
    items: Sequence[BatchItem],
    output: Path,
    *,
    backend: Callable[..., str],
    continue_on_error: bool = True,
) -> dict[str, object]:
    """Extract into one directory per source; never overwrite an existing output.

    Failures are recorded per file. No rollback of successful earlier items is
    attempted. A partially written failed output remains for inspection.
    """
    results: list[dict[str, str]] = []
    for item in items:
        destination = output / item.output_name
        if destination.exists():
            results.append(
                {
                    "source": str(item.source),
                    "output": str(destination),
                    "status": "failed",
                    "error": "Output already exists",
                }
            )
            if not continue_on_error:
                break
            continue
        try:
            backend("extract", str(item.source), str(destination))
        except Exception as exc:
            results.append(
                {
                    "source": str(item.source),
                    "output": str(destination),
                    "status": "failed",
                    "error": str(exc),
                }
            )
            if not continue_on_error:
                break
        else:
            results.append({"source": str(item.source), "output": str(destination), "status": "ok"})
    succeeded = sum(row["status"] == "ok" for row in results)
    return {
        "operation": "extract",
        "total": len(items),
        "processed": len(results),
        "succeeded": succeeded,
        "failed": len(results) - succeeded,
        "results": results,
    }
