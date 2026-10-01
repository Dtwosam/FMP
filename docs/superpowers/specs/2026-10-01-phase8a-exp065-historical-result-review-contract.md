# Phase 8A — EXP-065 Historical Result Review Contract

**Date:** 2026-10-01  
**Status:** SOURCE-ONLY REVIEW CONTRACT PREDECLARED / RUN IN PROGRESS  
**Decision:** DEC-467  
**Experiment:** EXP-20261001-065  
**Bound run:** 36905224184

## Purpose

DEC-467 predeclares how the only authorized EXP-065 historical run will be
reviewed after it reaches a terminal state.

The contract is deliberately result-agnostic. It binds the immutable run
identity and the already-frozen DEC-463 evidence semantics, but it does not
guess aggregate digests, evidence fingerprints, hypothesis outcomes, shortlist
contents, or any other result-dependent value while the run is still active.

No workflow mutation, dispatch, rerun, retry, replacement, artifact production,
historical execution, reserved-data access, candidate compilation, promotion,
Phase 8B, broker/order activity, real-money action, or trading authority is
introduced.

## Immutable run identity

The review contract binds exactly:

- run id: `36905224184`;
- workflow: `phase8a-exp065-pairwise-interaction`;
- workflow path: `.github/workflows/phase8a-exp065-pairwise-interaction.yml`;
- event: `workflow_dispatch`;
- branch: `main`;
- head SHA: `5faa733572576aa5a1c56176ac27c415eaaf6416`;
- run number: `1`;
- run attempt: `1`.

The bound head is merged DEC-466.

Any different run id, head, run number, or attempt fails closed.

## Frozen lineage

DEC-467 binds:

- DEC-466 merge:
  `5faa733572576aa5a1c56176ac27c415eaaf6416`;
- DEC-466 runtime authorization:
  `ccc99179a51145534e1b48b8520b2f743580c217`;
- DEC-466 read-only dispatch operator:
  `6a386c556e121d959ec1ea8bbb56dbb49b42dde2`;
- DEC-463 evidence contract:
  `ca68622ddfc9866f00569d558b2ab927be23686d`.

The DEC-463 protocol/miner lineage remains authoritative for every cell and
aggregate evidence object.

## Successful-run envelope

If the bound run concludes `success`, review requires exactly:

- 20 jobs;
- all 20 jobs completed successfully;
- job inventory = preflight + 18 frozen cell jobs + aggregate;
- 20 artifacts;
- exact artifact-name inventory = preflight + 18 cells + aggregate;
- every artifact non-expired;
- every artifact id positive;
- every artifact digest a valid SHA-256 digest.

The aggregate artifact id and digest are intentionally not predeclared. They are
result evidence and may only be frozen after the terminal run exists.

## Non-success terminal envelope

A failure, cancellation, or other non-success terminal conclusion still consumes
the one-shot slot permanently.

DEC-467 validates the immutable run identity for such a terminal outcome, but
does not reinterpret a non-success run as successful evidence production.

No rerun, retry, or replacement becomes available after a non-success outcome.

## Evidence review

For a successful run, all 18 cell evidence objects and the aggregate must first
pass the existing DEC-463 validators.

DEC-467 then cross-checks:

- exact run code commit on every evidence object;
- exact 18-cell EURUSD/GBPUSD/USDJPY × 5m/15m/1h × 60m/240m universe;
- exactly 760 nominal pairwise hypotheses per cell/horizon;
- aggregate cell fingerprints against the supplied cell evidence;
- aggregate evaluable/qualifying/deduplicated counts against each cell;
- aggregate shortlist/frozen inventories against each cell;
- global shortlist cap <=54;
- global frozen cap <=18;
- `RETROSPECTIVE_ALREADY_SEEN`;
- `untouched_oos=false`;
- `reserved_robustness_opened=false`;
- the frozen pairwise output kind.

The total nominal hypothesis count is therefore fixed at 13,680.

Result-dependent evaluable, qualifying, deduplicated, shortlist, and frozen
counts are not frozen until terminal evidence exists.

## Result-state mapping

The review contract derives only a descriptive retrospective result state:

- zero qualifying hypotheses:
  `ZERO_PAIRWISE_INTERACTION_QUALIFIERS`;
- qualifiers but no frozen carry-forward:
  `PAIRWISE_INTERACTION_QUALIFIERS_WITHOUT_FROZEN_CARRY_FORWARD`;
- one or more frozen retrospective carry-forwards:
  `PAIRWISE_INTERACTION_FROZEN_CARRY_FORWARD_PRESENT`.

These labels do not constitute validation, promotion, or trading authority.

## Authority boundary

The following remain false:

- rerun;
- retry;
- replacement;
- reserved robustness access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

The reserved 2023-01-01 through 2026-08-20 block remains closed.

## Source pins

Review-contract source:

`src/fmp/discovery/exp065_historical_result_review_contract.py`

blob:

`d10bade3857beaec6e977525b651e66156dce87e`.

Focused tests:

`tests/test_phase8a_exp065_historical_result_review_contract.py`

blob:

`eb4a43906a24b7b6301df732f108110895c6755d`.

## Next gate

After run `36905224184` becomes terminal:

`FREEZE_EXP065_HISTORICAL_RESULT_AFTER_TERMINAL_RUN`.

That gate may bind the observed terminal job/artifact inventory, aggregate
artifact identity/digest, raw aggregate JSON SHA-256, canonical evidence
fingerprint, protocol/upstream evidence fingerprints, all 18 cell fingerprints,
and the observed retrospective hypothesis counts.

Nothing in DEC-467 authorizes use of reserved data or a rerun.
