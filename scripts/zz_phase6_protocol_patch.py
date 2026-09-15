from __future__ import annotations

from pathlib import Path
import subprocess


def replace_exact(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"missing exact replacement target in {path}: {old!r}")
    if text.count(old) != 1:
        raise SystemExit(f"replacement target must occur exactly once in {path}: {old!r}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_exact(
    "docs/superpowers/specs/2026-09-15-phase6-statistical-ml-filter-design.md",
    "**Status:** APPROVED IN CHAT — PENDING WRITTEN-SPEC REVIEW",
    "**Status:** APPROVED",
)

decision_path = Path("docs/decision-log.md")
decision = decision_path.read_text(encoding="utf-8")
index_old = "- DEC-030 — Phase 5 leakage-safe feature-engine acceptance review — APPROVED\n"
index_new = index_old + "- DEC-031 — Phase 6 statistical / ML filter protocol — APPROVED\n"
if index_old not in decision or decision.count(index_old) != 1:
    raise SystemExit("DEC-030 index anchor missing or duplicated")
decision = decision.replace(index_old, index_new, 1)
section = """

## DEC-031 — Phase 6 statistical / ML filter protocol

**Date:** 2026-09-15
**Status:** APPROVED

Phase 6 begins under the user-approved written design in `docs/superpowers/specs/2026-09-15-phase6-statistical-ml-filter-design.md`. The design is authoritative for `EXP-20260915-007` unless a later explicitly approved decision creates a new experiment or supersedes a named rule.

Frozen experiment scope:

- The only rule baselines are the unchanged Phase 4 serious candidates: USDJPY 15m session breakout with 5-pip buffer and 1.5x target range, and USDJPY 1h volatility breakout with 2.0x range expansion and fixed 1.0R target.
- Phase 5 feature identity remains `fmp-feature-v1` at checkpoint `fmp-v1-phase5-features` / `e0b2fc7bf12b0c9cd9d76668564df6b7714b1fe0`; accepted USDJPY processed-manifest SHA-256 remains `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`.
- Fit: 2015-01-01 through 2018-12-31 inclusive.
- Selection: 2019-01-01 through 2020-12-31 inclusive.
- Validation: 2021-01-01 through 2023-12-31 inclusive.
- The final untouched test remains 2024-01-01 through 2026-08-20 inclusive and normal Phase 6 APIs must fail before opening any required 2024+ source or feature partition.
- Model rows use exactly the 48 frozen Phase 5 feature values plus signal direction and must join at the exact strategy observation / `available_at_utc` identity. No future observation, target outcome, realized PnL, or validation statistic may be an input.
- The primary label is `target_before_stop`, resolved from future historical BID/ASK only after the feature row is frozen. Accepted Phase 3 stop/target/time-exit ordering remains authoritative, including conservative same-bar ambiguity.
- Training-only preprocessing is median imputation for both models and standard scaling for logistic regression only. Preprocessing parameters are fit on the fit period and frozen afterward; all-null fit columns fail closed.
- The modeling dependency is exactly `scikit-learn==1.9.1`. The only model families are the predeclared L2 logistic regression and shallow histogram gradient boosting configurations in the approved design, with global seed `20260915`.
- Score cutoffs are derived from fit scores only at retained fractions exactly 0.75, 0.50, and 0.25. Selection or validation scores may not alter a cutoff.
- Selection evaluates exactly six filtered variants per strategy on 2019-2020 at 0.2-pip adverse slippage and may freeze at most one challenger using the approved financial gate and deterministic tie-break. Validation cannot rescue a strategy with no qualifying selection-period challenger.
- There is no refit after selection. Any selected challenger is evaluated on 2021-2023 using the exact 2015-2018-fitted preprocessing, estimator, and cutoff. The 0.2-pip validation gate and 0.5-pip robustness gate are mandatory; 1.0 pip is diagnostic only.
- Financial comparison always uses the unchanged Phase 3 BID/ASK backtester, 0.25% requested risk, 0.50% hard per-trade maximum, 1.00% simultaneous risk maximum, 1.50% UTC day-start realized-loss halt, zero commission, and zero financing.
- Phase 6 may PASS whether an ML filter is promoted or all ML challengers are rejected, provided both frozen strategies complete the predeclared deterministic leakage-safe experiment. Failed variants remain evidence.
- No strategy-parameter retuning, new feature family, target-aware feature selection, pooled/cross-pair/cross-timeframe model, probability-based sizing, AutoML, neural network, post-result threshold widening, broker/live/demo path, or real-money trading is authorized under this experiment.

Consequences: Phase 6 is ACTIVE only for test-first implementation and execution of `EXP-20260915-007`. Phase 5 remains frozen PASS at `fmp-v1-phase5-features`; Phase 7 remains unstarted; the 2024-01-01 through 2026-08-20 final-test period remains locked; broker/live/demo integration and real-money trading remain locked; DEC-008 remains unchanged.
"""
if "## DEC-031 — Phase 6 statistical / ML filter protocol" in decision:
    raise SystemExit("DEC-031 section already present")
decision_path.write_text(decision.rstrip() + section + "\n", encoding="utf-8")

state_path = Path("docs/project-state.md")
state = state_path.read_text(encoding="utf-8")
header_old = (
    "**Current phase:** Phase 5 — Leakage-Safe Feature Engineering\n"
    "**Phase status:** PASS\n"
    "**Next milestone:** Phase 6 design remains a separate approval gate; final-test data remains locked"
)
header_new = (
    "**Current phase:** Phase 6 — Statistical / ML Filters\n"
    "**Phase status:** ACTIVE\n"
    "**Next milestone:** Implement and execute frozen `EXP-20260915-007`; final-test data remains locked"
)
if state.count(header_old) != 1:
    raise SystemExit("Phase 5 top-level state anchor missing or duplicated")
state = state.replace(header_old, header_new, 1)
phase6_old = (
    "## Phase 6 — UNSTARTED\n\n"
    "Phase 6 model fitting and statistical/ML experiments remain unauthorized pending a separate explicitly approved design and implementation gate. No labels, models, final-test access, broker/live/demo integration, or candidate retuning is authorized by Phase 5 acceptance. Broker/live/demo integration and real-money trading remain locked; DEC-008 remains unchanged."
)
phase6_new = """## Phase 6 — ACTIVE

DEC-031 freezes the statistical / ML filter protocol for `EXP-20260915-007`. Phase 6 evaluates optional candidate-level filters only; it does not create a new strategy or retune the two frozen Phase 4 candidates.

- Candidate A: USDJPY 15m session breakout, 5-pip buffer, 1.5x target range.
- Candidate B: USDJPY 1h volatility breakout, 2.0x range expansion, fixed 1.0R target.
- feature checkpoint: `fmp-v1-phase5-features` at `e0b2fc7bf12b0c9cd9d76668564df6b7714b1fe0`
- feature schema: `fmp-feature-v1`, exact 48 feature values plus signal direction for modeling
- accepted USDJPY processed-manifest SHA-256: `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`
- experiment: `EXP-20260915-007`
- fit: 2015-01-01 through 2018-12-31 inclusive
- selection: 2019-01-01 through 2020-12-31 inclusive
- external validation: 2021-01-01 through 2023-12-31 inclusive
- models: exact L2 logistic regression and shallow histogram gradient boosting under `scikit-learn==1.9.1`
- fit-derived retained fractions: 0.75, 0.50, 0.25
- no refit after selection before external validation
- primary label: `target_before_stop` under unchanged Phase 3 BID/ASK stop/target/time-exit semantics
- Phase 3 risk and execution semantics: unchanged
- Final-test touched: NO

Normal Phase 6 tooling cannot open any required source or feature partition reaching 2024-01-01 or later. Phase 7 remains UNSTARTED. Broker/live/demo integration and real-money trading remain locked; DEC-008 remains unchanged."""
if state.count(phase6_old) != 1:
    raise SystemExit("Phase 6 UNSTARTED section anchor missing or duplicated")
state_path.write_text(state.replace(phase6_old, phase6_new, 1), encoding="utf-8")

allowed = {
    "docs/superpowers/specs/2026-09-15-phase6-statistical-ml-filter-design.md",
    "docs/decision-log.md",
    "docs/project-state.md",
}
changed = set(subprocess.check_output(["git", "diff", "--name-only"], text=True).splitlines())
if changed != allowed:
    raise SystemExit(f"unexpected changed files: {sorted(changed)}")
subprocess.run(["git", "diff", "--check"], check=True)
