from pathlib import Path

MANIFESTS = (
    "accepted Phase 2 processed manifests, schema `fmp-canonical-1m-v1`; "
    "EURUSD `fd7676282e6e667c39754b09b43a43288a0a877fec588cd2601a601e2b0edf6a`, "
    "GBPUSD `a6ee73e94781f48a43f2792328528d242455d4f7f4f2e0a5760446df21ba4d94`, "
    "USDJPY `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`."
)
COMMON = {
    "Date": "2026-09-14",
    "Data manifest/version": MANIFESTS,
    "Pair(s)": "EURUSD, GBPUSD, USDJPY",
    "Timeframe(s)": "5m, 15m, 1h",
    "Data range": "accepted Phase 2 coverage 2015-01-01 through 2026-08-20 inclusive; development and validation only.",
    "Train period": "2015-01-01 through 2020-12-31 inclusive",
    "Validation period": "2021-01-01 through 2023-12-31 inclusive",
    "Final-test touched?": "NO",
    "Random seed (if relevant)": "not applicable; deterministic strategy and backtester.",
    "Spread/cost model": "historical BID/ASK spread; zero commission; zero financing.",
    "Slippage model": "0.2, 0.5, 1.0 pips per fill, adverse on every execution side.",
    "Risk assumptions": "accepted Phase 3 policy unchanged: 0.25% requested risk, 0.50% hard per-trade max, 1.00% simultaneous max, 1.50% UTC day-start realized-loss halt.",
}
ORDER = [
    "Date", "Status", "Hypothesis", "Code commit", "Data manifest/version", "Pair(s)",
    "Timeframe(s)", "Data range", "Train period", "Validation period", "Final-test touched?",
    "Strategy/model", "Features", "Parameters/search space", "Random seed (if relevant)",
    "Spread/cost model", "Slippage model", "Risk assumptions", "Trade count",
    "Net return after costs", "Expectancy/trade", "Profit factor", "Max drawdown",
    "Key subperiod results", "Robustness/cost sensitivity", "Result summary", "Conclusion",
    "Reason", "Follow-up",
]


def entry(exp_id: str, title: str, **values: str) -> str:
    record = dict(COMMON)
    record.update(values)
    missing = [key for key in ORDER if key not in record]
    if missing:
        raise RuntimeError(f"missing fields for {exp_id}: {missing}")
    lines = [f"### {exp_id} — {title}", ""]
    lines.extend(f"- {key}: {record[key]}" for key in ORDER)
    return "\n".join(lines)


records = [
    entry(
        "EXP-20260914-003",
        "Mean reversion baseline",
        **{
            "Status": "FAIL",
            "Hypothesis": "Fresh intraday displacement from a preceding rolling midpoint-close distribution may revert toward its pre-existing mean strongly enough to overcome historical spread and adverse slippage under fixed-risk execution. No profitability was assumed.",
            "Code commit": "`87003a3982ca61eb6fd030c5291616d98dbb0c1a`",
            "Strategy/model": "deterministic London-session mean-reversion baseline using preceding-N midpoint-close population mean/std, fresh z-score excursions, first signal only, and exact 16:00 Europe/London flat.",
            "Features": "midpoint close, rolling mean, rolling population standard deviation, and current/previous z-score; Phase 3 historical BID/ASK execution remained authoritative.",
            "Parameters/search space": "lookbacks 4h/8h/16h × fresh-excursion thresholds 1.5σ/2.0σ; exactly 6 configurations per pair/timeframe.",
            "Trade count": "no promoted candidate; full 324-row matrix retained in evidence.",
            "Net return after costs": "no promoted candidate; all 54 development and all 54 validation baseline rows were negative.",
            "Expectancy/trade": "no promoted candidate; all baseline rows were negative on both splits.",
            "Profit factor": "no promoted candidate; development range 0.6150–0.9596 and validation range 0.5396–0.9582 at baseline.",
            "Max drawdown": "no candidate-level value; fixed-risk drawdowns remain in benchmark evidence.",
            "Key subperiod results": "the family failed broadly rather than through one isolated chronology reversal.",
            "Robustness/cost sensitivity": "zero baseline survivors; 0.5/1.0-pip rows remain diagnostic evidence only and cannot rescue the family.",
            "Result summary": "merged-main benchmark run `34875463677` completed SUCCESS; 18/18 artifacts and 324/324 rows independently verified with zero integrity/identity/grid/candidate-reuse/accounting errors.",
            "Conclusion": "REJECT",
            "Reason": "zero of 54 pair/timeframe/lookback/threshold points achieved positive net return, positive expectancy, and PF > 1 on both development and validation at 0.2-pip baseline.",
            "Follow-up": "retain EXP-001 unchanged; no post-result expansion; final-test remains locked. Detailed evidence: `docs/phase4-mean-reversion-evidence.md`.",
        },
    ),
    entry(
        "EXP-20260914-004",
        "Previous-day high/low rejection baseline",
        **{
            "Status": "FAIL",
            "Hypothesis": "Penetration beyond the previous completed New-York-close FX session high/low followed by a close back inside may revert toward the frozen previous-day midpoint strongly enough to overcome costs. No profitability was assumed.",
            "Code commit": "`7db3a747236942fa393521e5866e3245d1a22a99`",
            "Strategy/model": "deterministic previous-day high/low rejection using the most recent completed New-York-close FX session, first directional rejection only, and exact 16:00 Europe/London flat.",
            "Features": "previous-day midpoint high/low/midpoint and current midpoint penetration/rejection; Phase 3 BID/ASK execution.",
            "Parameters/search space": "penetration buffers 0/2/5 pips; no post-result expansion.",
            "Trade count": "sole baseline survivor USDJPY 5m / 5-pip buffer had 29 development and 28 validation trades.",
            "Net return after costs": "+4.0039% development and +0.0657% validation for the sole baseline survivor at 0.2 pips.",
            "Expectancy/trade": "+$138.0644 development and +$2.3461 validation.",
            "Profit factor": "1.9002 development and 1.0133 validation.",
            "Max drawdown": "2.0245% development and 1.7179% validation.",
            "Key subperiod results": "validation negative in 2021 and 2022 and positive only in 2023; top three winners contributed about 85.38% of validation positive R.",
            "Robustness/cost sensitivity": "validation turned negative at 0.5-pip slippage; neighboring 0/2-pip buffers were negative on both splits; 1.0-pip validation also failed.",
            "Result summary": "merged-main benchmark run `34883815436` completed SUCCESS; 18/18 artifacts and 162/162 rows independently verified with zero integrity/identity/grid/candidate-reuse/accounting errors.",
            "Conclusion": "REJECT",
            "Reason": "the only baseline survivor was thin, isolated, cost-sensitive, chronologically concentrated, and winner-dependent, failing the predeclared robustness review.",
            "Follow-up": "no candidate promoted and no rescue search authorized. Detailed evidence: `docs/phase4-previous-day-rejection-evidence.md`.",
        },
    ),
    entry(
        "EXP-20260914-005",
        "Rolling volatility-breakout baseline",
        **{
            "Status": "PASS",
            "Hypothesis": "A close outside a preceding rolling 8h midpoint channel accompanied by contemporaneous range expansion may continue far enough to overcome historical spread and adverse slippage. No profitability was assumed.",
            "Code commit": "`3bf36186900f5065e9e3ddced0305865433b9d69`",
            "Strategy/model": "deterministic rolling 8h volatility breakout; strict close beyond rolling channel plus current range expansion; first signal only; signal-bar extreme stop; fixed 1.0R target; exact 16:00 Europe/London flat.",
            "Features": "rolling midpoint high/low, median reference bar range, current midpoint range, and expansion multiple.",
            "Parameters/search space": "range-expansion multipliers 1.0x/1.5x/2.0x; fixed 1.0R target.",
            "Trade count": "promoted USDJPY 1h / 2.0x point had 596 development and 364 validation trades.",
            "Net return after costs": "+11.4235% development and +5.5971% validation at 0.2 pips.",
            "Expectancy/trade": "+$19.1670 development and +$15.3766 validation.",
            "Profit factor": "1.2321 development and 1.1931 validation.",
            "Max drawdown": "2.5228% development and 1.9853% validation.",
            "Key subperiod results": "all six development years positive; validation negative in 2021 but positive in 2022 and 2023; top-three winner dependence about 1.30% development and 2.22% validation positive R.",
            "Robustness/cost sensitivity": "survives 0.5-pip stress on both splits but fails 1.0-pip diagnostic; neighboring multipliers and adjacent timeframes do not confirm the development edge.",
            "Result summary": "merged-main benchmark run `34888225242` completed SUCCESS; 18/18 artifacts and 162/162 rows independently verified; exactly one of 27 baseline points survived: USDJPY 1h / 2.0x.",
            "Conclusion": "PROMOTE",
            "Reason": "the exact predeclared point clears both chronological splits, survives required 0.5-pip stress, has a substantial sample and low drawdown, broad development-year support, and very low top-winner dependence despite parameter/timeframe isolation and 2021 weakness.",
            "Follow-up": "freeze USDJPY 1h / 2.0x / fixed 1.0R as the second serious Phase 4 candidate alongside EXP-001. Detailed evidence: `docs/phase4-volatility-breakout-evidence.md`.",
        },
    ),
    entry(
        "EXP-20260914-006",
        "Session high/low sweep-rejection baseline",
        **{
            "Status": "FAIL",
            "Hypothesis": "Intrabar penetration beyond the frozen 00:00–08:00 Europe/London session high/low followed by a strict close back inside may revert toward the frozen session midpoint strongly enough to overcome costs. No profitability was assumed.",
            "Code commit": "`120348d4a5df806f674551590610b216a9bc33ac`",
            "Strategy/model": "deterministic session high/low sweep-rejection; frozen 00:00–08:00 Europe/London midpoint range; strict rejection back inside; first signal only; signal-bar extreme stop; session-midpoint target; exact 16:00 flat.",
            "Features": "frozen session midpoint high/low/midpoint and current midpoint sweep/rejection state.",
            "Parameters/search space": "penetration buffers 0/2/5 pips; no alternate session or rescue grid.",
            "Trade count": "no promoted candidate; clearest split-only point USDJPY 5m / 2 pips had 337 development and 240 validation trades.",
            "Net return after costs": "that point reversed from +1.9167% development to -15.4056% validation at baseline.",
            "Expectancy/trade": "+$5.6874 development versus -$64.1899 validation.",
            "Profit factor": "1.0282 development versus 0.6706 validation.",
            "Max drawdown": "7.6380% development versus 16.7821% validation.",
            "Key subperiod results": "zero of 27 pair/timeframe/buffer points cleared the required development-and-validation gate; two USDJPY 1h validation-only qualifiers failed development.",
            "Robustness/cost sensitivity": "no baseline survivor, so downstream cost rows cannot rescue any point and remain evidence only.",
            "Result summary": "merged-main benchmark run `34895426037` completed SUCCESS; 18/18 artifacts and 162/162 rows independently verified with zero ZIP/manifest/identity/grid/candidate-reuse/accounting/cost/risk errors.",
            "Conclusion": "REJECT",
            "Reason": "no exact predeclared buffer achieved positive net return, positive expectancy, and PF > 1 on both development and validation at 0.2-pip baseline.",
            "Follow-up": "promote nothing; retain EXP-001 and EXP-005 candidates frozen unchanged. This completes all six planned Phase 4 baseline families. Detailed evidence: `docs/phase4-session-sweep-rejection-evidence.md`.",
        },
    ),
]

log_path = Path("docs/experiment-log.md")
log = log_path.read_text(encoding="utf-8")
if "### EXP-20260914-003 —" not in log:
    log = log.rstrip() + "\n\n" + "\n\n".join(records) + "\n"
for number in range(1, 7):
    exp_id = f"EXP-20260914-{number:03d}"
    if log.count(f"### {exp_id} —") != 1:
        raise RuntimeError(f"experiment registry count mismatch: {exp_id}")
log_path.write_text(log, encoding="utf-8")

for filename, old, new in [
    ("docs/phase4-volatility-breakout-evidence.md", "**Outcome decision:** DEC-025 — pending evidence-closure merge  ", "**Outcome decision:** DEC-025 — APPROVED"),
    ("docs/phase4-session-sweep-rejection-evidence.md", "**Outcome decision:** DEC-027 — pending evidence-closure merge  ", "**Outcome decision:** DEC-027 — APPROVED"),
]:
    path = Path(filename)
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"stale outcome marker missing: {filename}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")

test_path = Path("tests/test_phase4_experiment_registry_state.py")
test_path.write_text(
    "from pathlib import Path\n"
    "import unittest\n\n"
    "ROOT = Path(__file__).resolve().parents[1]\n\n"
    "class Phase4ExperimentRegistryTests(unittest.TestCase):\n"
    "    def test_registry_and_outcome_statuses_are_complete(self) -> None:\n"
    "        registry = (ROOT / 'docs/experiment-log.md').read_text(encoding='utf-8')\n"
    "        vol = (ROOT / 'docs/phase4-volatility-breakout-evidence.md').read_text(encoding='utf-8')\n"
    "        sweep = (ROOT / 'docs/phase4-session-sweep-rejection-evidence.md').read_text(encoding='utf-8')\n"
    "        for number in range(1, 7):\n"
    "            exp_id = f'EXP-20260914-{number:03d}'\n"
    "            self.assertEqual(registry.count(f'### {exp_id} —'), 1, exp_id)\n"
    "        self.assertGreaterEqual(registry.count('Final-test touched?: NO'), 6)\n"
    "        self.assertIn('**Outcome decision:** DEC-025 — APPROVED', vol)\n"
    "        self.assertIn('**Outcome decision:** DEC-027 — APPROVED', sweep)\n"
    "        self.assertNotIn('pending evidence-closure merge', vol)\n"
    "        self.assertNotIn('pending evidence-closure merge', sweep)\n\n"
    "if __name__ == '__main__':\n"
    "    unittest.main()\n",
    encoding="utf-8",
)
