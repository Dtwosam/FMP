# Phase 8A — Annual Catalogue Recovery Clean-Install V2

**Date:** 2026-10-04  
**Status:** SOURCE-READY REPAIR / RUN 376 UNCONSUMED  
**Decision:** DEC-517 implementation repair

## Live failure

The first installed DEC-517 recovery workflow ran as GitHub Actions run
`37190929052` on main commit
`5417fddc015be92ed843de40be097381367b2c24`.

It validated the original failed executor and the still-single annual
`workflow_dispatch` inventory, then failed at the clean-checkout guard after
`pip install -e .`. No annual workflow was dispatched, so the replacement
annual slot remains exact global run 376 / attempt 1.

## Repair

The recovery workflow keeps the same workflow identity and permits only its
second push run / attempt 1. It explicitly validates failed recovery run
`37190929052` before doing any work.

All live successor workflows now install the exact runtime dependencies without
an editable project install:

- `requirements/exp061-discovery-run.txt`
- `scikit-learn==1.9.1`

The repository source continues to resolve through `PYTHONPATH=src`, so no
editable-install metadata is needed. Every existing clean-checkout guard remains
active.

The exact workflow blob chain is rebound in order:

1. recovery executor;
2. DEC-513 replacement runtime evidence reviewer;
3. DEC-514 2016 activation planner;
4. DEC-518/519/521 2016 runtime installer and exact run-377 dispatcher;
5. DEC-522 run-377 reviewer and its Python source validator.

## Authority boundary

This repair authorizes only the already-approved recovered 2015 replacement
dispatch when all existing fail-closed checks pass. It does not authorize a
rerun of annual run 1, a retry of failed recovery run 1, run 377 except through
the existing DEC-521 chain after successful 2015 evidence, run 378+, 2017+
execution, strategy promotion, broker mutation, order placement, real-money
action, or trading.
