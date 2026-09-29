# Phase 8A — EXP-062 Workflow Install-Activation Contract

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY INSTALL-ACTIVATION CONTRACT / ACTIVE WORKFLOW ABSENT  
**Decision:** DEC-396  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-395

DEC-396 consumes the corrected concrete DEC-395 runtime-evidence freeze and
authorizes only the source contract for future activation of the executor workflow
installation path.

It pins:

- DEC-395 runtime-freeze blob:
  `9832ab2381c71c3587314eb9c6f31cb8b286421b`;
- DEC-395 runtime-freeze fingerprint:
  `7b5170f7af52561cd1a7cf78683065ca0ebef59bda2fdb81f25073ef1abced6f`;
- dormant executor template blob:
  `51ce87584369be957482460d81649adb1cb9f05d`;
- the exact DEC-392 proof evidence transitively through DEC-395.

The four predecessor source-only gates remain true and DEC-396 adds only
`active_one_shot_historical_executor_workflow_install_activation_source_authorized=true`.

Actual workflow-install authorization, installed state, executor availability,
historical-result dispatch, execute mode, reserved data, candidate/promotion,
Phase 8B, demo/live, real-money, and trading remain false.

Next gate: read-only current-main workflow install-activation preflight.
