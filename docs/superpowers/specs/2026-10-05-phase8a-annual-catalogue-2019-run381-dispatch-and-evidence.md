# Phase 8A — 2019 Run-381 Dispatch and Evidence Binding

**Date:** 2026-10-05  
**Status:** ATOMIC ONE-SHOT DISPATCH + READ-ONLY REVIEW  
**Decisions:** DEC-565 / DEC-566

## Concrete source

The dispatcher consumes only concrete DEC-564 evidence:

- workflow run: `37309216521`;
- workflow head: `79bffed4149cdeee1f74b8c02efdec42cb05c800`;
- artifact: `11344423884`;
- artifact digest: `sha256:2d828fa08459a23172057722e8befc69d89891734e95980a4241be5121ac0db4`;
- preflight fingerprint: `33ea75e1f34b2d643617be37e254644193506dea7fd959772c9eb00115088709`.

DEC-564 freezes only main / 2019 / predecessor run
`37237817538` / global annual run 381 / attempt 1.

## DEC-565 exact dispatch

DEC-565 is a path-scoped, one-shot repository-hosted dispatcher with
`contents: read` and `actions: write`.

Before dispatch it:

- requires its first workflow run / attempt 1;
- pins the DEC-564 source and CLI, DEC-566 reviewer source and CLI, installed
  2019 gate/runtime, and active annual workflow;
- requires the atomic DEC-565/566 landing to contain only the whitelisted
  dispatcher/reviewer/tests/docs files;
- downloads and verifies the exact DEC-564 artifact, digest, and fingerprint;
- rechecks main has not moved;
- requires the exact annual history:
  - run 1: failure;
  - run 376: failure;
  - run 377 / 2015: success;
  - run 378 / 2016: success;
  - run 379 / 2017: success;
  - run 380 / 2018: success;
- rejects any existing run 381+.

It then submits exactly:

`annual_segment_label=2019`

with predecessor:

`previous_annual_freeze_run_id=37237817538`

and resolves only global annual run 381 / attempt 1 on the atomic landing head.
Any run 382+ fails the dispatcher. The DEC-565 receipt claims submission only,
not a result.

## DEC-566 read-only evidence binding

DEC-566 is installed in the same atomic landing before DEC-565 can submit run
381. It is read-only (`contents: read`, `actions: read`) and supports both
the normal successful `workflow_run` path and an explicit manual recovery
path for the same exact run identity.

For successful run 381 it requires:

- exact run identity and landing head;
- exact successful DEC-565 dispatcher and dispatch receipt;
- all 20 annual jobs successful;
- all 20 annual artifacts present with exact names;
- freeze ZIP SHA-256 matching the GitHub artifact digest;
- a valid embedded 2019 annual freeze with 18 cells and 89,460 directional
  records.

The resulting DEC-566 binding is concrete runtime evidence only. It grants no
2020 execution or later authority.

## Authority boundary

Rerun, retry, replacement, run 382+, 2020+ execution, cross-year result
production, Strategy V1 synthesis, promotion, Phase 8B, broker mutation,
demo/live orders, real-money action, and trading remain false.

## Next gate

`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2020_EXECUTION_PREFLIGHT`
