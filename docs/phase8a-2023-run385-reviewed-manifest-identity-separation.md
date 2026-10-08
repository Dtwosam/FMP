# DEC-625 — 2023 independently reviewed identity vs untrusted GitHub runner context

**Status: UNINSTALLED, SOURCE-ONLY, UNAPPROVED SYNTHETIC FIXTURE, NOT AN EXECUTION AUTHORIZATION.**

## Security question

DEC-622 checks whether hypothetical runner values match a frozen tag-ref, workflow name/ref and code SHA. DEC-624 identifies the three job admission/pre-install/pre-evidence boundaries where any future active check belongs. Neither model, however, authenticates where its **expected** ref and SHA came from. An unsafe implementation could compare `GITHUB_SHA` against a copy of `GITHUB_SHA` derived from the same runner environment, yielding a meaningless tautology. A maliciously moved tag could then appear valid while every self-reported string agrees.

**Reviewing an observed commit and deriving the approved expectation from the observed commit are separate actions.** A future real workflow must first receive a separately approved exact immutable identity tuple with independently authenticated provenance, and only then compare live event/ref/checkout/workflow identity against it. A string field saying “reviewed” in the runner context is not provenance.

## What the inert DEC-625 contract provides

An exact source-pinned fixed fixture containing the proposed tag-ref, code commit SHA, workflow definition SHA, named workflow, path and current Git blob identity, 2023 runtime path and Git blob identity, year 2023, research run 385/attempt 1 and predecessor 2022 run `37663157285`.

A separate fabricated GitHub runner observation contains event name, ref, ref type, checkout code SHA, workflow definition SHA, repository, workflow, workflow-ref path@tag, annual segment, run number and attempt, and predecessor run. Their equality is **only a deterministic synthetic string comparison**. The fixture ref `refs/tags/fmp/phase8a/2023/run385/dec622-unapproved-fixture` and fabricated SHA `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` are intentionally unapproved. They do not establish a real tag or an authenticated reviewed commit.

The predicate never builds an approved manifest from `GITHUB_REF`, `GITHUB_SHA`, `GITHUB_WORKFLOW_REF`, `GITHUB_WORKFLOW_SHA`, or a caller-supplied `provenance` label. It requires an exact compiled fixture rather than caller-selected expected values. Its **25 adversarial cases** reject missing/extra context and manifest fields, wrong run/attempt/ref/path/repository/year, type confusion, and a particularly important attack: *changing both the purported reviewed SHA and the observed SHA (or both refs) to the same new value*. Matching both sides alone is not independent provenance.

The report is pinned to the **unchanged installed** annual workflow Git blob `09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1` and 2023 authorization runtime Git blob `cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191`; it validates all three installed workflow job shapes. Its SHA-256 fingerprint is a deterministic report integrity checksum, **not a signature or approval**. Regeneration from exact source rejects re-fingerprinted forged permissions or JSON boolean/integer substitutions.

```sh
PYTHONPATH=src python scripts/phase8a_annual_pattern_catalogue_2023_review_manifest_identity_separation.py assess --out /tmp/dec625-review-manifest-separation.json
```

This command only audits the checkout and writes its report **outside** the checkout. It cannot install actual job conditions, mutate a tag, read GitHub permissions, grant research access, dispatch an annual run, retry an attempt or trade.

## What's still missing

1. A **real** administrator-backed continuously enforced immutable tag/ref with no bypass, validated using independently authenticated controls across the actual dispatch window. Current `main` remains unprotected and repository rulesets absent in the latest read-only observation.
2. A genuinely external, immutable reviewed expected identity tuple. **Do not obtain the expected SHA from the untrusted context being checked**, a mutable reference, or the reporting tool itself.
3. A separately approved and CI-reviewed **installed** three-job workflow amendment with job admission before checkout, exact trusted-ref/SHA check before setup/install, and checked 2023 runtime identity before any evidence metadata/API/artifact access.
4. Fresh annual workflow inventory, distinct one-shot action authorization, and fail-closed terminal handling for ambiguous dispatch responses. No attempt-2 or run-386 replacement.

Issue #779 remains OPEN. Any user-facing or machine-consumed DEC-625 report must retain `review_manifest_independently_authenticated=false`, `immutable_tag_proven=false`, `annual_dispatch_authorized=false`, `run385_action_authorized=false`, `trading_authorized=false`, `dispatch_blocked=true`. No future-year research, protected historical reads, cross-year synthesis, Phase 8B, brokerage, demo/live or real-money trading is authorized.
