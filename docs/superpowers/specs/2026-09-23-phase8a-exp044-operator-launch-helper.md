# Phase 8A — EXP-044 Manual Operator Launch Helper

**Date:** 2026-09-23  
**Status:** APPROVED BEFORE ANY EXP-044 RESULT-PRODUCING RUN  
**Decision:** DEC-081  
**Experiment:** EXP-20260923-044

## 1. Purpose

The EXP-044 feature and outcome workflows intentionally remain manual `workflow_dispatch` workflows.

The connected ChatGPT GitHub app currently exposes workflow read/retry actions but no initial workflow-dispatch action. The authorized remote Mac may also be unavailable.

DEC-081 adds an operator-side CLI so an authorized machine with GitHub CLI access can perform the exact manual dispatch without relying on remembered commands or weakening the workflow trigger.

## 2. Dry-run default

The helper is:

`python scripts/phase8a_exp044_operator.py`

It has two stages:

- `features`
- `outcomes --feature-run-id <id>`

Without `--execute`, the helper performs all available preflight checks and prints the exact dispatch command but does not dispatch anything.

Actual dispatch requires an explicit `--execute` flag.

## 3. Checkout gate

Before either stage can become ready, the helper requires:

- local branch exactly `main`;
- local HEAD to be a valid Git SHA;
- a fresh fetched `origin/main`;
- local HEAD exactly equal to `origin/main`;
- a clean working tree;
- origin remote exactly identifying `Dtwosam/FMP`;
- valid GitHub CLI authentication.

This prevents result-producing dispatch from an unmerged, stale, dirty, or wrong repository checkout.

## 4. Duplicate-run gate

Before feature dispatch, the helper queries the EXP-044 feature workflow's manual `main` runs.

If any manual `main` run already exists, it refuses to create a duplicate and requires the operator to inspect the existing run/evidence.

Before outcome dispatch, the same rule is applied to the outcome workflow.

The helper does not automatically retry or replace an existing result-producing run.

## 5. Outcome source-run gate

Outcome dispatch additionally requires an exact positive feature-run ID.

Before preparing the command, the helper fetches and verifies that run is:

- the exact `phase8a-exp044-market-features` workflow;
- the exact feature workflow path;
- a `workflow_dispatch` event;
- from `main`;
- completed;
- successful;
- bound to a valid 40-character Git head SHA.

The outcome workflow independently repeats these checks after dispatch and revalidates the aggregate feature evidence.

## 6. Exact commands

The feature command is fixed to:

`gh workflow run phase8a-exp044-market-features.yml --ref main -R Dtwosam/FMP`

The outcome command is fixed to:

`gh workflow run phase8a-exp044-market-outcomes.yml --ref main -R Dtwosam/FMP -f feature_run_id=<exact successful feature run id>`

No alternative branch or workflow path is accepted by the helper.

## 7. Result boundary

A successful `gh workflow run` submission means only that the dispatch request was submitted.

The helper explicitly does not claim that:

- a workflow run exists yet;
- the run succeeded;
- feature evidence exists;
- outcome evidence exists;
- DEC-074 readiness exists;
- model fitting is authorized.

Those states still require authoritative GitHub Actions evidence.

## 8. Safety boundary

DEC-081 does not change any workflow trigger or research rule.

It does not authorize:

- model fitting;
- model selection;
- promotion;
- shadow trading;
- demo orders;
- broker mutation;
- live orders;
- real-money trading.

## 9. Next gate

The next hard gate remains the first authoritative manual dispatch of `phase8a-exp044-market-features` from merged `main`.

DEC-081 only makes that existing manual gate safer and reproducible.
