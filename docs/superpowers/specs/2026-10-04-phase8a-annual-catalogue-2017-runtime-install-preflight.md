# Phase 8A — 2017 Runtime Authorization Install Preflight

**Date:** 2026-10-04  
**Status:** READ-ONLY CONCRETE PREFLIGHT / NO REPOSITORY MUTATION  
**Decision:** DEC-537

## Concrete source plan

DEC-537 consumes the successful DEC-536 plan evidence:

- workflow run: `37215086807`;
- workflow head: `585feb304ab11ac2fead24eac05233960ba80e0e`;
- artifact: `11307494750`;
- artifact digest:
  `sha256:80395e51c57ca26788ef4291d7cdf1e6e3e79ef6cf92893e9d37d14dd8bc2adc`.

The plan itself remains bound to successful DEC-535 authorization run
`37213629059` and artifact `11307204031`.

## Exact future mutation

The only future install target remains exactly two files:

1. `src/fmp/discovery/annual_pattern_catalogue_2017_runtime_authorization.py`
   from dormant gate blob `c1853eeec55ee98b3155a6054f07cf360793ba9b`;
2. `src/fmp/discovery/annual_pattern_catalogue_runtime.py`
   from dormant runtime target blob
   `e9cbc76dc9e6866e80088d223498fbcc3b870fd1`.

The current runtime is still
`b564f5a26fdef146fc6080962e7c4762b0b5949a`; the 2017 gate target remains absent.

## Preflight contract

The repository-hosted DEC-537 builder is path-scoped, read-only, and requires:

- current main to equal the DEC-537 landing commit;
- annual history exactly
  `{1 failure, 376 failure, 377 success, 378 success}`;
- no annual run 379+;
- exact DEC-536 artifact ZIP digest;
- exact DEC-535 authorization / DEC-536 plan linkage;
- exact run 379 / attempt 1;
- predecessor annual run ID `37206992367`.

It emits a preflight fingerprint and immutable artifact only.

## Authority boundary

DEC-537 does not authorize repository mutation, runtime installation, runtime gate
activation, annual dispatch, historical reads/execution/results, run 380+, 2018+,
cross-year synthesis, Strategy V1 promotion, Phase 8B, broker mutation, demo/live
orders, real-money action, or trading.

## Next gate

`EXACT_ANNUAL_PATTERN_CATALOGUE_2017_RUNTIME_AUTHORIZATION_INSTALL_MUTATION_AFTER_DEC537`
