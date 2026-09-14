from pathlib import Path

DECISION = Path("docs/decision-log.md")
STATE = Path("docs/project-state.md")
SPEC = Path("docs/superpowers/specs/2026-09-14-phase5-leakage-safe-feature-engine-design.md")
TEST = Path("tests/test_phase5_feature_protocol_state.py")

# Decision log: add DEC-029 exactly once to the index and append the approved decision.
decision = DECISION.read_text(encoding="utf-8")
if "DEC-029" in decision:
    raise SystemExit("DEC-029 already present")
index_marker = "- DEC-028 — Phase 4 baseline strategy research acceptance review — APPROVED\n"
if decision.count(index_marker) != 1:
    raise SystemExit("DEC-028 index marker mismatch")
decision = decision.replace(
    index_marker,
    index_marker + "- DEC-029 — Phase 5 leakage-safe feature-engine protocol — APPROVED\n",
    1,
)
decision = decision.rstrip() + "\n\n## DEC-029 — Phase 5 leakage-safe feature-engine protocol\n\n**Date:** 2026-09-14  \n**Status:** APPROVED\n\nPhase 5 begins under the user-approved written design in `docs/superpowers/specs/2026-09-14-phase5-leakage-safe-feature-engine-design.md`. The design is authoritative for `fmp-feature-v1` unless a later approved decision explicitly supersedes it.\n\nFrozen V1 scope and leakage controls:\n\n- Feature tables cover exactly EURUSD, GBPUSD, and USDJPY at 5m, 15m, and 1h. No separate 1m feature matrix is authorized.\n- Normal Phase 5 feature generation may open processed source partitions only through 2023-12-31. Any request whose required source coverage reaches 2024-01-01 or later must fail before that final-test partition is opened.\n- A feature row for a left-labelled bar beginning at `T` and width `D` becomes available only at `T + D`; the current fully closed bar may be used, but no observation ending after `available_at_utc` may contribute.\n- `fmp-feature-v1` contains exactly eight promoted families: returns, volatility/range, trend/structure, momentum, candle structure, session/time, market location, and spread/quote quality. Relative source activity, cross-pair joins, multi-timeframe joins, labels, models, and target-driven feature selection are not authorized in this version.\n- Price-distance features use deterministic midpoint OHLC with pip sizes EURUSD/GBPUSD `0.0001` and USDJPY `0.01`; Phase 3 BID/ASK execution semantics are unchanged.\n- Rolling and exact-duration features require finite, exact-cadence source history. They never shorten lookbacks or generically forward-fill across closures/gaps. Warm-up and incomplete-reference cases remain null.\n- Session/time features use named time zones with the approved Asia `09:00–17:00 Asia/Tokyo`, London `08:00–16:00 Europe/London`, and New York `08:00–17:00 America/New_York` definitions, including DST-mismatch tests.\n- Previous-day/session location levels may persist only by explicit completed-reference semantics; incomplete sessions are never used. Previous FX day retains the tested New-York-close convention.\n- Every promoted family must pass leakage tests including prefix equivalence, future perturbation, current-closed-bar allowance, cadence/closure behavior, reference-session completeness, DST correctness, deterministic regeneration, schema/key guards, and the hard final-test reader block.\n- Phase 5 acceptance is exactly 3 pairs × 3 timeframes = 9 source-free generation cells over 2015-01-01 through 2023-12-31, with reproducible manifests/digests and unchanged repository-wide regression surfaces.\n\nConsequences: Phase 5 is ACTIVE for test-first implementation of the approved leakage-safe feature engine. Phase 4 remains frozen PASS at checkpoint `fmp-v1-phase4-baselines`. The 2024-01-01 through 2026-08-20 final-test period remains locked; Phase 6 model fitting, broker/live/demo integration, and real-money trading remain unauthorized. DEC-008 remains unchanged.\n"
DECISION.write_text(decision, encoding="utf-8")

# Approved written spec status.
spec = SPEC.read_text(encoding="utf-8")
old_status = "**Status:** PROPOSED — written-spec approval required before DEC-029, implementation, or feature generation  "
new_status = "**Status:** APPROVED — frozen by DEC-029 before implementation or feature generation  "
if spec.count(old_status) != 1:
    raise SystemExit("spec status marker mismatch")
spec = spec.replace(old_status, new_status, 1)
SPEC.write_text(spec, encoding="utf-8")

# Project state: advance only to Phase 5 implementation, preserve later locks.
state = STATE.read_text(encoding="utf-8")
old_header = (
    "**Current phase:** Phase 4 — Baseline Strategy Research  \n"
    "**Phase status:** PASS\n"
    "**Next milestone:** Begin a separate Phase 5 leakage-safe feature-engine design from the frozen Phase 4 checkpoint; final-test data remains locked\n"
)
new_header = (
    "**Current phase:** Phase 5 — Leakage-Safe Feature Engineering  \n"
    "**Phase status:** ACTIVE\n"
    "**Next milestone:** Implement and verify `fmp-feature-v1` under DEC-029; final-test data remains locked and 2024+ processed partitions are not readable by normal Phase 5 tooling\n"
)
if state.count(old_header) != 1:
    raise SystemExit("project-state header marker mismatch")
state = state.replace(old_header, new_header, 1)
old_phase5 = (
    "## Phase 5 — UNSTARTED\n\n"
    "Phase 5 is the next project phase but has not started. It may begin only as separate leakage-safe feature-engine work under the approved project source. Phase 4 PASS does not authorize final-test inspection, broker/live integration, or real-money trading.\n\n"
    "Real-money trading remains locked; DEC-008 remains unchanged."
)
new_phase5 = (
    "## Phase 5 — ACTIVE\n\n"
    "DEC-029 freezes the leakage-safe `fmp-feature-v1` protocol in `docs/superpowers/specs/2026-09-14-phase5-leakage-safe-feature-engine-design.md`. Phase 5 may implement and validate only that predeclared feature layer across EURUSD/GBPUSD/USDJPY at 5m/15m/1h, using processed source coverage no later than 2023-12-31. Normal Phase 5 tooling must fail before opening any processed partition reaching 2024-01-01 or later.\n\n"
    "The eight approved families are returns, volatility/range, trend/structure, momentum, candle structure, session/time, market location, and spread/quote quality. Relative source activity, 1m feature matrices, cross-pair or multi-timeframe joins, labels, models, target-driven feature selection, and strategy retuning remain out of scope.\n\n"
    "Phase 4 remains frozen PASS at checkpoint `fmp-v1-phase4-baselines`; both serious candidates remain unchanged. Phase 6 model fitting, broker/live/demo integration, final-test inspection, and real-money trading remain locked; DEC-008 remains unchanged."
)
if state.count(old_phase5) != 1:
    raise SystemExit("Phase 5 state marker mismatch")
state = state.replace(old_phase5, new_phase5, 1)
STATE.write_text(state, encoding="utf-8")

# Durable state guard.
TEST.write_text(
    '''import unittest\nfrom pathlib import Path\n\n\ndef read(path: str) -> str:\n    return Path(path).read_text(encoding="utf-8")\n\n\nclass Phase5FeatureProtocolStateTests(unittest.TestCase):\n    def test_dec029_and_approved_spec_freeze_phase5_protocol(self) -> None:\n        decision = read("docs/decision-log.md")\n        spec = read("docs/superpowers/specs/2026-09-14-phase5-leakage-safe-feature-engine-design.md")\n        self.assertIn("DEC-029 — Phase 5 leakage-safe feature-engine protocol — APPROVED", decision)\n        self.assertIn("## DEC-029 — Phase 5 leakage-safe feature-engine protocol", decision)\n        self.assertIn("**Status:** APPROVED", spec)\n        self.assertIn("fmp-feature-v1", spec)\n        self.assertIn("2024-01-01 or later", spec)\n        self.assertIn("before that partition is opened", spec)\n\n    def test_project_state_advances_only_to_locked_phase5_feature_work(self) -> None:\n        state = read("docs/project-state.md")\n        self.assertIn("## Phase 4 — PASS", state)\n        self.assertIn("fmp-v1-phase4-baselines", state)\n        self.assertIn("**Current phase:** Phase 5 — Leakage-Safe Feature Engineering", state)\n        self.assertIn("**Phase status:** ACTIVE", state)\n        self.assertIn("## Phase 5 — ACTIVE", state)\n        self.assertIn("2024-01-01 or later", state)\n        self.assertIn("Phase 6 model fitting", state)\n        self.assertIn("real-money trading remain locked", state.lower())\n        self.assertIn("DEC-008 remains unchanged", state)\n\n\nif __name__ == "__main__":\n    unittest.main()\n''',
    encoding="utf-8",
)
