# UTSA CS 5243 Computer Vision Assignments

Course infrastructure and setup for the individual assignments A1-A5. Each assignment's own README and notebook describe what it covers.

## Start here

This course uses two kinds of folders, and it matters which is which:

- **`<WORKSPACE>`** — a folder *you* create, with any name you like (this guide uses `Assignments/` as an example). It holds `common-setup/` and each released `A1/`, `A2/`, ... as **direct siblings** — `common-setup/` is not a parent of the assignment folders, and the assignment folders are not nested inside it.
- **`common-setup/`** — a fixed-name folder produced by extracting `cs5243-common-setup.zip` directly into `<WORKSPACE>`. It holds the shared `cs5243/` package, `docs/`, `scripts/`, `student/`, and course-wide `config/` files. Its name never changes, so paths below spell it out literally as `<WORKSPACE>/common-setup/...` rather than using a placeholder.

### Getting the course materials

Course materials are distributed on Canvas as two kinds of ZIP files, in a two-step workflow:

1. Create one folder anywhere convenient to hold everything for this course — call it `Assignments/` (or any name you like); this is `<WORKSPACE>` below.
2. **`cs5243-common-setup.zip`** — download once, at the start of the course, and extract it directly into `<WORKSPACE>`. Extracting produces `<WORKSPACE>/common-setup/`.
3. **`cs5243-A#.zip`** — download one of these from Canvas as each assignment is released, and extract it directly into the *same* `<WORKSPACE>` folder (not somewhere else, and not into `common-setup/`). Extracting produces a self-contained sibling folder named for the assignment, such as `<WORKSPACE>/A1/`. Repeat for each assignment as it is released, so you end up with `<WORKSPACE>/A1/`, `<WORKSPACE>/A2/`, and so on alongside `<WORKSPACE>/common-setup/`.

Do **not** re-extract `cs5243-common-setup.zip` again after the first time — you already have the shared `cs5243/` package, `docs/`, `scripts/`, `student/`, and course-wide `config/` files, and re-extracting would just overwrite them with identical copies. Each `cs5243-A#.zip` is intentionally lean (only that assignment's files, including its own `config/A#.yml`) and is self-contained, so it always produces a clean top-level `A#/` folder no matter where you extract it — just make sure that's inside `<WORKSPACE>`.

If you obtained the repository by cloning it directly instead of downloading Canvas ZIPs, you already have everything in one place (this repository's root is `<WORKSPACE>`, with `common-setup/` and each `A#/` already laid out as siblings) and can skip this section.

### First-time setup

1. Install a current Miniforge or Conda distribution for your operating system.
2. Open a new terminal and create the one course environment:

   ```bash
   conda env create --file "<WORKSPACE>/common-setup/environment.yml"
   conda activate cs5243
   python -m pip install --editable "<WORKSPACE>/common-setup"
   python -m pytest "<WORKSPACE>/A#/tests_public" -q
   ```

3. Launch JupyterLab at the workspace folder, so both `common-setup/` and every `A#/` are visible in one session:

   ```bash
   jupyter lab "<WORKSPACE>"
   ```

Use the platform guide for [Windows 11](docs/setup-windows-11.md), [Apple Silicon macOS](docs/setup-macos-apple-silicon.md), or [Ubuntu](docs/setup-ubuntu.md) if installation needs platform-specific troubleshooting.

### Everyday assignment workflow

1. Activate the environment: `conda activate cs5243`.
2. Launch JupyterLab with `jupyter lab "<WORKSPACE>"`.
3. Complete the assigned notebook and source files individually — the notebook lives at `<WORKSPACE>/A#/A#.ipynb`.
4. Run `python "<WORKSPACE>/common-setup/scripts/validate_submission.py" --assignment A# --preflight` when starting a substantive assignment.
5. Use workspace-relative paths and keep datasets outside the assignment folder.
6. Restart the kernel, run all cells, inspect the results, and save.
7. Export HTML without re-executing. The `classic` template preserves the figure descriptions used by the assignment notebooks:

   ```bash
   jupyter nbconvert --to html --template classic "<WORKSPACE>/A#/A#.ipynb" --output A#.html
   ```

8. Validate and package from any directory — the scripts live under `common-setup/` while the submission itself lives under the sibling `A#/` folder:

   ```bash
   python "<WORKSPACE>/common-setup/scripts/validate_submission.py" --assignment A#
   python "<WORKSPACE>/common-setup/scripts/package_submission.py" --assignment A#
   ```

The packager stops on validation errors. Warnings remain in the report for review. The predictable output is `LastName_FirstName_A#.zip` beside the assignment directory, containing one folder with the same name.

### Update the environment

When an updated `environment.yml` is published:

```bash
conda activate cs5243
conda env update --name cs5243 --file "<WORKSPACE>/common-setup/environment.yml" --prune
python -m pip install --editable "<WORKSPACE>/common-setup"
python -m pytest "<WORKSPACE>/A#/tests_public" -q
```

Do not create a second course environment unless specifically directed to do so.

## Canvas submission checklist

Open the ZIP before uploading and confirm:

- there is exactly one top-level folder named `LastName_FirstName_A#`;
- the executed notebook and rendered HTML are present;
- `src/` contains your required source files;
- `outputs/` contains only selected figures, tables, or videos;
- `validation-report.json` reports zero errors;
- no datasets, environments, caches, checkpoints, hidden files, or temporary files are present.

A PDF export is not required.

## Course infrastructure rules

- A1-A5 are individual assignments. Research-project policy is outside this repository.
- Required work uses environment version 2026.1. Do not require or depend on additional packages without written approval.
- The environment does not establish a GPU requirement or a CPU-only policy. Generic PyTorch packages may use hardware supported by the student's system and installation.
- Use Pillow or OpenCV for supported assignment image I/O. On some Apple Silicon installations, importing torchvision may emit a harmless optional JPEG-extension warning; see [troubleshooting](docs/troubleshooting.md).
- Generative AI may support conceptual clarification, debugging, code suggestions, and documentation interpretation, but meaningful use must be disclosed in every assignment. Students remain responsible for understanding, testing, and explaining all work. AI may not replace experimental analysis, failure analysis, reflection, or interpretation, and may not bypass required implementations. Students may be asked to explain submitted work.
- Never submit datasets, model caches, environments, or large trained models.

More detail is available in the [student workflow and troubleshooting guide](docs/student-workflow.md).
