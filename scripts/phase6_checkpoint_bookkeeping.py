from pathlib import Path

CLOSURE_SHA = "5d387b7ca93d04c498eb04c376e0dd92f1fe1953"
CHECKPOINT = "fmp-v1-phase6-models"
TESTS_RUN = "34972534430"
PHASE3_RUN = "34972534435"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one occurrence, found {count}")
    return text.replace(old, new, 1)


evidence_path = Path("docs/phase6-ml-filter-evidence.md")
evidence = evidence_path.read_text(encoding="utf-8")
evidence = replace_once(
    evidence,
    "**Checkpoint:** `fmp-v1-phase6-models` — PENDING",
    f"**Checkpoint:** `{CHECKPOINT}` — CREATED at `{CLOSURE_SHA}`",
    "evidence checkpoint header",
)
closure_section = f"""## Closure checkpoint

The source-free Phase 6 acceptance closure merged to `main` at `{CLOSURE_SHA}`. Fresh verification on that exact merge commit completed successfully before checkpoint creation:

- tests run `{TESTS_RUN}` — SUCCESS, 573/573 tests PASS, workflow YAML PASS, compile PASS.
- Phase 3 acceptance run `{PHASE3_RUN}` — SUCCESS.
- Phase 1 source-capable workflows remained suppressed by the `[phase1-no-source]` closure path.

The immutable lightweight checkpoint `{CHECKPOINT}` was then created and independently verified to resolve directly to commit `{CLOSURE_SHA}` (`type = commit`). No Phase 7 work, final-test access, broker/live/demo integration, or real-money trading was opened by checkpoint creation.

"""
evidence = replace_once(
    evidence,
    "## Acceptance conclusion\n",
    closure_section + "## Acceptance conclusion\n",
    "evidence acceptance conclusion",
)
evidence = replace_once(
    evidence,
    "Phase 6 is therefore formally **PASS**. Checkpoint `fmp-v1-phase6-models` remains **PENDING** until this source-free acceptance closure is merged and fresh merged-main tests plus Phase 3 acceptance succeed. Phase 7 remains UNSTARTED. The final-test period remains locked, and no broker/live/demo integration or real-money trading is authorized.",
    f"Phase 6 is therefore formally **PASS**. Checkpoint `{CHECKPOINT}` is **CREATED** at the verified closure merge `{CLOSURE_SHA}` after tests run `{TESTS_RUN}` and Phase 3 acceptance run `{PHASE3_RUN}` both succeeded. Phase 7 remains UNSTARTED. The final-test period remains locked, and no broker/live/demo integration or real-money trading is authorized.",
    "evidence final checkpoint sentence",
)
evidence_path.write_text(evidence, encoding="utf-8")

state_path = Path("docs/project-state.md")
state = state_path.read_text(encoding="utf-8")
state = replace_once(
    state,
    "**Next milestone:** Create immutable Phase 6 checkpoint; Phase 7 remains UNSTARTED and final-test data remains locked",
    "**Next milestone:** Phase 6 is closed at its immutable checkpoint; Phase 7 remains UNSTARTED and final-test data remains locked",
    "project-state next milestone",
)
state = replace_once(
    state,
    "- checkpoint: PENDING (`fmp-v1-phase6-models`)",
    f"- checkpoint: `{CHECKPOINT}` — CREATED at `{CLOSURE_SHA}`\n- closure merge: `{CLOSURE_SHA}`\n- post-merge tests run: `{TESTS_RUN}` — SUCCESS, 573/573 tests PASS, workflow YAML PASS, compile PASS\n- post-merge Phase 3 acceptance run: `{PHASE3_RUN}` — SUCCESS",
    "project-state checkpoint",
)
state_path.write_text(state, encoding="utf-8")
