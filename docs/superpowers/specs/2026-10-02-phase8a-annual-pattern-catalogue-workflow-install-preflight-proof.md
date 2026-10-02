# Phase 8A Annual Pattern Catalogue Workflow Install Preflight Proof Contract

**Decision:** DEC-481  
**Experiment:** EXP-20261002-067  
**Status:** SOURCE-ONLY PROOF CONTRACT / REPOSITORY MUTATION LOCKED  
**Source preflight:** DEC-480 head `3eb2886530adfa5f27ddb49ed32d0294a4bc2432`

## Purpose

DEC-481 defines the exact evidence contract for a future repository-hosted,
read-only proof of the DEC-480 workflow-install preflight.

It does not create the proof workflow, install the annual catalogue workflow,
dispatch that workflow, read historical market artifacts, execute catalogue mining,
or produce annual catalogue results.

## Source binding

The proof contract binds the exact Git blob of:

`src/fmp/discovery/annual_pattern_catalogue_workflow_install_preflight.py`

Any preflight-source drift fails closed.

The supplied DEC-480 preflight must pass its own full semantic validator before a
DEC-481 proof can be compiled.

## Repository-hosted identity

A valid future proof must bind one exact successful proof run.

The run must have:

- the frozen proof workflow name;
- the frozen proof workflow path;
- event `workflow_dispatch`;
- branch `main`;
- head SHA equal to the validated DEC-480 preflight's exact expected main SHA;
- run attempt 1;
- completed status;
- successful conclusion;
- exact caller-supplied positive run ID.

The separately supplied main-branch metadata must resolve to the same exact commit.

This prevents a proof from being attached to a different branch, moving main head,
different workflow, failed run, or rerun.

## Bound preflight evidence

The proof binds:

- DEC-480 preflight fingerprint;
- DEC-480 embedded install-action fingerprint;
- exact main head;
- exact proof run ID;
- exact proof workflow identity;
- exact proof-run event, branch, head SHA, attempt, completed status, and successful conclusion.

Those run-provenance fields are retained inside the frozen proof itself and are
semantically revalidated after fingerprint verification. A rehashed hand-built proof
therefore cannot drop or alter the successful manual-run facts.

The proof itself receives a canonical SHA-256 fingerprint.

Rehashing a changed authority field does not bypass validation because authority
fields are checked semantically after fingerprint validation.

## Authority

DEC-481 keeps false:

- repository mutation;
- annual workflow installation;
- annual workflow installed;
- annual workflow dispatch;
- historical artifact reads;
- historical annual catalogue execution;
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

`SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_PROOF_WORKFLOW_SOURCE`

That gate may define the read-only proof workflow source required to generate this
evidence contract, but it must not install or dispatch the annual catalogue
workflow or open historical execution.
