from pathlib import Path

# Decision log: index + append-only DEC-028.
decision_path = Path("docs/decision-log.md")
decision = decision_path.read_text(encoding="utf-8")
index_old = "- DEC-027 — Phase 4 session high/low sweep-rejection experiment outcome — APPROVED\n"
index_new = index_old + "- DEC-028 — Phase 4 baseline strategy research acceptance review — APPROVED\n"
if decision.count(index_old) != 1:
    raise SystemExit("DEC-027 index marker mismatch")
if "## DEC-028 — Phase 4 baseline strategy research acceptance review" in decision:
    raise SystemExit("DEC-028 already present")
decision = decision.replace(index_old, index_new, 1)
decision = decision.rstrip() + """


## DEC-028 — Phase 4 baseline strategy research acceptance review

**Date:** 2026-09-14
**Status:** APPROVED

Phase 4 is accepted as PASS under the project-source acceptance gate. All six planned baseline families completed deterministic development/validation benchmarking and are recorded in the human-readable experiment registry, including rejected experiments. The six authoritative matrices comprise 108/108 successful pair/timeframe/split cells and 1,620/1,620 independently inspected frozen benchmark rows across EXP-001 through EXP-006. Every Phase 4 experiment records `Final-test touched?: NO`.

The acceptance gate is satisfied through the serious-candidate path. Two research candidates remain frozen unchanged: **USDJPY 15m / 5-pip breakout buffer / 1.5x target-range** from EXP-001 and **USDJPY 1h / 2.0x range-expansion multiplier / fixed 1.0R** from EXP-005. EXP-002 trend continuation, EXP-003 mean reversion, EXP-004 previous-day rejection, and EXP-006 session sweep-rejection remain rejected with their negative evidence preserved. No post-result rescue search or candidate retuning is authorized by this acceptance review.

Consequences: Phase 4 is formally PASS and closed. Checkpoint `fmp-v1-phase4-baselines` is to be created at the verified merged acceptance-closure commit after post-merge source-free regression checks succeed. Phase 5 becomes the next project phase but remains UNSTARTED until its own leakage-safe design/implementation work begins. The final untouched 2024-01-01 through 2026-08-20 test period remains locked; this decision does not authorize final-test inspection. Broker/live integration and real-money trading remain locked; DEC-008 remains unchanged. Detailed evidence is in `docs/phase4-acceptance-evidence.md`.
"""
decision_path.write_text(decision, encoding="utf-8")

# Project state: close Phase 4 without starting Phase 5.
state_path = Path("docs/project-state.md")
state = state_path.read_text(encoding="utf-8")
replacements = [
    (
        "**Current phase:** Phase 4 — Baseline Strategy Research  \n**Phase status:** ACTIVE  \n**Next milestone:** Complete the Phase 4 acceptance/checkpoint review now that all six planned baseline families are benchmarked; both serious candidates remain frozen unchanged and final-test data remains locked",
        "**Current phase:** Phase 4 — Baseline Strategy Research  \n**Phase status:** PASS  \n**Next milestone:** Create checkpoint `fmp-v1-phase4-baselines` at the verified acceptance-closure commit, then begin a separate Phase 5 leakage-safe feature-engine design; final-test data remains locked",
    ),
    (
        "## Phase 4 — ACTIVE",
        "## Phase 4 — PASS",
    ),
    (
        "DEC-018 freezes the chronological split, final-test lock, left-labelled timing bridge, exact shared cost assumptions, and unchanged Phase 3 risk settings. DEC-019 freezes the completed trend-continuation family-specific protocol, DEC-020 freezes the completed mean-reversion family-specific protocol, DEC-021 records the mean-reversion rejection, DEC-022 freezes the previous-day high/low rejection protocol, DEC-023 records the EXP-004 FAIL / REJECT outcome, DEC-024 freezes the EXP-005 rolling volatility-breakout protocol, DEC-025 records the EXP-005 PASS / PROMOTE outcome, and DEC-026 freezes the EXP-006 session high/low sweep-rejection protocol and DEC-027 records the EXP-006 FAIL / REJECT outcome; DEC-018 remains authoritative for shared research rules.",
        "DEC-018 freezes the chronological split, final-test lock, left-labelled timing bridge, exact shared cost assumptions, and unchanged Phase 3 risk settings. DEC-019 freezes the completed trend-continuation family-specific protocol, DEC-020 freezes the completed mean-reversion family-specific protocol, DEC-021 records the mean-reversion rejection, DEC-022 freezes the previous-day high/low rejection protocol, DEC-023 records the EXP-004 FAIL / REJECT outcome, DEC-024 freezes the EXP-005 rolling volatility-breakout protocol, DEC-025 records the EXP-005 PASS / PROMOTE outcome, DEC-026 freezes the EXP-006 session high/low sweep-rejection protocol, DEC-027 records the EXP-006 FAIL / REJECT outcome, and DEC-028 records the Phase 4 PASS acceptance review; DEC-018 remains authoritative for shared research rules.",
    ),
    (
        "Phase 4 remains ACTIVE pending its explicit acceptance/checkpoint review. All six planned baseline families are now complete. Two serious research candidates remain frozen unchanged: the EXP-001 USDJPY 15m / 5-pip / 1.5x session-breakout point and the EXP-005 USDJPY 1h / 2.0x / fixed-1.0R volatility-breakout point. EXP-004 and EXP-006 remain FAIL / REJECT. The Phase 4 baseline acceptance gate can now be reviewed against the approved project source; this status does not authorize final-test access. The final-test period remains locked and checkpoint `fmp-v1-phase4-baselines` is not created until the acceptance closure is merged.\n\n## Phase 5 — UNSTARTED\n\nPhase 5 has not started. No ML/feature-engine promotion is authorized by the Phase 4 baseline work completed so far.\n\nReal-money trading remains locked; DEC-008 remains unchanged.",
        "Phase 4 is formally PASS under DEC-028. All six planned baseline families have complete benchmark evidence and experiment-log entries. Two serious research candidates remain frozen unchanged: the EXP-001 USDJPY 15m / 5-pip / 1.5x session-breakout point and the EXP-005 USDJPY 1h / 2.0x / fixed-1.0R volatility-breakout point. EXP-002, EXP-003, EXP-004, and EXP-006 remain FAIL / REJECT. Detailed acceptance evidence is `docs/phase4-acceptance-evidence.md`. The final-test period remains locked. Checkpoint `fmp-v1-phase4-baselines` is created only after the merged acceptance closure passes post-merge verification.\n\n## Phase 5 — UNSTARTED\n\nPhase 5 is the next project phase but has not started. It may begin only as separate leakage-safe feature-engine work under the approved project source. Phase 4 PASS does not authorize final-test inspection, broker/live integration, or real-money trading.\n\nReal-money trading remains locked; DEC-008 remains unchanged.",
    ),
]
for old, new in replacements:
    if state.count(old) != 1:
        raise SystemExit(f"project-state marker mismatch: {old[:80]}")
    state = state.replace(old, new, 1)
state_path.write_text(state, encoding="utf-8")

# Regression guard for the phase transition and locks.
test_path = Path("tests/test_phase4_acceptance_state.py")
test_path.write_text(
    '''from pathlib import Path\nimport unittest\n\nROOT = Path(__file__).resolve().parents[1]\n\n\nclass Phase4AcceptanceStateTests(unittest.TestCase):\n    def test_phase4_is_pass_and_phase5_remains_unstarted(self) -> None:\n        state = (ROOT / "docs/project-state.md").read_text(encoding="utf-8")\n        decision = (ROOT / "docs/decision-log.md").read_text(encoding="utf-8")\n        evidence = (ROOT / "docs/phase4-acceptance-evidence.md").read_text(encoding="utf-8")\n\n        self.assertIn("**Phase status:** PASS", state)\n        self.assertIn("## Phase 4 — PASS", state)\n        self.assertIn("## Phase 5 — UNSTARTED", state)\n        self.assertIn("DEC-028", state)\n        self.assertEqual(decision.count("## DEC-028 — Phase 4 baseline strategy research acceptance review"), 1)\n        self.assertIn("- DEC-028 — Phase 4 baseline strategy research acceptance review — APPROVED", decision)\n        self.assertIn("**Result:** PASS", evidence)\n        self.assertIn("Final-test touched?: NO", evidence)\n        self.assertIn("final-test period remains locked", state.lower())\n        self.assertIn("Real-money trading remains locked", state)\n        self.assertNotIn("## Phase 5 — ACTIVE", state)\n\n\nif __name__ == "__main__":\n    unittest.main()\n''',
    encoding="utf-8",
)
