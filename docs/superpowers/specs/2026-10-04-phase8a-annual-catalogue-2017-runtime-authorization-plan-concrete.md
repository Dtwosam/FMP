# Phase 8A — Concrete 2017 Runtime Authorization Plan

**Date:** 2026-10-04  
**Status:** READ-ONLY CONCRETE PLAN / RUNTIME NOT INSTALLED  
**Decision:** DEC-536

## Concrete source authorization

DEC-536 is bound to the successful DEC-535 repository-hosted authorization:

- workflow run: `37213629059`;
- workflow head: `3283a51a41e4c3f71079be9ab9758fa739ab87b2`;
- artifact: `11307204031`;
- artifact digest:
  `sha256:db62ce19a4f0805fa8255cdc25a1b3e8e35883e2aead2f98569077221273bb8c`.

The DEC-535 source blob remains
`ef70a0aec215943a2d992a484fd95feb390c6e07`.

## Runtime state and frozen targets

The current installed annual runtime remains
`b564f5a26fdef146fc6080962e7c4762b0b5949a` and does not route 2017.
The 2017 runtime gate target remains absent.

DEC-536 freezes, but does not install:

- gate template blob
  `c1853eeec55ee98b3155a6054f07cf360793ba9b`;
- runtime target blob
  `e9cbc76dc9e6866e80088d223498fbcc3b870fd1`.

The future gate is exact to annual segment 2017, run 379 / attempt 1, and
predecessor annual run ID `37206992367`.

## Repository-hosted plan builder

The DEC-536 workflow is path-scoped to its own landing and has only
`contents: read` and `actions: read`. It:

1. proves the exact successful DEC-535 run and artifact;
2. verifies the artifact ZIP digest;
3. rechecks current main and annual history
   `{1 failure, 376 failure, 377 success, 378 success}`;
4. requires run 379 to remain absent;
5. builds the DEC-536 plan;
6. uploads immutable plan evidence.

It cannot dispatch the annual catalogue, push a commit, install the runtime
gate, rerun workflows, or mutate broker/order/trading state.

## Authority boundary

At the DEC-536 plan layer, runtime installation, runtime gate activation,
repository mutation, workflow dispatch, historical reads/execution/results,
run 380+, 2018+, cross-year synthesis, Strategy V1 promotion, Phase 8B,
broker mutation, demo/live orders, real-money action, and trading all remain
false.

## Next gate

`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2017_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_AFTER_CONCRETE_DEC536`
