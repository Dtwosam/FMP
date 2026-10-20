# DEC-1902 — Integrated synthetic engine admission rejects malformed input without I/O

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2150 `687aff3cbf510f2b6509bd56bc7004102487c485`.

The new QuoteBar, Decision and ScheduledExit validators must be invoked before the Phase3 engine consumes input data or performs any external work. Three tests exercise `run_backtest` with malformed members or malformed collection types at all three ingress points, while denying subprocess spawning, socket creation, built-in file opens and OS file opens. Each malformed request must result in a controlled contract `ValueError`. The tests operate only on constructed synthetic quote bars and decisions, not actual market data.

These mocks verify the tested Python path, **not real privileged runner isolation**, actual GitHub branch/ruleset protection, broker connectivity safety or independent evidence of market returns. Three new proposed source-defined test methods bring the total to **6,877**. No program was deployed and the lineage remains unmerged, requiring exact-head Phase3/full historical-general CI and qualified review.

External #779/#820/#821 remain open, all eight independent administrator/ref/OS/provenance/one-shot/human proofs MISSING. Protected 2023/run385/attempt1, later discovery and Strategy V1 economics, shadow/demo/live broker activity, real money and installed workflow/ref/ruleset changes remain BLOCKED.
