# DEC-1754 — Prevent annual freeze and Phase 7 benchmark evidence laundering

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Source-only child of PR #2000 at `3d32b769d50075aee023a841b1bda9de857ceb11`, with no research or trading authorization.

The DEC-1752 diagnostic was closed to unexpected keys by DEC-1753, but still checked only the **2023** row in the annual catalogue and omitted meaningful values from other years and the Phase 7 cost benchmarks. A forged later-year `HISTORICALLY_FROZEN` status could coexist with a BLOCKED 2023 run. This draft closes that gap:

- Require all twelve correctly ordered annual segments: historically accepted 2015–2022; blocked 2023 run385/attempt1; 2024, 2025 and partial 2026 blocked on their exact predecessors; no year promotion.
- Preserve the 2022/run384 historical (not freshly dispatched) provenance and six external one-shot prerequisites.
- Keep annual catalogues incomplete, researcher thresholds unpassed and human/strategy promotion authorizations false.
- Preserve the **reported Phase 7 historical** net returns at slippage 0.2/0.5/1.0 pips, including the negative `-0.562118%` at 1.0 pip. These are not new StrategyV1 or forward results.
- Preserve the distinction between a public snapshot with zero repository rulesets and verified effective no-bypass controls, and retain the required claims for **both unapproved alternative security remediation routes**.

Adds **22 targeted mutations**, **6349 cumulative proposed methods**, exercising the actual offline diagnostic rather than merely checking an unrelated test fixture. All mutations are temporary copies; clean and malformed packets must still never output `READY` or trade.

No extra year processed, no protected historical source I/O, annual run385 dispatch or retry, workflow/ref/ruleset/runner mutation, Strategy V1 selection, shadow, broker/demo/live order, real-money action or claim of profitability. All external #779/#820/#821 blockers remain. Require exact-head Phase3/full historical-general CI and independent review.
