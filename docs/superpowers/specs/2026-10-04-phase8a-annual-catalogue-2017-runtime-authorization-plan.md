# Phase 8A — 2017 Runtime Authorization Plan

**Date:** 2026-10-04  
**Status:** DORMANT SOURCE-ONLY PLAN / NO REPOSITORY MUTATION  
**Decision:** DEC-536

## Source authorization

DEC-536 consumes only a valid DEC-535 authorization for annual segment 2017,
exact annual workflow run 379 / attempt 1, with predecessor 2016 annual run
`37206992367`.

The DEC-535 source is pinned to blob
`ef70a0aec215943a2d992a484fd95feb390c6e07`.

## Frozen dormant targets

DEC-536 freezes two future install targets without applying them:

- 2017 runtime gate template:
  `docs/superpowers/templates/annual_pattern_catalogue_2017_runtime_authorization.py.disabled`
  at blob `c1853eeec55ee98b3155a6054f07cf360793ba9b`;
- annual runtime target:
  `docs/superpowers/templates/annual_pattern_catalogue_runtime_with_2017_authorization.py.disabled`
  at blob `e9cbc76dc9e6866e80088d223498fbcc3b870fd1`.

The current installed runtime remains
`b564f5a26fdef146fc6080962e7c4762b0b5949a` and has no 2017 route.

The dormant gate is exact to:

- annual segment 2017;
- workflow run 379 / attempt 1;
- predecessor run ID `37206992367`.

The dormant runtime target adds only the 2017/run-379 route and preserves the
installed 2016/run-378 route and the existing 2015 routes.

## Authority boundary

DEC-536 performs no repository mutation and no workflow dispatch. Runtime
authorization remains uninstalled and inactive. Historical reads, execution,
and result production remain false at the plan layer.

Rerun, retry, replacement, run 380+, 2018+, cross-year synthesis, Strategy V1
promotion, Phase 8B, broker mutation, demo/live orders, real-money action, and
trading remain locked.

## Next gate

`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2017_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_AFTER_CONCRETE_DEC535`
