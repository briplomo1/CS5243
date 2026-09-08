# A1 deterministic dataset

This small dataset supports controlled experiments with channel order, color, datatype, orientation, aspect ratio, and video. All media are generated deterministically by course staff; no external media are used.

| Asset | Shape / format | Purpose |
|---|---:|---|
| `images/channel_order.png` | 300 × 720, RGB uint8 | Makes RGB/BGR mistakes immediately visible |
| `images/color_shapes*.png` | 400 × 640, RGB uint8 | Exactly aligned normal, dim, and warm color-rule trials |
| `images/intensity_ramp_16bit.png` | 256 × 512, grayscale uint16 | Datatype and range investigation |
| `images/portrait_scene.png` | 540 × 360, RGB uint8 | Portrait-oriented crop and layout case |
| `images/wide_scene.jpg` | 300 × 720, RGB uint8 JPEG | Wide aspect ratio and lossy encoding case |
| `video/moving_shapes.mp4` | 320 × 240, 48 frames, 12 fps | Four-second video sampling and transformation |

`metadata/color_regions.yml` records generation parameters and exact test regions. `SHA256SUMS` supports integrity checks. Run `a1_tools.verify_asset_checksums()` rather than editing these files.

The complete distributed dataset is intentionally well below the Canvas artifact limit.
