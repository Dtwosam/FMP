# DEC-1985 — Align deeply nested JSON rejection with regression contract

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent child of #2233 at `0779f36cfc55633fb21faa7b0d64bac35b572f78`.

CI evidence: full historical/general suite PASS for #2225–#2230; full-suite FAIL for #2231 run 39527644930 and #2232 run 39527885806 because their deep JSON test expected a ValueError while the parser accepted the input; full-suite FAIL for #2233 run 39528099666 because the newly added 64-depth JSON tree walker correctly refused the forged deeply nested metric but raised `artifact report exceeds JSON nesting depth`, while the previously committed test checked the older `nesting limit` message.

Retain the 64-depth defensive JSON tree validation; align its controlled ValueError wording to `nesting limit` so the original deep nested test asserts the refusal rather than brittle text. The #2233 writer-parity test also accepts this error wording. This is a **small controlled reporting verifier repair** only, not altered strategy, market-data assumptions, protected research or training.

No new test methods: inventory remains **7,053 proposed source-defined tests**. All historical failed CI remains FAIL. Own exact-head Phase3 and full historical/general suites must pass before this draft is treated as validated.

**DRAFT NEVER MERGE NEVER PROMOTE.** Phase8A #779/#820/#821 and eight external independently supplied security/approval proofs remain missing; protected 2023/run385/attempt1, later research, Strategy V1, installed runner/ref/workflow changes, demo/live broker, real capital and merges blocked.
