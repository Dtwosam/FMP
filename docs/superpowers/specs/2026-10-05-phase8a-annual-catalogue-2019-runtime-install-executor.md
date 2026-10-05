# Phase 8A — 2019 Runtime Authorization Install Executor

**Date:** 2026-10-05  
**Status:** BOUNDED TWO-FILE INSTALL / ANNUAL DISPATCH LOCKED  
**Decision:** DEC-561

## Concrete DEC-560 source

DEC-560 builder run `37299664787` completed successfully as run 1 /
attempt 1 on main
`bacb20c1d1541ac0b46076cef8ca9fe898559339`.

Its immutable action artifact is:

- artifact id: `11341025756`
- artifact digest:
  `sha256:dcd16ee2ddbdf9c5b17acfe6e79b54f1dbf6a38a839362ecc91a896f41520354`
- action fingerprint:
  `c68df812693da1edfc5ab568afef50b2e70797a04b4c44cf22de7c3fc15bea35`

The action is exact to annual segment 2019, future annual workflow run 381 /
attempt 1, with successful 2018 predecessor run `37237817538`.

## Exact install

DEC-561 may mutate exactly two files, in the frozen order:

1. create
   `src/fmp/discovery/annual_pattern_catalogue_2019_runtime_authorization.py`
   with blob
   `d87fe85a5b426fa92caf7d6cc165445590f4097c`;
2. replace
   `src/fmp/discovery/annual_pattern_catalogue_runtime.py`
   from blob
   `410180c34a9e3500bbbb42310a5253b993ac7785`
   to blob
   `07ddfe7a968de10cd1d4f8592760cc9eb9e6300e`.

No other changed file is accepted.

## One-shot repository executor

The executor is path-scoped to its own first push, with `contents: write` and
`actions: read` only. Before staging a mutation it requires:

- exact successful DEC-560 run, artifact id, digest, and action fingerprint;
- current main equal to the executor landing commit;
- current runtime still
  `410180c34a9e3500bbbb42310a5253b993ac7785`;
- 2019 gate target absent;
- annual workflow history exactly
  `{1 failure, 376 failure, 377 success, 378 success, 379 success, 380 success}`;
- no annual run 381 or later.

Before pushing, it compiles the installed 2019 gate/runtime, proves the exact
2019/run381/predecessor route, proves the existing 2018/run380 route remains
valid, and rejects 2019/run382.

After the exact two-file commit reaches main, the executor emits an immutable
DEC-561 receipt binding the install commit and installed blobs.

## Authority boundary

DEC-561 installs the 2019 runtime gate but does not dispatch the annual
workflow. Annual dispatch, rerun/retry/replacement, run 382+, 2020+ execution,
strategy/promotion, broker mutation, order placement, real-money action, and
trading remain locked.

Next gate:
`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2019_DISPATCH_PREFLIGHT`.
