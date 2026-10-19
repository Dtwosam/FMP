# DEC-1666 — Unpaired UTF-16 surrogate refusal inside array-contained evidence objects

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent, one-commit tests/docs child of #1912 at `9f6771a25669c9db21fc41ad8a775de098722192`. Adds 25 synthetic regression tests (**4,212 proposed source-defined methods**).

A decoded JSON string containing a lone high (`\\ud800`) or low (`\\udc00`) UTF-16 surrogate is not a valid Unicode scalar value. This test matrix injects one such character into either a child **key** or a child **value** within each of six nested evidence-array paths: runs, jobs, PR comparison files, Phase 3 scenarios, full Git tree entries, and merge-parent records. The 24 negative cases cover high/low × key/value × six array locations. Python's basic JSON parser successfully decodes the test input, but strict bounded review must respond with the exact `BUNDLE_JSON_UNICODE_UNREVIEWED` verdict in text and stdin—not attempt downstream nested source review.

Each case preserves the original clean caller envelope, asserts safe verdict shape, no synthetic changed-file path echo, and that no independent original OS proof, exclusive server dispatch proof, or annual-run authority is granted. One clean source-only nonauthorizing control completes the tests.

Own exact-head Phase 3 and historical/general CI and qualified independent review required. Tests/docs only; no production/parser/resource-limit/workflow/security updates, protected original/archive/artifact access, annual dispatch/retry, merge/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
