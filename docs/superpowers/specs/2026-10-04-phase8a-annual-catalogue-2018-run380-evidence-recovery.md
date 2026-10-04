# Phase 8A — 2018 Run-380 Evidence Recovery

**Date:** 2026-10-04  
**Status:** READ-ONLY SUCCESSOR RECOVERY  
**Decision:** DEC-555

## Trigger condition

Annual catalogue run `37237817538` completed successfully as global run
`380` / attempt `1` on
`30971a996f514670a6f836d8e45cf80137197a4f`.

All 20 annual jobs succeeded and all 20 expected artifacts exist. The 2018
annual freeze artifact is `11315584379` with digest
`sha256:ce2cdb7b4aa5fa9a0c7130e444b067463f333c0324942d57166d60b0af42e2c1`.

DEC-554 dispatcher run `37237807553` completed successfully on the same head.
Its immutable receipt artifact is `11316382138` with digest
`sha256:684b436c37ad31d4933b8253495acb4dfbdd912adfca3a354e90cde49e355ed9`.

GitHub did not create the automatic DEC-555 `workflow_run` successor. No
DEC-555 reviewer run exists.

## Recovery

The recovery workflow is path-scoped and one-shot. It has only
`contents: read` and `actions: read` permissions and performs no workflow
dispatch or rerun.

It requires:

- exact annual history through successful run 380 and no run 381+;
- zero prior DEC-555 reviewer runs;
- exact successful run 380 / attempt 1;
- exact successful DEC-554 dispatcher and receipt artifact;
- exact 2018 freeze artifact and digest;
- the frozen DEC-555 reviewer source, CLI, dispatcher, segment-evidence,
  2018 preflight, installed 2018 gate/runtime, and active annual-workflow blobs.

It then runs the same DEC-555 review locally inside the recovery job and uploads
one immutable recovered 2018 runtime binding.

## Authority boundary

The recovery does not authorize or perform annual dispatch, rerun, retry,
replacement execution, run 381+, 2019 execution, Strategy V1 synthesis,
promotion, Phase 8B, broker mutation, order placement, real-money action, or
trading.

The next gate after a valid recovered binding remains:

`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2019_EXECUTION_PREFLIGHT`
