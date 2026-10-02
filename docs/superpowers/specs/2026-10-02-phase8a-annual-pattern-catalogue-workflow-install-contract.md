# Phase 8A Annual Pattern Catalogue Workflow Installation Contract

**Decision:** DEC-479  
**Experiment:** EXP-20261002-067  
**Status:** SOURCE-ONLY INSTALL CONTRACT / REPOSITORY MUTATION LOCKED  
**Source workflow:** DEC-478 head `aaf4ea66b2b5b908228102dfa387aae7d03ea4d9`

## Purpose

DEC-479 freezes the exact future repository mutation required to install the dormant
DEC-478 annual-catalogue workflow source.

It does not perform that mutation.

## Exact source bindings

The installation contract binds the exact Git blob identities of:

- `src/fmp/discovery/annual_pattern_catalogue_workflow_source.py`;
- `scripts/phase8a_annual_pattern_catalogue.py`;
- `docs/superpowers/templates/phase8a-annual-pattern-catalogue.yml.disabled`.

The dormant source validator must still pass, and the reserved active workflow path
must still be absent.

Any source blob drift fails closed.

## Only allowed future mutation

The only allowed future repository change is:

- source:
  `docs/superpowers/templates/phase8a-annual-pattern-catalogue.yml.disabled`
- target:
  `.github/workflows/phase8a-annual-pattern-catalogue.yml`
- mutation kind: create target from the exact source bytes;
- target must not already exist;
- after installation, active bytes must exactly equal the frozen dormant template.

The dormant template, CLI, and workflow source contract are explicitly forbidden
from changing as part of that installation action.

## Current authority

DEC-479 does not authorize the repository mutation.

`REPOSITORY_MUTATION_AUTHORIZED` remains false, and
`require_repository_mutation_authorized()` fails closed.

The following also remain false:

- workflow template installation;
- workflow installed;
- workflow dispatch;
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

`SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT`

That gate may verify the exact current-main state and expose the one allowed install
action as evidence, but it must not perform the repository mutation.
