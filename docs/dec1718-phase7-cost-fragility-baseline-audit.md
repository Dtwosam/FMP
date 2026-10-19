# DEC-1718 — Phase 7 historical after-cost fragility: exact source audit

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs-only child of #1964 at `29186bb275f8e67253c6d1327cfc33d24f22e385`.

This adds **10 source-defined methods** (**5,864 proposed total**) anchored to the *already accepted* Phase 7 historical Stage 2 walk-forward evidence file. It reads **only** `docs/phase7-walk-forward-evidence.md`; no historical private artifacts, new strategies, current quotes, broker connection or trading operations.

### What matters economically

| Adverse slippage | Historical net return | Net PnL on frozen evaluation convention | Historical profit factor |
| --- | ---: | ---: | ---: |
| 0.2 pips | +0.757266% | +$757.27 | 1.062731 |
| 0.5 pips | +0.262176% | +$262.18 | 1.021310 |
| 1.0 pips | -0.562118% | -$562.12 | 0.955760 |

All 3 historical scenarios contain 199 recorded trades; positive-window counts are 5, 4 and 4 out of 7, respectively. A purely **linear arithmetic interpolation** between the already reported 0.5- and 1.0-pip net returns crosses zero around **0.659 pip**. This is *not* a live trading threshold, reliable cost forecast, fitted slippage law, strategy change, or a forecast of future profits. The frozen gate correctly treats the adverse 1.0-pip case as **diagnostic only** and promotes the historical baseline only to *shadow design*, never demo/live.

The new tests make the sample size, spread/cost sensitivity, 1.0-pip historical loss, exact frozen metrics, positive-window counts and limited promotion semantics visible and regression-checked. The original published evidence remains unchanged. This is financially relevant **negative or cautionary evidence**, not an alpha-discovery run.

### Phase position

Phase 8A remains annual catalogue discovery under DEC-268/DEC-469. 2023 run385 is still blocked by issue #779; DEC-650/#820 runner OS isolation and DEC-651/#821 one-shot admission remain unverified. The Phase 7 baseline is **not** Strategy V1, a full Phase 8A portfolio, untouched final-test evidence for new strategies, or earnings. Only annual catalogue completion, cross-year synthesis, frozen Strategy V1, robustness, fresh shadow, fixed-version demo, Phase 10 and separately explicit Phase 11 approval could move it toward real-money operation.

**Safety:** zero production/parser/workflow/security changes, zero annual execution/retry, no protected evidence, broker operations, strategy promotion or trading. Own exact-head Phase3/full historical-general CI and qualified independent review required.