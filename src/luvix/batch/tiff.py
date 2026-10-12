"""Sequential TIFF batch orchestration; delegates to the existing exporter."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path

from luvix.batch.discovery import BatchItem


def export_tiff_many(
    items: Sequence[BatchItem],
    output: Path,
    *,
    exporter: Callable,
    bit_depth: int,
    transfer: str,
    reference_white_nits: float | None = None,
    external_pq_icc: Path | None = None,
    embed_icc: bool = True,
    continue_on_error: bool = True,
) -> dict:
    suffix = "HDR_Linear32" if bit_depth == 32 else "HDR_PQ16"
    results = []
    for item in items:
        destination = output / f"{item.source.stem}_{item.source.suffix[1:].upper()}_{suffix}.tif"
        if destination.exists():
            row = dict(
                source=str(item.source),
                output=str(destination),
                status="failed",
                error="Output already exists",
            )
        else:
            try:
                details = exporter(
                    item.source,
                    destination,
                    bit_depth=bit_depth,
                    transfer=transfer,
                    reference_white_nits=reference_white_nits,
                    external_pq_icc=external_pq_icc,
                    embed_icc=embed_icc,
                )
                row = dict(
                    source=str(item.source), output=str(destination), status="ok", details=details
                )
            except Exception as exc:
                row = dict(
                    source=str(item.source),
                    output=str(destination),
                    status="failed",
                    error=str(exc),
                )
        results.append(row)
        if row["status"] == "failed" and not continue_on_error:
            break
    succeeded = sum(r["status"] == "ok" for r in results)
    return dict(
        operation="export_tiff",
        total=len(items),
        processed=len(results),
        succeeded=succeeded,
        failed=len(results) - succeeded,
        results=results,
    )
