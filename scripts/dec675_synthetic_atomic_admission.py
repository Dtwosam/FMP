from __future__ import annotations

"""DEC-675: offline atomic synthetic reservation; NEVER dispatches GitHub Actions.

Nothing here authenticates a GitHub ref, grants run authority, or contacts a
network. The database is always generated in a disposable private directory.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
from typing import Any

sys.dont_write_bytecode = True

SLOT = "dec675_disposable_slot_only"
EXPECTED_SHA = "a" * 40
EXPECTED_ACTOR = "local_synthetic_actor"
EXPECTED_PAYLOAD = "public_fake_payload"


def _answer(kind: str, detail: str) -> dict[str, Any]:
    return {
        "status": kind,
        "detail": detail,
        "can_authorize_dispatch": False,
        "server_enforcement_verified": False,
        "annual_run_385_consumed": False,
    }


def _initialize(db: Path) -> None:
    """Fail if an existing database would be overwritten or reset."""
    fd = os.open(db, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    os.close(fd)
    with sqlite3.connect(db, timeout=5) as conn:
        conn.execute("""CREATE TABLE reservations (
            slot TEXT PRIMARY KEY,
            expected_sha TEXT NOT NULL,
            expected_actor TEXT NOT NULL,
            expected_payload TEXT NOT NULL,
            state TEXT NOT NULL CHECK (state IN ('UNCLAIMED', 'RESERVED', 'HANDOFF_UNKNOWN')),
            claim_id TEXT
        )""")
        conn.execute(
            "INSERT INTO reservations VALUES (?, ?, ?, ?, 'UNCLAIMED', NULL)",
            (SLOT, EXPECTED_SHA, EXPECTED_ACTOR, EXPECTED_PAYLOAD),
        )


def _claim(db: Path, *, sha: str, actor: str, payload: str,
           claim_id: str) -> dict[str, Any]:
    """One SQLite transaction. This is not coupled to a GitHub dispatch."""
    if not all(isinstance(x, str) and 0 < len(x) <= 128
               for x in (sha, actor, payload, claim_id)):
        return _answer("BLOCKED", "invalid synthetic claim input")
    if sha != EXPECTED_SHA or actor != EXPECTED_ACTOR or payload != EXPECTED_PAYLOAD:
        return _answer("BLOCKED", "synthetic source/actor/payload mismatch")
    try:
        # URI mode=rw ensures a failed/restarted consumer never creates a new
        # database that could be mistaken for a fresh single-use slot.
        connection = sqlite3.connect(db.as_uri() + "?mode=rw", uri=True,
                                     timeout=5, isolation_level=None)
    except (sqlite3.Error, OSError, ValueError):
        return _answer("BLOCKED", "synthetic ledger unavailable; fail stop")
    try:
        connection.execute("BEGIN IMMEDIATE")
        result = connection.execute(
            """UPDATE reservations SET state='RESERVED', claim_id=?
               WHERE slot=? AND state='UNCLAIMED'
                 AND expected_sha=? AND expected_actor=? AND expected_payload=?""",
            (claim_id, SLOT, sha, actor, payload),
        )
        if result.rowcount != 1:
            connection.rollback()
            return _answer("BLOCKED", "slot already reserved or manifest mismatch")
        connection.commit()
        return _answer("SYNTHETIC_RESERVATION_UNVERIFIED",
                       "one disposable SQLite reservation recorded; NO DISPATCH")
    except sqlite3.Error:
        try:
            connection.rollback()
        except sqlite3.Error:
            pass
        # Commit may have been durable despite an error; NEVER retry based on
        # a local exception, and never declare an aborted external operation.
        return _answer("BLOCKED", "reservation state uncertain; DO NOT RETRY")
    finally:
        connection.close()



def _mark_synthetic_handoff_unknown(db: Path, claim_id: str) -> dict[str, Any]:
    """Durably record an unknown result BEFORE a hypothetical remote action.

    There is NO remote action or callback. Never declare delivered, successful
    dispatch, cancelled, or replay-safe: only a terminal fake unknown state.
    """
    if not isinstance(claim_id, str) or not (0 < len(claim_id) <= 128):
        return _answer("BLOCKED", "invalid fake reservation identity")
    try:
        conn = sqlite3.connect(db.as_uri() + "?mode=rw", uri=True,
                               timeout=5, isolation_level=None)
    except (sqlite3.Error, OSError, ValueError):
        return _answer("BLOCKED", "synthetic ledger unavailable; no replay")
    try:
        conn.execute("BEGIN IMMEDIATE")
        result = conn.execute(
            """UPDATE reservations SET state='HANDOFF_UNKNOWN'
               WHERE slot=? AND state='RESERVED' AND claim_id=?""",
            (SLOT, claim_id),
        )
        if result.rowcount != 1:
            conn.rollback()
            return _answer("BLOCKED", "no matching reservation or already unknown")
        conn.commit()
        return _answer("SYNTHETIC_HANDOFF_UNKNOWN",
                       "locally marked UNKNOWN before any possible transport; DO NOT RETRY")
    except sqlite3.Error:
        try:
            conn.rollback()
        except sqlite3.Error:
            pass
        return _answer("BLOCKED", "synthetic handoff ledger uncertain; DO NOT RETRY")
    finally:
        conn.close()


def _inspect(db: Path) -> tuple[str, str | None]:
    with sqlite3.connect(db.as_uri() + "?mode=ro", uri=True) as conn:
        row = conn.execute("SELECT state, claim_id FROM reservations WHERE slot=?", (SLOT,)).fetchone()
        if row is None:
            raise ValueError("synthetic slot missing")
        return row[0], row[1]


def run_demo(workers: int = 24) -> dict[str, Any]:
    """A single successful *fake* reservation across concurrent SQLite clients."""
    if sys.platform != "linux" or not os.path.isdir("/tmp") or os.path.islink("/tmp"):
        return _answer("BLOCKED", "fixed disposable Linux scratch root unavailable")
    if type(workers) is not int or not (2 <= workers <= 32):
        return _answer("BLOCKED", "unsafe worker count")
    try:
        with tempfile.TemporaryDirectory(prefix="dec675-disposable-", dir="/tmp") as directory:
            db = Path(directory) / "only-synthetic.sqlite3"
            _initialize(db)
            with ThreadPoolExecutor(max_workers=workers) as pool:
                tasks = [pool.submit(_claim, db, sha=EXPECTED_SHA, actor=EXPECTED_ACTOR,
                                     payload=EXPECTED_PAYLOAD, claim_id=f"attempt-{i}")
                         for i in range(workers)]
                outcomes = [task.result(timeout=15) for task in tasks]
            winners = [x for x in outcomes if x["status"] == "SYNTHETIC_RESERVATION_UNVERIFIED"]
            blocked = [x for x in outcomes if x["status"] == "BLOCKED"]
            persisted, claim_id = _inspect(db)
            replay = _claim(db, sha=EXPECTED_SHA, actor=EXPECTED_ACTOR,
                            payload=EXPECTED_PAYLOAD, claim_id="replay-after-crash")
            unknown = _mark_synthetic_handoff_unknown(db, claim_id or "")
            unknown_state, unknown_claim = _inspect(db)
            second_handoff = _mark_synthetic_handoff_unknown(db, claim_id or "")
            post_unknown_replay = _claim(db, sha=EXPECTED_SHA,
                                         actor=EXPECTED_ACTOR, payload=EXPECTED_PAYLOAD,
                                         claim_id="replay-after-unknown")
            checks = {
                "exactly_one_atomic_fake_reservation": len(winners) == 1,
                "other_contenders_rejected": len(blocked) == workers - 1,
                "durable_reservation_observed": persisted == "RESERVED" and
                                                claim_id is not None and claim_id != "replay-after-crash",
                "replay_after_restart_rejected": replay["status"] == "BLOCKED",
                "ambiguous_handoff_is_terminal": (
                    unknown["status"] == "SYNTHETIC_HANDOFF_UNKNOWN"
                    and unknown_state == "HANDOFF_UNKNOWN"
                    and unknown_claim == claim_id
                    and second_handoff["status"] == "BLOCKED"
                    and post_unknown_replay["status"] == "BLOCKED"
                ),
                "no_authorizing_output": all(x["can_authorize_dispatch"] is False and
                                               x["server_enforcement_verified"] is False
                                               for x in outcomes),
            }
            return {
                **_answer("LOCAL_DISPOSABLE_WITNESS_UNVERIFIED" if all(checks.values()) else "BLOCKED",
                          "fake SQLite concurrency only; server-side GitHub lock UNVERIFIED"),
                "synthetic_attempts": workers,
                "synthetic_winners": len(winners),
                "observed_checks": checks,
            }
    except (OSError, ValueError, sqlite3.Error, TimeoutError):
        return _answer("BLOCKED", "local synthetic concurrency witness failed")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=False,
        description="DEC-675 offline synthetic atomic admission test. NEVER run GitHub Actions.")
    parser.add_argument("--execute-disposable-demo", action="store_true")
    args = parser.parse_args(argv)
    verdict = run_demo() if args.execute_disposable_demo else _answer(
        "BLOCKED", "explicit disposable demo opt-in required")
    print(json.dumps(verdict, sort_keys=True, separators=(",", ":")))
    return 3 if verdict["status"] == "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
