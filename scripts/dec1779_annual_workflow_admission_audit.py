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



def inspect_installed_cell_matrix(source_text):
    """Validate historical installed matrix shape, not data or run readiness."""
    blocks = extract_job_steps(source_text)
    cell = blocks["annual_cell"]["source"]
    rows = re.findall(
        r"^          - symbol: ([A-Z]{6})\n"
        r"            timeframe: (5m|15m|1h)\n"
        r"            horizon: (60|240)\n"
        r"            feature_artifact_id: \"([0-9]+)\"\n"
        r"            feature_zip_sha256: ([0-9a-f]{64})\n"
        r"            outcome_artifact_id: \"([0-9]+)\"\n"
        r"            outcome_zip_sha256: ([0-9a-f]{64})$",
        cell, re.MULTILINE,
    )
    expected = {
        (symbol, timeframe, horizon)
        for symbol in ("EURUSD", "GBPUSD", "USDJPY")
        for timeframe in ("5m", "15m", "1h")
        for horizon in ("60", "240")
    }
    actual = [(symbol, timeframe, horizon) for
              symbol, timeframe, horizon, *_ in rows]
    _require(
        len(rows) == 18 and len(set(actual)) == 18
        and set(actual) == expected,
        "historical installed 18-cell matrix incomplete, broadened or duplicated",
    )
    artifacts = {}
    for symbol, timeframe, horizon, feature_id, feature_sha, outcome_id, outcome_sha in rows:
        key = (symbol, timeframe)
        values = (feature_id, feature_sha, outcome_id, outcome_sha)
        _require(all(int(v) > 0 for v in (feature_id, outcome_id)),
                 "historical artifact ID must be positive")
        if key in artifacts:
            _require(artifacts[key] == values,
                     "two horizons disagree on immutable source artifact lineage")
        else:
            artifacts[key] = values
    _require(len(artifacts) == 9,
             "historical matrix must have nine distinct pair/timeframe sources")
    _require(
        len(set(artifacts.values())) == 9,
        "different pair/timeframe sources share one unexpected artifact pair",
    )
    _require(
        "    needs: annual_preflight\n" in cell
        and "      fail-fast: false\n" in cell
        and "      max-parallel: 3\n" in cell
        and "    needs: annual_cell\n" in blocks["annual_freeze"]["source"],
        "historical annual job dependency or parallelization contract changed",
    )
    _require(
        "Download all 18 annual catalogue cell products" in
        blocks["annual_freeze"]["steps"],
        "freeze job must depend on all 18 historically declared cell artifacts",
    )
    return {
        "historical_cell_count": len(rows),
        "historical_unique_pair_timeframe_inputs": len(artifacts),
        "symbols": ["EURUSD", "GBPUSD", "USDJPY"],
        "timeframes": ["5m", "15m", "1h"],
        "horizons_minutes": [60, 240],
        "matrix_cells": [
            {"symbol": symbol, "timeframe": timeframe, "horizon_minutes": int(horizon)}
            for symbol, timeframe, horizon, *_ in rows
        ],
        "dataset_artifact_ids_and_hashes_not_reauthenticated": True,
        "historical_matrix_does_not_authorize_market_source_io": True,
        "installed_job_dependency_assertions_are_source_only": True,
    }



def inspect_pregate_step_payloads(source_text):
    """Inspect step payloads, not labels. No runtime or security attestation."""
    jobs = extract_job_steps(source_text)
    observations = {}
    for job in EXPECTED_JOBS:
        block = jobs[job]["source"]
        sections = {}
        matches = list(re.finditer(r"^      - name: ([^\n]+)\n",
                                   block, re.MULTILINE))
        for i, match in enumerate(matches):
            end = matches[i+1].start() if i+1 < len(matches) else len(block)
            _require(match[1] not in sections,
                     "duplicate command payload name: " + job)
            sections[match[1]] = block[match.end():end]
        _require(tuple(sections) == tuple(jobs[job]["steps"]),
                 "top-level steps/payload parsing mismatch: " + job)
        checkout = sections["Checkout"]
        python = sections["Set up Python"]
        install = sections["Install pinned annual catalogue runtime"]
        branch = sections["Require exact merged main manual dispatch"]
        gate = sections[EXACT_GATE_STEP[job]]
        _require(
            "        uses: actions/checkout@v6\n" in checkout
            and "        uses: actions/setup-python@v6\n" in python
            and '          python-version: "3.12.14"\n' in python,
            "historical checkout/setup command changed: " + job,
        )
        _require(
            "        run: python -m pip install -r "
            "requirements/exp061-discovery-run.txt -e .\n" in install,
            "historic unguarded install payload changed: " + job,
        )
        _require(
            '          test "$GITHUB_EVENT_NAME" = "workflow_dispatch"' in branch
            and '          test "$GITHUB_REF" = "refs/heads/main"' in branch,
            "historic main branch/test guard payload changed: " + job,
        )
        _require(
            "          python scripts/phase8a_annual_pattern_catalogue.py "
            "require-execution \\\n" in gate
            and "--annual-segment-label" in gate
            and "--code-commit" in gate
            and "$GITHUB_SHA" in gate,
            "historic in-run execution guard command/arguments changed: " + job,
        )
        _require(
            "permissions:\n  contents: read\n  actions: read\n" in source_text,
            "historical workflow top-level permissions changed",
        )
        names = jobs[job]["steps"]
        _require(names.index("Checkout") < names.index(
            "Require exact merged main manual dispatch") < names.index(
            "Install pinned annual catalogue runtime") < names.index(
            EXACT_GATE_STEP[job]),
            "historic pre-gate command ordering changed",
        )
        observed = [
            {"name": "Checkout", "payload": "actions/checkout@v6",
             "zero_based_step_index": names.index("Checkout")},
            {"name": "Set up Python",
             "payload": "actions/setup-python@v6 (Python 3.12.14)",
             "zero_based_step_index": names.index("Set up Python")},
            {"name": "Install pinned annual catalogue runtime",
             "payload": "python -m pip install -r "
                        "requirements/exp061-discovery-run.txt -e .",
             "zero_based_step_index": names.index(
                 "Install pinned annual catalogue runtime")},
        ]
        if job == "annual_preflight":
            fetch = sections["Fetch exact accepted EXP-044 source snapshots"]
            validation = sections["Validate exact accepted EXP-044 source snapshots"]
            _require(
                all(
                    'gh api "repos/$GITHUB_REPOSITORY/actions/runs/'
                    + run + '"' in fetch
                    for run in ("35867307338", "35876715434")
                )
                and "GH_TOKEN:" in fetch and "github.token" in fetch
                and fetch.count("          gh api ") == 4,
                "historical preflight metadata fetch operation changed",
            )
            _require(
                "          python scripts/phase8a_annual_pattern_catalogue.py "
                "preflight \\\n" in validation,
                "historical preflight source validation changed",
            )
            _require(
                names.index("Fetch exact accepted EXP-044 source snapshots")
                < names.index("Validate exact accepted EXP-044 source snapshots")
                < names.index(EXACT_GATE_STEP[job]),
                "source preflight network access unexpectedly reordered",
            )
            observed.extend((
                {"name": "Fetch exact accepted EXP-044 source snapshots",
                 "payload": "four gh api calls for two historical runs/artifact lists",
                 "zero_based_step_index": names.index(
                     "Fetch exact accepted EXP-044 source snapshots")},
                {"name": "Validate exact accepted EXP-044 source snapshots",
                 "payload": "phase8a_annual_pattern_catalogue.py preflight",
                 "zero_based_step_index": names.index(
                     "Validate exact accepted EXP-044 source snapshots")},
            ))
        observations[job] = {
            "actual_pregate_setup_and_read_payloads": sorted(
                observed, key=lambda item: item["zero_based_step_index"]),
            "static_source_only_not_actual_runner_trace": True,
            "no_early_admission_or_immutable_server_ref_proven": True,
        }
    return observations


def report_blocked_admission(path=WORKFLOW):
    source = read_offline_source(path)
    actual = hashlib.sha1(
        b"blob " + str(len(source)).encode("ascii") + b"\0" + source
    ).hexdigest()
    _require(actual == EXPECTED_GIT_BLOB_SHA1,
             "installed workflow bytes differ from reviewed historical source")
    decoded = source.decode("utf-8")
    result = classify_reviewed_step_order(decoded)
    matrix = inspect_installed_cell_matrix(decoded)
    pregate = inspect_pregate_step_payloads(decoded)
    return {
        "schema": "fmp_dec1779_offline_workflow_step_order_v1",
        "disposition": "BLOCKED_NOT_EXECUTABLE_AND_NOT_ADMIN_ATTESTED",
        "source_workflow": ".github/workflows/phase8a-annual-pattern-catalogue.yml",
        "historical_source_git_blob_sha1": actual,
        "source_sha_and_live_ref_at_dispatch_not_authenticated": True,
        "observed_jobs": result,
        "historical_matrix_inventory": matrix,
        "historical_pregate_payloads": pregate,
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
