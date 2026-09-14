from pathlib import Path

FILES = [
    "tests/test_phase4_mean_reversion_evidence_state.py",
    "tests/test_phase4_mean_reversion_state.py",
    "tests/test_phase4_previous_day_rejection_state.py",
    "tests/test_phase4_research_state.py",
    "tests/test_phase4_session_breakout_evidence_state.py",
    "tests/test_phase4_session_sweep_state.py",
    "tests/test_phase4_trend_continuation_evidence_state.py",
    "tests/test_phase4_trend_continuation_state.py",
    "tests/test_phase4_volatility_breakout_state.py",
]

old = '**Phase status:** ACTIVE'
new = '**Phase status:** PASS'

for filename in FILES:
    path = Path(filename)
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected exactly one stale phase-status assertion in {filename}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")

extra_replacements = [
    (
        "tests/test_phase4_research_state.py",
        'self.assertIn("## Phase 4 — ACTIVE", text)',
        'self.assertIn("## Phase 4 — PASS", text)',
    ),
    (
        "tests/test_phase4_session_sweep_state.py",
        'self.assertIn("All six planned baseline families are now complete", state)',
        'self.assertIn("All six planned baseline families have complete benchmark evidence and experiment-log entries", state)',
    ),
]

for filename, stale, current in extra_replacements:
    path = Path(filename)
    text = path.read_text(encoding="utf-8")
    if text.count(stale) != 1:
        raise SystemExit(f"expected exactly one stale wording assertion in {filename}")
    path.write_text(text.replace(stale, current, 1), encoding="utf-8")
