# Apple HDR integration fixtures

These are mundane real-world iPhone captures contributed for Luvix interoperability testing.

- `iphone_hdr_heic.heic`: Apple HDR gain-map HEIC.
- `iphone_hdr_jpeg.jpg`: Apple HDR gain-map JPEG.

Before inclusion, queried GPS and capture-time metadata were removed from the sanitized copies. The fixtures retain the image, gain-map, color, and orientation information required to exercise Luvix. Private originals remain excluded by `.gitignore`.

The repository license applies to these contributed test fixtures. Do not replace them with private photographs or files containing precise location metadata.

Current expected characteristics include Display P3, EXIF orientation 6, a 5712x4284 stored base, and a 2856x2142 L008 gain map. Tests should prefer behavioral assertions over treating these exact dimensions as a universal Apple format contract.
