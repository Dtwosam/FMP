# Phase 8A — EXP-045 Artifact-Backed Runner and Aggregate Evidence Source

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-045 HISTORICAL MODEL RESULT
**Decision:** DEC-097
**Experiment:** EXP-20260923-045

## 1. Purpose

DEC-095 froze the post-result-informed EXP-045 successor protocol.

DEC-096 implemented the deterministic source-only EXP-045 training/evaluation core.

DEC-097 freezes the artifact-backed loader boundary and deterministic aggregate-result evidence contract that a later separately authorized historical run may use.

DEC-097 remains source-only.

It does not create a CLI, GitHub Actions workflow, operator dispatch state, historical fit, model result, promotion, or trading authorization.

## 2. Frozen source dependencies

DEC-097 binds exactly:

- DEC-091 verified historical data-loader source Git blob:
  `27c0848d16722a22b4762f5842396c2aebc92bec`;
- DEC-094 failed-run review source Git blob:
  `2260ad4ad08a7e9874bd28030be977a3e71436f9`;
- DEC-095 successor protocol source Git blob:
  `44129fc5337fb55b9c7d81f5ba0561ea788bd264`;
- DEC-096 successor training-core source Git blob:
  `3f0bc1bfa9640d08175e72cdf131bb97c94d562c`.

The DEC-097 runner source itself is frozen at Git blob:

`adebcc48130e8800741810c239528ef6c21eea6e`

The successor protocol fingerprint is recomputed at runtime.

Any drift in the bound dependency bytes fails closed.

## 3. Historical data reuse

EXP-045 does not reacquire or rematerialize market history.

It reuses the already-persisted EXP-044 data-preparation evidence:

- feature run `35867307338`;
- feature aggregate artifact `10753455784`;
- feature evidence fingerprint `1288f0fa0ca62069d651f86c21ff9d799e46f24c2eac2b555f177ee2dcfa0815`;
- outcome run `35876715434`;
- outcome aggregate artifact `10758027876`;
- outcome evidence fingerprint `b24ad576e8234870dabf73000dacd7053241bf9c2b23e9f15dc8125d40c17117`;
- readiness artifact `10757578276`;
- readiness fingerprint `412573f505ec7912ff934cc6338cf4591b604e0beddb2cb6abb79447c777b105`;
- the same exact nine persisted feature-cell artifacts;
- the same exact nine persisted outcome-cell artifacts.

The reused readiness object remains an EXP-044 data-preparation artifact. DEC-097 treats it only as the verified historical source-data contract.

EXP-045 model-result evidence therefore records:

`source_data_experiment_id=EXP-20260923-044`

while model-result identity remains:

`experiment_id=EXP-20260923-045`

No reused historical data is recharacterized as untouched OOS.

## 4. Data-loader reuse boundary

DEC-097 reuses only the DEC-091 verified cell-loader functions for:

- authoritative readiness fingerprint validation;
- exact manifest identity;
- processed Phase 2 manifest identity;
- exact code-commit bindings;
- artifact-partition count;
- partition path safety;
- SHA-256;
- byte size;
- declared and actual row count;
- frozen column order;
- schema fingerprint;
- source feature/outcome cross-binding.

The old DEC-091 model-result compiler and old DEC-090 training function are not used to create EXP-045 model evidence.

The reused loader module is byte-bound so later changes cannot silently alter EXP-045 artifact consumption.

## 5. Authoritative runner fail-closed boundary

The source exposes an artifact-backed bundle runner for future use, but under DEC-097:

`AUTHORITATIVE_SUCCESSOR_MODEL_RESULT_EXECUTION_AUTHORIZED=false`

and:

`SUCCESSOR_MODEL_FIT_AUTHORIZED=false`.

The runner checks that authorization before:

- source dependency validation;
- readiness validation;
- artifact loading;
- calling the DEC-096 training core.

Therefore DEC-097 itself cannot produce a historical EXP-045 model result.

If a future decision opens execution, the runner must then validate the exact bound source blobs before artifact access.

## 6. Cell-result validation

The aggregate compiler requires all 18 exact DEC-095 cells.

Every cell result must bind:

- `EXP-20260923-045`;
- DEC-096 training-core version and decision;
- exact DEC-090 base-core blob identity carried by DEC-096;
- DEC-095 protocol version, decision, and fingerprint;
- DEC-088 base protocol fingerprint;
- predecessor failed model run `35891605645`;
- `prior_result_informed=true`;
- `untouched_oos=false`;
- retrospective evidence label;
- all model-fit/promotion/trading flags false.

The compiler recomputes each cell's canonical result fingerprint rather than trusting the supplied digest.

## 7. Family-fit evidence

Each cell must contain exactly the two frozen family identities.

A successful family fit requires:

- status `FITTED`;
- fit-attempt count 1;
- valid preprocessor fingerprint;
- valid model fingerprint.

The only permitted unavailable-family state is the DEC-095 predeclared logistic state:

- family `logistic_regression`;
- status `FAILED_NON_CONVERGENCE`;
- failure reason `LBFGS_MAX_ITER_REACHED`;
- fit-attempt count 1;
- retry authorization false.

Unexpected fit statuses fail closed.

Each cell must preserve exactly six family/threshold variant slots.

## 8. Chronology-state validation

The aggregate compiler accepts only logically valid successor chronology:

### No model family available

`NO_MODEL_FAMILY_AVAILABLE -> LOCKED_NO_MODEL_FAMILY -> LOCKED_NO_MODEL_FAMILY`

### No financial challenger

`NO_MODEL_CHALLENGER -> LOCKED_NO_SELECTION -> LOCKED_NO_SELECTION`

### Selected but validation rejected

`SELECTED -> REJECT -> LOCKED_VALIDATION_REJECT`

### Selected and validation passed

`SELECTED -> PASS -> PASS|REJECT`

Any impossible chain fails closed.

## 9. Aggregate evidence identity

The deterministic aggregate evidence records:

- evidence version 1;
- DEC-097 runner version/decision;
- DEC-096 core version/decision;
- merged DEC-096 commit `f30a233bdc8229b9141ce3aa7c8e1b57a598c437`;
- DEC-096 core source blob;
- DEC-095 protocol version/decision;
- merged DEC-095 commit `f9c8a069076e1612c5d140dc85dffb83e100da6b`;
- DEC-095 protocol source blob/fingerprint;
- DEC-088 base protocol fingerprint;
- DEC-094 predecessor failure-review identity;
- failed run `35891605645` and its head SHA;
- `prior_result_informed=true`;
- `untouched_oos=false`;
- source-data EXP-044 evidence identities;
- all 18 exact cell-result fingerprints and chronology states;
- family fit status for logistic and HGB;
- the future execution code commit;
- all result/fit/promotion/trading locks false.

The aggregate evidence itself receives a canonical SHA-256 fingerprint.

Cell ordering is canonical, so result order from callers does not change the aggregate evidence.

The persisted-evidence validator removes the supplied aggregate fingerprint, recomputes canonical SHA-256, requires the exact future execution commit, revalidates all fixed protocol/core/predecessor/source-data identities, requires all 18 canonical cell summaries, validates chronology chains and family-fit statuses, and keeps every promotion/trading flag false.

A file loader performs the same validation before returning persisted aggregate JSON to any later operator/review layer.

## 10. Write semantics

The evidence writer is deterministic and conflict-sensitive.

Writing identical evidence to the same destination is idempotent.

Existing different content at that path fails closed.

## 11. Authorization locks

DEC-097 keeps:

- authoritative successor result execution false;
- successor model fit authorization false;
- model protocol result authorization false;
- promotion false;
- shadow false;
- demo-order false;
- broker mutation false;
- live-order false;
- real-money false;
- trading false.

No EXP-045 workflow exists or is dispatched.

## 12. Next gate

A later separate decision may freeze a manual EXP-045 workflow, CLI, and execution-gate source around the exact merged DEC-095/096/097 identities.

That source must remain non-executable until another separate result-authorization decision.

No historical EXP-045 result may be inferred from DEC-097 source or synthetic tests.
