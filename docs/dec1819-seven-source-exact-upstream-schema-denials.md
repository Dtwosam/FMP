# DEC-1819 — Exact upstream source schemas before seven-source reporting

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2065 at `8a727c422ecf91904eb7f3740744c13ece22e8ff`.

The seven-source compiler previously checked required BLOCKED flags but projected out unknown upstream six-source or blank worksheet metadata. A source reporter could inject a fictitious `approved` field and still produce a clean-looking machine-readable BLOCKED index. Both upstream reports now require their exact independently reviewed top-level field sets, ordinary dict types and no unknown, missing or malformed fields **before** any projection.

Four new adversarial tests check injected six-source approval metadata, forged blank worksheet signoff, missing fields and a CLI that emits no JSON for rejected input (exit 2). Normal report remains irrevocably BLOCKED (exit 3). **6,651 cumulative proposed source-defined tests.**

This is only local reporting consistency; no live administrator or runner OS attestation, GitHub ruleset/ref/workflow amendment, protected 2023/run385/attempt1 research, demo/live broker activity or strategy profitability. Eight independent proof packages and #779/#820/#821 still MISSING/BLOCKED. Exact-head Phase3/full CI and qualified review required.
