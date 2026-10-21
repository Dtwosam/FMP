# DEC-2070 — Computed Phase3 metrics versus source evidence audit parity

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2318 at `f707f344f7572f9d89d8c65740f9b94727f88eb3`.

The preceding DEC-2065–2069 witnesses used hand-calculated metrics dictionaries to test independently serialized ledger semantics. This draft additionally calls the installed `compute_backtest_metrics` function on those source-defined trade/checkpoint fixtures, verifying the metric producer and artifact writer/audit agree on canonical sign streaks and breakeven denominators.

Five new methods cover: full all-flat computed-metric writer/audit roundtrip; WIN/FLAT/WIN with a published flat gap; WIN/FLAT/WIN whose canonical same-time ID order instead publishes WIN/WIN/FLAT; cross-time realized LOSS/FLAT/LOSS whose canonical publication is FLAT/LOSS/LOSS; and reversed realization LOSS/FLAT/WIN with correct mixed trade distribution. The first three checks end-to-end writer/audit; the latter two independently check computed-metric semantics without overclaiming a float-order invariant that isn't guaranteed for all mixed outcomes. All source market PnL remains synthetic, not performance evidence. No production code changes.

**7,353 cumulative proposed methods** (+5). Own exact-head Phase3 and full historical/general suite mandatory. #2313 remains the last fully green parent until descendants' runs finish; historical failures are never relabeled. Phase8A #779/#820/#821 and eight independent security proofs remain blocked. No protected research, installed workflows/refs/runners, merges, strategy promotion, broker orders or real capital.
