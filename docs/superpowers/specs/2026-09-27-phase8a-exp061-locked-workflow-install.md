# Phase 8A — EXP-061 Locked Workflow Installation

**Date:** 2026-09-27  
**Status:** ACTIVE WORKFLOW INSTALLED / EXECUTION AND PROOF DISPATCH LOCKED  
**Decision:** DEC-276  
**Experiment:** EXP-20260927-061  
**Predecessor:** DEC-275

## 1. Purpose

DEC-276 installs the exact DEC-275 reviewed dormant workflow source at the reserved active GitHub Actions path without changing its execution semantics.

The installed workflow is:

- name: `phase8a-exp061-discovery`;
- path: `.github/workflows/phase8a-exp061-discovery.yml`;
- trigger surface: manual `workflow_dispatch`;
- expected historical branch if ever separately authorized: `main`;
- expected authoritative historical attempt if ever separately authorized: `1`.

Installation alone does not authorize a workflow proof dispatch and does not authorize historical discovery.

## 2. Exact source identity

DEC-276 copies the dormant template byte-for-byte.

- dormant template: `docs/superpowers/templates/phase8a-exp061-discovery.yml.disabled`;
- dormant template blob: `d4eb02d380ae8c9a5b95e6520cbb7ca192254cb9`;
- active workflow: `.github/workflows/phase8a-exp061-discovery.yml`;
- active workflow blob: `d4eb02d380ae8c9a5b95e6520cbb7ca192254cb9`.

Any byte-level drift invalidates the installation review.

## 3. Why installation is still safe

The active source retains DEC-275's hard execution gate:

`python scripts/phase8a_exp061.py require-execution --code-commit "$GITHUB_SHA"`

Under DEC-276 that command still raises before any historical cell artifact is opened.

The gate exists:

- in preflight after read-only upstream run/artifact metadata validation;
- before every historical cell's artifact download;
- before aggregate cell-evidence download/read.

Therefore accidental manual dispatch cannot produce an EXP-061 historical result while the gate remains false.

## 4. Read-only preflight behavior

A manually triggered workflow could technically enter preflight because the file now exists at an active GitHub Actions path.

Before the execution gate it may only:

- check manual-main workflow identity;
- checkout the exact workflow commit;
- install the pinned runtime;
- query read-only metadata for the two already-completed EXP-044 source runs and their artifact inventories;
- validate those snapshots and write preflight metadata.

It cannot download the nine feature artifacts or nine outcome artifacts because those steps live in cell jobs that require successful preflight, and preflight cannot pass the DEC-275 execution gate.

No historical market artifact bytes are opened by this locked state.

## 5. Dispatch governance

DEC-276 explicitly distinguishes technical workflow presence from governance authorization.

All remain false:

- ordinary workflow dispatch authorization;
- proof dispatch authorization;
- historical-result dispatch authorization;
- historical discovery execution;
- discovery-result production;
- rerun/retry/replacement;
- reserved 2023-2026 access;
- candidate compilation;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

A later decision must explicitly authorize a **proof-only dispatch** if we want to demonstrate on merged `main` that the active workflow stops at the gate.

That proof-only dispatch must not authorize historical result production.

## 6. Installation validator

`src/fmp/discovery/workflow_install.py` provides:

- Git blob SHA computation over workflow text;
- exact dormant/active text equality;
- exact dormant blob validation;
- exact active blob validation;
- installed-path validation from the repository checkout;
- independent proof-dispatch and historical-result-dispatch locks.

Focused tests require the active and dormant files to be byte-identical.

## 7. Frozen implementation identities

- active workflow blob: `d4eb02d380ae8c9a5b95e6520cbb7ca192254cb9`;
- dormant template blob: `d4eb02d380ae8c9a5b95e6520cbb7ca192254cb9`;
- install validator: `src/fmp/discovery/workflow_install.py`;
- install-validator blob: `e959a782fdbb6bf5b578e60e44f5e015b50086a6`;
- focused tests: `tests/test_phase8a_exp061_locked_workflow_install.py`;
- focused-test blob: `7996c2c1565352984ecd1bbff3ca538beda5b616`.

## 8. Result meaning

DEC-276 changes only repository installation state.

It produces no pattern hypothesis, no discovery shortlist, no validation survivor, no strategy, and no trading permission.

## 9. Next gate

After DEC-276 merges green, the next safe decision may authorize exactly one **proof-only manual-main dispatch** whose expected result is a fail-closed stop at the execution gate after read-only preflight.

That proof must freeze:

- exact merged-main head;
- exact workflow blob;
- exact run attempt;
- zero cell jobs executed;
- zero historical source artifacts downloaded;
- zero cell/aggregate result artifacts;
- no historical run-slot consumption.

Historical discovery/result execution must remain false.
