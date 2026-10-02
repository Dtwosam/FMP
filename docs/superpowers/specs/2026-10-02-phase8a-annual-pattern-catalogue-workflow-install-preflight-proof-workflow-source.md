# Phase 8A Annual Catalogue Install-Preflight Proof Workflow Source

**Decision:** DEC-482  
**Experiment:** EXP-20261002-067  
**Status:** SOURCE-ONLY DORMANT PROOF WORKFLOW / NOT INSTALLED  
**Source proof contract:** DEC-481 head `d14b7e0f1f549b8396d2855f80a2c020d9cc3fa4`

## Purpose

DEC-482 freezes the disabled read-only workflow source that can later produce the
DEC-480 preflight artifact needed by the DEC-481 repository-hosted proof contract.

It does not install the proof workflow and does not install or dispatch the annual
catalogue workflow.

## Read-only proof workflow shape

The disabled template performs only:

1. exact merged-main manual-dispatch checks;
2. pinned Python/runtime installation;
3. read-only fetch of the current `main` branch metadata;
4. DEC-480 `plan` execution with `GITHUB_SHA` as the exact expected main head;
5. upload of the resulting `preflight.json` artifact.

The run intentionally does not compile DEC-481 proof evidence inside itself,
because DEC-481 requires the proof run to already be completed successfully. A
later read-only post-run gate must bind the completed run metadata to the uploaded
preflight.

## Forbidden surfaces

The dormant template contains no:

- `gh workflow run`;
- annual catalogue cell execution;
- annual catalogue freeze execution;
- direct locked-runtime invocation;
- repository mutation authorization.

The reserved proof workflow path remains absent under DEC-482.

## Exact source dependencies

DEC-482 binds exact Git blobs for:

- the DEC-481 proof-contract source;
- the DEC-480 plan-only preflight CLI;
- the disabled proof-workflow template itself:
  `0d6c93e2af04501f9ac2589fd24d6672b2b41910`.

Any dependency or dormant-template byte drift fails closed before the structural
workflow checks are accepted.

## Authority

The following remain false:

- proof-workflow template installation;
- proof workflow installed;
- proof-workflow dispatch;
- annual workflow installation;
- annual workflow installed;
- annual workflow dispatch;
- historical artifact reads;
- annual catalogue execution;
- historical result production;
- next-segment execution;
- cross-year result production;
- Strategy V1 synthesis;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Next gate

`SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_PROOF_WORKFLOW_INSTALL_CONTRACT`

That gate may define the exact future mutation required to install the read-only
proof workflow, but must not install it or open any annual-catalogue execution
authority.
