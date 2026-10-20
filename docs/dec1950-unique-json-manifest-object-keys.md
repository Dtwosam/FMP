# DEC-1950 — Deny duplicate JSON keys in Phase3 artifact manifest

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source/tests/docs child of PR #2198 `72b23cabd75acf304569dba6d01fea5dec91ddf7`.

Python's default `json.loads` silently overwrites an earlier duplicate object member. Manifest protocol or artifact path metadata could therefore contain ambiguous keys (including one `../outside` path followed by another ordinary name), undermining a precise review of financial evidence. The new read-only artifact verifier now parses all manifest JSON objects with `object_pairs_hook` that refuses any duplicated member name before protocol/filename/digest checks, without reading untrusted path targets. Valid writer-produced manifests continue to parse unchanged.

Two synthetic methods create duplicated top-level protocol members and nested duplicate artifact path members, both rejected as `ValueError`. **6,984 cumulative proposed source-defined methods**. Own exact-head Phase3/full historical-general CI and independent artifact-security review mandatory. This validates local bytes and schema only, not independently authenticated source inputs, runner OS or strategy profitability.

Historical #2178–#2191 full test failures remain FAILED. New #2192–#2198 full suites require exact-commit results. Phase8A #779/#820/#821 and eight independent external security proof packages remain MISSING; accepted catalogue through 2022/run384, protected 2023/run385/attempt1 and future years, Strategy V1 economics, shadow/demo/live brokers and capital, installed GitHub refs/workflows/rulesets/runners remain BLOCKED. No protected dispatch, merges, broker orders or profit.
