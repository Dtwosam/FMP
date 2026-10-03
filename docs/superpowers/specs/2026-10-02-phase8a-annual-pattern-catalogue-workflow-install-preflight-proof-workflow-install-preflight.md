# Phase 8A Proof-Workflow Installation Preflight

**Decision:** DEC-484  
**Experiment:** EXP-20261002-067  
**Status:** SOURCE-ONLY READ-ONLY PREFLIGHT / REPOSITORY MUTATION LOCKED  
**Source install contract:** DEC-483 head `dedbe26106bbc791e8d13dea49656fcad14bc121`

## Purpose

DEC-484 defines a read-only repository preflight for the future DEC-483
proof-workflow installation action.

It does not perform repository mutation, install the proof workflow, dispatch any
workflow, read historical market artifacts, or execute annual catalogue research.

## Exact source checks

The preflight requires:

- the exact DEC-483 install-contract source blob;
- the full semantically validated DEC-483 source report;
- the exact DEC-482 proof-workflow source and pinned dormant template transitively;
- the exact DEC-481 proof-contract and DEC-480 plan-only CLI dependencies transitively;
- the reserved active proof-workflow path to remain absent.

Any source or target-state drift fails closed.

## Main-head binding

The caller supplies current `main` branch metadata plus one expected head SHA.

The branch must be exactly `main`, and its commit SHA must equal the supplied
expected head. A different branch, malformed metadata, or moving main head fails
closed.

## Install action evidence

DEC-484 embeds the full DEC-483 install-action payload and computes a canonical
SHA-256 fingerprint over it.

The preflight independently fingerprints itself, requires an exact top-level key
set, semantically validates the DEC-483 action, and requires the separately
reported install-source evidence to exactly match the validated action evidence.

Rehashing authority changes, nested target/source changes, source-report
substitution, or extra fields therefore fails closed.

## CLI surface

The preflight CLI exposes only:

`plan`

It has no install, execute, dispatch, or advance command.

## Finite bootstrap rule

DEC-484 terminates proof-workflow installation recursion. A read-only proof workflow
must not require another proof workflow to prove installation of the workflow that
would produce that proof.

After this preflight is merged and green, the next gate is an explicit operator
authorization for the single DEC-483 mutation: create the exact read-only proof
workflow from the frozen dormant-template bytes. That authorization is separate
from this preflight and is not implied by CI success.

## Authority

`proof_workflow_install_operator_authorization_required` is true.

Repository mutation, proof-workflow installation/dispatch, annual-workflow
installation/dispatch, historical artifact reads, annual catalogue execution,
historical result production, next-segment execution, cross-year result production,
Strategy V1 synthesis, promotion, Phase 8B, demo/live, broker mutation, real-money
action, and trading remain false.

## Next gate

`EXPLICIT_OPERATOR_ANNUAL_PATTERN_CATALOGUE_PROOF_WORKFLOW_INSTALL_AUTHORIZATION`

That gate may authorize only the exact DEC-483 file-creation mutation. It must not
authorize proof-workflow dispatch, annual-workflow installation/dispatch, or
historical annual-catalogue execution.
