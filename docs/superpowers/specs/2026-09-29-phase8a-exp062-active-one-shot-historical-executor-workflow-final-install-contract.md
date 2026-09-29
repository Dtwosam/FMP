# Phase 8A — EXP-062 Final Active Executor Workflow Install Contract

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY FINAL INSTALL CONTRACT / ACTIVE WORKFLOW ABSENT  
**Decision:** DEC-396  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-395

DEC-396 consumes the concrete DEC-395 runtime-evidence freeze and authorizes only a
new final workflow-install source contract. It intentionally uses a distinct module
from the older DEC-360 install contract so historical source pins remain immutable.

DEC-396 pins:

- DEC-395 runtime-freeze blob:
  `a941ec672cc5249401f4208435f0de3c6e6f6a4c`;
- DEC-395 runtime-freeze fingerprint:
  `9c44d78327d4467d4eb0717ae28d410f2543476b518eeecfea9bb2db9ba2682c`;
- dormant executor template blob:
  `51ce87584369be957482460d81649adb1cb9f05d`;
- exact DEC-392 proof evidence transitively through DEC-395;
- zero historical-result attempts and target run #2 / attempt 1.

The four predecessor source-only gates remain true and DEC-396 adds only the final
install-contract source gate. Actual workflow-install authorization, installed
state, executor availability, historical dispatch, execute mode, reserved data,
candidate/promotion, Phase 8B, demo/live, real-money, and trading remain false.

Next gate: read-only current-main final workflow-install preflight.
