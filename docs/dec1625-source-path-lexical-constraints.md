# DEC-1625 — Reject unsafe source path spelling before decoding source blobs

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1871 at `f499468686342c16453726fc25a5b4245075645a`. Seventeen regression methods (**3,557 proposed source-defined methods**).

Change only the label of one otherwise unchanged, canonically encoded Markdown source blob. Sixteen synthetic path labels exercise absolute paths, Windows drives and separators, dot and parent traversal, consecutive separators, trailing dot/space, Windows device-name aliases, decomposed Unicode, zero-width format controls and Unicode slash confusables. All must reject at the portable input boundary as exactly `BUNDLE_SOURCE_PATH_UNREVIEWED` across direct-memory, JSON-text and bounded stdin, without echoing untrusted source paths or authorizing a protected annual run. A clean control preserves source consistency but no annual approval.

These are caller-controlled offline strings, not authenticated GitHub objects or protected OS/run evidence. Own exact-head Phase 3/full historical general CI and independent review required. Tests/docs only; no production/parser/resource-budget/workflow/security controls, original/archive/artifact access, protected annual execution/retry, merging, deployment or trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
