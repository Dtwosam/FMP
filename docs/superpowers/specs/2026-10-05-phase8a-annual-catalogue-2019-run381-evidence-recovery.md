# Phase 8A — 2019 Run-381 Evidence Recovery

**Date:** 2026-10-05  
**Status:** READ-ONLY SUCCESSOR RECOVERY  
**Decision:** DEC-566

## Trigger condition

Annual catalogue run `37310525635` completed successfully as global run
`381` / attempt `1` on
`8bcee3a7a834743f08bd9ad73109bfc09609a2fe`.

All 20 annual jobs succeeded and all 20 expected artifacts exist. The 2019
annual freeze artifact is `11345931866` with digest
`sha256:cc3f5100c276e30df87d721a15843ff56b533354a5adaba6699d716a2daa8178`.

DEC-565 dispatcher run `37310506796` completed successfully on the same head.
Its immutable receipt artifact is `11345118826` with digest
`sha256:ab1f031f0b986521b64c2667029b48a8052c5f936bb0633aff536770fb64646f`.

GitHub did not create the automatic DEC-566 `workflow_run` successor. No
DEC-566 reviewer run exists.

## Recovery

The recovery workflow is path-scoped and one-shot. It has only
`contents: read` and `actions: read` permissions and performs no workflow
dispatch or rerun.

It requires:

- exact annual history through successful run 381 and no run 382+;
- zero prior DEC-566 reviewer runs;
- exact successful run 381 / attempt 1;
- exact successful DEC-565 dispatcher and receipt artifact;
- exact 2019 freeze artifact and digest;
- the frozen DEC-566 reviewer source, CLI, dispatcher, segment-evidence,
  2019 preflight, installed 2019 gate/runtime, and active annual-workflow blobs.

It then runs the same DEC-566 review locally inside the recovery job and uploads
one immutable recovered 2019 runtime binding.

## Authority boundary

The recovery does not authorize or perform annual dispatch, rerun, retry,
replacement execution, run 382+, 2020 execution, Strategy V1 synthesis,
promotion, Phase 8B, broker mutation, order placement, real-money action, or
trading.

The next gate after a valid recovered binding remains:

`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2020_EXECUTION_PREFLIGHT`
