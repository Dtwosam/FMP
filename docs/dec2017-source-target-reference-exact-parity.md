# DEC-2017 — Source TARGET reference-price exact parity

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2265 at `2897a92081a44aab8145de81af9b0f0cdf2fc0cd`.

The installed `evaluate_exit` routine emits a TARGET exit only when a non-null target is reached; it passes `position.target_price` unchanged to the reference fill. The evidence audit previously checked directional stop/target geometry, numerical price domains, and gross PnL from the exit reference, but a forged/rehashed artifact could alter target without changing exit reference or economic totals.

For the exact installed source-engine version, require `exit_reason == TARGET` to have a non-null target and `exit_reference_price == target_price` exactly. Other exit modes (STOP, scheduled TIME_EXIT, END_OF_DATA) must not be forced to the target. Generic synthetic/other-engine runs remain flexible, and this does not authenticate quote bars.

Align earlier *synthetic source-version test fixtures* with the source evaluator contract: the existing engine checkpoint fixture now declares the same 1.10125 target as its reference exit; the declared-slippage fixture uses its target reference as the target; the deliberate equal-price, zero-PnL pair is marked END_OF_DATA rather than falsely claiming a target fill at entry price. These fixture edits do not change engine production code or claim real bar provenance.

Four new source-defined test methods cover valid LONG/SHORT/USDJPY source TARGET fills, a checksum-verified forged target, a missing target with TARGET exit reason, and generic synthetic compatibility. **7,156 cumulative proposed source-defined methods** (+4). Exact-head Phase3 acceptance and full historical/general regression gate required; failed older CI remains failed.

Phase8A #779/#820/#821 and eight independent external security proofs remain blocked. No protected annual research, installed workflow/ref/runner changes, broker orders, strategy promotion, real-capital activity or merge.
