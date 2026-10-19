# DEC-1723 — AST regression guard for narrow pre-install CI exclusion

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent tests/docs-only child of #1969 at `239440d6be219ed5d72a2e90ed8009e4b3c49144`.

Adds **8 source-defined methods** (**5,884 proposed**). The historical/general workflow sets `FMP_PREINSTALL_SNAPSHOT=1` and intentionally omits the protected installed annual workflow from the reduced test tree. DEC-1722 specifically skips the 12 DEC-1716 source-pinned live-workflow-order assertions in that mode; it must **not** also skip when the source is unexpectedly absent in a normal checkout.

This AST-only guard reads the DEC-1716 **test source**, not the protected installed workflow. It runs in both reduced pre-install and ordinary checkouts and enforces: exact `@unittest.skipIf(os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1", ...)` predicate, no broad CI/missing-file skip, no swallowed missing-file exception, exact original workflow blob pin, all 12 unique method names, the core unsafe-order assertions still present, and absence of network/dispatch helper calls in the target test source.

A green AST guard is not actual execution of the 12 DEC-1716 source tests. Independent ordinary-checkout focused execution on the exact branch head remains outstanding and must not be inferred from historical/general CI skipping them. Correct external administrator/runner source approval and run-385 dispatch still require separate human gates under #779/#820/#821.

Only test and doc, zero installed workflow/security/parser/production changes, no protected historical-data read, annual run, retry, tag/branch/ruleset mutation, broker, demo/live or real-money trading. Own exact-head Phase 3/full historical/general CI and independent review required.
