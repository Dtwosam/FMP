# DEC-1864 — Fail closed on Boolean/non-numeric backtest cost inputs

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2111 `6a1692bb0fc01d58e99142bc659f2152fbd7f2bf`. Scoped pure backtest cost-contract change only; requires independent human review and own Phase3/full regression before promotion.

Python treats `True` and `False` as integer subtypes, so `math.isfinite(True)` and `math.isfinite(False)` succeed. Earlier slippage quote price/pips and fixed-commission rate checks did not reject those inputs. This can silently misprice synthetic fills or use a $1-per-million Boolean rate, compromising hypothetical after-cost economics.

Require built-in `int` or `float` inputs (not Boolean, strings, None or other scalars) for `apply_adverse_slippage(price, pips)` and `FixedCommissionPerMillion(usd_per_million_per_side)`. Preserve already-reviewed finite/positive/non-negative constraints and normalize OverflowError from abnormally large integer conversion into a controlled ValueError. Correct enums, three supported FX pairs, integer and float finite quotes/rates and normal adverse fill direction remain supported. **No external market data or broker orders** are involved.

Four new Phase3 test methods (**6,777 cumulative proposed source-defined**) cover nonnumeric/Boolean quote price, pip amount, commission rate and supported numeric values. These source-only drafts are NOT an authorized deployed backtester, validated Strategy V1, positive expectancy or live permission. Accepted annual research stops at 2022/run384; protected 2023/run385/attempt1, shadow/demo/real-money, installed ref/workflow/ruleset and broker activities remain BLOCKED. Eight independent security/inventory/human proof packages #779/#820/#821 still MISSING.
