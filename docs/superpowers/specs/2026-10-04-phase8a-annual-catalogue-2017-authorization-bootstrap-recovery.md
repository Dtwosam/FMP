# Phase 8A — DEC-535 Authorization Bootstrap Recovery

**Date:** 2026-10-04  
**Status:** READ-ONLY BOOTSTRAP REPAIR / RUN 379 UNCONSUMED  
**Decision:** DEC-535 implementation recovery

## Failure

The first repository-hosted DEC-535 workflow run,
`37213060816`, ran on main commit
`39e7bfaf072ef1943488f2feae732ff6a0800768`.

It successfully:

- bound the exact DEC-534 workflow run and artifact;
- verified the artifact digest;
- rechecked current main;
- proved the annual dispatch inventory still ends at successful run 378.

It then failed before authorization construction because the job had not installed
the pinned research dependencies and importing the annual catalogue stack raised
`ModuleNotFoundError: No module named 'polars'`.

No repository mutation or annual workflow dispatch occurred. Run 379 remains
unconsumed.

## Recovery

The same workflow identity is repaired for exact workflow run 2 / attempt 1.
Before continuing it proves failed run `37213060816` by ID, path, main head,
run number, attempt, status, and conclusion.

It then installs only the pinned dependencies:

- `requirements/exp061-discovery-run.txt`;
- `scikit-learn==1.9.1`.

The repository continues to resolve project source through `PYTHONPATH=src`;
no editable package install is used. The clean-checkout guard remains active.

The recovered workflow rebuilds the same DEC-535 source-only authorization and
still cannot mutate the repository or dispatch the annual catalogue.

## Authority boundary

Run 379 remains absent until later runtime-install and dispatch gates are
separately satisfied. Run 380+, 2018+, strategy promotion, broker mutation,
order placement, real-money action, and trading remain locked.
