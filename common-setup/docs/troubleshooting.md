# Troubleshooting

## Conda cannot solve or downloads fail

Update Conda in its base environment, reopen the terminal, and retry. Confirm the terminal is online and that institutional security software is not intercepting package downloads. Do not solve the problem by adding arbitrary channels.

## `cs5243` cannot be imported

Activate the environment and reinstall the local package:

```bash
conda activate cs5243
python -m pip install --editable "<WORKSPACE>/common-setup"
```

## Jupyter opens in the wrong folder

Launch it explicitly with `jupyter lab "<WORKSPACE>"` (the folder containing `common-setup/` and each `A#/` as siblings), so both the shared package and the assignment notebooks are visible in one session. The validation and packaging scripts discover their environment and workspace roots from their own location and can be invoked from any directory.

## HTML is missing or stale

Run all cells in Jupyter, save the notebook, then export without `--execute`:

```bash
jupyter nbconvert --to html --template classic "<WORKSPACE>/A#/A#.ipynb" --output A#.html
```

Open the resulting HTML and compare its visible outputs with the notebook. The `classic` template preserves the figure descriptions already attached to assignment outputs.

## Apple Silicon torchvision/JPEG warning

Older packages from PyTorch's retired Conda channel can emit a warning that torchvision's optional native image extension cannot find a JPEG library. Version 1.0 uses one coherent conda-forge channel so new environments avoid that mixed-channel combination. If an older environment still warns but `verify_environment()` succeeds, update it using the root README. Pillow and OpenCV are the supported image I/O paths for assignments; do not add a platform-specific JPEG pin.

## Validation reports an absolute path

Replace user- or drive-specific paths with `pathlib` paths derived from the repository or dataset root. The check is a warning because prose may legitimately discuss such a path.

## Packaging stops

Open `validation-report.json`, fix every error, rerun validation, and package again. Warnings do not block packaging but should be reviewed.
