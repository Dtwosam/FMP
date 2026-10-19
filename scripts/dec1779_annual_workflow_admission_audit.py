"""DEC-1779: historical-only, BLOCKED installed workflow step-order audit.

NO workflow run, GitHub API, credentials, market files, broker, job mutation,
admin attestation or safety gate is exercised by this offline source report.
The report is *deliberately incapable* of declaring security approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import runpy
import sys

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "phase8a-annual-pattern-catalogue.yml"
EVIDENCE_READER = ROOT / "scripts" / "dec1752_phase8a_readiness_report.py"
EXPECTED_GIT_BLOB_SHA1 = "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
EXPECTED_JOBS = ("annual_preflight", "annual_cell", "annual_freeze")
RISKY_BEFORE_GATE = (
    "Checkout", "Set up Python", "Install pinned annual catalogue runtime",
)
EXACT_GATE_STEP = {
    "annual_preflight": "Require separately authorized annual catalogue execution",
    "annual_cell": "Recheck separately authorized annual catalogue execution",
    "annual_freeze": "Recheck separately authorized annual catalogue execution",
}
EXPECTED_FIRST_STEPS = {
    "annual_preflight": (
        "Checkout", "Require exact merged main manual dispatch",
        "Resolve required prior annual segment", "Set up Python",
        "Install pinned annual catalogue runtime",
        "Fetch exact accepted EXP-044 source snapshots",
        "Validate exact accepted EXP-044 source snapshots",
        "Require separately authorized annual catalogue execution",
    ),
    "annual_cell": (
        "Checkout", "Require exact merged main manual dispatch",
        "Set up Python", "Install pinned annual catalogue runtime",
        "Recheck separately authorized annual catalogue execution",
    ),
    "annual_freeze": (
        "Checkout", "Require exact merged main manual dispatch",
        "Set up Python", "Install pinned annual catalogue runtime",
        "Recheck separately authorized annual catalogue execution",
    ),
}


class InvalidStaticEvidence(ValueError):
    """Source is different, truncated or ambiguous; never assume clearance."""


def _require(condition, message):
    if not condition:
        raise InvalidStaticEvidence(message)


def read_offline_source(path):
    """Reuse existing no-follow, bounded, dirfd source reader; no I/O beyond file."""
    helper = runpy.run_path(str(EVIDENCE_READER))["_read_regular_nofollow"]
    return helper(Path(path))


def extract_job_steps(source_text):
    """Parse only exact 2-space job labels and 6-space top-level step names.

    Not a YAML interpreter. Requires the reviewed workflow blob separately.
    """
    _require(type(source_text) is str, "workflow source must be UTF-8 text")
    blocks = {}
    for job in EXPECTED_JOBS:
        matches = list(re.finditer(
            r"^  " + re.escape(job) + r":\s*$", source_text, re.MULTILINE
        ))
        _require(len(matches) == 1, "missing or duplicate annual job: " + job)
        start = matches[0].end()
        next_job = re.search(r"^  [A-Za-z_][A-Za-z0-9_]*:\s*$",
                             source_text[start:], re.MULTILINE)
        end = start + next_job.start() if next_job else len(source_text)
        block = source_text[start:end]
        _require("    steps:\n" in block, "missing steps section: " + job)
        names = re.findall(r"^      - name: (.+)$", block, re.MULTILINE)
        _require(names and len(names) == len(set(names)),
                 "duplicate or empty annual job step: " + job)
        blocks[job] = {"steps": names, "source": block}
    return blocks


def classify_reviewed_step_order(source_text):
    jobs = extract_job_steps(source_text)
    outcomes = {}
    for job in EXPECTED_JOBS:
        names = jobs[job]["steps"]
        gate = EXACT_GATE_STEP[job]
        _require(
            names[:len(EXPECTED_FIRST_STEPS[job])] == list(
                EXPECTED_FIRST_STEPS[job]),
            "reviewed pre-gate sequence changed: " + job,
        )
        _require(names.count(gate) == 1, "missing/duplicate gate: " + job)
        gate_i = names.index(gate)
        _require(
            "python scripts/phase8a_annual_pattern_catalogue.py require-execution"
            in jobs[job]["source"],
            "historical gate runtime call absent: " + job,
        )
        earlier = [name for name in names[:gate_i] if name in RISKY_BEFORE_GATE]
        _require(len(earlier) == 3, "expected historical pre-gate setup ordering")
        check_i = names.index("Require exact merged main manual dispatch")
        _require(check_i > names.index("Checkout"),
                 "historic main ref check ordering unexpectedly changed")
        _require(
            'test "$GITHUB_REF" = "refs/heads/main"' in jobs[job]["source"],
            "historic installed runtime no longer explicitly main-bound",
        )
        outcomes[job] = {
            "gate_step_name": gate,
            "zero_based_in_job_gate_index": gate_i,
            "steps_before_gate": names[:gate_i],
            "risky_setup_before_gate": earlier,
            "checkout_before_runtime_gate": True,
            "main_ref_check_after_checkout": True,
            "requires_mutable_main_ref_in_job": True,
            "proved_precheckout_security_admission": False,
            "proved_preinstall_security_admission": False,
            "execution_authorized": False,
        }
    preflight = jobs["annual_preflight"]["steps"]
    _require(
        preflight.index("Fetch exact accepted EXP-044 source snapshots")
        < preflight.index(EXACT_GATE_STEP["annual_preflight"]),
        "historic preflight source fetch ordering unexpectedly changed",
    )
    outcomes["annual_preflight"]["source_snapshot_metadata_fetch_before_gate"] = True
    _require(
        'gh api "repos/$GITHUB_REPOSITORY/actions/runs/35867307338"'
        in jobs["annual_preflight"]["source"]
        and 'gh api "repos/$GITHUB_REPOSITORY/actions/runs/35876715434"'
        in jobs["annual_preflight"]["source"],
        "documentary source snapshot API calls no longer match historical order",
    )
    _require(
        "on:\n  workflow_dispatch:" in source_text
        and "ref: main" not in source_text,
        "installed manual-dispatch contract changed; require new review",
    )
    return outcomes


def report_blocked_admission(path=WORKFLOW):
    source = read_offline_source(path)
    actual = hashlib.sha1(
        b"blob " + str(len(source)).encode("ascii") + b"\0" + source
    ).hexdigest()
    _require(actual == EXPECTED_GIT_BLOB_SHA1,
             "installed workflow bytes differ from reviewed historical source")
    result = classify_reviewed_step_order(source.decode("utf-8"))
    return {
        "schema": "fmp_dec1779_offline_workflow_step_order_v1",
        "disposition": "BLOCKED_NOT_EXECUTABLE_AND_NOT_ADMIN_ATTESTED",
        "source_workflow": ".github/workflows/phase8a-annual-pattern-catalogue.yml",
        "historical_source_git_blob_sha1": actual,
        "source_sha_and_live_ref_at_dispatch_not_authenticated": True,
        "observed_jobs": result,
        "job_count": 3,
        "installed_workflow_requires_main": True,
        "precheckout_admission_proven": False,
        "preinstall_admission_proven": False,
        "authoritative_pre_dispatch_ref_lock_proven": False,
        "protected_2023_run385_attempt1_authorized": False,
        "annual_research_dispatch_authorized": False,
        "broker_or_trading_authorized": False,
        "allowed_actions": [],
        "next_external_review":
            "Independent administrator/security evidence of continuous no-bypass "
            "main identity or separately approved immutable-ref amendment; real "
            "installed early-admission/runner OS proofs; fresh one-shot run inventory; "
            "then separate human 2023/run385/attempt1 action.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="BLOCKED-only offline historic installed annual workflow audit")
    parser.add_argument("--workflow", type=Path, default=WORKFLOW)
    args = parser.parse_args(argv)
    try:
        report = report_blocked_admission(args.workflow)
    except (OSError, UnicodeError, TypeError, ValueError) as exc:
        print("BLOCKED: unreviewed static workflow source: " + str(exc),
              file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True, indent=2))
    return 3  # BLOCKED, never success or dispatch permission


if __name__ == "__main__":
    raise SystemExit(main())
