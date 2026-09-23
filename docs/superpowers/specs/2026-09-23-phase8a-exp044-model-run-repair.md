# Phase 8A — EXP-044 Reviewed Model-Run Repair and Replacement Gate

**Date:** 2026-09-23
**Status:** APPROVED AFTER FAILED RUN 35891605645 AND BEFORE ANY REPLACEMENT
**Decision:** DEC-094
**Experiment:** EXP-20260923-044

## 1. Observed first-run evidence

DEC-093 authorized exactly one historical EXP-044 model workflow.

That run was:

- run ID: `35891605645`;
- workflow: `phase8a-exp044-model-training`;
- event: `workflow_dispatch`;
- branch: `main`;
- head SHA: `e97fa03d0e94fd505d0f926eb730e01a41947880`;
- run attempt: 1;
- final status: `completed`;
- conclusion: `failure`.

The authorization preflight succeeded, including the main-only guard, first-run guard, frozen-source checks, exact Python/runtime installation, and authoritative execution gate.

The run produced zero uploaded artifacts and no aggregate model-result evidence. The aggregate job was skipped because one or more matrix jobs failed.

No promotion, shadow, demo, broker, live, real-money, or trading authorization was created.

## 2. Complete failure inventory

The nine pair/timeframe matrix jobs exhausted under `fail-fast: false`.

Five jobs completed both frozen 60m and 240m model-cell calculations successfully but failed only at artifact upload:

- EURUSD 5m;
- EURUSD 1h;
- GBPUSD 15m;
- GBPUSD 1h;
- USDJPY 1h.

The upload failure was deterministic: results were written under the hidden directory `.results`, while `actions/upload-artifact@v6` defaulted to `include-hidden-files: false`. GitHub therefore reported that no files were found.

Four jobs failed inside the frozen model computation:

- EURUSD 15m;
- GBPUSD 5m;
- USDJPY 5m;
- USDJPY 15m.

All four computation failures were the same condition:

`sklearn.exceptions.ConvergenceWarning: lbfgs failed to converge after 2000 iteration(s)`

The DEC-090 training core converted that warning into:

`RuntimeError: EXP-044 logistic regression failed to converge`

No separate computation failure class was observed.

## 3. What DEC-094 does not change

DEC-094 does not change DEC-088 model-selection information after seeing results.

It does not change:

- the logistic family;
- logistic penalty;
- `C`;
- solver;
- tolerance;
- intercept behavior;
- class weighting;
- random seed;
- `max_iter=2000`;
- preprocessing or standardization;
- histogram gradient boosting configuration;
- confidence thresholds;
- target;
- feature set;
- chronological splits;
- financial gates;
- tie-break order;
- no-refit rule;
- upstream feature/outcome/readiness artifacts.

No solver fallback, iteration increase, hyperparameter search, result-derived scaling change, family expansion, or threshold movement is authorized.

## 4. Family-level non-convergence handling

DEC-094 amends only training-core failure handling.

Each frozen family is still attempted exactly once on the fit split.

If the frozen logistic regression emits the same convergence failure at its unchanged 2,000-iteration ceiling:

- its family fit status is `FAILED_NON_CONVERGENCE`;
- failure reason is `LBFGS_MAX_ITER_REACHED`;
- no logistic probabilities are scored;
- its exact three 0.50/0.60/0.70 variants remain represented in evidence;
- those variants are marked `FAMILY_UNAVAILABLE`;
- each is ineligible for selection;
- no logistic fallback or refit occurs.

The already-predeclared histogram gradient boosting family may continue under its unchanged frozen configuration.

If HGB yields a passing frozen variant, normal selection/validation/retrospective-holdout logic continues unchanged.

This preserves non-convergence as negative model-family evidence rather than converting it into a tuned post-result model.

## 5. Artifact-upload repair

Both result-producing upload steps explicitly set:

`include-hidden-files: true`

This applies to:

- pair/timeframe `.results` artifacts;
- aggregate `.model-evidence/model-result-evidence.json`.

No result contents, naming, or evidence semantics are changed by this repair.

## 6. Reviewed failed predecessor

Run `35891605645` is the only reviewed failed model predecessor.

The replacement workflow preflight requires exactly one prior manual-main model run and verifies that it is:

- ID `35891605645`;
- status `completed`;
- conclusion `failure`;
- head SHA `e97fa03d0e94fd505d0f926eb730e01a41947880`.

Any other prior-run set fails closed.

Therefore DEC-094 does not authorize a generic retry mechanism.

## 7. Replacement operator state

The read-only operator uses the existing reviewed-failure chain selector.

When the latest model run is exactly reviewed failed run `35891605645`, it may report:

`MODEL_RUN_REPLACEMENT_DISPATCH_REQUIRED`

with the same frozen model workflow dispatch command.

Only that stage carries model-result/fit/dispatch authorization true.

After a replacement exists:

- in-progress replacement -> `MODEL_RUN_IN_PROGRESS`;
- failed replacement -> `MODEL_RUN_REVIEW_REQUIRED`;
- successful replacement with verified aggregate evidence -> `MODEL_RESULT_REVIEW_REQUIRED`.

A failed replacement is not automatically reviewed for another replacement.

## 8. Source identities

DEC-094 keeps the DEC-088 protocol identity and DEC-091 artifact-runner source unchanged.

The repaired training-core Git blob is:

`e2c93370d1b4956c9a1e7103eee01ee9c4ec91c3`

The reviewed-replacement workflow Git blob is:

`37164e5d2dd06848e5f76ef50a6731017300beaa`

The execution gate validates these checked-out bytes before any replacement fit can run.

## 9. Result boundary

DEC-094 itself dispatches nothing and claims no model result.

The failed first run remains preserved in GitHub Actions history.

A replacement may run only after DEC-094 is merged and the read-only operator independently reports the reviewed replacement dispatch state.

Even a successful replacement produces retrospective model evidence only.

Promotion, shadow admission, demo orders, broker mutation, live orders, real-money trading, and trading authorization remain false pending a separate review decision.
