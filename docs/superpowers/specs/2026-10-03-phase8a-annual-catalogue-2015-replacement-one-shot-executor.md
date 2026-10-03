# Phase 8A — 2015 Replacement One-Shot Executor

**Date:** 2026-10-03  
**Status:** REPOSITORY-HOSTED ONE-SHOT EXECUTOR / REPLACEMENT RUN ONLY  
**Decision:** DEC-512  
**Predecessors:** DEC-498, DEC-499

DEC-512 closes the operational gap left after the failed first 2015 annual-catalogue run.

The repository-hosted executor is installed as a main-push/path-scoped workflow. On its first merged-main run it must:
- verify the exact repaired annual workflow, runtime, DEC-498 authorization source, DEC-499 preflight source, and DEC-499 CLI blobs;
- prove that the executor itself is on run 1 / attempt 1;
- query current main and the target annual workflow inventory;
- rebuild and validate the exact DEC-499 read-only preflight against the executor merge SHA;
- require the sole prior annual run to be failed run \`37126711695\` / run 1 / attempt 1;
- submit exactly one target dispatch for annual segment \`2015\` on \`main\`;
- resolve exactly target run 2 / attempt 1 at the same merge SHA;
- reject any observed run 3+;
- write an immutable dispatch receipt without claiming a result.

The executor grants no retry, rerun, third-or-later annual run, 2016+ execution, cross-year synthesis, Strategy V1, promotion, Phase 8B, demo/live order, broker mutation, real-money action, or trading authority.

## Next gate

\`REVIEW_2015_REPLACEMENT_RUN_WITH_DEC_500\`
