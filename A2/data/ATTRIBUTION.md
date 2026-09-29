# Attribution and license

Most A2 assets (`test_pattern_gray.png`, `color_scene.png`, `gaussian_noisy.png`, `impulse_noisy.png`, `blend_left.png`, `blend_right.png`, `blend_mask.png`, `blend_mask_spot.png`, `blend2_left.png`, `blend2_right.png`, `blend2_mask.png`, `exposure_under.png`, `difficult_high_frequency.png`) were generated programmatically by CS 5243 course staff and are released under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).

The `blend3_*` and `blend4_*` assets are center-cropped from two real photograph pairs retained from this course's own prior offerings — the classic apple/orange pyramid-blending demonstration in the style of Burt and Adelson (1983), used in image-processing courses for decades. These specific image files (`apple.png`, `orange.png`, `apple-orange-mask.png`, `apple2.png`, `orange2.png`, `apple2-orange2-mask.png`) were carried forward from the course's legacy assignment materials; course staff did not independently trace their original photographer or first publication, so no external license or source URL is claimed here. They are used for the same continued internal teaching purpose as in prior semesters of this course, not redistributed as an independently licensed dataset.

| Asset | Source photo | Notes |
|---|---|---|
| `blend3_left.png` | `apple.png` | Classic course apple/orange demo pair; paired hard vertical mask. |
| `blend3_right.png` | `orange.png` | Same pair as above. |
| `blend4_left.png` | `apple2.png` | Second course demo pair (close-up apple/orange); paired hard circular mask. |
| `blend4_right.png` | `orange2.png` | Same pair as above. |

`blend3_mask.png` and `blend4_mask.png` are the paired hard-edged masks (`apple-orange-mask.png`, `apple2-orange2-mask.png`) carried forward with their photo pairs — not procedurally generated, and deliberately hard-edged (not feathered) so that direct blending (splicing) shows an obvious seam that Laplacian pyramid blending then visibly smooths.

Source photographs and masks are stored unmodified in `instructor/A2/reference/real_photo_sources/` (instructor-only) and are resized/cropped to the shared 385×257 blend-pair canvas by `instructor/A2/reference/generate_assets.py::load_real_photo` and `::load_real_mask`.

If you can identify the original photographer/source for `apple.png`, `orange.png`, `apple2.png`, or `orange2.png`, please update this file with proper attribution.
