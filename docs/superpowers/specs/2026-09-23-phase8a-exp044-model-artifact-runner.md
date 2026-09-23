# Phase 8A — EXP-044 Artifact-Backed Model Runner Source

**Date:** 2026-09-23
**Status:** APPROVED — SOURCE IMPLEMENTATION ONLY; AUTHORITATIVE MODEL RESULT RUN STILL LOCKED
**Decision:** DEC-091
**Experiment:** EXP-20260923-044

## 1. Purpose

DEC-090 implemented the deterministic in-memory training/evaluation core. DEC-091 adds the source required to consume the already-persisted, already-verified EXP-044 feature and outcome artifacts without regenerating market data.

DEC-091 does not authorize an authoritative historical model fit. It adds no GitHub Actions model-training workflow, no model-training CLI, and no operator dispatch mapping.

## 2. Frozen upstream identities

The artifact-backed source is pinned to:

- DEC-088 protocol commit `a9305ba9c42b7224e5d4b3f7d26f268447cdf469`;
- DEC-088 protocol fingerprint `1caeec61c7b1a9a6863caafc4c3e85bc8cbcfd5f504f2f7473afe0d4b9c55605`;
- DEC-090 merged training-core commit `640274df9dcbefa0feee599bffdeb63a581db780`;
- feature run `35867307338`;
- feature code commit `b71912e254d2a597c0ef55b5e1b3b87b052039ea`;
- feature evidence artifact `10753455784`;
- feature evidence fingerprint `1288f0fa0ca62069d651f86c21ff9d799e46f24c2eac2b555f177ee2dcfa0815`;
- outcome run `35876715434`;
- outcome code commit `edeb43bb4de88923e3349caa8ace36350839ccb8`;
- outcome evidence artifact `10758027876`;
- outcome evidence fingerprint `b24ad576e8234870dabf73000dacd7053241bf9c2b23e9f15dc8125d40c17117`;
- readiness artifact `10757578276`;
- readiness fingerprint `412573f505ec7912ff934cc6338cf4591b604e0beddb2cb6abb79447c777b105`.

The nine exact feature-cell and nine exact outcome-cell GitHub artifact IDs and GitHub SHA-256 digests are frozen in source.

## 3. Readiness revalidation

The runner source does not trust the readiness fingerprint merely because the JSON contains the expected string.

It removes the fingerprint field, recomputes the canonical readiness SHA-256, and requires the recomputed value to equal the frozen readiness fingerprint.

It also requires:

- exactly nine readiness cells;
- exact feature/outcome code commits and evidence fingerprints;
- exact `fmp-market-feature-v1` / `fmp-market-outcome-grid-v1` identities;
- `RETROSPECTIVE_ALREADY_SEEN`;
- `data_preparation_complete=true`;
- protocol-source-open authorization true;
- model-result, model-fit, promotion, shadow, demo, broker, live, and real-money authorizations false.

## 4. Cell artifact verification

For each extracted feature or outcome cell directory, DEC-091 verifies `manifest.json` before any model calculation.

Each manifest is bound to the corresponding readiness cell through its manifest SHA-256 and processed Phase 2 manifest SHA-256.

Every listed parquet partition is then checked for:

- safe relative path with no path traversal;
- existence;
- exact SHA-256;
- exact byte size;
- positive declared row count;
- exact row count after parquet read;
- exact frozen column order.

Manifest artifact paths must be sorted and unique.

The concatenated frame must equal the declared total row count and the manifest schema fingerprint.

Authoritative full-history cells require exactly 140 listed monthly partitions. Feature coverage must remain 2015-01 through 2026-08.

## 5. Feature-specific checks

Feature cells additionally require:

- `fmp-market-feature-v1`;
- base definition `fmp-feature-v1`;
- retrospective evidence;
- `model_training_authorized=false`;
- exact row count and unique-key count from readiness;
- exact feature-generation code commit.

## 6. Outcome-specific checks

Outcome cells additionally require:

- `fmp-market-outcome-grid-v1`;
- exact feature manifest SHA binding;
- exact feature evidence fingerprint;
- exact source-feature row count;
- exact labeled-row count;
- horizons exactly 60m and 240m;
- slippage scenarios exactly 0.2, 0.5, and 1.0 pips per fill;
- `model_fit_authorized=false`;
- exact outcome-generation code commit.

## 7. Deterministic result evidence source

DEC-091 also freezes the aggregate model-result evidence format before any authoritative result exists.

The compiler requires exactly all 18 DEC-088 model cells, each with:

- DEC-090 training-core identity;
- DEC-088 protocol identity/fingerprint;
- retrospective evidence label;
- a valid per-cell result fingerprint;
- selection, validation, and retrospective-holdout status;
- all promotion/shadow/demo/broker/live/real-money flags false.

Cell ordering is canonical, so aggregate evidence is independent of input ordering.

The aggregate binds the upstream feature/outcome/readiness identities and has its own canonical evidence fingerprint.

## 8. Execution lock

`AUTHORITATIVE_MODEL_RESULT_EXECUTION_AUTHORIZED = False`.

The authoritative bundle runner checks this flag before loading cells or calling the DEC-090 model core and raises if it is false.

Therefore DEC-091 source cannot produce an authoritative historical model result.

Synthetic tests exercise artifact verification and evidence compilation only. DEC-090's synthetic-only model tests remain non-authoritative.

## 9. No regeneration

The future authoritative runner must consume the exact persisted feature and outcome artifacts from runs `35867307338` and `35876715434`.

It may not regenerate features, rematerialize outcomes, reacquire Dukascopy data, or silently substitute later artifacts.

## 10. Authorization locks

DEC-091 authorizes no:

- authoritative historical fit;
- model-protocol result;
- promotion;
- shadow campaign admission;
- demo order;
- broker mutation;
- live order;
- real-money trading.

## 11. Next gate

A later separate decision must bind the exact merged DEC-091 source commit before adding an executable model-training workflow or changing `AUTHORITATIVE_MODEL_RESULT_EXECUTION_AUTHORIZED`.

That later gate must verify the same upstream artifact metadata and readiness/protocol identities before exactly one result-producing workflow may be dispatched.
