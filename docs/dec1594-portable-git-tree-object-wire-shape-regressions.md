# DEC-1594 — Reject malformed full Git tree wire entries at portable ingress

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1840 at `bc275f79e9766beeff2f7ca3a594197d91c2b016`. Thirteen synthetic regression methods (**3,114 proposed source-defined methods**).

Git tree snapshots are not proof merely because they reference an expected path or include syntactically valid Base64 changed-source values. These tests inject out-of-order parent entries, uppercase/short/nonhex/missing/numeric Git entry SHAs, embedded separators and a NUL in leaf paths, a noncanonical `40000` tree mode, list-valued mode, non-array tree collections, and non-object entries. The source bytes and the flat `nodes` inventory are held intact. Assert specific existing `TREE_CHAIN_*` diagnostics and parity between direct-memory, JSON-text and bounded stdin reviews; no caller-supplied source-path echo or protected annual authority.

These are offline assertions on untrusted caller-provided evidence; no GitHub object is authenticated. Require own exact-head Phase 3/historical-general CI and qualified independent review. Tests/docs only; do not change production, parser/budgets, workflow/security/admission controls, protected originals/archives/artifacts, annual dispatch/retry, merge, deployment, or trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
