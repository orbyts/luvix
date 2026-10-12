# Changelog

## [0.1.5] - 2026-10-12

### Added
- Batch input discovery for mixed Apple HDR HEIC/JPEG files and directories, with optional recursion.
- Batch upright base/gain-map/manifest extraction into one directory per source.
- Batch 32-bit linear and 16-bit PQ TIFF export using the existing single-image HDR engine.
- Batch manifest-paired HEIC/JPEG rebuilding and structural validation.
- Per-file results, JSON summaries, fail-fast option, and overwrite protection.
- Fifteen sanitized real iPhone fixtures spanning HEIC/JPEG and EXIF orientations 1 and 6.

### Fixed
- Batch rebuild now creates its output directory before writing files.

### Validated
- 15/15 fixture inspections and extractions.
- 15/15 32-bit linear and 15/15 16-bit PQ TIFF exports with matching ICC and orientation metadata.
- 15/15 rebuilt images and 15/15 structural validations; output-directory creation verified.
- 86 automated tests, Ruff, formatting, and lockfile checks passed before release preparation.

### Notes
- The tested tagged PQ workflow still requires an external compatible ICC profile.
- No HDR reconstruction, PQ math, or TIFF encoding algorithms were changed.


## [0.1.4] - 2026-10-12

### Added
- Apple iPhone HDR gain-map JPEG support across inspection, HDR probing, extraction, rebuild, validation, and TIFF export.
- Sanitized real iPhone HEIC/JPEG fixtures for macOS integration coverage.
- Upright, spatially aligned component extraction with source/editing geometry recorded in the manifest.
- Internal full-resolution HDR fidelity metrics for regression analysis; these metrics do not gate user edits.

### Changed
- Rebuild is container-aware: HEIC sources rebuild as HEIC and JPEG sources as JPEG.
- Rebuild reverses extraction orientation normalization and restores source orientation metadata.
- Component edit validation is intentionally limited to structural geometry and decodability; Luvix does not police artistic, exposure, color, or same-geometry pixel edits.
- Native backend errors no longer duplicate the CLI `Error:` prefix.

### Validated
- Real orientation-6 HEIC and JPEG captures extract to upright 4284x5712 bases and 2142x2856 gain maps, then rebuild to the original 5712x4284 / 2856x2142 raw geometry with orientation 6.
- JPEG-derived 32-bit linear HDR TIFF export preserves source orientation and embeds the matching tested linear profile.
- JPEG-derived 16-bit PQ TIFF export writes 16-bit RGB, orientation 6, and a supplied compatible `P3 PQ` ICC profile.
- HEIC rebuild regression remains structurally valid with Display P3 and orientation preserved.

### Notes
- Luvix does not redistribute the external Adobe-compatible P3 PQ ICC used during validation.
- HEIC/JPEG rebuilds are lossy container encodes; internal fidelity measurements characterize Luvix-induced differences but are not user-edit acceptance criteria.
- Batch Apple HDR workflows shipped in v0.1.5.

## [0.1.3] - 2026-10-11

### Added
- Pretty-printed JSON output for `inspect` and `inspect-hdr`.
- `--compact` output for machine-readable single-line JSON.
- Swift compiler and Xcode toolchain readiness diagnostics.
- Actionable diagnostics when the Xcode license has not been accepted.
- Release/milestone/slice-based engineering roadmap.

### Changed
- `doctor` now distinguishes Swift installation, Xcode toolchain readiness,
  and Apple HDR backend readiness.
- `ROADMAP.md` is now the shared engineering ledger and source of truth for
  release progress, acceptance criteria, evidence, and next actions.

### Notes
- HDR reconstruction, gain-map processing, TIFF encoding, PQ math, and color
  management algorithms are unchanged from v0.1.2.
- The next planned release is v0.1.4, focused on Apple JPEG gain maps.



## [0.1.2] - 2026-10-10

### Changed
- Reworked the user guide around the installed `luvix` CLI instead of
  source-checkout `uv run` commands.
- Added clearer installation and quick-start documentation for PyPI users.
- Updated `luvix doctor` to report the HDR capabilities implemented in Luvix.
- Added macOS and Swift runtime readiness reporting for the Apple HDR backend.
- Clarified that 16-bit PQ export currently requires a compatible external
  PQ ICC profile.

### Fixed
- Removed obsolete bootstrap diagnostics claiming that HDR processing was
  not implemented.
- Removed the outdated "HDR processing begins in Luvix 0.0.2" message.

### Notes
- HDR decoding, reconstruction, TIFF encoding, PQ math, and color-management
  algorithms are unchanged from v0.1.1.



## [0.1.0] - 2026-10-10

### Added
- Apple HDR HEIC inspection and gain-map metadata reporting.
- Independent SDR base and HDR gain-map extraction.
- HDR HEIC reconstruction after editing either component.
- Structural HDR validation.
- Native Apple HDR decoding into extended linear RGB.
- 32-bit floating-point linear HDR TIFF export.
- 16-bit PQ HDR TIFF export with external ICC profile support.
- Source-aware color management for tested Display P3 and sRGB workflows.
- Original image orientation preservation.
- User guide, architecture documentation, and development roadmap.

### Notes
- Apple HDR HEIC is the currently validated input format.
- 32-bit linear TIFF export has been validated in Photoshop.
- 16-bit PQ TIFF export has been validated using an externally supplied
  Adobe-compatible P3 PQ ICC profile.
- Additional input formats, color spaces, and gain-map standards remain
  on the roadmap.



All notable changes to Gaincraft will be documented in this file. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

HDR processing is planned for 0.0.2.

## [0.0.1] - 2026-07-17

### Added

- Initial public Python package and `gaincraft` console entry point.
- `gaincraft --version`.
- Read-only `gaincraft doctor` diagnostics with human-readable and JSON output.
- Packaging, linting, tests, CI, and trusted PyPI publishing configuration.

### Not included

- HDR image processing. Gain-map-aware processing begins in 0.0.2.

[Unreleased]: https://github.com/orbyts/gaincraft/compare/v0.0.1...HEAD
[0.0.1]: https://github.com/orbyts/gaincraft/releases/tag/v0.0.1
