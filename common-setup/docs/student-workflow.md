# Student workflow and troubleshooting

The root [README](../README.md) is the canonical quick start. This page explains the workflow in more detail.

## Getting the course materials

Canvas distributes two kinds of ZIP files in a two-step workflow: a one-time `cs5243-common-setup.zip` (shared `cs5243/` package, `docs/`, `scripts/`, `student/`, and course-wide `config/` files) and a lean, self-contained, per-assignment `cs5243-A#.zip` released for each assignment. First create one workspace folder yourself, with any name (`<WORKSPACE>` below — the root README uses `Assignments/` as its example). Extract the common-setup ZIP once, directly into `<WORKSPACE>`, producing `<WORKSPACE>/common-setup/`. For every later assignment, extract that assignment's ZIP directly into the *same* `<WORKSPACE>` folder — it produces a self-contained top-level folder named for the assignment (e.g. `<WORKSPACE>/A1/`, including its own `data/` assets and `config/A1.yml`) as a direct sibling of `common-setup/`, not nested inside it. Do not re-extract the common-setup ZIP. See the root README's "Getting the course materials" section for the full walkthrough.

## Supported systems

Windows 11, Apple Silicon macOS, and Ubuntu are supported through the same `environment.yml`, environment name `cs5243`, and Python 3.11. Keep the workspace folder in a locally available, user-writable location. Quote paths that contain spaces.

## Files and paths

- Launch JupyterLab at `<WORKSPACE>` so both `common-setup/` and every `A#/` notebook are visible in one session.
- Use `pathlib` and course/environment discovery (`cs5243.data.find_repository_root` for `common-setup/`, `cs5243.data.find_course_root` for `<WORKSPACE>`); do not paste `/Users/...`, `/home/...`, or `C:\Users\...` paths into submitted work.
- Store datasets outside an assignment submission folder.
- Put your Python source in the assignment's `src/` folder and only selected grading evidence in `outputs/`.

## HTML, validation, and packaging

At the start of an assignment, run validation with `--preflight`. It checks repository/package access, assignment/environment identity, starter signatures, and checksummed assets without requiring completed implementations, final outputs, or filled identity fields.

Run all notebook cells interactively, save, and then export HTML without `--execute`. This avoids silently changing results during export. From the command line, use `--template classic` so the notebooks' figure descriptions are preserved in HTML. Full validation checks structure and safety but does not execute or grade algorithms.

Errors block packaging. Warnings identify items to review, such as placeholder text, machine-specific paths, hidden content, or unusually large files. Resolve warnings when applicable and rerun validation.

Packaging creates one Canvas folder and includes only explicitly allowed notebook, HTML, source, output, and report files. Always inspect the ZIP yourself.

## External resources and assistance

Generative AI tools may be used for conceptual clarification, debugging assistance, code suggestions, and help interpreting documentation. In Section 0, disclose every meaningful use and briefly state how it contributed; write `None` if there were none. You remain responsible for understanding, testing, and explaining all submitted work. AI may not replace your own experimental analysis, failure analysis, reflection, or interpretation, and it may not bypass a required implementation. You may be asked to explain selected work.

## Additional packages

Do not make required work depend on a package absent from `environment.yml` unless approved in writing. If an approved experiment uses an extra package, document it, keep required results reproducible in the standard environment, and do not modify the shared environment file yourself.

See [troubleshooting.md](troubleshooting.md) for common failures.
