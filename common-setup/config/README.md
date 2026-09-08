# Public validation contracts

`schema.yml` documents the supported keys, including optional image, numeric-array, and ASCII-PLY validation. Each assignment's active Version 1.0 contract lives beside that assignment's own files, at `<WORKSPACE>/A#/config/A#.yml` (a sibling of `common-setup/`, not nested inside it), rather than here. Those per-assignment contracts control structural, identity, version, artifact, file-safety, notebook, and packaging checks; A1-A5 also define non-executing preflight asset/signature checks and a flexible single extension artifact.

Validation never executes student code. Errors block packaging; warnings remain visible in `validation-report.json` for student and grader review.
