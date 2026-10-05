# Phase 8A — 2020 Annual Catalogue Execution Preflight

**Date:** 2026-10-05  
**Status:** SOURCE-READY READ-ONLY PREFLIGHT / RUN 382 LOCKED  
**Decision:** DEC-567

## Purpose

DEC-567 defines the next annual-first gate after concrete 2019 runtime evidence
(DEC-566). It does not authorize execution. It freezes the exact conditions that
must hold before any 2020 execution authorization can be considered.

## Required predecessor state

The preflight accepts only a valid DEC-566 2019 runtime binding for:

- annual segment `2019`;
- workflow run `381`, attempt `1`;
- run ID `37310525635`;
- head `8bcee3a7a834743f08bd9ad73109bfc09609a2fe`;
- successful conclusion;
- bound runtime evidence;
- no next-segment or trading authority.

The annual workflow inventory must contain exactly seven manual runs:
failed runs `1` and `376`, then successful annual runs `377` through
`381` for 2015 through 2019 respectively.

## Frozen next identity

If all predecessor evidence validates, DEC-567 records only:

- annual segment: `2020`;
- prior segment: `2019`;
- previous annual freeze run ID: `37310525635`;
- expected next annual workflow run: `382`;
- expected attempt: `1`;
- preflight mode: read-only.

## Authority boundary

DEC-567 contains no workflow dispatch command and grants no historical artifact
read, catalogue execution, result production, next-segment execution, cross-year
comparison, Strategy V1 synthesis, promotion, Phase 8B, demo order, broker
mutation, live order, real-money, or trading authority.

A concrete repository-hosted workflow must wait for the successful DEC-566
artifact and pin that artifact's ID, digest, and binding fingerprint before the
2020 authorization gate may advance.
