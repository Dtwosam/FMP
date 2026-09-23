# Phase 8B — Interrupted Segment Observability Amendment

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY PHASE 8B ACCEPTANCE RESULT
**Decision:** DEC-072
**Experiment:** EXP-20260923-043
**Depends on:** DEC-052, DEC-053, DEC-071
**Scope:** read-only progress observability for interrupted/unclosed prospective segment directories; no capture, repair, deletion, closure, acceptance, or promotion

## 1. Purpose

DEC-052 deliberately retains a prospective segment directory if capture is
interrupted before `prospective-segment.json` is written. Such a directory can
never count as closed campaign evidence.

DEC-053 counts unclosed segment directories when at least one valid closed
segment exists.

DEC-071 reuses that loader for read-only progress, but its empty-campaign branch
loses the unclosed count when there are **zero closed segments**. A first capture
that crashes can therefore leave one retained interrupted directory while
`progress` incorrectly reports zero.

DEC-072 fixes that observability defect without changing campaign evidence or
acceptance semantics.

## 2. Segment inventory

The campaign-close module must expose one deterministic read-only segment
inventory over:

`<campaign-dir>/segments/`

The inventory reports:

- sorted closed segment IDs;
- sorted unclosed segment-directory IDs;
- closed segment count;
- unclosed segment-directory count.

A directory is **closed** only when it contains
`prospective-segment.json`. Closed directories continue through the exact
DEC-053 validation path.

A directory without that close artifact is retained as **unclosed** and is never
loaded into aggregate simulation.

Non-directory entries under `segments/` remain outside segment evidence.

## 3. Empty campaign behavior

If the segment root is absent:

- closed count = 0;
- unclosed count = 0;
- both ID lists are empty.

If the segment root contains only unclosed directories:

- outcome remains `PHASE8B_PROGRESS_NO_CLOSED_SEGMENTS`;
- `eligible_closed_segment_count=0`;
- `unclosed_segment_directory_count` reports the true count;
- `unclosed_segment_ids` reports the sorted directory names.

Interrupted evidence is not silently promoted, deleted, repaired, or rewritten.

## 4. Mixed campaign behavior

When valid closed segments and unclosed directories coexist, DEC-071 aggregate
simulation and replay remain unchanged.

The progress report additionally includes:

- `closed_segment_ids`;
- `unclosed_segment_ids`;
- exact counts consistent with those lists.

Unclosed directories remain excluded from:

- observation bounds;
- London-date completeness;
- completed-trade counts;
- represented strategy/pair counts;
- financial metrics;
- replay.

## 5. Terminal context

The progress report adds:

`campaign_terminal_present`.

This is diagnostic only. It is derived from the presence of
`campaign-terminal.json`.

A terminal marker does not change historical progress accounting and does not
authorize any new capture or review.

## 6. Validation

A new progress validator must enforce:

- protocol / decision / experiment identity;
- sorted unique segment-ID lists;
- count/list parity;
- no segment ID appearing in both closed and unclosed lists;
- terminal flag is boolean;
- all authorization fields remain false;
- deterministic progress fingerprint over the report.

DEC-071 reports produced before DEC-072 are not persisted artifacts and require
no migration.

## 7. Safety

DEC-072:

- writes no campaign artifact;
- starts no capture;
- repairs no interrupted segment;
- deletes no evidence;
- creates no closure/review/acceptance artifact;
- changes no DEC-051 threshold;
- changes no strategy/risk logic;
- performs no broker mutation;
- authorizes no Phase 9 action or order.

## 8. Operator meaning

An unclosed segment directory means only that an attempted capture did not
produce a clean DEC-052 close artifact.

The operator may retain it for forensic inspection and start a later fresh
segment under the existing protocol. The unclosed directory itself never counts
toward Phase 8B acceptance.

## 9. Next boundary

After DEC-072, progress observability is reliable from the very first attempted
capture, including crash-before-first-close scenarios.

The next meaningful milestone remains real prospective MT5 DEMO evidence.
