# Phase 8A — EXP-065 Locked Pairwise Runtime Wiring

**Date:** 2026-10-01  
**Status:** ACTIVE WORKFLOW INSTALLED / HISTORICAL EXECUTION LOCKED  
**Decision:** DEC-464  
**Experiment:** EXP-20261001-065  
**Predecessor:** DEC-463

## Purpose

DEC-464 installs the deterministic source wiring needed to run EXP-065 later,
without authorizing any historical execution now.

The installed workflow, CLI, and runtime-source contract are deliberately
fail-closed. Every path that could open a historical artifact or read a historical
cell result is preceded by a hard execution gate that is false under DEC-464.

## Frozen lineage

DEC-464 binds:

- merged DEC-463 commit
  `c8c2c8d2dd5be5ff73655b09730d9eb18f9c3737`;
- DEC-463 evidence contract blob
  `ca68622ddfc9866f00569d558b2ab927be23686d`;
- DEC-462 pairwise miner blob
  `7dac382838d2b8fcc4df5d02c4949ad65c17635b`;
- repaired DEC-461 protocol blob
  `b54267d790667659749a96123ad23a491ff50dfa`;
- EXP-062 repaired non-finite feature adapter blob
  `491ba8c92cb6e6e4c715bfb1ecb934b6949e1596`;
- EXP-062 source contract blob
  `e20ded13de24f99e8ea6cfdc6cb0d1309d984f24`;
- EXP-061 range-limited loader blob
  `df1d029a6f8b8d3862ebbf990ed1170a5982e1ea`;
- runtime requirements blob
  `1ff32214dee10d877a067e750cd69ffad96d5fe5`.

No alternative source, loader, adapter, feature repair path, symbol, timeframe,
horizon, or data range is introduced.

## Installed runtime source

Runtime source:

`src/fmp/discovery/exp065_runtime_source.py`

Git blob:

`717b43e3bfd656b51e22819cf948f8cd6485f334`.

It freezes:

- workflow name `phase8a-exp065-pairwise-interaction`;
- event `workflow_dispatch`;
- branch `main`;
- run attempt 1;
- exact 18-cell topology;
- one preflight job;
- 18 cell jobs;
- one aggregate job;
- exactly 20 expected jobs and 20 expected artifacts;
- exact artifact names bound to the code commit;
- exact EXP-044 feature/outcome source snapshots already accepted by the
  predecessor source contracts;
- exact source dependency Git blobs;
- byte-identical dormant and active workflow source;
- exact CLI Git blob.

## Workflow and CLI pins

Dormant template:

`docs/superpowers/templates/phase8a-exp065-pairwise-interaction.yml.disabled`

Installed active workflow:

`.github/workflows/phase8a-exp065-pairwise-interaction.yml`

Both are byte-identical at Git blob:

`75d0e4df56d5c4ced5aff614e236cf0e1bb078e1`.

Locked CLI:

`scripts/phase8a_exp065.py`

Git blob:

`38e3eb9a5c2733655c845291d6bc3160e5fa0291`.

The CLI is based on the pre-activation EXP-064 pattern, not the later
execution-authorized EXP-064 CLI.

## Exact source composition

Each future EXP-065 cell, if a later decision separately authorizes execution,
would compose only:

1. the frozen EXP-044 feature/outcome artifacts;
2. the frozen EXP-061 range-limited loader;
3. the EXP-062 non-finite-to-null adapter;
4. the DEC-462 in-memory EXP-065 pairwise miner;
5. the DEC-463 EXP-065 evidence contract.

The pairwise protocol remains the repaired DEC-461 protocol.

The source boundary remains 2015-01-01 through 2022-12-31 already-seen design
evidence. The reserved 2023-01-01 through 2026-08-20 block is not opened.

## Gate ordering

The active workflow contains a dedicated
`Require separately authorized EXP-065 execution` step before any historical
artifact download.

The CLI also calls
`require_historical_execution_authorized(...)` before:

- loading historical feature/outcome artifacts in the `cell` command;
- opening historical cell-evidence files in the `aggregate` command.

Under DEC-464 the gate always raises because historical execution remains false.

Therefore a manual workflow start cannot reach the historical artifact download
step under this decision.

## Predecessor isolation

The workflow validator rejects predecessor cell or aggregate CLIs, including the
EXP-064 runtime CLI.

EXP-064 is not a runtime dependency of EXP-065. The only EXP-064 strings retained
in the runtime source are explicit negative checks that reject predecessor CLI
invocation.

## Authority state

DEC-464 sets:

- workflow source authorized: true;
- workflow installed: true.

DEC-464 keeps false:

- workflow dispatch authorization;
- historical execution authorization;
- historical result authorization;
- rerun authorization;
- retry authorization;
- replacement-run authorization;
- reserved robustness access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading.

No execute mode, dispatcher, executor, run-slot authorization, or result-review
authorization is introduced.

## Focused tests

Focused tests:

`tests/test_phase8a_exp065_locked_runtime_wiring.py`

Git blob:

`aecd7003d93d6de43565a5b22a663121cf2ccb68`.

They prove:

- exact DEC-463 merge lineage;
- exact DEC-463/462/461 dependency blobs;
- exact EXP-062/061 source path;
- exact 18-cell / 20-job / 20-artifact topology;
- byte-identical dormant and installed workflow;
- exact CLI blob;
- exact EXP-044 source snapshots;
- execution gate ordering before historical reads/downloads;
- predecessor EXP-064 CLI rejection;
- hard-closed execution boundary;
- all downstream authority locks.

## Next gate

After DEC-464 is green and merged, the next gate is a separate source-only
one-shot EXP-065 historical-result slot authorization bound to the exact merged
DEC-464 runtime.

That later decision may define only the first exact manual-main run,
run number 1 / attempt 1, as the potential single slot. It must keep workflow
dispatch, historical execution, rerun, retry, replacement, reserved access, and
all downstream trading authority false.

DEC-464 itself does not dispatch EXP-065 and does not authorize execution.
