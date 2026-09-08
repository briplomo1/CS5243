# Apple Silicon macOS setup notes

Follow the root [first-time setup](../README.md#first-time-setup) using the arm64 Miniforge installer.

- Confirm `uname -m` reports `arm64` and `conda info` reports `osx-arm64`.
- Do not mix an Intel/x86_64 Conda installation with an arm64 environment.
- If macOS blocks access to a synced course folder, grant Terminal access in System Settings or work in a locally available user-writable folder.
- If an older environment emits torchvision's optional JPEG warning, follow the update guidance in [troubleshooting](troubleshooting.md); do not add a JPEG pin.

The everyday workflow, update command, export command, and Canvas checklist are centralized in the root README.
