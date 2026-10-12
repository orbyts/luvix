# Luvix

[![Tests](https://github.com/orbyts/luvix/actions/workflows/test.yml/badge.svg)](https://github.com/orbyts/luvix/actions/workflows/test.yml)

**Luvix** is a command-line HDR interoperability toolkit for photographers. It helps move HDR photographs between capture, editing, and delivery applications when their gain-map formats or HDR representations are not directly compatible.

For example, an iPhone photo can contain an SDR base and an HDR gain map. Luvix can inspect and extract those components, reconstruct the HDR image, and export a high-precision TIFF for editing in a familiar application such as Photoshop. It can also rebuild supported Apple gain-map captures after component edits. The goal is to preserve HDR intent, color information, and metadata across workflows, not to replace the editor.

## Current support

**v0.1.5:** Apple iPhone gain-map HEIC and JPEG on macOS using ImageIO/Core Image and Swift. `inspect`, `inspect-hdr`, upright component `extract`, geometry-checked `rebuild`, `validate`, and `export tiff` are exercised with real sanitized iPhone fixtures. The 32-bit floating-point linear TIFF path uses a matching linear ICC profile. The 16-bit PQ path accepts an externally supplied compatible PQ ICC profile; Luvix does not redistribute the Adobe reference profile used during validation.

Extraction normalizes the SDR base and gain map into the same upright editing orientation. Rebuild checks only structural geometry and decodability, reverses that orientation normalization, and restores the source orientation. Pixel, color, exposure, and other same-geometry edits are intentionally the user's responsibility.

**Batch workflows (v0.1.5):** Mixed Apple HEIC/JPEG input discovery, upright component extraction, 32-bit linear / 16-bit PQ TIFF export, manifest-paired rebuild and structural validation, and per-file JSON reporting. Processing is sequential and never overwrites existing outputs.

Luvix is an interoperability layer, not a RAW developer or general-purpose photo editor. Conventional RAW files should continue through established RAW editing workflows when those tools already handle them correctly. New input formats are added when they address a demonstrated HDR interoperability need.

## Install

Recommended for a command-line application:

```bash
uv tool install luvix
luvix --version
```

Alternatively, use `pipx install luvix`, or install `luvix` with pip inside an activated virtual environment. Once installed, run `luvix` directly. `uv run luvix` is for development from a source checkout.

The native Apple HDR backend requires macOS and a usable Swift/Xcode toolchain. Use `luvix doctor` to check the environment.

## Quick start

```bash
luvix doctor
luvix inspect ~/Pictures/photo.HEIC
luvix inspect ~/Pictures/photo.JPG
luvix extract ~/Pictures/photo.HEIC --output ~/Pictures/work/photo
luvix export tiff ~/Pictures/photo.HEIC \
  --bit-depth 32 --transfer linear --color-space source \
  --output ~/Pictures/work/photo_linear32.tif
```

For 16-bit PQ output, supply a compatible external PQ ICC and an explicit reference white. See the user guide for the complete workflow and current limitations. Commands that rebuild or convert images should be verified against their output format and color metadata before professional delivery.

## Batch quick start (macOS)

Batch commands accept mixed Apple HDR HEIC/JPEG sources. Output is never overwritten.

```bash
luvix batch extract ~/Pictures/iPhone --output ~/Pictures/Extracted --json
luvix batch export tiff ~/Pictures/iPhone --bit-depth 32 --transfer linear --color-space source --output ~/Pictures/Linear32 --json
luvix batch export tiff ~/Pictures/iPhone --bit-depth 16 --transfer pq --color-space source --reference-white 203 --icc-profile ~/ColorProfiles/P3_PQ.icc --output ~/Pictures/PQ16 --json
luvix batch rebuild ~/Pictures/Extracted --sources ~/Pictures/iPhone --output ~/Pictures/Rebuilt --json
luvix batch validate ~/Pictures/Rebuilt --sources ~/Pictures/iPhone --extracted ~/Pictures/Extracted --json
```

Extraction creates a directory per input image, named with its source extension (for example `IMG_9203.HEIC/base.png`). `--recursive` enables recursive discovery; `--fail-fast` stops after the first per-image failure. A compatible external PQ ICC is required for the tested tagged 16-bit PQ workflow. See the [user guide](docs/USER_GUIDE.md) for details.

## Editing paths

Luvix favors the least-destructive workflow that fits the edit. For color-only or other component-safe edits, `extract` writes the SDR base and gain map in the same upright editing orientation; `rebuild` checks their geometry and restores the source orientation when packaging the Apple HDR image. Luvix does not judge the artistic or pixel-level content of those edits.

For crop, resize, generative fill, compositing, or other geometry-changing edits, reconstruct the HDR image and work in a high-precision raster such as 32-bit linear TIFF or 16-bit PQ TIFF. A new gain map can then be generated by a compatible downstream workflow; generalized gain-map generation is planned for Luvix's later interoperability work.

## Documentation

- [User guide](docs/USER_GUIDE.md): commands, output formats, and troubleshooting.
- [Architecture](docs/ARCHITECTURE.md): gain-map model, color handling, and format constraints.
- [Roadmap](ROADMAP.md): release ledger, Apple JPEG, batch workflows, ISO 21496-1 / Ultra HDR, libvips/libultrahdr, and future gain-map generation.
- [Release checklist](docs/RELEASE_CHECKLIST.md): CI, package verification, publishing, and installed-package tests.
- [Changelog](CHANGELOG.md)

## Development

Development commands and contribution workflows are separate from normal CLI usage. The Python package is cross-platform, but the current Apple HDR processing backend is macOS-only. Refer to the project source and release checklist for development validation.

## License

Apache License 2.0. Do not redistribute proprietary reference ICC profiles or private photographs without appropriate rights.
