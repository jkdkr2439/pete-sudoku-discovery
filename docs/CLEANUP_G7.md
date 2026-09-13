# Repository Cleanup — G7

Date: 2026-09-14

## Before

- runtime/: 182.33 MB at first audit; later growth came from continuous physical and Sandbox journals.
- tools/_vendor/: 83.68 MB of reproducible imageio-ffmpeg binaries.
- ignored Python and pytest caches were present.
- the scheduler had reached 19 solved worlds before the final safe-boundary stop.

## Preserved evidence

- Original empty-to-solved MP4 and manifest remain tracked.
- One complete Sandbox world trace is preserved as artifacts/proof/PETE_SANDBOX_TRACE_G6_20260914.jsonl.
- Its manifest records the record count, first/last operation, attempts, authoritative result and SHA-256.
- Architecture, brainstorm, plans, checkpoints and design-loop history remain tracked.

## Cleanup rule

Runtime journals, browser profiles, screenshots, caches and downloaded tool binaries are regenerated outputs. They do not belong in the portable repository. Proof-video dependencies are now declared under the optional proof dependency group.
## Result

- Removed: 269.5 MB.
- Preserved trace: 104 records, BEGIN through COMPLETE, 51 attempts, 45,542 bytes.
- Trace SHA-256: 69d738b1234782480cda3bf0d6b3901d180d081508f6cbc941d4143d284df0db.
- Test suite: 12 passed.
- Boundary audit: PASS.
- Proof-tool syntax and pyproject metadata: PASS.
- Cache-free test mode: PASS.
