# Phase 8A — Annual Catalogue Workflow Install Receipt

**Date:** 2026-10-03  
**Status:** ANNUAL WORKFLOW INSTALLED / EXECUTION LOCKED  
**Decision:** DEC-491  
**Predecessor:** DEC-490

DEC-491 records the consumed explicit operator authorization and installed state for
the annual-pattern-catalogue workflow.

It pins:
- DEC-490 runtime-evidence-binding source blob
  `ed6eccd796a6c35f9ed768a4bc1ce2d4ae78f830`;
- DEC-479 install-contract source blob
  `f9ac5dc517ec3efbb50057ade66c5b5aab2f52b3`;
- dormant annual-workflow template blob
  `31633e87b79551f5b7dfa6b0deb76a82eb070129`;
- active installed annual-workflow blob
  `31633e87b79551f5b7dfa6b0deb76a82eb070129`.

The active workflow is byte-identical to the frozen dormant template and remains
manual `workflow_dispatch` only with `contents: read` and `actions: read`.
It contains three separate `require-execution` checks: annual preflight, annual
cell, and annual freeze.

The installation authorization is consumed by the exact file creation. No further
repository mutation is authorized by this receipt.

Annual-workflow dispatch, historical artifact reads, annual catalogue execution,
result production, next-segment execution, cross-year result production, Strategy
V1 synthesis, promotion, Phase 8B, demo/live, broker mutation, real-money action,
and trading remain false.

## Next gate

`EXPLICIT_ANNUAL_PATTERN_CATALOGUE_2015_EXECUTION_AUTHORIZATION_BEFORE_RUN`

The first 2015 run requires a separate explicit authorization. DEC-491 does not
dispatch the workflow.
