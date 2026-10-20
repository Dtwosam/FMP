# DEC-1971 — Audit stored trade and rejection chronology

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source/tests/docs child of PR #2219 at `4c120819de58de1098f0aa889b08dce8444820d9`.

The optional stored Phase3 audit now checks PnL arithmetic, trade/rejection identity and equity checkpoint chronology, but it previously accepted a self-rehashed trade whose exit timestamp preceded its entry or a rejection evaluated before the decision. Add a common ordinary UTC-marked ISO timestamp parser for the audit, also used by checkpoint validation. Require builtin UTC datetime meaning for trade entry/exit and rejection decision/evaluation JSON strings, with exit at/after entry and evaluated at/after decision. Preserve valid same-bar entry/exit and same-time rejection semantics.

Two synthetic methods forge and rehash a reversed trade entry/exit pair and a backdated rejection evaluation, both refused despite matching SHA256 manifest hashes. **7,018 cumulative proposed source-defined tests**. Own exact-head Phase3/full historical/general suites and qualified reporting review mandatory. This checks internal self-consistency only, not independently authenticated quotes, true economic returns or authorized protected research.

All older failed CI remains FAILED. Phase8A #779/#820/#821 and eight external independent administrator/ref/installed three-job early admission/privileged OS runner/DEC609–610 provenance/fresh 2023 inventory/separate human authorization proofs MISSING. Accepted historical catalogue stops 2022/run384. Protected 2023/run385/attempt1, subsequent annual discovery, Strategy V1 economics, shadow/demo/live brokers/funds and installed GitHub refs/workflows/rulesets/runners blocked. No protected dispatch, merges, trading or money.
