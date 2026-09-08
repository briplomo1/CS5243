# Student-facing conventions

Begin with the `common-setup/README.md`; it is the canonical setup, workflow, packaging, and Canvas checklist.

- A1-A5 are individual assignments.
- Put student-authored Python in each assignment's `src/` folder.
- Put only selected grading evidence in `outputs/`.
- Keep datasets, environments, caches, temporary files, and checkpoints outside the assignment directory.
- Use only approved dependencies for required work.
- Declare external resources and generative-AI assistance in notebook Section 0.

The `student/src/` and `student/outputs/` folders document conventions only; actual work belongs within the assigned `<WORKSPACE>/A#/` folder, a sibling of `common-setup/` (not nested inside it).
