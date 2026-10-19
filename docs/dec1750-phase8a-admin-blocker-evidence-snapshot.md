# DEC-1750 — Read-only administrator blocker evidence snapshot

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent tests/docs-only child of PR #1996, SHA `0621fbf13d64aae10f15bea890232a0f33d0de46`.

## Newly observed blocker state (read only, 2026-10-19)

- GitHub `refs/heads/main` observed at `53e203133bbc141b2f48c7b8b8241d56b35166a3`, with branch `protected:false`.
- Repository ruleset list returned zero items. This observation **does not prove inherited organization rulesets were inspected**, or a future no-bypass lock.
- GitHub issue #779 documents the irreversible check-then-dispatch race: server-side `workflow_dispatch --ref main` can resolve a mutable ref *after* local SHA verification, consuming run385 on unreviewed code.
- Historical 2022/run384 remains the documented predecessor. **No fresh independently signed/current read of the ten-run inventory or run385 unconsumed state occurred in this draft.**
- This snapshot is time-limited. It is not evidence of conditions at an eventual action time and not a reviewer attestation.

## Two mutually exclusive possible remediation paths (both blocked)

1. Independently authenticated administrator enforcement of exclusive continuous `main` identity through the entire server-side dispatch, including all bypass/push/merge actors, ref deletion/recreation, and every requested lock interval; reauthenticate installed workflow, OS runner and historical provenance; then separately review the fresh one-shot.
2. Independently approved source-of-truth **immutable-ref execution amendment**, separately implemented, re-tested under exact installed three-job precheckout/preinstall/preaccess and runner isolation checks, and separately authorized as a replacement for the mutable-main path. No such amendment or workflow change is authorized by this draft.

The adjacent JSON records **eight external evidence requirements**, all currently **MISSING** with null proof reference and signoff. Independent qualified administrators and operators—not these source tests—must provide actual evidence, attest its freshness, review the permitted path and record a distinct human action decision. No secret evidence should be published in draft PR text. If any proof is missing, no action.

Adds **20** source-defined methods (**6274 proposed cumulative**) validating the source snapshot is immutable in its denials, retains exact run385 attempt1 identity, rejects duplicate JSON members and does not masquerade as trading approval. This is test/documentation only; CI green cannot unlock issue #779, #820 or #821.

No main/tag/ruleset mutation, protected history, annual read or dispatch/retry, Strategy V1 selection, cross-year evaluation, phase8b shadow, broker/demo/live orders or trading. Own exact-head Phase 3/full historical-general CI and independent qualified review still required.
