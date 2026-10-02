# Phase 8A Annual Pattern Catalogue Workflow Installation Preflight

**Decision:** DEC-480  
**Experiment:** EXP-20261002-067  
**Status:** SOURCE-ONLY READ-ONLY PREFLIGHT / REPOSITORY MUTATION LOCKED  
**Source install contract:** DEC-479 head `95750234d3bce325563f15c605c2312756562ee6`

## Purpose

DEC-480 defines a read-only repository preflight for the future DEC-479 workflow
installation action.

It proves that the exact install contract and source files are present, that the
expected `main` head is being inspected, and that the reserved active workflow path
is still absent.

It does not install a workflow, mutate the repository, dispatch a workflow, read
historical market artifacts, execute the annual catalogue, or produce results.

## Exact source validation

The preflight validates:

- the exact Git blob of the DEC-479 install-contract source;
- all exact DEC-479 source bindings;
- the exact dormant workflow template blob;
- the exact dormant CLI and workflow-source blobs transitively through DEC-479;
- continued absence of
  `.github/workflows/phase8a-annual-pattern-catalogue.yml`.

Any source drift fails closed.

## Main-branch identity

The caller must provide read-only branch metadata whose:

- branch name is exactly `main`;
- commit SHA exactly matches the supplied expected head SHA.

A different branch, malformed branch metadata, or main-head drift fails closed.

This binds any later repository-hosted proof to one exact main commit rather than
to a moving branch name.

## Install action fingerprint

DEC-480 embeds the full DEC-479 install-action payload and computes a canonical
SHA-256 fingerprint over it.

The install action itself still states that repository mutation is unauthorized.

The separately reported `install_sources` evidence must exactly equal the semantically
validated DEC-479 `source_validation` payload. Rehashing a substituted source-evidence
block therefore fails closed even when the outer fingerprint is recomputed.

A validator recomputes both:

- the outer DEC-480 preflight fingerprint;
- the embedded DEC-479 install-action fingerprint.

Rehashing a tampered preflight does not permit an authority escalation because all
authority fields are checked semantically after fingerprint validation.

## CLI surface

The preflight CLI exposes only:

`plan`

It has no:

- install command;
- execute command;
- dispatch command;
- advance command.

The `plan` command reads supplied main-branch metadata, builds the read-only
preflight, validates it, and writes only the preflight JSON output.

## Authority

The following remain false:

- repository mutation;
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

`REPOSITORY_HOSTED_READ_ONLY_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_PROOF`

A later gate may run this exact preflight against repository-hosted read-only
metadata and freeze the proof. It must not install or dispatch the workflow.
