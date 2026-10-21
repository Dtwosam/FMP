# DEC-2033 — Signed source custom financing economics regression witnesses

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2281 at `86325ce5fd5e1b10f03210cd59f21caeadd1bd5a`.

The installed source engine permits a user-defined `FinancingModel.cost_usd` that returns finite signed charges or credits, with `financing_cost_usd` directly incorporated as a subtraction in the source's exact net PnL calculation. The optional source auditor rightly enforces zero for the built-in `zero_financing` model but must not apply that restriction to a distinct custom financing model. DEC-2031/2032 tightened exact source net PnL and realized equity arithmetic; these tests verify those checks still admit legitimately negative or positive financing records.

Three new source-defined methods: positive source-model acceptance of either a $1.25 debit or credit with reconstructed net and realized equity; rehashed 1e-9 financing drift under either sign must fail exact source net PnL arithmetic; and generic synthetic near-equal financing behavior remains tolerated. No production code changed. This synthetic custom model label proves only field consistency; it does **not** authenticate a real cost model or externally charged financing.

**7,213 proposed cumulative source-defined methods** (+3). Requires own exact-head Phase3 and full historical/general suite; prior failed full suites remain failures. Phase8A #779/#820/#821 and eight independent security proofs remain blocked. No protected research, installed workflows/refs/runners, merges, strategy promotion, broker orders or real funds.
