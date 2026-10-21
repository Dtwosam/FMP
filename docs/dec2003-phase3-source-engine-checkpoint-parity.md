# DEC-2003 — Source-engine checkpoint/trade-close parity

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2251 at `5547fc349f30a11046464a897c852a3d311618e4`.

The source `run_backtest` initializes one realized equity checkpoint at the first quote bar and appends one checkpoint for each finalized trade, recording precisely the trade exit timestamp and its realized post-trade risk equity. The ordinary artifact auditor checked checkpoint chronology and independently validated trade before/after arithmetic but could accept rehashed source-engine reports where checkpoints omit a closing trade, falsely claim a checkpoint balance, or misstate a close time.

For artifacts whose run identity explicitly declares the **currently installed** `BACKTEST_ENGINE_VERSION` and a valid starting equity, enforce exactly one initial checkpoint plus one per stored trade; starting equity must match the initial checkpoint; every subsequent checkpoint must match its canonical trade close timestamp and after-equity. Do not impose this source-engine-specific shape on synthetic/alternative reports that omit the version field. Digest verifier remains purely byte-integrity oriented.

Four source-defined tests cover a compatible two-trade run, a self-rehashed missing close checkpoint, altered starting checkpoint, and incorrect closing balance/time. Total **7,112 cumulative proposed source-defined tests** (+4). Exact-head Phase3 and historical/general regressions required. Previous failed runs remain recorded; new green acceptance is not a substitute for full tests.

Phase8A issues #779/#820/#821 and eight independent proof packages unresolved. No protected annual 2023/run385/attempt1, later research, installed runner/ref/workflow changes, broker orders, strategy promotion, merges or capital deployment.
