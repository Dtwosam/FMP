# Phase 8A — EXP-062 Workflow Install-Execution Preflight Proof Runtime Freeze

**Date:** 2026-09-29  
**Status:** CONCRETE RUNTIME-EVIDENCE BINDING / NO INSTALL OR DISPATCH  
**Decision:** DEC-395  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-392, DEC-393, DEC-394

DEC-395 binds the real successful DEC-392 merged-main workflow
install-execution-preflight proof and deterministically replays the DEC-393 review
plus DEC-394 freeze.

## Concrete proof evidence

- merged main head: `dc1a2cfd5a11595f2ad943277f79e043625bd3e9`
- proof run: `36568114050` / run #1 / attempt 1
- proof job: `109405007879`
- proof artifact: `11032917944`
- artifact ZIP / GitHub digest SHA-256:
  `f8119b5845f9ba824caebaa48012d19f41668767b71773d94d305f4f78f5c103`
- raw DEC-391 preflight SHA-256:
  `a9fd545df8c2dc2f05813df5e827f5e9685d5c7c6ea521ca07b6a709ca188601`
- canonical DEC-391 preflight SHA-256:
  `bd91ae808a6ed1fdc24c4fb5b64b8744a13a53fbe3a6d58d0f5062ba26eea78b`
- DEC-394 deterministic freeze fingerprint:
  `9357b1c6591a801237acacf7cb7eab1f5302608770ad7b3033566bda39cb3548`

DEC-395 also pins the exact DEC-393 reviewer and DEC-394 freeze-builder source
blobs and the DEC-334 terminal-review contract.

All four source-only gates remain true. The active executor workflow path remains
absent. Actual workflow-install authorization, installed state, historical executor
availability, historical-result dispatch, execute mode, rerun/retry/replacement,
reserved 2023-2026 access, candidate compilation/promotion, Phase 8B, demo,
broker/live, real-money, and trading remain false.

The next safe gate is a source-only active executor workflow install contract. DEC-395
does not install the workflow and does not add an install or dispatch command.
