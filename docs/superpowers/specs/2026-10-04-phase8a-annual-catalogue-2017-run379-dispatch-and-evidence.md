# Phase 8A — 2017 Run-379 Dispatch and Evidence Binding

**Date:** 2026-10-04  
**Status:** ATOMIC DISPATCH + REVIEWER SOURCE-READY  
**Decisions:** DEC-543 / DEC-544

## Concrete predecessor

DEC-542 completed successfully as workflow run `37226222971` on
`edbbfd0ba3d33ecb61aa3ba6604bd954e98a83f1`.

Its immutable final-preflight artifact is:

- artifact id: `11311294443`
- artifact digest:
  `sha256:d26a3d27a026546568dccab7305f44facdbfcbc749d2aac5f9233f43f86b61ea`
- preflight fingerprint:
  `ef31f7ea8c5e50dacee9cd2462b701d17e422f1507b2eb048db781c764d4b2db`

The frozen dispatch parameters are exact annual segment `2017`, predecessor
freeze run `37206992367`, expected annual workflow run `379` / attempt `1`,
and ref `main`.

## DEC-543 exact one-shot dispatch

DEC-543 is a path-scoped push executor installed together with DEC-544.

Before dispatch it:

- requires its own exact workflow run `1` / attempt `1`;
- verifies DEC-542's exact workflow run, artifact digest, and preflight fingerprint;
- requires the annual workflow, installed 2017 gate, and installed runtime blobs to
  remain unchanged;
- requires the merge from the DEC-542 head to contain only the exact atomic
  DEC-543/544 source, tests, CI, and documentation files;
- rechecks current `main` and exact annual history
  `{1 failure, 376 failure, 377 success/2015, 378 success/2016}`;
- rejects any annual run `379` or later.

It may then submit exactly one annual catalogue workflow dispatch with:

- `annual_segment_label=2017`
- `previous_annual_freeze_run_id=37206992367`
- ref `main`

It resolves exact run `379` / attempt `1`, rejects run `380+`, and writes
an immutable dispatch receipt. The receipt claims submission only, never a result.

## DEC-544 read-only runtime evidence binding

DEC-544 is installed in the same merge before DEC-543 can submit run 379, so the
normal `workflow_run` completion event cannot race the reviewer installation.

The reviewer also exposes a read-only manual recovery entry point bound to a
specific run id/head/number. It never reruns annual research.

For a successful run 379, DEC-544 requires:

- exact annual workflow identity and head;
- exact successful DEC-543 dispatcher provenance at the same head;
- the DEC-543 dispatch receipt bound to that run;
- exactly 20 successful jobs and 20 non-expired artifacts;
- the SHA-256 verified 2017 freeze artifact;
- a valid DEC-477 annual segment freeze with 18 cells and 89,460 directional
  records.

The resulting binding records only concrete 2017 runtime evidence.

## Authority boundary

DEC-543 authorizes only the already-frozen 2017 run 379 / attempt 1 dispatch.
DEC-544 is read-only.

Neither decision authorizes a rerun, retry, replacement, run 380+, 2018+
execution, cross-year synthesis, Strategy V1 promotion, Phase 8B, broker
mutation, demo/live order placement, real-money action, or trading.

## Next gate

After concrete successful DEC-544 evidence:

`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2018_EXECUTION_PREFLIGHT`
