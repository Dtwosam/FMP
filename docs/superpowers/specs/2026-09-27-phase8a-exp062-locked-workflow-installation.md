# Phase 8A — EXP-062 Locked Active Workflow Installation

**Date:** 2026-09-27  
**Status:** ACTIVE WORKFLOW INSTALLED / PROOF + HISTORICAL DISPATCH LOCKED  
**Decision:** DEC-300  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-299

## Purpose

DEC-300 installs the exact reviewed DEC-299 dormant EXP-062 workflow at its reserved active path without opening any dispatch or historical execution authority.

Active path:

`.github/workflows/phase8a-exp062-discovery.yml`

Dormant template:

`docs/superpowers/templates/phase8a-exp062-discovery.yml.disabled`

Both files must be byte-identical.

## Exact workflow identity

Frozen dormant template blob:

`1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50`

Frozen active workflow blob:

`1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50`

The installation validator rejects any semantically similar but byte-different active workflow.

## Runtime behavior remains locked

The active workflow is manual-only and retains the DEC-299 hard execution gate:

`python scripts/phase8a_exp062.py require-execution --code-commit "$GITHUB_SHA"`

That gate remains before:

- any cell source artifact is used for discovery;
- any cell-result evidence is read by aggregate.

Under DEC-300, the gate still raises because DEC-299 historical execution authorization remains false.

## Authorization state

DEC-300 records:

- active workflow installed: true;
- workflow dispatch authorized: false;
- proof dispatch authorized: false;
- historical-result dispatch authorized: false;
- historical discovery execution authorized: false;
- discovery-result production authorized: false.

It also keeps false:

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

## Frozen implementation

Installation contract:

`src/fmp/discovery/exp062_workflow_install.py`

Git blob:

`febb2bc00342364c67a75c69439136079eba0a2c`

Active workflow:

`.github/workflows/phase8a-exp062-discovery.yml`

Git blob:

`1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50`

Focused tests:

`tests/test_phase8a_exp062_locked_workflow_install.py`

Git blob:

`fbf18f73d4a660dbd4d33bdfb95dc6c8f416ec0a`

## Next gate

After DEC-299/300 are green and merged, the next safe layer is a **proof-only terminal contract and read-only proof operator**.

That proof must demonstrate on merged main that:

- source validation succeeds;
- the execution gate fails exactly as expected;
- no cell discovery executes;
- no aggregate discovery executes;
- the EXP-062 historical-result slot remains unused.

Proof dispatch itself must remain separately authorized from historical-result dispatch.
