# Windows 11 setup notes

Follow the root [first-time setup](../README.md#first-time-setup) using current Miniforge for Windows. Run commands in Miniforge Prompt or PowerShell after Conda initialization.

- Keep the repository in a user-writable folder and mark it “Always keep on this device” if OneDrive Files On-Demand is enabled.
- Quote `<COURSE_ROOT>` because Windows course paths commonly contain spaces.
- If `conda` is not recognized, reopen Miniforge Prompt rather than manually editing `PATH`.
- Use `pathlib` in Python; do not submit drive-specific paths such as `C:\Users\...`.

The everyday workflow, update command, export command, and Canvas checklist are centralized in the root README. See [troubleshooting](troubleshooting.md) before changing channels or installing extra packages.
