# Phase 8A — 2018 Dispatch-Action Preflight

**Date:** 2026-10-04  
**Status:** SOURCE-READY READ-ONLY PREFLIGHT / NOT DISPATCHED  
**Decision:** DEC-553

## Concrete authorization source

DEC-552 completed successfully as workflow run `37234867097` on
`8a02d66cfd0aee43e105e9057a813c0dffcc6dde`.

Its immutable authorization artifact is `11314579371`, digest
`sha256:b30f3995ca0207b65f772b15b84b23d61d9f1826ba77aabadb2a0e84064d8709`,
with authorization fingerprint
`eb0089103203b334c12800643f74cc838e8e9e140b4b7868f48ba74793d1d043`.

## Frozen dispatch parameters

DEC-553 performs no dispatch. It validates that the live annual history remains
exactly `{1, 376, 377, 378, 379}`, with successful 2017 run
`37227536041` as the immediate predecessor and no run 380 or later present.

The only frozen future dispatch parameters are:

- ref: `main`;
- annual segment: `2018`;
- previous annual freeze run id: `37227536041`;
- expected annual workflow run: `380`;
- expected attempt: `1`.

The builder also pins the active annual workflow, installed 2018 runtime gate,
and installed annual runtime blobs.

## Authority boundary

The preflight carries forward the exact DEC-552 authorization contract but keeps
`dispatch_command_present=False`, `dispatch_action_executed=False`, and
`preflight_read_only=True`.

Rerun, retry, replacement execution, run 381+, 2019+, cross-year synthesis,
Strategy V1 synthesis, promotion, Phase 8B, broker mutation, demo/live orders,
real-money action, and trading remain false.

## Next gate

`EXACT_2018_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_DISPATCH_ON_CURRENT_MAIN`.
