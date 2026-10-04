# Phase 8A — 2017 Dispatch Action Preflight

**Date:** 2026-10-04  
**Status:** SOURCE-READY READ-ONLY FINAL PREFLIGHT  
**Decision:** DEC-542

## Concrete predecessor

DEC-541 is concrete from workflow run `37223700484` on
`070b5ab9a9e6635ca26fa43f67ab71fdd49b3c1d`.

Its immutable authorization artifact is:

- artifact id: `11310658984`
- artifact digest:
  `sha256:97ee57fdb892b7041276bcd6c56da7ab06422e719c8b74aa322e35be80d243a3`
- authorization fingerprint:
  `16d42cb2552df761b80e0b32a23de5378f143c004946cfe2c816f280b17d8e8e`

The authorization is limited to annual segment `2017`, exact annual workflow
run `379` / attempt `1`, with predecessor freeze run
`37206992367`.

## DEC-542 contract

DEC-542 is a read-only final action preflight. It:

- validates the exact DEC-541 source and concrete authorization artifact;
- requires the installed 2017 runtime gate blob
  `c1853eeec55ee98b3155a6054f07cf360793ba9b`;
- requires the installed runtime blob
  `e9cbc76dc9e6866e80088d223498fbcc3b870fd1`;
- requires the active annual workflow blob
  `09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1`;
- rechecks the exact annual history:
  failed run 1, failed run 376, successful 2015 run 377, successful 2016 run 378;
- rejects any existing run 379 or later;
- freezes only:
  - ref `main`;
  - `annual_segment_label=2017`;
  - `previous_annual_freeze_run_id=37206992367`;
  - expected run `379` / attempt `1`.

The repository-hosted DEC-542 workflow has only `contents: read` and
`actions: read`. It contains no `gh workflow run` command and performs no
repository mutation.

## Authority boundary

DEC-542 does not dispatch the annual workflow. It does not authorize a rerun,
retry, replacement, run 380+, 2018+, cross-year strategy synthesis, promotion,
broker mutation, demo/live order, real-money action, or trading.

## Next gate

`EXACT_2017_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_DISPATCH_ON_CURRENT_MAIN`
