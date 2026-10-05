# Phase 8A — 2020 Runtime Authorization Install Preflight

**Date:** 2026-10-05  
**Status:** SOURCE-READY READ-ONLY INSTALL PREFLIGHT / RUN 382 UNCONSUMED  
**Decision:** DEC-570

## Concrete source plan

DEC-570 consumes only the corrected concrete DEC-569 plan from workflow run
`37318488687` on main
`9f95010b402ce8413833dcdd5d051b2b45e795e7`.

The immutable source-plan artifact is:

- artifact id: `11349042014`
- artifact digest: `sha256:855375a850fe4e90475f5f5b9dd4d4721fba5bbac6ce8162d3c9d6d3854bbc7f`
- canonical plan SHA-256: `794ea5631bee374ec7a2e05c5efcb33e35f008d188114c879f7d2e68be72a7b0`

The plan's next gate is
`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2020_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_AFTER_CONCRETE_DEC569`.

## Exact future mutation

The preflight validates a future two-file mutation only:

1. create
   `src/fmp/discovery/annual_pattern_catalogue_2020_runtime_authorization.py`
   from dormant blob `695a50b418da752e1bd37d6302f209033ab611f5`;
2. replace
   `src/fmp/discovery/annual_pattern_catalogue_runtime.py`
   from installed blob `07ddfe7a968de10cd1d4f8592760cc9eb9e6300e`
   with target blob `4e124365430672fa63825b272001937c60151644`.

No mutation is performed by DEC-570.

## Live invariants

The repository-hosted DEC-570 builder is path-scoped, first-run-only, and
contents/actions read-only. Before producing evidence it requires:

- the exact successful corrected DEC-569 workflow run 2 / attempt 1;
- exact DEC-569 artifact id and digest;
- current main equal to the DEC-570 landing commit;
- exact annual history containing failed runs 1 and 376 plus successful runs
  377 through 381;
- no annual run 382 or later;
- exact DEC-568 authorization, DEC-569 plan, installed runtime, dormant gate,
  and dormant runtime-target source blobs.

## Authority boundary

DEC-570 is read-only. Repository mutation, runtime installation, runtime-gate
activation, annual run-382 dispatch, historical reads/execution/results,
run 383+, 2021+ execution, cross-year synthesis, Strategy V1, promotion,
Phase 8B, broker mutation, demo/live orders, real-money action, and trading
remain locked.

Next gate:
`EXACT_ANNUAL_PATTERN_CATALOGUE_2020_RUNTIME_AUTHORIZATION_INSTALL_MUTATION_AFTER_DEC570`.
