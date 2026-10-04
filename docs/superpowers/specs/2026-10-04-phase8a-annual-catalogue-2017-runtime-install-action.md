# Phase 8A — 2017 Runtime Authorization Install Action

**Date:** 2026-10-04  
**Status:** EXACT TWO-FILE ACTION CONTRACT / MUTATION NOT APPLIED  
**Decision:** DEC-538

## Concrete source preflight

DEC-538 consumes the successful DEC-537 install-preflight evidence:

- workflow run: `37215789401`;
- workflow head: `f8a8de09adc4b64b84b2129eacbc38d0eb00e645`;
- artifact: `11308490990`;
- artifact digest:
  `sha256:892512ac79d2b372372871a143d887f01e5c96d9ed60ea8243f1cbfb4b7cc6ea`.

DEC-537 remains bound to concrete DEC-536 and DEC-535 evidence.

## Exact mutation contract

DEC-538 freezes exactly two ordered actions:

1. create
   `src/fmp/discovery/annual_pattern_catalogue_2017_runtime_authorization.py`
   from dormant blob `c1853eeec55ee98b3155a6054f07cf360793ba9b`;
2. update
   `src/fmp/discovery/annual_pattern_catalogue_runtime.py`
   from current blob `b564f5a26fdef146fc6080962e7c4762b0b5949a`
   to dormant target blob
   `e9cbc76dc9e6866e80088d223498fbcc3b870fd1`.

The action remains exact to annual segment 2017, workflow run 379 / attempt 1,
and predecessor run ID `37206992367`.

## Head separation

The source DEC-537 preflight is immutably bound to its landing commit
`f8a8de09adc4b64b84b2129eacbc38d0eb00e645`. DEC-538 does not rewrite that
historical head. Instead, its builder revalidates the current DEC-538 landing
commit, unchanged runtime blob, absent 2017 gate, and unconsumed run-379 slot
before compiling the action.

## Authority boundary

The DEC-538 contract sets repository mutation authority true only for the exact
two-file action above. It does **not** claim that the runtime is installed or
active and does not authorize annual dispatch, historical execution/results,
run 380+, 2018+, Strategy V1 promotion, Phase 8B, broker mutation, demo/live
orders, real-money action, or trading.

The repository-hosted DEC-538 builder itself has only `contents: read` and
`actions: read` and cannot apply the mutation.

## Next gate

`APPLY_EXACT_ANNUAL_PATTERN_CATALOGUE_2017_RUNTIME_AUTHORIZATION_INSTALL_ACTION_AFTER_DEC538`
