 # Assignment 2: Image Processing and Pyramid Blending

**Individual** · **100 points**

A2 develops student-owned filtering, enhancement, pyramids, and blending. Task details and points are in `A2.ipynb`; installation and general workflow are in the repository README.

## A2 workflow

```bash
conda activate cs5243
jupyter lab /path/to/workspace/A2/A2.ipynb
python /path/to/workspace/common-setup/scripts/validate_submission.py --assignment A2 --preflight
```

Implement reusable graded functions in `src/student_code.py`. Use the notebook for experiments, artifacts, and analysis. Execute it, export `A2.html`, validate, and package with the commands in Section 10.

## Artifact formats

- `experiment_metrics.csv`: cumulative long-form records with `experiment, method, condition, metric, value, units`. Additional useful columns are allowed. Append later finite-valued records without deleting earlier experiments.
- `pyramid_metrics.json`: `levels` (integer level count), `level_shapes` (list of per-level shapes, finest first, each `[H, W]` or `[H, W, C]`), `reconstruction.max_abs_error`, `reconstruction.mean_abs_error`, and `reconstruction.dtype`. Also record `source_image` (the file name the saved pyramid was built from). Additional diagnostic keys are allowed.

## Mathematical contracts

- `convolve2d_manual` performs true mathematical convolution, including spatial reversal of the odd 2-D kernel.
- Its `reflect` border is NumPy `reflect`/OpenCV `BORDER_REFLECT_101`; `edge` repeats the boundary value; and `constant` pads with zero.
- `gaussian_kernel` requires a positive odd integer size and positive sigma.
- `sharpen_image` requires nonnegative amount and positive sigma and must not clip its float32 result. It computes `image + amount * (image - blur)`, where `blur` is a Gaussian blur of the given sigma, so `amount = 0` returns the input unchanged and the output is linear in `amount`. Choose the Gaussian support yourself and state your choice; a reasonable convention is `max(3, 2 * ceil(3 * sigma) + 1)`. Grading checks the unsharp structure, not one exact kernel size.
- Noise inputs are normalized float images. Gaussian sigma must be nonnegative; impulse probability must be in `[0,1]`; all randomness must come only from the supplied generator.
- `apply_gamma` computes `output = image ** gamma` on normalized floating-point values. Gamma below 1 brightens; gamma above 1 darkens.
- In `laplacian_pyramid_blend`, mask 0 selects `image_a`, mask 1 selects `image_b`, and intermediate values blend between them.
- `add_impulse_noise` selects each spatial pixel independently with the requested probability using the supplied generator. A selected pixel becomes 0 or 1 with equal probability, and all channels receive the same impulse.
- `normalize_contrast` computes both percentiles jointly over every image value and channel, then applies one global affine mapping: the lower value maps to 0, the upper to 1, and values outside that interval are clipped. Require `0 <= low < high <= 100`; equal computed percentile values raise `ValueError`.
- `histogram_equalize_gray` accepts only 2-D `uint8`, uses 256 bins, subtracts the first nonzero CDF value, maps the CDF to the full uint8 range with NumPy nearest-even rounding (`np.rint`), and returns a constant image unchanged.

Pyramids contain exactly `levels` float32 arrays in finest-to-coarsest order. Reduction uses Gaussian prefiltering and ceiling-halving, so `(H, W)` becomes `((H + 1) // 2, (W + 1) // 2)`; `cv2.pyrDown` is approved. Expansion must target the recorded finer shape; `cv2.pyrUp` or an equivalent Gaussian expansion is approved. Calling a library routine that constructs an entire pyramid or blend is not allowed. Equivalent documented border behavior and harmless floating-point differences are accepted.

`data/images/` includes four aligned blend pairs, one of which ships with two masks, giving five mask geometries so blending experiments are not limited to one seam: `blend_left.png`/`blend_right.png` with `blend_mask.png` (soft vertical seam) or `blend_mask_spot.png` (circular seam), `blend2_left.png`/`blend2_right.png` with `blend2_mask.png` (diagonal seam), and two pairs of real fruit photographs with hard-edged (non-feathered) masks — `blend3_left.png`/`blend3_right.png` with `blend3_mask.png` (hard vertical seam) and `blend4_left.png`/`blend4_right.png` with `blend4_mask.png` (hard circular seam), credited in `data/ATTRIBUTION.md`. The hard real-photo masks make the contrast obvious between the two blending methods: direct blending (splicing) leaves a visible seam that Laplacian pyramid blending visibly smooths. See `metadata/assets.json` for the full grouping.

## Public tests

```bash
pytest A2/tests_public -q
```

Skipped implementation tests are expected in the untouched starter. Applicable tests should pass after implementation; public tests do not guarantee full correctness. Use only the public tests distributed here.

## Official resources

These references explain the relevant tools and APIs. They do not prescribe solutions to the assignment.

- NumPy: [array operations](https://numpy.org/doc/stable/reference/routines.array-manipulation.html), [padding](https://numpy.org/doc/stable/reference/generated/numpy.pad.html), and [random generators](https://numpy.org/doc/stable/reference/random/generator.html)
- OpenCV: [filtering](https://docs.opencv.org/4.x/d4/d86/group__imgproc__filter.html), [border modes](https://docs.opencv.org/4.x/d2/de8/group__core__array.html), [bilateral filtering](https://docs.opencv.org/4.x/d4/d86/group__imgproc__filter.html), [histograms and CLAHE](https://docs.opencv.org/4.x/d6/dc7/group__imgproc__hist.html), and [pyramids](https://docs.opencv.org/4.x/d4/d1f/tutorial_pyramids.html)
- scikit-image: [image metrics](https://scikit-image.org/docs/stable/api/skimage.metrics.html)
- Matplotlib: [`imshow`](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.imshow.html)
- Pandas: [`DataFrame.to_csv`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html)
- Python: [`json.dump`](https://docs.python.org/3/library/json.html#json.dump)

Most distributed A2 media are course-staff-generated CC0 assets; the `blend3_*`/`blend4_*` real-photo pairs are retained course-legacy teaching images (see `data/ATTRIBUTION.md`).
