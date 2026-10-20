# DEC-1922 — Validate rejection evidence before Phase3 artifact publication

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2170 at `5e7bdfb879125e65ef9a2ffb58825ae3d5c9ac76`.

A `RejectionRecord` is structurally typed but has no constructor validation. The artifact writer could otherwise publish a record with an untyped or forged rejection code, malformed ID/symbol, nonstring/control-character explanation or non-UTC/backdated evaluation timestamp and still produce a manifest. Require ordinary bounded printable identifiers and explanations, exact supported FX symbol, genuine `RejectionCode` enum, canonical UTC datetime fields and evaluation not preceding the decision. Perform all checks before serialization or filesystem mutation. Normal synthetic NO_TRADE and timing rejection evidence remains compatible.

Three synthetic regression methods cover malformed rejection enums/identities, malformed explanations, and time spoofing/backdating with no artifact files created. **6,928 cumulative proposed source-defined methods**. Own exact-head Phase3/full historical-general CI and independent evidence review remain mandatory. These guards do not independently prove authenticated market provenance or broker approval.

Phase8A #779/#820/#821 and eight external administrator/ref/runner isolation/provenance/one-shot/human proof packages remain MISSING; protected 2023/run385/attempt1, later annual discovery, Strategy V1 economics, shadow/demo/Phase10/11 broker/live funds and installed GitHub ref/workflow/ruleset/runner changes BLOCKED. No protected dispatch, trading or profit claim.
