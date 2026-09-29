# Phase 8A — EXP-062 Workflow Install-Activation Preflight Proof Runtime Freeze

**Date:** 2026-09-29  
**Status:** CONCRETE RUNTIME-EVIDENCE BINDING / NO INSTALL OR DISPATCH  
**Decision:** DEC-401  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-398, DEC-399, DEC-400

DEC-401 binds the real successful DEC-398 merged-main workflow
install-activation-preflight proof.

It pins:

- head `9dd433b406bef6dc8660d897ccab5bcb1b0da99b`;
- run `36579901387`, run #1 / attempt 1;
- job `109445012411`;
- artifact `11039017180`;
- artifact/ZIP SHA-256
  `c19012d3e4fc794e40a930e0eac82d799773f6a9050bf56adc75a0b0f2245b85`;
- raw DEC-397 preflight SHA-256
  `8db03c11f255bcc724c4d7c18df7e5a8f539039032dbb5787291ca8810427116`;
- canonical DEC-397 preflight SHA-256
  `229fec80d76273f5320966acb63d0661ff7aa03c04ded8d953bb3e9e3f363ceb`;
- DEC-400 deterministic freeze fingerprint
  `441c508902f816faee66c58768552a7d3ab05f0b145193a3e6349f18c9062808`.

DEC-401 re-runs the merged DEC-399 reviewer and DEC-400 deterministic freeze and
pins their exact source blobs plus the DEC-334 terminal-review contract.

All five predecessor source-only gates remain true. The active executor workflow
path remains absent. Actual workflow-install authorization, installed state,
historical executor availability, historical-result dispatch, execute mode,
rerun/retry/replacement, reserved 2023-2026 access, candidate compilation/promotion,
Phase 8B, demo, broker/live, real-money, and trading remain false.

## Next gate

The next safe gate is a new source-only active executor workflow-install contract.
No workflow installation or historical dispatch is authorized by DEC-401.
