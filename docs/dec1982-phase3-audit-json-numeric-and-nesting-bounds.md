# DEC-1982 — Bound audit JSON numeric parse and nesting failures

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2230 `5513c4722206f85da0daeaa2b613048d03340e0f`.

The optional Phase3 artifact audit's JSON loader already rejects duplicate object keys and spelled `NaN`/`Infinity` constants. However Python JSON parsing can silently turn a valid-looking numeric exponent `1e309` into a non-finite float. If this appears in an otherwise ignored metrics field, the audit could certify a self-rehashed file that the writer's `_jsonable` contract would reject. Very large integers or deeply nested JSON can also bypass controlled audit errors.

Use parser callbacks to refuse non-finite floats and integers exceeding the writer's 512-bit ceiling, checking digit length before potentially expensive integer conversion. Convert parser-recursion errors into bounded audit ValueErrors. Three synthetic methods forge and rehash unknown metric fields containing overflowed exponent numbers, 200-digit integers and 2000-level nested arrays. Low-level digest verification still sees matching SHA256, but the separate opt-in audit must refuse them.

**7,047 cumulative proposed source-defined tests** (+3), not an independently confirmed full-suite pass. Own exact-head Phase3 and historical/general CI required. Old failures remain FAIL. Phase8A #779/#820/#821 and eight independent administrator/source/installed-job/real-runner/provenance/inventory/human-approval proofs missing. No protected research, merges, runner/ref/workflow changes, broker orders or capital.
