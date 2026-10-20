# DEC-1923 — Canonical trade artifact structure and chronology

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2171 at `0081bf0853383b9f149bf229f741400bb4ce290d`.

`TradeRecord` is a frozen dataclass but has no constructor-level field validation. A fabricated `BacktestRun` could otherwise publish trade evidence with an invalid identity, unsupported FX pair, stringified direction/exit reason, Boolean/oversized position units or a non-UTC/backdated exit. The artifact writer now validates bounded printable trade/decision IDs, supported symbol, exact directional/exit enums, supported positive integer units and UTC/nonbackward timestamps before output creation. Same-bar close remains permitted. Earlier metric amount and evidence JSON guards remain in force; this does not independently validate trade profitability or historic input provenance.

Three synthetic regression methods cover malformed trade identities/enums/size, bad/backdated timestamps without artifact output, and valid same-bar synthetic close. **6,931 cumulative proposed source-defined methods**. Own exact-head Phase3/full historical-general CI and qualified evidence review required.

External Phase8A #779/#820/#821 and eight independent security proofs still MISSING/BLOCKED. Protected 2023/run385/attempt1, later discovery, Strategy V1 economics, shadow/demo/live broker capital and installed GitHub workflow/ref/ruleset/runner changes are not authorized. No protected dispatch, trading or money.
