from __future__ import annotations

"""DEC-671: purely offline 2023 run-385 race model; NEVER dispatch."""

import argparse
from dataclasses import dataclass, field
from itertools import permutations
import json
from typing import Any

APPROVED_SHA = "a" * 40
UNREVIEWED_SHA = "b" * 40
RUN_NUMBER = 385
EVENTS = ("update_main", "competing_dispatch", "our_dispatch")


@dataclass
class Model:
    """Toy order-sensitive state, NOT a model of all GitHub trust principals."""

    freeze_ref: bool
    exclusive_dispatcher: bool
    main_sha: str = APPROVED_SHA
    next_run: int = RUN_NUMBER
    observed_before: str | None = None
    allocations: list[tuple[int, str, str]] = field(default_factory=list)
    our_allocated: tuple[int, str, str] | None = None

    def step(self, operation: str) -> None:
        if operation == "review_main":
            self.observed_before = self.main_sha
        elif operation == "update_main":
            if not self.freeze_ref:
                self.main_sha = UNREVIEWED_SHA
        elif operation == "competing_dispatch":
            if not self.exclusive_dispatcher:
                self.allocations.append((self.next_run, self.main_sha, "unapproved-input"))
                self.next_run += 1
        elif operation == "our_dispatch":
            # An ordinary client can only check before invoking dispatch.
            # This naive request has no server-side compare-and-dispatch.
            if self.observed_before == APPROVED_SHA:
                event = (self.next_run, self.main_sha, "approved-input")
                self.allocations.append(event)
                self.our_allocated = event
                self.next_run += 1
        else:
            raise ValueError("unexpected synthetic transition")

    def violated(self) -> bool:
        consumed = next((event for event in self.allocations if event[0] == RUN_NUMBER), None)
        if consumed is None or consumed != (RUN_NUMBER, APPROVED_SHA, "approved-input"):
            return True
        return self.our_allocated != consumed


def explore(freeze_ref: bool, exclusive_dispatcher: bool) -> dict[str, Any]:
    """Enumerate six orders AFTER review_main, without network or external IO."""
    unsafe: list[str] = []
    for order in permutations(EVENTS):
        state = Model(freeze_ref=freeze_ref, exclusive_dispatcher=exclusive_dispatcher)
        state.step("review_main")
        for operation in order:
            state.step(operation)
        if state.violated():
            unsafe.append(" -> ".join(("review_main",) + order))
    return {
        "tested_schedules": 6,
        "unsafe_schedules": len(unsafe),
        "first_counterexample": unsafe[0] if unsafe else None,
        "model_consistent": not unsafe,
    }


def assess(freeze_ref: bool, exclusive_dispatcher: bool) -> dict[str, Any]:
    results = explore(freeze_ref, exclusive_dispatcher)
    findings = []
    if not freeze_ref:
        findings.append("mutable main ref can race a pre-dispatch client check")
    if not exclusive_dispatcher:
        findings.append("competing dispatch can consume the unique annual run number")
    if results["unsafe_schedules"]:
        findings.append("offline schedule exhibits irreversible run385 misallocation")
    # Even if both flags claim to hold, this tool CANNOT authenticate actual
    # GitHub branch/ruleset/admin bypass or Actions-write exclusive controls.
    return {
        "status": "BLOCKED" if findings else "MODEL_CONSISTENT_UNVERIFIED",
        "findings": sorted(findings),
        "schedules_checked": results["tested_schedules"],
        "unsafe_schedules": results["unsafe_schedules"],
        "first_counterexample": results["first_counterexample"],
        "can_authorize_dispatch": False,
        "server_enforcement_verified": False,
        "annual_run_385_consumed": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        add_help=False, description="DEC-671 offline one-shot dispatch race model; NEVER dispatch")
    parser.add_argument("--execute-offline-model", action="store_true")
    parser.add_argument("--assume-ref-frozen", action="store_true")
    parser.add_argument("--assume-dispatch-exclusive", action="store_true")
    args = parser.parse_args(argv)
    if not args.execute_offline_model:
        result = {
            "status": "BLOCKED", "findings": ["explicit offline model opt-in missing"],
            "can_authorize_dispatch": False, "server_enforcement_verified": False,
            "annual_run_385_consumed": False,
        }
    else:
        result = assess(args.assume_ref_frozen, args.assume_dispatch_exclusive)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 3 if result["status"] == "MODEL_CONSISTENT_UNVERIFIED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
