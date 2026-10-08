# DEC-617 — Inert protected-2023 tag-ref guard rehearsal

**Decision:** DEC-617. **Release state:** source-only design validation, not an active guard, tag, workflow patch, immutable-ref witness, or dispatch authorization.

## Source binding

DEC-616 merged in PR #785 at main 4144f9ba783511fdde51456bbe81f45a40b5e8ca after full exact-head CI success. The open security blocker remains issue #779. The next reserved research run is exactly the annual 2023 run 385 / attempt 1, preceded by successful 2022 freeze run id 37663157285. Run 385 has not been dispatched.

The installed workflow .github/workflows/phase8a-annual-pattern-catalogue.yml remains Git blob 09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1. Each of annual_preflight, annual_cell (18 matrix instances) and annual_freeze checks exact main-branch GITHUB_REF. In each job event/ref checks precede pinned package install, authorization and data/artifact download. **DEC-617 does not edit or bypass these active guards.**

The 2023 authorization gate blob cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191 validates the shape of code_commit and the one-shot run identity but does not itself bind code SHA to one specific future reviewed immutable tag. A tag design needs this reviewed SHA/ref binding, not only changed YAML. Annual runtime blob 0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3 stays unchanged.

## Offline behavior

DEC-617 adds a stdlib-only offline rehearsal that verifies the exact existing workflow source and guard ordering. Its synthetic predicate tests a hypothetical ref and code SHA with event workflow_dispatch, tag namespace refs/tags/fmp/phase8a/2023/run385/<suffix>, segment 2023, run 385, attempt 1 and predecessor 37663157285. Tests reject wrong event/ref/SHA, branch impersonation, wrong year, number 386, attempt 2, ambiguous types and wrong predecessor.

Identifiers supplied to the synthetic predicate are test strings, not GitHub admin evidence. Even a synthetic match keeps: active_workflow_tag_compatible=false, candidate_guard_installed=false, runtime_amendment_authorized=false, workflow_amendment_authorized=false, immutable_tag_proven=false, annual_workflow_dispatch_authorized=false, dispatch_blocked=true, dispatch_action_executed=false and trading_authorized=false.

The assess-only CLI emits a fingerprinted report, refuses conflicting output overwrites, does not call any GitHub API and cannot create tags, change branch settings, dispatch annual research or trade.

## Required separate future approval

1. Separately authorize exact workflow/runtime source amendment. Verify new ref+GITHUB_SHA binding for all three jobs and authoritative 2023 runtime before protected historical reads.
2. Retest identity and effective authorization on actual GitHub runtime; preserve frozen historical provenance, 18-cell matrix, preflight and freeze receipts, and single run-385 attempt semantics.
3. Obtain authenticated admin evidence of exact tag rules, full inherited rule scope, update/deletion restrictions, no usable bypass, and continuous immutability throughout server dispatch. A positive DEC-616 static candidate is not sufficient.
4. Confirm run 385 remains unconsumed and obtain a separate explicit one-shot action decision before execution. An ambiguous submission is not grounds for retry.
5. Inspect every resulting job, source SHA and artifact hash before declaring any research result accepted. Keep 2024+, cross-year comparisons, strategy promotion, Phase 8B, broker mutation and trading locked.

The alternative exclusive-main branch lock route under issue #779 remains possible only with equally authoritative administrator evidence.

## Inert example

The offline command accepts a hypothetical candidate ref and 40-digit lowercase commit SHA and writes only a local assessment:

    PYTHONPATH=src python scripts/phase8a_annual_pattern_catalogue_2023_tag_ref_guard_rehearsal.py assess --candidate-tag-ref refs/tags/fmp/phase8a/2023/run385/reviewed-v1 --reviewed-commit-sha aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa --out /tmp/dec617-synthetic-rehearsal.json

The all-a SHA is a **test fixture**, not a real approved commit.

Documentation: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_dispatch
