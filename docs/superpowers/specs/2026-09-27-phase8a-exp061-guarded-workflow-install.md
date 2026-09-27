# Phase 8A — EXP-061 Guarded Workflow Installation

**Date:** 2026-09-27  
**Status:** ACTIVE WORKFLOW SOURCE INSTALLED / EXECUTION STILL LOCKED  
**Decision:** DEC-276  
**Experiment:** EXP-20260927-061  
**Predecessor:** DEC-275

## 1. Purpose

DEC-276 installs the exact reviewed DEC-275 workflow bytes at the reserved active GitHub Actions path while keeping every result-producing authority false.

Installed path:

`.github/workflows/phase8a-exp061-discovery.yml`

Reviewed dormant source:

`docs/superpowers/templates/phase8a-exp061-discovery.yml.disabled`

Both files have the exact same Git blob:

`d4eb02d380ae8c9a5b95e6520cbb7ca192254cb9`

No workflow behavior changes during installation.

## 2. Presence is not authorization

After DEC-276, GitHub may expose the workflow's manual-dispatch UI because the source is now under `.github/workflows`.

That UI presence does **not** authorize a historical result run.

The source still imports DEC-275's execution gate, where:

- workflow dispatch authorization = false;
- historical result-run authorization = false;
- historical discovery execution authorization = false;
- discovery-result authorization = false.

The preflight job validates sources and then calls the closed execution gate before any cell job can begin.

Every cell and the aggregate path also recheck the same gate.

## 3. Exact installed topology

The installed source remains the DEC-274 topology:

- `exp061-preflight`;
- 18 runtime matrix cells explicitly named
  `exp061-cell-<symbol>-<timeframe>-<horizon>m`;
- `exp061-aggregate`.

The expected successful run inventory therefore remains exactly 20 jobs and exactly 20 commit-scoped artifacts.

## 4. Exact upstream source pins

The installed workflow remains pinned to:

- feature run `35867307338`, head `b71912e254d2a597c0ef55b5e1b3b87b052039ea`;
- outcome run `35876715434`, head `edeb43bb4de88923e3349caa8ace36350839ccb8`;
- aggregate feature evidence artifact `10753455784`;
- aggregate outcome evidence artifact `10758027876`;
- the exact nine feature-cell and nine outcome-cell artifact IDs/digests frozen by DEC-275.

No workflow input exists to substitute alternative data runs.

## 5. Installation proof

`validate_installed_workflow` requires:

- the reviewed dormant source to validate;
- the active source to validate;
- byte-for-byte equality between active and dormant source;
- the DEC-275 historical execution gate to remain false;
- workflow-dispatch authorization to remain false.

`validate_installed_workflow_paths` performs that check directly on the repository paths.

## 6. Focused tests

Focused tests require:

- active workflow source exists;
- dormant template exists;
- active bytes equal dormant bytes exactly;
- the reviewed workflow blob identity remains `d4eb02d...`;
- preflight's `require-execution` call occurs before the cell job definition;
- the manual-dispatch trigger is present;
- source-installed/reviewed flags are true;
- every dispatch/result/trading authority is false;
- the execution gate still raises after installation;
- any active-source byte drift fails validation.

No workflow dispatch is performed by DEC-276 or its tests.

## 7. Frozen implementation identities

- active workflow blob: `d4eb02d380ae8c9a5b95e6520cbb7ca192254cb9`;
- reviewed dormant template blob: `d4eb02d380ae8c9a5b95e6520cbb7ca192254cb9`;
- install contract: `src/fmp/discovery/workflow_install.py`;
- install-contract blob: `391cab86565e927a8d74eb3262591b22f2172472`;
- focused tests: `tests/test_phase8a_exp061_guarded_workflow_install.py`;
- focused-test blob: `6cc19fd55dfeb19972292f1532530ed245c51a0d`.

## 8. Run-slot preservation

DEC-276 must not dispatch the installed workflow.

Therefore it does not consume the future authoritative attempt-1 run slot defined by DEC-274.

A later authorization decision must verify that no prior manual-main EXP-061 discovery run exists before it can open that slot.

## 9. Authorization boundary

All remain false:

- workflow dispatch authorization;
- historical result-run authorization;
- historical discovery execution;
- discovery-result production;
- rerun/retry/replacement;
- reserved 2023-2026 access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## 10. Next gate

The next safe gate is governance-only and must occur before any dispatch:

1. verify zero prior manual-main EXP-061 discovery runs;
2. freeze a workflow-internal first-run guard;
3. freeze the exact terminal reviewer for success and non-success;
4. freeze a read-only operator plan that still emits no dispatch command.

Only after that governance source merges green may a later separate decision consider authorizing one historical attempt.
