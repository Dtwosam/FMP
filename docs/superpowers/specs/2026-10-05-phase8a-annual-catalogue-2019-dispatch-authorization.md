# Phase 8A — 2019 Dispatch Authorization

**Date:** 2026-10-05  
**Status:** SOURCE-ONLY AUTHORIZATION / NOT DISPATCHED  
**Decision:** DEC-563

## Concrete DEC-562 source

DEC-562 builder run `37305622078` completed successfully as run 1 /
attempt 1 on main
`236fc332c3d0fb0ad52a25038e764cd0f4e5d49f`.

Its immutable preflight artifact is:

- artifact id: `11344155034`
- artifact digest:
  `sha256:b7245744efdd4cd646b8eac6f094e9198e0f4d0cd2d36883c70685fa0feffbb7`
- preflight fingerprint:
  `b02c7c68f682f9706e3f9e4a6e4ade7826e1abb47d01330f543279221063fe45`

The preflight binds the exact installed 2019 runtime, successful predecessor
run `37237817538`, and unconsumed annual run 381 / attempt 1.

## Source-only authorization

DEC-563 turns only the execution contract flags required for the future 2019
annual research run to true:

- annual workflow dispatch authorization;
- historical artifact reads;
- historical catalogue execution;
- historical result production.

It remains source-only. There is no dispatch command and no dispatch action is
executed by this decision or its repository-hosted builder.

Before emitting evidence, the builder revalidates the exact DEC-562 artifact,
current installed runtime blobs, annual history through successful run 380, and
the continued absence of any run 381 or later.

## Authority boundary

Rerun/retry/replacement, run 382+, 2020+ execution, cross-year synthesis,
strategy promotion, Phase 8B, broker mutation, order placement, real-money
action, and trading remain false.

Next gate:
`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2019_DISPATCH_ACTION_PREFLIGHT`.
