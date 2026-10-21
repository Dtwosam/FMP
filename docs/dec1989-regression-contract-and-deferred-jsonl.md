# DEC-1989 — Repair three exact-head historical/general failures

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Parent #2237, exact SHA `13b123dc821a9fa4acb6a8094981a55c48f3c0c3`.

Full general/historical regressions: #2234 FAILED (one wrong error-text expectation), #2235 FAILED (30 failures after eager JSONL canonicality check), #2236 FAILED (30 failures), #2237 FAILED (3 failures). Their statuses remain permanently recorded. On #2237 (run 39575251520) the three failures are:
1. **Deep nested JSON:** two tests asserted different wording for the same intended rejection. Keep the implementation's `JSON nesting limit` and update the earlier 70-level fixture's expectation only.
2. **Pretty rejection JSONL:** test constructed a multiline indented JSON object, not an independently parseable one-record-per-line JSONL row. Keep the parser's earlier precise `valid JSON` failure behavior, and change this canonical-format test to create a **single-line**, semantically valid JSON with spaced separators so the parser can reach the canonical-format rejection.
3. **Duplicate trade identifier:** an existing forged two-record fixture has noncanonical JSON spacing in its **first** otherwise-valid record and a duplicate identifier in its second record. The early canonicality refusal on record 1 obscured the downstream integrity violation. Defer JSONL byte-format refusal until the entire trade/rejection file has passed all per-row, cross-row, count and digest checks. Keep the same strict canonical bytes requirement and continue rejecting otherwise-valid noncanonical rows.

No new tests; cumulative inventory still **7,060 proposed source-defined methods**. Exact-head independent Phase3 and historical/general CI needed. This is a tested-by-CI repair proposal, not a declaration that the run passed.

No installed workflow changes, no protected 2023/run385/attempt1 dispatch, no security proof substitution, no demo/live broker activity or real capital, no merge. Phase8A issues #779/#820/#821 and eight independent external proofs remain blocked.
