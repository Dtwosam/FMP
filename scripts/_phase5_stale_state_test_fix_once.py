from pathlib import Path

FILES = [
    "tests/test_phase4_acceptance_state.py",
    "tests/test_phase4_checkpoint_state.py",
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

REPLACEMENTS = (
    (
        '"**Current phase:** Phase 4 — Baseline Strategy Research"',
        '"**Current phase:** Phase 5 — Leakage-Safe Feature Engineering"',
    ),
    ('"**Phase status:** PASS"', '"**Phase status:** ACTIVE"'),
    ('"## Phase 5 — UNSTARTED"', '"## Phase 5 — ACTIVE"'),
)

for filename in FILES:
    path = Path(filename)
    text = path.read_text(encoding="utf-8")
    original = text
    replacement_count = 0
    for old, new in REPLACEMENTS:
        count = text.count(old)
        replacement_count += count
        text = text.replace(old, new)
    if replacement_count == 0:
        raise SystemExit(f"no stale Phase 4/5 state assertion found in {filename}")
    if text == original:
        raise SystemExit(f"no change made in {filename}")
    path.write_text(text, encoding="utf-8")
