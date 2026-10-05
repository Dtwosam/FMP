# Phase 8A — 2020 Annual Catalogue Execution Authorization

**Date:** 2026-10-05  
**Status:** SOURCE-ONLY AUTHORIZATION / RUNTIME NOT INSTALLED / NO DISPATCH  
**Decision:** DEC-568

## Purpose

DEC-568 converts the concrete read-only DEC-567 preflight into a bounded source
authorization for exactly the 2020 annual catalogue research run.

It does not install a runtime gate and does not submit a workflow dispatch.

## Exact source preflight

DEC-568 accepts only:

- DEC-567 workflow run: `37313687059`;
- workflow head: `35115a69cae452d0afd922549fe41b4b8e404fd7`;
- preflight artifact: `11346985812`;
- artifact digest:
  `sha256:182be0b68d721e3267a84bab37c5a3bcb5c25b84b546ba9565c20b6c2ee1f1b0`;
- preflight fingerprint:
  `bfccf190a7abad8464bafbf96a039305a8034f754fdc7cd05f5825c65398204f`.

The preflight must still identify 2020, predecessor 2019, previous annual freeze
run ID `37310525635`, and expected annual run `382` / attempt `1`.

## Authorized research scope

At the source-contract layer only, DEC-568 records these permissions as true:

- annual workflow dispatch authorization for the bounded 2020 contract;
- historical artifact read;
- historical catalogue execution;
- historical result production.

These permissions are not yet installed into the annual runtime.

## Locked runtime/action scope

The following remain false:

- runtime authorization installed;
- runtime gate active;
- dispatch command present;
- dispatch action executed;
- rerun/retry/replacement;
- run 383 or later;
- next-segment execution;
- cross-year result production;
- Strategy V1 synthesis;
- promotion / Phase 8B;
- demo/live orders;
- broker mutation;
- real-money action;
- trading.

The repository-hosted DEC-568 builder has only `contents: read` and
`actions: read` permissions and uploads only the immutable authorization
artifact.

## Next gate

`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2020_RUNTIME_AUTHORIZATION_PLAN`
