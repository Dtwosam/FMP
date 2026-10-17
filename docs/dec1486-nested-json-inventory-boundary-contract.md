# DEC-1486 — Distinguish valid nested JSON object inventory from top-level shape

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Forward-only one-commit tests/docs child of #1731, exact parent `78bfc6648da8941e0fd8985d2e096a155a3a2e5e`. Ten synthetic regression methods: **2,109 proposed source-defined test methods**.

## Verified historical CI failure

#1730's full historical/general suite completed with exactly one failure in the inherited #1729 boundary test `test_boundary_object_depth_reaches_shape_check`. A legal, 512-level nested JSON object was decoded as a Python `dict`, then correctly rejected by `review_bundle_envelope` as `BUNDLE_KEY_INVENTORY_UNREVIEWED`, not `BUNDLE_SHAPE_UNREVIEWED`. The source code and parser were behaving correctly; the test asserted the wrong contract. This draft changes only that false expectation and its test name.

## Regression coverage

Ten new methods distinguish JSON grammar errors, valid objects missing the required 15-category envelope, and scalar/array top-level shape failures. Exact and over-limit object/mixed nesting, duplicate keys, unmatched delimiter types, quoted keys containing brackets, and permanently false annual admission are covered. No relaxation of the 512-level lexical cap or of the bundle category contract. Never echo untrusted input.

Own head-associated PR merge-checkout Phase 3 and full historical/general CI plus qualified independent review required. DEC-650/#820 independent protected-original OS no-write and DEC-651/#821/#779 immutable exclusive one-shot 2023 run385/attempt1 GitHub server admission remain **BLOCKED**. No protected data/artifacts, annual dispatch/retry, installed workflow/security changes, merges, deployment, or trading.
