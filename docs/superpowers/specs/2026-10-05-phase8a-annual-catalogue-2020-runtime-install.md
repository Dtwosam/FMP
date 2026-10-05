# Phase 8A — 2020 Runtime Authorization Installation

**Date:** 2026-10-05  
**Decision:** DEC-572  
**Status:** EXACT TWO-FILE INSTALL / NO ANNUAL DISPATCH

## Concrete source

DEC-572 consumes only the successful corrected DEC-571 action artifact:

- workflow run: `37327905209` (run 2 / attempt 1)
- head: `4ed1da1cdc5a8df1272fb1f06a803a57a8043427`
- artifact: `11352259131`
- artifact digest: `sha256:082c09ed64042f2c63252676be1d63aab6553c3cd92e3995256498ac4744b423`
- action fingerprint: `0d617a5261a25d1fbdcc661fcc9518be63081ca442fb2ac068a2206f875e6939`

The failed DEC-571 run 1 remains immutable provenance and is not retried.

## Exact mutation

The installer may change exactly two files:

1. create `src/fmp/discovery/annual_pattern_catalogue_2020_runtime_authorization.py`
   at blob `695a50b418da752e1bd37d6302f209033ab611f5`;
2. replace `src/fmp/discovery/annual_pattern_catalogue_runtime.py`
   from `07ddfe7a968de10cd1d4f8592760cc9eb9e6300e`
   with `4e124365430672fa63825b272001937c60151644`.

Before mutation, the executor requires the exact annual history
`{1, 376, 377, 378, 379, 380, 381}`, with runs 1 and 376 failed and runs
377–381 successful, and rejects any existing run 382+.

Before pushing, it proves:
- 2020 / run 382 / attempt 1 is accepted only with predecessor run
  `37310525635`;
- 2019 / run 381 remains accepted with predecessor run `37237817538`;
- 2020 / run 383 remains rejected.

## Boundary

DEC-572 performs no annual workflow dispatch. It does not authorize rerun/retry,
run 383+, 2021+ execution, cross-year synthesis, strategy promotion, broker or
order mutation, real-money action, or trading.
