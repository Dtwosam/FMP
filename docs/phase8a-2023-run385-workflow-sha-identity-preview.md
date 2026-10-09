# DEC-632 — offline workflow-definition SHA identity preview

This is an **inert regression model**, not an admission token, approval, installed runtime change, or authority to consume 2023 annual run 385. It does not call GitHub, create a tag, read protected historical data, or execute the annual catalogue workflow.

## Provenance gap

On pull_request, GitHub normally checks out a synthetic merge ref (refs/pull/N/merge) rather than the raw PR head. An "exact-head CI" claim therefore needs separate provenance for the actual tested merge tree. During the PR #796–801 audit, #797–801 merge trees equalled their source-head trees; #796's tree differed by two upstream-main files. This must not be conflated with a failed CI check or used as merge approval.

For a future *separately reviewed* immutable-tag design, **github.ref** identifies the selected branch or tag and **github.sha** its resolved commit; **github.workflow_ref** identifies the workflow path/ref and **github.workflow_sha** separately identifies the workflow definition's commit. Checking only the first three identities could miss a workflow-definition identity change. A matching tag spelling alone is not immutability proof. GitHub's workflow-dispatch REST ref accepts a branch or tag, not a raw commit SHA. The current installed annual workflow still explicitly accepts refs/heads/main in its preflight, cell, and freeze jobs, so this preview cannot execute it on a tag.

## Offline negative-path contract

The Python module in src/fmp/discovery/annual_pattern_catalogue_2023_workflow_sha_identity_preview.py checks a **fabricated, never-approved** repository/event/tag/commit/workflow-ref/workflow-SHA/run tuple. A fully matching tuple means only synthetic_exact_tuple_match=true; all dispatch, run 385, retry, and trading authorizations stay **false**. Its 22 adverse cases include workflow SHA changing while the tag and source SHA remain unchanged, source SHA changing while workflow SHA remains fixed, ref/path mismatches, missing fields, and forged authority metadata.

The resulting report is deterministic and source-bound; modifying a permission flag and recomputing a superficial SHA-256 still fails verification. This is *not* authentication: real admission needs externally attested reviewer approval, separately approved workflow/runtime amendments, no-bypass tag authority, server-ref/commit/workflow provenance checked before any protected read, and a separately authorized one-shot action. A job reporting Success because it was skipped is not proof of admission.

Official sources:
- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- https://docs.github.com/en/actions/reference/workflows-and-actions/contexts
- https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event

**Unaffected:** installed annual YAML, 2023 runtime authorization, GitHub ref/rulesets, research run 385, strategy/broker/trading permissions.
