# DEC-1781 — Verify installed pre-authorization commands, not only step labels

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent child of #2027 at 3f1a249ca78ac93bb623464cff212f543a5c50f4.

DEC-1779/1780 documented the three annual jobs' source checkout, Python setup and pinned runtime installation before their in-run authorization check, and preflight's earlier read-only metadata requests. Labels alone can conceal a changed command. This draft inspects the source `uses` and `run` payload of the same pinned installed workflow, verifies checkout/setup/Python 3.12.14/pinned install, mutable main-ref check, in-run execution command and source metadata fetch plus preflight validation.

It records the actual static payload and zero-indexed step position, but explicitly **does not authenticate the real runner or prove effective early admission**. The source-only diagnostic remains BLOCKED with nonzero exit 3, invalid file exit 2, and cannot dispatch or authorize run385. 9 additional targeted tests (6524 cumulative proposed source-defined) reject changed checkout, install, main check, GITHUB_SHA parameter, metadata API source, and validation command.

Independent admin no-bypass GitHub controls (#779), runner OS and immutable-ref remediation review (#820/#821), full one-shot inventory and separately scoped human action remain absent. No protected annual data, workflow/ruleset/ref change, broker/demo/live orders or trading. Exact-head Phase3/full CI and qualified review required.
