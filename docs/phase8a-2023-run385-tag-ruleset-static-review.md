# DEC-616 — Read-only tag-ruleset evidence-shape review for annual run 385

**Status:** source-only proposal; no tag, workflow/runtime edit, research dispatch or trading approval.
**Depends on:** merged DEC-615 / PR #784 at main d2123d505d1cb8065a3e5afe9f74e28d4b1d2f0e and open blocker #779.
**Alternative path:** independently witnessed exclusive main lock remains a separate possibility.

## Scope and reason

DEC-615 established that the installed annual workflow (Git blob
09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1) checks
GITHUB_REF=refs/heads/main inside **annual_preflight**, **annual_cell** and
**annual_freeze**. A workflow_dispatch ref pointing at a tag therefore fails
the existing workflow. No patched annual workflow is installed or approved.

GitHub supports tag rulesets restricting updates and deletion, but a ruleset
can have bypass principals, a target mismatch, uninspected inherited rules,
or an evaluation-only enforcement state. The input is not an authenticated
configuration witness merely because it is JSON copied from a REST endpoint.

DEC-616 adds an **offline, untrusted-input static shape checker**:
src/fmp/discovery/annual_pattern_catalogue_2023_tag_ruleset_static_review.py,
scripts/phase8a_annual_pattern_catalogue_2023_tag_ruleset_static_review.py,
and focused negative tests. It is intentionally incapable of releasing the
one-shot run-385 gate. Its only positive field, static_ruleset_candidate,
means caller-supplied data matches a deliberately conservative shape.

## Proposed namespace, not a created tag

The design-only namespace is refs/tags/fmp/phase8a/2023/run385/<suffix>
where suffix is a lowercase simple ref component. No specific final suffix or
commit is selected, blessed or created here. There is no API write.

For a candidate static match, the supplied tag-ref JSON must report the exact
full ref, type=commit (lightweight tag), and exactly the reviewed 40-digit
lowercase commit SHA. The supplied applicable ruleset collection must:

- explicitly include inherited rulesets and claim complete enumeration,
  with both claims treated as untrusted user-supplied metadata;
- contain at least one active **tag** ruleset with an **exact** include of
  this tag ref, no exclusions, an empty bypass_actors list, and both
  update and deletion restrictions inside that same ruleset;
- reject glob/prefix/~ALL conditions, missing attributes, evaluate mode,
  missing update/deletion restrictions or nonempty bypass lists.

GitHub may support alternative equivalent policy configurations. They are
intentionally not accepted as a static candidate without a separate review.

## Offline use

Capture the ref object and the **full details** of all applicable rulesets
(including inherited sources) independently with authorized read access.
For example, JSON input shapes are:

    {"ref":"refs/tags/fmp/phase8a/2023/run385/reviewed-v1",
     "object":{"type":"commit","sha":"<reviewed 40-character commit>"}}

    [{"target":"tag","enforcement":"active","bypass_actors":[],
      "conditions":{"ref_name":{
        "include":["refs/tags/fmp/phase8a/2023/run385/reviewed-v1"],
        "exclude":[]}},
      "rules":[{"type":"update"},{"type":"deletion"}]}]

Example assessment command (not a dispatch action):

    PYTHONPATH=src python \
      scripts/phase8a_annual_pattern_catalogue_2023_tag_ruleset_static_review.py \
      assess --tag-ref refs/tags/fmp/phase8a/2023/run385/reviewed-v1 \
      --reviewed-commit-sha <reviewed-40-hex-sha> \
      --git-ref-json tag-ref.json --rulesets-json applicable-rulesets.json \
      --includes-inherited-rulesets --enumeration-complete \
      --out dec616-static-review.json

Do not treat the flags as independent evidence of enumeration or validity.
The output has deterministic JSON SHA-256 fingerprinting and refuses to
overwrite conflicting files. An attacker controlling the input can produce a
positive static candidate; that candidate is **not an authorization**.

## Explicit non-authority and subsequent release gates

All reports, including positive static candidates, always retain:

- snapshot_authenticated=false, ruleset_enforcement_witnessed=false,
  bypass_permissions_independently_reviewed=false;
- immutable_tag_proven=false, exclusive_tag_lock_proven=false,
  annual_workflow_tag_compatible=false;
- source_runtime_amendment_reviewed=false,
  one_shot_dispatch_decision_present=false,
  annual_workflow_dispatch_authorized=false and dispatch_blocked=true;
- dispatch_action_executed=false, rerun/retry/replacement=false,
  run 386+/later years/cross-year work=false, broker/demo/live/real-money
  and trading authorization=false.

A real future tag path still needs (1) a separately reviewed and merged
workflow/runtime amendment for the three guards and exact GITHUB_SHA
binding, (2) independently authenticated and time-relevant repository/admin
policy evidence, effective exact-tag coverage and all bypass paths,
(3) verified tag target and immutability **throughout the server-side API
dispatch transaction**, (4) exact annual history and run-385 consumption
check, and (5) a **separate explicit one-shot action authorization**.
Pre- and post-dispatch checks alone cannot repair a race or ambiguous
submission. Never retry, rerun or replace run 385.

The exclusive-main-lock design under issue #779 remains the alternate route.
No source code in DEC-616 edits the protected annual workflow, creates a ref,
changes protection, accesses historical datasets, dispatches research or
trades.

GitHub reference:
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository
- https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event
