# DEC-1691 — Repair malformed numeric precedence inventory fixture

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1937 at `c4d552a0d33af2ef24a29938c88042904bb03e04`.

The full historical/general CI run for #1929 failed to import `test_dec1478_portable_ci_source_bundle_envelope.py` because of an unmatched closing parenthesis in the inventory branch of `_assert_malformed_numeric_precedes_outer_fault` (line 17417 in #1929). The malformed root-member generator comprehension was never executable; even tests unrelated to the helper could not import this module.

This draft makes a minimal test-fixture-only syntax repair: iterate over the already sorted original evidence members, omit `schema` before serializing, use any malformed numeric replacement for its original category, and join the resulting serialized root fields. This preserves the existing precedence contract while restoring module importability. No tests are removed, no new test methods are added: **5,141 proposed source-defined methods**. It is a remediation candidate, **not yet a CI-verified checkpoint**.

Own exact-head Phase 3/full historical-general CI and independent qualified review required; earlier child drafts remain unverified until the corrected exact head runs successfully. No parser/production/limits/workflow/security updates, protected originals/archive/artifacts, annual dispatch/retry, merging/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 **BLOCKED**.
