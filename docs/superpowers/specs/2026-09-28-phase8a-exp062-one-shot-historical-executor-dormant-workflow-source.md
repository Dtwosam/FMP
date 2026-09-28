# Phase 8A — EXP-062 Dormant One-Shot Historical Executor Workflow Source

**Date:** 2026-09-28  
**Status:** DORMANT DISABLED TEMPLATE SOURCE / ACTIVE WORKFLOW UNINSTALLED  
**Decision:** DEC-355  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-354

## Purpose

DEC-355 adds the dormant disabled source template for the future one-shot historical
executor workflow.

The template lives outside `.github/workflows/` and is therefore inert. It contains
the exact future one-shot dispatch behavior for review without installing or enabling
that behavior.

## Frozen source identities

DEC-355 pins:

- DEC-354 installation-source contract blob:
  `e4fc6a7d1faaca50bc6936597f0e8b66fe096985`;
- dormant executor template blob:
  `51ce87584369be957482460d81649adb1cb9f05d`;
- active discovery workflow blob:
  `1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50`.

Dormant template path:

`docs/superpowers/templates/phase8a-exp062-one-shot-historical-executor.yml.disabled`

Reserved active executor path:

`.github/workflows/phase8a-exp062-one-shot-historical-executor.yml`

## One-shot behavior encoded in the dormant template

If later installed under an explicit gate, the template would:

- trigger only by `workflow_dispatch`;
- require executor run #1 / attempt 1 on exact merged main;
- require the frozen historical discovery workflow source;
- require the historical-result slot to still be empty;
- submit exactly one
  `gh workflow run phase8a-exp062-discovery.yml --ref main`;
- resolve exactly historical run #2 / attempt 1;
- write an immutable executor receipt;
- reject rerun/retry/replacement authority.

The template needs `actions: write` only because a future installed executor would
need to dispatch the discovery workflow. That permission is inert while the file
remains disabled outside `.github/workflows/`.

## Safety boundary

DEC-355 does not install the executor workflow and does not authorize historical
dispatch. Install authorization, installed state, executor availability, dispatch,
execute mode, reserved 2023-2026 access, candidate compilation/promotion, Phase 8B,
demo, broker/live, real-money, and trading remain false.

## Next gate

The next safe gate is a repository-hosted read-only proof of the dormant executor
workflow source before any install-capable step is considered.
