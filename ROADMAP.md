# Luvix Roadmap

Status: active engineering ledger.

This document is the source of truth for Luvix development. A completed item requires evidence, not merely implemented code. At the beginning of each work session, identify the active release and earliest incomplete slice, verify repository state, and continue from the recorded next action.

If priorities change, update this roadmap first.

## Vision

Luvix is a format-independent HDR and gain-map utility: a Swiss Army knife for inspecting, splitting, reconstructing, generating, validating, and converting HDR image representations.

The long-term goal is a common workflow above native and third-party imaging backends such as Apple ImageIO/Core Image, libvips, and libultrahdr.

Luvix should eventually support both directions:

```text
gain-map image -> components -> reconstructed HDR -> editable raster
SDR + HDR -> generated gain map -> gain-map image
```

The public CLI should describe operations rather than backend implementation details.

## Current position

Release: **v0.1.3**

Theme: Apple-native HDR foundation and CLI polish.

Active slice: **R1.3 — release**

Evidence:
- Pretty JSON is the default for `inspect` and `inspect-hdr`.
- `--compact` provides single-line JSON for scripting.
- `doctor` probes Swift/Xcode readiness.
- Apple HDR backend reports ready on the validated macOS environment.
- Xcode-license/toolchain failures receive actionable diagnostics.
- 61 automated tests pass.
- Ruff and formatting checks pass.
- uv lockfile resolves successfully.
- This roadmap is now the shared engineering ledger.

Next action:
1. Finalize v0.1.3 changelog.
2. Run release validation.
3. Commit and push `feature/cli-polish`.
4. Run GitHub CI and merge to `main`.
5. Publish GitHub v0.1.3 release.
6. Verify Trusted Publishing to PyPI.
7. Install/upgrade from PyPI and smoke-test the installed CLI.
8. Begin **v0.1.4 / A1 — Apple JPEG discovery**.

Blockers: none known.

## Supported today

### Apple gain-map HEIC
- Inspect Apple HDR HEIC base and auxiliary gain-map structure.
- Probe distinct SDR and HDR ImageIO decode requests.
- Extract SDR base and gain map.
- Rebuild HEIC after editing the base, gain map, or both.
- Validate core HDR structure.
- Reconstruct full-resolution HDR RGB.
- Export 32-bit floating-point linear HDR TIFF.
- Export 16-bit unsigned PQ HDR TIFF.
- Preserve source orientation in TIFF output.

### 32-bit linear TIFF
- Float32 RGB.
- Extended linear HDR values above 1.0 preserved.
- Matching linear ICC embedded.
- Original orientation preserved.
- Visually validated in Photoshop for the tested Display P3 Apple capture.

### 16-bit PQ TIFF
- ST 2084 PQ encoding.
- 16-bit unsigned RGB.
- Explicit reference-white policy.
- Orientation preserved.
- Compatible external PQ ICC supported.
- Adobe-compatible P3 PQ profile validated visually in Photoshop.
- Numerically validated against the 32-bit linear reference.

Current limitation: Luvix does not yet ship a redistributable built-in PQ profile, and arbitrary ICC/color-space conversion is not yet promised.

### Distribution
- GitHub releases
- PyPI
- `uv tool install luvix`
- `pipx install luvix`
- conventional isolated `pip` installation

Homebrew packaging is planned.

## Release history

### v0.1.0 — Gaincraft functional prototype
Historical pre-rebrand release. Established Apple HDR inspection, extraction, rebuild, structural validation, native HDR reconstruction investigation, and initial HDR TIFF work.

### v0.1.1 — Luvix distribution and HDR TIFF workflow
Established the Gaincraft -> Luvix rebrand, PyPI distribution, Trusted Publishing, validated 32-bit linear HDR TIFF, and validated 16-bit PQ using a compatible external ICC profile.

### v0.1.2 — User-facing installation and diagnostics
Established installed-CLI documentation, PyPI quick start, functional `doctor` reporting, Apple runtime diagnostics, and removal of obsolete bootstrap messaging.

## v0.1.3 — CLI polish

### S1 — Pretty structured output
- [x] `luvix inspect` pretty-prints valid JSON by default.
- [x] `luvix inspect-hdr` pretty-prints valid JSON by default.

### S2 — Compact machine output
- [x] `inspect --compact` emits single-line JSON.
- [x] `inspect-hdr --compact` emits single-line JSON.

### S3 — Native toolchain diagnostics
- [x] Detect Swift compiler installation.
- [x] Probe actual Swift/Xcode usability.
- [x] Distinguish installed compiler from ready Xcode toolchain.
- [x] Report Apple HDR backend readiness.
- [x] Provide actionable Xcode-license diagnostics.

### S4 — Regression validation
- [x] 61 tests passing.
- [x] Ruff clean.
- [x] Formatting clean.
- [x] uv lockfile valid.
- [x] Real Apple HDR `inspect-hdr --compact` smoke test passed.

### S5 — Engineering ledger
- [x] Releases divided into milestones/slices.
- [x] Active position and next action explicit.
- [x] Acceptance criteria distinguish implementation from verification.
- [x] Future architecture recorded.
- [x] Decision log and progress protocol defined.

### R1.3 — Release
- [ ] CHANGELOG documents v0.1.3.
- [ ] Local release checks pass.
- [ ] Distribution builds and metadata validation pass.
- [ ] Swift resources are present in the wheel.
- [ ] GitHub CI passes.
- [ ] Changes merge into `main`.
- [ ] GitHub v0.1.3 release published.
- [ ] PyPI reports `luvix==0.1.3`.
- [ ] Installed PyPI CLI passes version/doctor/native smoke tests.

## v0.1.4 — Apple JPEG gain maps

Theme: complete the Apple-native 0.1.x foundation across Apple's gain-map containers before introducing generalized third-party backends.

### A1 — Apple JPEG discovery
Status: next after v0.1.3.

Acceptance:
- [ ] Obtain/create at least one verified Apple JPEG gain-map fixture.
- [ ] Document `CGImageSource`/auxiliary-image structure.
- [ ] Record base/gain-map dimensions, format, metadata, ICC, orientation and headroom.
- [ ] Compare HDR-aware decode behavior with HEIC.
- [ ] Keep private fixtures out of the public repository.

### A2 — Apple JPEG inspection
- [ ] `luvix inspect` recognizes supported Apple JPEG gain maps.
- [ ] `inspect-hdr` performs the HDR decode probe.
- [ ] Ordinary unsupported JPEGs fail clearly.
- [ ] Public/synthetic tests cover detection.

### A3 — Apple JPEG extraction
- [ ] Extract editable SDR base and gain map.
- [ ] Write a deterministic rebuild manifest.
- [ ] Preserve required source metadata.

### A4 — Apple JPEG rebuild
- [ ] Base-only edit.
- [ ] Gain-map-only edit.
- [ ] Both edited.
- [ ] Validate dimensions/orientation.
- [ ] Never silently resample or rotate.

### A5 — HDR reconstruction and TIFF export
- [ ] Reconstruct into the shared linear representation.
- [ ] 32-bit linear TIFF matches the HEIC workflow.
- [ ] 16-bit PQ uses the same color-management contract.
- [ ] Numerical comparison against reference HDR decode is within tolerance.

### A6 — Apple backend cleanup
- [ ] Move container-specific decisions behind the Apple backend.
- [ ] Preserve existing HEIC behavior.
- [ ] Define supported/unsupported Apple gain-map variants.

### R1.4 — Release
- [ ] HEIC regression suite passes.
- [ ] Apple JPEG integration suite passes.
- [ ] Documentation updated.
- [ ] GitHub CI passes.
- [ ] PyPI installation smoke test passes.

## v0.2.x — Generalized HDR and gain-map engine

Theme: move beyond Apple-native representations using libvips/libultrahdr and generalized color/gain-map workflows. The architecture must support both reconstruction and future gain-map generation from paired SDR/HDR sources.

### M2.1 — Common HDR/gain-map model
Define backend-neutral SDR base, HDR image, gain map, metadata, primaries/white point, transfer function, reference white/headroom, orientation, and monochrome vs multichannel/color gain maps.

Acceptance:
- [ ] Core model does not depend on HEIC, JPEG, ImageIO, libvips, or libultrahdr.
- [ ] Existing Apple workflows map into the model.
- [ ] Model supports both decode and future generation/encode workflows.

### M2.2 — libvips backend
- [ ] Detect libvips/pyvips capabilities.
- [ ] Evaluate HDR/high-precision operations.
- [ ] Evaluate `uhdrload`/`uhdrsave` by runtime version.
- [ ] Keep libvips optional.
- [ ] Add numerical high-precision round-trip tests.

### M2.3 — libultrahdr backend
- [ ] Runtime/library detection.
- [ ] Public/synthetic fixtures.
- [ ] Decode tests.
- [ ] Encode tests.
- [ ] Metadata round-trip tests.

### M2.4 — ISO 21496-1 / Ultra HDR interoperability
Distinguish ISO 21496-1, Ultra HDR conventions, libultrahdr, libvips, ImageMagick, browser behavior, and Adobe interoperability.

Acceptance:
- [ ] Standards/implementation differences documented.
- [ ] `inspect`, `extract`, rebuild/encode supported.
- [ ] Browser/reference-viewer tests documented.
- [ ] Numerical HDR reconstruction tests pass.

### M2.5 — Generalized color management
- [ ] Separate primaries from transfer functions.
- [ ] Validate Display P3, Rec.2020, and sRGB-primary workflows as appropriate.
- [ ] Support linear and PQ, with HLG planned.
- [ ] Establish redistributable built-in HDR profile strategy.
- [ ] P3 PQ no longer requires a proprietary external profile.
- [ ] Unsupported profiles fail explicitly.

### M2.6 — Gain-map generation from SDR + HDR
Goal: support the inverse of reconstruction.

```text
SDR source + HDR source
          |
          v
  normalized/aligned pair
          |
          v
     gain-map model
          |
          +--> Apple representation where supported
          +--> ISO / Ultra HDR JPEG
```

Research includes gain calculation, offsets, min/max boost, gamma, HDR capacity/headroom, color normalization, clipping, monochrome vs color gain maps, and alignment.

Acceptance:
- [ ] Synthetic reference vectors.
- [ ] SDR/HDR pair reconstructs to expected HDR within tolerance.
- [ ] Generated metadata documented.
- [ ] At least one standards-compatible encoded output.
- [ ] No assumption that gain maps are always monochrome.

### M2.7 — Cross-format conversion

Examples:
```text
Apple HEIC gain map -> 32-bit linear TIFF
Apple HEIC gain map -> Ultra HDR JPEG
Apple JPEG gain map -> Ultra HDR JPEG
Ultra HDR JPEG      -> 32-bit linear TIFF
HDR + SDR pair      -> Ultra HDR JPEG
```

Acceptance:
- [ ] Explicit conversion matrix.
- [ ] No silent loss of unsupported metadata.
- [ ] Fidelity metrics for each supported conversion.
- [ ] Clear warnings for lossy conversions.

### R2 — v0.2 release gate
- [ ] Apple 0.1.x regression suite remains green.
- [ ] Backend-neutral architecture documented.
- [ ] libvips/libultrahdr support documented by version.
- [ ] ISO/Ultra HDR fixtures/tests public where licensing allows.
- [ ] Generalized color tests pass.
- [ ] Gain-map generation numerically validated.
- [ ] Cross-format conversions have acceptance evidence.
- [ ] Installed-package smoke tests pass.

## v0.3.x — Advanced production workflows

### P3.1 — Multichannel/color gain maps
### P3.2 — Registration and alignment
### P3.3 — Batch workflows
### P3.4 — Fidelity and validation
### P3.5 — Performance
### P3.6 — Distribution and Homebrew

Detailed goals include per-channel gain preservation, SDR/HDR alignment, deterministic batch processing, stronger numerical/perceptual validation, reduced full-frame copies, parallelism where safe, a Homebrew tap, and evaluation of precompiled native components.

## 1.0 direction

Luvix 1.0 should provide a stable documented CLI for:
- format detection
- inspection
- component extraction
- rebuild/encoding
- HDR reconstruction
- gain-map generation
- cross-format conversion
- high-precision raster export
- generalized color management
- strong validation
- stable machine-readable output contracts
- reproducible installation

The exact 1.0 format matrix will be determined by evidence gathered through 0.x releases.

## Backlog

- HLG-specific workflows.
- AVIF/JXL and other HDR containers when ecosystem support warrants.
- Tone-mapping utilities.
- GUI/front-end possibilities.
- Plugin architecture for optional processing.
- Trinity-specific color correction as an optional module, never core HDR I/O.
- Cloud publishing workflows.
- More extensive metadata preservation/editing.
- Windows/Linux-native alternatives for Apple-specific workflows.

Backlog items do not override the active release.

## Explicit non-goals / constraints

- Never silently crop, rotate, resample, gamut-map, or tone-map.
- Never label pixels with an incompatible ICC/profile.
- Never call inherently lossy encoding non-destructive.
- Never commit private photos/GPS metadata merely to make tests pass.
- Never bundle proprietary profiles without redistribution rights.
- Keep libvips/libultrahdr optional for Apple workflows unless explicitly changed.
- Never assume all gain maps are monochrome.
- Never assume all HDR images use Display P3.
- A milestone is not complete until verification evidence exists.

## Decision log

- **2026-10-09:** Establish Apple gain-map HEIC inspect/extract/rebuild/validate before broader formats.
- **2026-10-09:** Prioritize 32-bit linear and 16-bit PQ TIFF before orientation UX refinement.
- **2026-10-09:** Treat primaries and transfer functions as separate concerns.
- **2026-10-09:** Keep Trinity-specific correction outside core HDR I/O.
- **2026-10-10:** Validate 32-bit linear TIFF as the primary Photoshop HDR editing master.
- **2026-10-10:** Numerically validate 16-bit PQ against the linear reference.
- **2026-10-10:** Use compatible external PQ ICC until a redistributable implementation is verified.
- **2026-10-10:** Rename Gaincraft to Luvix before first PyPI publication.
- **2026-10-10:** Use GitHub Actions + PyPI Trusted Publishing for releases.
- **2026-10-11:** Make `ROADMAP.md` the shared engineering ledger and source of truth.
- **2026-10-11:** Keep the 0.1.x line focused on Apple-native source formats.
- **2026-10-11:** Make v0.2.x the generalized libvips/libultrahdr/color/gain-map-generation phase.
- **2026-10-11:** Preserve future bidirectional workflows: gain-map -> HDR and SDR+HDR -> gain map.

## Progress protocol

1. Start every Luvix work session by reading `ROADMAP.md`.
2. Check repository branch/status and run the existing relevant tests.
3. Identify the active release and earliest incomplete slice.
4. Work only on that slice unless a blocker or explicit priority change occurs.
5. If priorities change, update this roadmap first.
6. Add/update tests with implementation.
7. A checked item requires verification evidence.
8. Keep private fixtures outside the public repository.
9. Run Ruff, formatting, pytest, lock validation, and relevant native/integration tests.
10. Record evidence, blockers, decisions, and the exact next action here.
11. Keep changes reviewable with Git.
12. Do not merge, tag, or publish until the release gate is satisfied.
