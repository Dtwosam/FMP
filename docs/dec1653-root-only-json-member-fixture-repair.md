# DEC-1653 — Root-only serialized JSON member rewriting (CI repair)

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit tests/docs child of #1899 at `96203c6e2ed83f5d8350fc7bbcf1fef0ed347162`, preserving the exact-base lineage.

The #1899 general suite failed three synthetic tests: `test_portable_top_duplicate_tree_refused`, `test_portable_top_escaped_tree_equivalent`, and `test_portable_null_last_duplicate_tree_refused`. Those fixtures incorrectly assumed the JSON spelling `"tree":` occurs just once across an entire nested bundle. It appears seven times, including nested evidence objects; the reviewer code was not shown to be at fault.

This repair constructs the sorted canonical envelope at the **root member boundary**, replacing only the named outer key/value representation. It retains all nested members and avoids global string matching. Revisit the DEC-1646, DEC-1647, and DEC-1652 helpers; add two regression tests that enforce nested-tree preservation and caller-input immutability. Existing per-category JSON/stdin, grammar rejection, source-only and blocked annual-run assertions continue unchanged. **3,966 proposed source-defined unittest methods** (+2), subject to independent CI confirmation.

Tests/docs only: no production/parser/resource-limit/workflow/security gate code; no protected original/archive/artifact access, annual dispatch/retry, merging, deployment or trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
