# Phase 8A — EXP-044 Phase 2 Release Preservation

**Date:** 2026-09-23  
**Status:** APPROVED BEFORE ANY EXP-044 RESULT-PRODUCING RUN  
**Decision:** DEC-082  
**Experiment:** EXP-20260923-044

## 1. Purpose

EXP-044 depends on three already accepted Phase 2 GitHub Actions artifacts.

DEC-078 established that those original Actions artifacts are time-limited and currently expire in December 2026.

DEC-082 adds a manual preservation workflow that republishes the exact already accepted Phase 2 ZIP bytes as GitHub release assets before expiry.

This is preservation only. It is not a new Dukascopy acquisition and does not create a new historical dataset.

## 2. Frozen original identities

The preservation contract remains bound to:

- Phase 2 source run: `34782357048`;
- Phase 2 source head SHA: `158c1c121655867b7fb2886fe755585dfcd682ec`;
- EURUSD Actions artifact `10325737935`;
- GBPUSD Actions artifact `10326096831`;
- USDJPY Actions artifact `10327600628`;
- the exact frozen ZIP SHA-256 for each symbol;
- the exact frozen ZIP byte size for each symbol;
- the exact processed-manifest SHA-256 for each symbol.

## 3. Preservation release identity

The release identity is frozen as:

- tag: `fmp-phase2-accepted-artifacts-v1`;
- title: `FMP Phase 2 accepted artifacts v1`.

The three release ZIP names are:

- `phase2-full-history-EURUSD.zip`;
- `phase2-full-history-GBPUSD.zip`;
- `phase2-full-history-USDJPY.zip`.

A fourth asset, `phase2-preservation-manifest.json`, records the exact original Actions artifact IDs, source run/head, ZIP hashes/sizes, and processed-manifest hashes.

## 4. Manual preservation workflow

The workflow is:

`.github/workflows/phase8a-exp044-preserve-phase2.yml`

It remains `workflow_dispatch` only and requires merged `main`.

Before creating a release it:

1. refuses an existing preservation release with the frozen tag;
2. downloads each original Actions artifact;
3. verifies exact ZIP byte size;
4. verifies exact ZIP SHA-256;
5. extracts the ZIP only for verification;
6. verifies the embedded processed-manifest SHA-256.

No external provider or Dukascopy endpoint is contacted.

## 5. Draft-first publication

The release is created as a draft.

The workflow uploads the three exact ZIP files plus the preservation manifest.

Before publication, the release API response must prove:

- the exact frozen tag and title;
- draft state;
- non-prerelease state;
- exactly the expected four assets;
- each ZIP asset is fully uploaded;
- each ZIP asset byte size equals the frozen size;
- each ZIP release-asset digest equals the frozen ZIP SHA-256.

Only after those checks pass may the workflow publish the release.

The workflow does not use asset replacement or `--clobber`.

## 6. Operator helper

DEC-081 is extended with a dry-run-by-default command:

`python scripts/phase8a_exp044_operator.py preserve-phase2`

Actual workflow dispatch still requires:

`--execute`

The helper preserves the same clean-main, exact-origin, GitHub-CLI-auth, and duplicate-run safeguards already used for EXP-044 feature/outcome dispatch.

## 7. Research identity boundary

The release is a byte-for-byte preservation copy.

DEC-082 does not:

- alter the original Phase 2 acceptance decision;
- alter any historical observation;
- alter any processed manifest;
- authorize silent substitution of different bytes;
- authorize fresh Dukascopy acquisition;
- authorize model fitting or selection;
- authorize promotion or any trading action.

Any later workflow that consumes the preservation release must separately validate the exact frozen ZIP and processed-manifest identities before use.

## 8. Next gate

The preferred sequence is:

1. preserve the exact accepted Phase 2 artifacts while the original Actions artifacts remain available;
2. dispatch `phase8a-exp044-market-features` from merged `main`;
3. continue through the existing feature-evidence, outcome-evidence, and DEC-074 readiness gates.

DEC-082 itself produces no market-research result.
