# Phase 8A — Explicit Successor Orchestration

**Date:** 2026-10-04  
**Status:** SOURCE-READY ONE-SHOT RECOVERY / 2017 LOCKED  
**Decision:** DEC-529

## Live evidence

Fresh 2015 annual catalogue run `37198002653` completed successfully as global
run 377 / attempt 1 on commit
`a89db974be9a94481e7ed0990476bc661012f1e4`.

All 20 jobs completed successfully and the run produced the expected 20
artifacts, including the deterministic 2015 annual freeze.

The installed DEC-513 `workflow_run` successor did not start after run 377
completed. No DEC-513 artifact was produced and no 2016 execution was started.
The failure is therefore successor orchestration, not annual evidence.

## Recovery design

DEC-529 adds explicit `workflow_dispatch` recovery inputs to the existing
DEC-513, DEC-514, DEC-518→521, and DEC-522 workflows. Their existing evidence,
source-hash, main-head, and authority checks remain in place.

A new path-scoped push workflow runs once when its own file lands on main. It:

1. proves the exact annual inventory is failed run 1, failed run 376, successful
   run 377, with no run 378;
2. explicitly dispatches DEC-513 against exact successful run
   `37198002653`;
3. waits for successful DEC-513 evidence before explicitly dispatching DEC-514;
4. waits for successful DEC-514 before explicitly dispatching the existing
   DEC-518→521 install/plan/dispatch executor;
5. waits for exact 2016 annual run 378 / attempt 1 and requires success;
6. uses an automatically triggered DEC-522 reviewer if one exists, otherwise
   submits one exact manual DEC-522 review;
7. emits an immutable DEC-529 receipt.

Automatic successors of manually recovered DEC-513/DEC-514 runs are
intentionally suppressed so the explicit path cannot race a duplicate
activation or installer.

## Authority boundary

The orchestrator does not directly dispatch the annual catalogue workflow.
Only the existing DEC-521 executor can submit run 378 after the installed-state
checks pass.

No retry or rerun is authorized. Run 379+, 2017 execution, cross-year strategy
synthesis, promotion, Phase 8B, broker mutation, demo/live orders, real-money
action, and trading remain locked.
