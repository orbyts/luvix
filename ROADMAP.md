# Luvix Roadmap

Status: active engineering ledger.

This document is the source of truth for Luvix development. A completed item requires evidence, not merely implemented code. At the beginning of each work session, identify the active release and earliest incomplete slice, verify repository state, and continue from the recorded next action.

If priorities change, update this roadmap first.

## Vision

Luvix is an HDR interoperability toolkit for photographers: a Swiss Army knife for inspecting, splitting, reconstructing, generating, validating, and converting HDR/gain-map representations when capture and editing applications do not exchange them correctly. It bridges representations without replacing the professional editor or duplicating workflows already handled correctly by existing tools.

The long-term goal is a common workflow above native and third-party imaging backends such as Apple ImageIO/Core Image, libvips, and libultrahdr.

Luvix should eventually support both directions:

```text
gain-map image -> components -> reconstructed HDR -> editable raster
SDR + HDR -> generated gain map -> gain-map image
```

The public CLI should describe operations rather than backend implementation details. Luvix is not a general-purpose RAW developer or photo editor. RAW/DNG interoperability is considered only if a specific, demonstrated HDR compatibility gap warrants it; speculative RAW ingestion is not a roadmap milestone.

## Current position

Release: **v0.1.4 (release candidate)**

Theme: Apple iPhone HDR gain-map interoperability across HEIC and JPEG.

Active slice: **R1.4 — release validation**.

Verified evidence (through 2026-10-12):
- Genuine iPhone 16 Pro HEIC/JPEG HDR gain-map captures characterized; sanitized public candidates retain L008 gain maps, Display P3, orientation 6, and distinct SDR/HDR ImageIO decodes.
- HEIC and JPEG inspect, inspect-hdr, extraction, rebuild, validation, and 32-bit linear TIFF paths work on the real fixtures.
- Extraction normalizes orientation 6 into upright 4284x5712 base and 2142x2856 gain-map PNGs; rebuild restores 5712x4284 / 2856x2142 raw geometry and orientation 6.
- Geometry mismatch is rejected; semantic/color/exposure edits are intentionally not policed.
- JPEG-derived 16-bit PQ TIFF writes 16-bit RGB, orientation 6, and a supplied compatible `P3 PQ` ICC.
- HEIC rebuild regression validates structurally with Display P3 and orientation preserved.
- Internal fidelity baselines exist for lossy rebuild regression, but fidelity does not gate user edits.
- 71 automated tests passed after orientation/geometry implementation; Ruff, formatting, and uv lock checks passed.

Next action:
1. Apply v0.1.4 release-prep updates, run public fixture/native integration tests, and visually smoke-test the JPEG-derived PQ TIFF in Photoshop if not already done.
2. Run Ruff, formatting, pytest, lock, build, Twine, and wheel-resource checks.
3. Commit/push `feature/apple-jpeg`, run GitHub CI, merge to `main`, tag/release v0.1.4, and verify PyPI plus an installed-package smoke test.
4. Advance the ledger to **v0.1.5 / B1 — batch input discovery and contract**.

Blockers: none known. The external P3 PQ ICC used for validation must not be committed or packaged.

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
Status: released. GitHub PR #5 merged with 12 passing checks; installed PyPI v0.1.3 verified on macOS with `doctor`, HEIC `inspect`, and `inspect --compact`.

- [x] CHANGELOG documents v0.1.3.
- [x] Local release checks passed (61 tests, Ruff, lock).
- [x] GitHub CI passed and changes merged into `main`.
- [x] GitHub v0.1.3 release and PyPI installation verified by installed CLI.

Evidence note: artifact build metadata and wheel-resource verification for this particular release were not independently supplied in this conversation; do not infer them from the successful installed smoke test.

## v0.1.4 — Apple JPEG gain maps

Theme: complete the Apple-native 0.1.x foundation across Apple's HEIC/JPEG gain-map containers.

### A1 — Apple JPEG discovery
- [x] Genuine iPhone HEIC/JPEG gain-map fixtures obtained and sanitized for public regression use.
- [x] JPEG ImageIO auxiliary layout characterized: L008 2856x2142; HEIC comparison L008 2856x2142.
- [x] Display P3, orientation 6, and distinct SDR/HDR decode behavior verified.
- [x] Queried GPS/capture-time metadata removed from public fixture candidates; private originals remain ignored.

### A2 — Apple JPEG inspection
- [x] `inspect` recognizes the real Apple JPEG gain map.
- [x] `inspect-hdr` produces distinct SDR/HDR renders with extended-linear values above 1.0.
- [x] Public fixture integration coverage is included for macOS.

### A3 — Apple JPEG extraction
- [x] Extract editable SDR base and gain map.
- [x] Manifest records source orientation and editing geometry.
- [x] Base and gain map are exported in the same upright editing orientation.

### A4 — JPEG/HEIC rebuild and geometry contract
- [x] Container-aware JPEG rebuild implemented; output is genuine JPEG with readable HDR gain map.
- [x] HEIC rebuild regression remains valid.
- [x] Rebuild checks supplied component dimensions/decodability and reverses orientation normalization.
- [x] Real orientation-6 JPEG and HEIC extract -> rebuild -> validate tests passed.
- [x] Independently rotated/resized component geometry is rejected.
- [x] Same-geometry artistic/color/exposure/pixel edits are intentionally the user's responsibility.
- [x] Full-resolution HDR fidelity baseline retained as internal engineering evidence only.
- [ ] Avoiding unnecessary compressed-base re-encoding remains a future optimization, not a v0.1.4 blocker.

### A5 — HDR reconstruction and TIFF export
- [x] JPEG HDR reconstruction produces extended-linear Display P3 values above 1.0.
- [x] JPEG -> 32-bit linear TIFF writes embedded ICC and source orientation metadata.
- [x] JPEG -> 16-bit PQ TIFF writes 16-bit RGB, source orientation, and supplied compatible P3 PQ ICC.
- [x] Existing HEIC 32-bit linear and 16-bit PQ paths remain covered by the 0.1.x regression suite.
- [ ] Final Photoshop visual smoke check for the JPEG-derived PQ TIFF, if not already completed.

### A6 — Apple backend cleanup
- [x] HEIC/JPEG destination selection is encapsulated in the Apple ImageIO backend.
- [x] Existing HEIC behavior is preserved by regression validation.
- [x] Current supported Apple gain-map contract is explicit: ImageIO-readable HEIC/JPEG with Apple HDR auxiliary gain map; tested fixtures use L008 and Display P3.

### R1.4 — Release
Status: active.

- [ ] Public sanitized HEIC/JPEG fixtures committed with fixture documentation.
- [ ] Native macOS fixture integration tests pass from the committed checkout.
- [ ] README, user guide, changelog, and roadmap reflect v0.1.4 behavior.
- [ ] Ruff, format, pytest, and `uv lock --check` pass.
- [ ] sdist/wheel build and Twine metadata checks pass.
- [ ] All required Swift backend resources are present in the wheel.
- [ ] Proprietary/reference ICC files are absent from Git and distributions.
- [ ] GitHub CI passes and changes merge into `main`.
- [ ] GitHub v0.1.4 release publishes successfully to PyPI.
- [ ] Installed PyPI v0.1.4 passes version, doctor, HEIC/JPEG inspect, extraction/rebuild, and TIFF smoke tests.

## v0.1.5 — Batch Apple HDR workflows

Theme: apply the established single-image Apple HEIC/JPEG interoperability operations to collections, without changing HDR/color algorithms.

### B1 — Input discovery and batch contract
- [ ] Support explicit files and directory inputs; define recursion, extension filtering, and unsupported-file policy.
- [ ] Deterministic output naming and directory layout; refuse overwrite by default.
- [ ] Document planned CLI syntax before implementation.

### B2 — Batch component extraction
- [ ] Extract SDR base, gain map, and manifest per supported image.
- [ ] Isolate per-file errors; continue when configured.
- [ ] Preserve the single-image extraction and metadata contracts.

### B3 — Batch 32-bit linear HDR TIFF conversion
- [ ] Export 32-bit float TIFF for HEIC and JPEG sources.
- [ ] Preserve per-file orientation, color interpretation, and ICC behavior.
- [ ] Verify output metadata and numerical values against single-image export.

### B4 — Batch 16-bit PQ TIFF conversion
- [ ] Support explicit reference white and compatible PQ ICC configuration.
- [ ] Validate color-space/profile compatibility per input; fail safely when mismatched.
- [ ] Verify parity with single-image PQ output.

### B5 — Batch rebuild and validation
- [ ] Define safe source/component pairing and manifest discovery.
- [ ] Rebuild supported Apple gain-map images without cross-pairing components.
- [ ] Validate structure and record per-file results.

### B6 — Reporting and reliability
- [ ] Human-readable progress and machine-readable JSON summary.
- [ ] Deterministic success/failure exit semantics.
- [ ] Tests for empty inputs, mixed formats, collisions, interrupted runs, and partial failures.

### R1.5 — Release
- [ ] Batch integration tests pass with HEIC and JPEG fixtures.
- [ ] User guide documents batch commands and output layout.
- [ ] CI, package build, and independent installed-PyPI smoke test pass.

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
### P3.3 — Advanced batch orchestration
### P3.4 — Fidelity and validation
### P3.5 — Performance
### P3.6 — Distribution and Homebrew

Detailed goals include per-channel gain preservation, SDR/HDR alignment, advanced cross-backend batch orchestration beyond v0.1.5, stronger numerical/perceptual validation, reduced full-frame copies, parallelism where safe, a Homebrew tap, and evaluation of precompiled native components.

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

### Conditional research — camera-neutral scene-linear interchange

**Status:** unscheduled feasibility backlog; not part of v0.1.4, v0.1.5, or committed v0.2.x scope.

An independent RAW/film-simulation research project will test whether standardized, camera-characterized, scene-referred RGB intermediates (candidate: half-float or float32 OpenEXR) can be produced reproducibly from different camera sources. The useful output format, color space, exposure normalization and precision must be determined empirically. Luvix may later accept or emit such a representation **only where it solves a demonstrated HDR interoperability gap**. This does not authorize RAW demosaicing, general RAW development, or film simulation inside Luvix.

Decision gate before promotion into an active release:
- [ ] Independent research identifies a concrete downstream interchange problem not adequately solved by existing tools.
- [ ] Candidate intermediate(s) and color/metadata contract are documented and numerically validated.
- [ ] Scope remains an HDR/interchange adapter, not a RAW development engine.
- [ ] Release assignment, acceptance criteria and tests are approved and recorded here.


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
- Do not implement RAW development, demosaicing, lens corrections, or general retouching; evaluate RAW/DNG only if a specific HDR interoperability problem is demonstrated.
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

- **2026-10-11:** Define Luvix by HDR interoperability rather than RAW development or general photo editing; investigate RAW/DNG only when a concrete compatibility gap is found.
- **2026-10-11:** Add v0.1.5 for batch Apple HEIC/JPEG extraction, TIFF conversion, rebuild, and validation.
- **2026-10-11:** Record real iPhone HEIC/JPEG discovery evidence; keep private originals excluded and audit sanitized public fixture candidates before committing.

- **2026-10-12:** Record camera-neutral scene-linear EXR (half/full float) as a conditional, unscheduled interoperability feasibility item; keep RAW normalization and AI film research separate pending evidence.
- **2026-10-12:** Define v0.1.4 rebuild validation as a simple geometry/decodability contract; semantic image edits remain the user's responsibility.
- **2026-10-12:** Normalize extracted base and gain map to the same upright editing orientation and reverse that transform on rebuild.
- **2026-10-12:** Keep HDR fidelity metrics as internal regression evidence rather than a user rebuild gate.

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
