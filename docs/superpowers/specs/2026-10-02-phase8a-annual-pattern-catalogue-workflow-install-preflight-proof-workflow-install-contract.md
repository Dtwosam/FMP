# Phase 8A Annual Catalogue Install-Preflight Proof Workflow Installation Contract

**Decision:** DEC-483  
**Experiment:** EXP-20261002-067  
**Status:** SOURCE-ONLY INSTALL CONTRACT / REPOSITORY MUTATION LOCKED  
**Source proof workflow:** DEC-482 head `532ab82a6c028c4f4cdf47d9515f18ef83457c45`

## Purpose

DEC-483 freezes the exact future repository mutation required to install the
disabled read-only DEC-482 proof workflow.

It does not perform that mutation.

## Exact source bindings

The installation contract validates the full DEC-482 dormant source contract and
binds exact Git blobs for:

- the DEC-482 proof-workflow source module;
- the disabled proof-workflow template.

The DEC-482 source validation must also preserve its exact DEC-481 proof-contract
and DEC-480 plan-only CLI dependencies. The reserved active proof-workflow path must
remain absent.

Any dependency, source-module, or template drift fails closed.

## Only allowed future mutation

The only allowed future repository change is:

- source:
  `docs/superpowers/templates/phase8a-annual-pattern-catalogue-workflow-install-preflight-proof.yml.disabled`
- target:
  `.github/workflows/phase8a-annual-catalogue-workflow-install-preflight-proof.yml`
- mutation kind: create target from the exact source bytes;
- target must not already exist;
- after installation, active bytes must exactly equal the frozen dormant template.

The dormant template, DEC-482 source module, DEC-481 proof contract, and DEC-480
plan-only CLI are explicitly forbidden from changing as part of that installation
action.

The action payload has an exact top-level key set and semantically validates all
nested source and mutation evidence.

## Current authority

DEC-483 does not authorize repository mutation.

`REPOSITORY_MUTATION_AUTHORIZED` remains false, and
`require_repository_mutation_authorized()` fails closed.

The following also remain false:

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

`SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_PROOF_WORKFLOW_INSTALL_PREFLIGHT`

That gate may verify the exact current-main source state and expose the one allowed
proof-workflow installation action as evidence, but it must not perform the
repository mutation or open annual-catalogue execution.
