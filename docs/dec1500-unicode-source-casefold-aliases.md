# DEC-1500 — Reject source-map case-fold path collisions

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent, one-commit tests/docs child of #1745 at `f33a58c0941df16ff7b739200b364b7d247a6fae`. Nine synthetic methods: **2,244 proposed source-defined test methods**.

DEC-1493/1494 normalize the *validity* of each individual source label, but allow two different keys in the same source bytes map whose Unicode `casefold()` results are equal. Such labels can alias on case-insensitive file systems, making offline source-evidence comparison ambiguous. For each of the `changed_bytes_b64` and `ci_workflow_bytes_b64` maps, reject any repeated casefold label using `BUNDLE_SOURCE_CASE_COLLISION_UNREVIEWED` without reading a file or rewriting the original label. Check after canonical path validation, before Base64 decoding. Map cardinality and path length are independently bounded.

Nine tests cover ASCII case aliases in both maps, Unicode sharp-s and accented case aliases, distinct paths/extensions, traversal rejection, stdin output non-disclosure, and an unchanged clean source-consistency-only fixture. This is a conservative reviewer contract; it is not proof of a repository's original OS protection or immutable GitHub server authorization.

Own exact-commit Phase 3/full historical/general CI and independent qualified review mandatory. DEC-650/#820 witnessed original-file OS no-write and DEC-651/#821/#779 exclusive immutable protected 2023 run385/attempt1 server admission remain **BLOCKED**. No protected run/retry, original/archive/artifact access, workflow/security changes, merges, deployment or trading.
