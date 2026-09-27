# Phase 8A — EXP-062 Experiment Identity Propagation

**Date:** 2026-09-27  
**Status:** SOURCE-ONLY IDENTITY PROPAGATION / EXECUTION LOCKED  
**Decision:** DEC-294  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-293

## Purpose

DEC-294 makes the discovery protocol, pattern miner, and cell-evidence layer explicitly experiment-aware while preserving EXP-061 as the exact default identity.

This is required because EXP-062 is a new experiment. Repaired results must never reuse EXP-061 pattern/evidence identities.

## Backward-compatible defaults

The existing public defaults remain:

`EXP-20260927-061`

Calling the protocol, miner, or cell-evidence functions without an explicit experiment id retains EXP-061 semantics.

Focused tests require:

- implicit EXP-061 protocol payload equals explicit EXP-061 payload;
- implicit EXP-061 protocol fingerprint equals explicit EXP-061 fingerprint;
- implicit EXP-061 pattern fingerprint equals explicit EXP-061 fingerprint;
- implicit EXP-061 cell evidence equals explicit EXP-061 cell evidence.

## EXP-062 identity

EXP-062 passes:

`EXP-20260927-062`

explicitly.

The experiment id is included in:

- protocol payload/fingerprint;
- pattern fingerprints;
- discovery-miner shortlist fingerprints;
- cell evidence;
- nested cell-evidence fingerprint validation.

Therefore identical market pattern definitions under EXP-061 and EXP-062 have distinct immutable fingerprints.

## Cross-experiment rejection

An EXP-062 cell evidence object validates only when the caller supplies EXP-062 as the expected experiment id.

Validation under the default EXP-061 identity fails closed.

Empty experiment ids also fail closed.

## Frozen implementation

Protocol:

`src/fmp/discovery/pattern_protocol.py`

Git blob:

`eb91fcae9726a05e0513e4eab4c6f5dce37747c6`

Miner:

`src/fmp/discovery/pattern_miner.py`

Git blob:

`6216748e7faac95a0f5b510033d395a156d4bbf4`

Cell adapter/evidence:

`src/fmp/discovery/market_learning_adapter.py`

Git blob:

`5c73de45ca4704811623ff6d879abcf0009693b8`

Focused identity tests:

`tests/test_phase8a_exp062_experiment_identity_propagation.py`

Git blob:

`522ecc23b70d02b359d303690db975278857a349`

## Scope boundary

DEC-294 does not yet parameterize:

- aggregate evidence;
- run-contract workflow/artifact names;
- workflow source/runtime authorization;
- terminal review.

Those remain later EXP-062 gates.

## Locks

DEC-294 authorizes no:

- historical source/result execution;
- workflow dispatch;
- discovery result;
- reserved 2023-2026 robustness access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading.

## Next gate

The next source gate is EXP-062 aggregate/run-contract identity:

- aggregate evidence must require EXP-062 cell evidence;
- aggregate protocol fingerprint must use EXP-062;
- workflow/job/artifact names must be EXP-062-specific;
- execution must remain locked.
