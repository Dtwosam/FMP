# Phase 8A — EXP-062 Installed Executor Dispatch-Preflight Proof

**Date:** 2026-09-30  
**Status:** REPOSITORY-HOSTED READ-ONLY PREFLIGHT PROOF / NO RUN  
**Decision:** DEC-426  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-425

DEC-426 adds a push-to-main, first-run/attempt-1 read-only proof of the DEC-425
installed-executor dispatch preflight.

The proof pins DEC-424/425 source identities, the active executor workflow, the
active discovery workflow, and the pinned planning runtime. It has contents/actions
read permissions only and no `workflow_dispatch` trigger.

A valid proof requires:

- exact merged `main`;
- proof workflow run #1 / attempt 1;
- active executor workflow installed with its pinned blob;
- executor workflow run count still zero;
- historical-result attempt count still zero;
- unused historical-result slot;
- target run #2 / attempt 1;
- dispatch, execute mode, rerun/retry/replacement, reserved-data, Phase 8B,
  demo/live, real-money, and trading authority all false.

The workflow runs only the DEC-425 `plan` surface and uploads only its JSON
preflight artifact.

## Next gate

After a real successful DEC-426 run on merged `main`, the next safe step is strict
proof review and deterministic freezing. No executor dispatch is authorized.
