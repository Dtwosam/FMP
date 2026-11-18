"""Auditable reading of unprotected experiment documents.

The append-only trial ledger remains the record of transcribed trials.
This module does not rewrite it and does not invent a programme-wide total.
A heading count is not a trial count. A result row is not another trial.
An engineering or governance note is not a market experiment.

Counting rules
--------------

- Research programme: every record in the experiment log and the ledger.
  Its trial total stays unknown unless one source states that total.
- Hypothesis family: related rules that would have to be counted together
  before a multiple-testing adjustment. Historical families in this
  repository are not closed.
- Strategy configuration: one distinct rule-and-parameter combination.
  Only a printed total is verified. A per-cell factor is not multiplied
  into a total.
- Research trial: one evaluation of a stated hypothesis or configuration
  on a declared dataset and protocol.
- Result row: one reported measurement, including a split or a cost case.
- Engineering test: software, workflow, accounting, or simulator work.
  It is not a market experiment.

Benjamini-Yekutieli adjustment is available only through
``family_correction_status`` after the caller supplies a closed family.
Historical documents do not supply that family. The status is then
``INSUFFICIENT_TRIAL_CENSUS`` or ``INSUFFICIENT_STATISTICAL_EVIDENCE``.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
from pathlib import Path
from typing import Mapping

from fmp.research.multiple_testing import benjamini_yekutieli
from fmp.research.trial_ledger import load_trials

VERIFIED = "verified"
PARTIAL = "partially_supported"
UNAVAILABLE = "unavailable"
CONFLICTED = "conflicted"

INSUFFICIENT_TRIAL_CENSUS = "INSUFFICIENT_TRIAL_CENSUS"
INSUFFICIENT_STATISTICAL_EVIDENCE = "INSUFFICIENT_STATISTICAL_EVIDENCE"
ELIGIBLE_FOR_BY_ADJUSTMENT = "ELIGIBLE_FOR_BY_ADJUSTMENT"

_HEADING = re.compile(r"^### (EXP-\d{8}-\d+)\b[^\n]*", re.MULTILINE)
_PER_CELL = re.compile(
    r"exactly (\d+) (?:predeclared |strategy )?configurations per pair/timeframe",
    re.IGNORECASE,
)
_ROWS = re.compile(r"\b(\d+)/\1 (configuration )?rows\b", re.IGNORECASE)
_IDENTITIES = re.compile(
    r"exactly (\d+) pair/timeframe/configuration identities",
    re.IGNORECASE,
)
_OF_POINTS = re.compile(
    r"\b(?:zero|one) of (\d+) pair/timeframe/[A-Za-z0-9/_ -]*points\b",
    re.IGNORECASE,
)
_BASELINE_POINTS = re.compile(
    r"exactly one of (\d+) baseline points",
    re.IGNORECASE,
)
_SPLIT_POINTS = re.compile(
    r"all (\d+) development and all \1 validation",
    re.IGNORECASE,
)
# A commit token contains a hex letter. Numeric artifact and run IDs do not.
_SHA = re.compile(r"`((?=[0-9a-f]*[a-f])[0-9a-f]{7,40})`")
_P_VALUE = re.compile(r"\bp-value\b|\bp\s*=\s*0\.\d+", re.IGNORECASE)
_YEAR = re.compile(r"\b(20[0-2][0-9])\b")
_ENGINEERING = re.compile(
    r"\b(workflow|preflight|freeze|proof|authorization|operator|runtime)\b|DEC-\d+",
    re.IGNORECASE,
)


def counting_rules() -> tuple[str, ...]:
    """Stable statement of the rules the parser applies."""
    return (
        "A programme-wide trial count stays unknown unless a source states that total.",
        "An experiment heading is not a trial.",
        "A printed configuration total is the only verified configuration count.",
        "A per-cell factor is recorded and is not multiplied into a total.",
        "A result row is a measurement dimension, not an additional trial.",
        "The same configuration cited by the ledger and the experiment log is one record.",
        "Repeated experiment IDs are kept apart and are not summed.",
        "Engineering, governance, and simulator checks are not market trials.",
        "A family can be sent to Benjamini-Yekutieli only when it is closed and every member has a valid p-value.",
        "A complete count does not make a p-value valid.",
    )


def _count(value: int | None, status: str, provenance: list[dict[str, str]]) -> dict[str, object]:
    return {"value": value, "status": status, "provenance": provenance}


def _blank_count() -> dict[str, object]:
    return _count(None, UNAVAILABLE, [])


def _integers(pattern: re.Pattern[str], text: str) -> list[int]:
    return [int(match.group(1)) for match in pattern.finditer(text)]


def _unique(values: list[int]) -> int | None:
    unique = sorted(set(values))
    if len(unique) == 1:
        return unique[0]
    return None


def _bullet(section: str, label: str) -> str | None:
    prefix = f"- {label}:"
    for line in section.splitlines():
        if line.startswith(prefix):
            return line[len(prefix):].strip()
    return None


def _sections(text: str, source: str) -> list[dict[str, object]]:
    matches = list(_HEADING.finditer(text))
    sections = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections.append({
            "experiment_id": match.group(1),
            "title": match.group(0)[4:].strip(),
            "body": text[match.end():end],
            "source": source,
            "occurrence_in_file": index + 1,
        })
    return sections


def _printed_configuration_total(body: str, source: str) -> dict[str, object]:
    found: list[tuple[int, str]] = []
    for pattern, label in (
        (_IDENTITIES, "exactly N pair/timeframe/configuration identities"),
        (_OF_POINTS, "N pair/timeframe points"),
        (_BASELINE_POINTS, "exactly one of N baseline points"),
        (_SPLIT_POINTS, "all N development and all N validation"),
    ):
        for value in _integers(pattern, body):
            found.append((value, label))
    if not found:
        return _blank_count()
    values = sorted({item[0] for item in found})
    provenance = [
        {"source": source, "locator": label, "quote": str(value)}
        for value, label in found
    ]
    if len(values) != 1:
        return _count(None, CONFLICTED, provenance)
    return _count(values[0], VERIFIED, provenance)


def _result_rows(body: str, source: str) -> dict[str, object]:
    values = _integers(_ROWS, body)
    if not values:
        return _blank_count()
    provenance = [{
        "source": source,
        "locator": "N/N rows",
        "quote": str(value),
    } for value in values]
    unique = _unique(values)
    if unique is None:
        return _count(None, CONFLICTED, provenance)
    return _count(unique, VERIFIED, provenance)


def _per_cell(body: str, source: str) -> dict[str, object]:
    values = _integers(_PER_CELL, body)
    if not values:
        return _blank_count()
    provenance = [{
        "source": source,
        "locator": "configurations per pair/timeframe",
        "quote": str(value),
    } for value in values]
    unique = _unique(values)
    if unique is None:
        return _count(None, CONFLICTED, provenance)
    return _count(unique, PARTIAL, provenance)


def _merge_counts(left: dict[str, object], right: dict[str, object]) -> dict[str, object]:
    provenance = list(left["provenance"]) + list(right["provenance"])
    left_value = left["value"]
    right_value = right["value"]
    if left["status"] == UNAVAILABLE:
        return right
    if right["status"] == UNAVAILABLE:
        return left
    if left["status"] == CONFLICTED or right["status"] == CONFLICTED:
        return _count(None, CONFLICTED, provenance)
    if left_value != right_value:
        return _count(None, CONFLICTED, provenance)
    status = VERIFIED if left["status"] == VERIFIED or right["status"] == VERIFIED else PARTIAL
    return _count(left_value if isinstance(left_value, int) else None, status, provenance)


def _ledger_configuration(evidence: Mapping[str, object], source: str) -> dict[str, object]:
    note = str(evidence.get("note") or "")
    count = evidence.get("trial_count")
    lowered = note.lower()
    present = (
        evidence.get("available") is True
        and isinstance(count, int)
        and not isinstance(count, bool)
    )
    if not present:
        return _blank_count()
    provenance = [{
        "source": source,
        "locator": "statistical_evidence.trial_count",
        "quote": note or str(count),
    }]
    # A scoped count such as "not the earlier N-configuration search" is a
    # different evaluation. It is preserved as a quote and is not a grid total.
    if "not the earlier" in lowered or "configuration" not in lowered:
        return _count(None, UNAVAILABLE, provenance)
    return _count(count, VERIFIED, provenance)


def _ledger_rows(evidence: Mapping[str, object], source: str) -> dict[str, object]:
    rows = evidence.get("result_rows")
    if isinstance(rows, int) and not isinstance(rows, bool) and rows >= 0:
        return _count(rows, VERIFIED, [{
            "source": source,
            "locator": "statistical_evidence.result_rows",
            "quote": str(rows),
        }])
    return _blank_count()


def _role(title: str, body: str, ledger: Mapping[str, object] | None) -> str:
    version = "" if ledger is None else str(ledger.get("version") or "")
    if version == "not-a-trial":
        return "not_a_market_trial"
    if version.startswith("return_vs_ruin") or version.startswith("retail_costs"):
        return "measurement_tool"
    parameters = _bullet(body, "Parameters/search space") or ""
    if parameters.lower().startswith("no search space"):
        return "frozen_candidate_reevaluation"
    if (
        _printed_configuration_total(body, "")["status"] != UNAVAILABLE
        or _result_rows(body, "")["status"] != UNAVAILABLE
        or _per_cell(body, "")["status"] != UNAVAILABLE
    ):
        return "strategy_configuration_search"
    if _ENGINEERING.search(title) or _ENGINEERING.search(body[:500]):
        return "engineering_or_governance"
    return "unclassified"


def _exposure(body: str, ledger: Mapping[str, object] | None) -> dict[str, object]:
    data_range = _bullet(body, "Data range") or ""
    train = _bullet(body, "Train period") or ""
    validation = _bullet(body, "Validation period") or ""
    final_test = _bullet(body, "Final-test touched?")
    window = " ".join((data_range, train, validation))
    years = {int(year) for year in _YEAR.findall(window)}
    overlaps = any(2015 <= year <= 2022 for year in years)
    ledger_exposure = {} if ledger is None else ledger.get("data_exposure")
    ledger_overlap = None
    ledger_untouched = None
    if isinstance(ledger_exposure, Mapping):
        if isinstance(ledger_exposure.get("overlaps_2015_2022"), bool):
            ledger_overlap = ledger_exposure["overlaps_2015_2022"]
        if isinstance(ledger_exposure.get("untouched_validation"), bool):
            ledger_untouched = ledger_exposure["untouched_validation"]
    if ledger_overlap is True:
        overlaps = True
    if not years and ledger_overlap is None:
        overlap_status = UNAVAILABLE
        overlaps_value = None
    else:
        overlap_status = VERIFIED if years or ledger_overlap is not None else UNAVAILABLE
        overlaps_value = overlaps if overlap_status == VERIFIED else None
    if overlaps_value is True:
        untouched = False
        untouched_status = VERIFIED
    elif ledger_untouched is False or (final_test or "").upper().startswith("YES"):
        untouched = False
        untouched_status = VERIFIED
    elif ledger_untouched is True and overlaps_value is not True:
        untouched = True
        untouched_status = PARTIAL
    else:
        untouched = None
        untouched_status = UNAVAILABLE
    scored_2024_through_2026 = "2024" in window and "2025" in window
    return {
        "overlaps_2015_2022": overlaps_value,
        "overlaps_2015_2022_status": overlap_status,
        "untouched_validation": untouched,
        "untouched_validation_status": untouched_status,
        "final_test_touched_quote": final_test,
        "scored_2024_through_2026": scored_2024_through_2026,
        "data_range": data_range or None,
        "train_period": train or None,
        "validation_period": validation or None,
    }


def _correction(role: str, duplicate: bool, configuration: dict[str, object], body: str) -> tuple[str, str | None]:
    if role in {"engineering_or_governance", "not_a_market_trial", "measurement_tool"}:
        return "no", None
    if (
        role in {"unclassified", "declared_search_not_executed", "frozen_candidate_reevaluation"}
        or duplicate
        or configuration["status"] != VERIFIED
    ):
        return "no", INSUFFICIENT_TRIAL_CENSUS
    if _P_VALUE.search(body) is None:
        return "no", INSUFFICIENT_STATISTICAL_EVIDENCE
    return "unknown", INSUFFICIENT_STATISTICAL_EVIDENCE


def _hypothesis_family(
    title: str,
    role: str,
    ledger: Mapping[str, object] | None,
) -> str | None:
    """Family label copied from a ledger version, or from a market-trial title."""
    if ledger is not None:
        version = str(ledger.get("version") or "").strip()
        if version and version != "not-a-trial":
            return version
    if role in {
        "strategy_configuration_search",
        "declared_search_not_executed",
        "frozen_candidate_reevaluation",
        "unclassified",
    }:
        return title
    return None


def _overlap_note(duplicate: bool, ledger_match: bool) -> str | None:
    notes = []
    if duplicate:
        notes.append("Repeated experiment ID. These sections are kept apart and are not summed.")
    if ledger_match:
        notes.append("The experiment log and the trial ledger use this ID. They are stored as one record.")
    if not notes:
        return None
    return " ".join(notes)


def _executed_count(
    configuration: dict[str, object],
    rows: dict[str, object],
) -> tuple[str, dict[str, object]]:
    if configuration["status"] == VERIFIED and rows["status"] == VERIFIED:
        provenance = list(configuration["provenance"]) + list(rows["provenance"])
        return "evaluated_grid", _count(configuration["value"], VERIFIED, provenance)
    if configuration["status"] == VERIFIED:
        return "printed_total_not_an_execution", _blank_count()
    return "not_printed", _blank_count()


def _record_from_section(
    section: Mapping[str, object],
    ledger: Mapping[str, object] | None,
    *,
    occurrence_index: int,
    occurrence_count: int,
) -> dict[str, object]:
    experiment_id = str(section["experiment_id"])
    body = str(section["body"])
    source = str(section["source"])
    title = str(section["title"])
    configuration = _printed_configuration_total(body, source)
    rows = _result_rows(body, source)
    if ledger is not None:
        evidence = ledger.get("statistical_evidence")
        if isinstance(evidence, Mapping):
            configuration = _merge_counts(
                configuration,
                _ledger_configuration(evidence, "trial-ledger"),
            )
            rows = _merge_counts(rows, _ledger_rows(evidence, "trial-ledger"))
    meaning, executed = _executed_count(configuration, rows)
    role = _role(title, body, ledger)
    if meaning == "printed_total_not_an_execution" and re.search(
        r"NO BENCHMARK|Trade count: pending",
        body,
        re.IGNORECASE,
    ):
        role = "declared_search_not_executed"
    duplicate = occurrence_count > 1
    eligible, blocker = _correction(role, duplicate, configuration, body)
    commits = list(dict.fromkeys(_SHA.findall(body)))
    if ledger is not None:
        ledger_commit = str(ledger.get("source_commit") or "")
        if ledger_commit and ledger_commit not in commits:
            commits.append(ledger_commit)
    missing = []
    if configuration["status"] != VERIFIED:
        missing.append("No single printed configuration total.")
    if rows["status"] != VERIFIED:
        missing.append("No single printed result-row total.")
    if executed["status"] != VERIFIED:
        missing.append("Printed configuration text does not by itself show an executed trial count.")
    if not commits:
        missing.append("No source commit quoted in the section.")
    if duplicate:
        missing.append("This experiment ID is reused, so the sections are not one trial.")
    return {
        "record_id": f"{experiment_id}#{occurrence_index}",
        "experiment_id": experiment_id,
        "title": title,
        "hypothesis_family": _hypothesis_family(title, role, ledger),
        "role": role,
        "configuration_meaning": meaning,
        "source_document": source,
        "source_commits": commits,
        "occurrence_index": occurrence_index,
        "occurrence_count": occurrence_count,
        "duplicate_experiment_id": duplicate,
        "potential_duplicate_or_overlap": _overlap_note(duplicate, ledger is not None),
        "research_period": {
            "data_range": _bullet(body, "Data range"),
            "train_period": _bullet(body, "Train period"),
            "validation_period": _bullet(body, "Validation period"),
        },
        "data_exposure": _exposure(body, ledger),
        "configuration_count": configuration,
        "configurations_per_pair_timeframe": _per_cell(body, source),
        "executed_trial_count": executed,
        "result_row_count": rows,
        "evidence_locations": [source] + (["trial-ledger"] if ledger is not None else []),
        "missing_information": missing,
        "eligible_for_statistical_correction": eligible,
        "correction_blocker": blocker,
        "p_values_present": _P_VALUE.search(body) is not None,
    }


def _ledger_only(trial: Mapping[str, object]) -> dict[str, object]:
    experiment_id = str(trial["trial_id"])
    evidence = trial.get("statistical_evidence")
    evidence_map = evidence if isinstance(evidence, Mapping) else {}
    configuration = _ledger_configuration(evidence_map, "trial-ledger")
    role = _role("", "", trial)
    return {
        "record_id": f"{experiment_id}#ledger",
        "experiment_id": experiment_id,
        "title": experiment_id,
        "hypothesis_family": _hypothesis_family(experiment_id, role, trial),
        "role": role,
        "source_document": "trial-ledger",
        "source_commits": [str(trial.get("source_commit") or "")],
        "occurrence_index": 1,
        "occurrence_count": 1,
        "duplicate_experiment_id": False,
        "potential_duplicate_or_overlap": None,
        "research_period": {},
        "data_exposure": _exposure("", trial),
        "configuration_count": configuration,
        "configuration_meaning": "ledger_only",
        "configurations_per_pair_timeframe": _blank_count(),
        "executed_trial_count": _blank_count(),
        "result_row_count": _ledger_rows(evidence_map, "trial-ledger"),
        "evidence_locations": ["trial-ledger"],
        "missing_information": [
            "This ledger row has no experiment-log section.",
            "The programme-wide trial count remains unknown.",
        ],
        "eligible_for_statistical_correction": "no",
        "correction_blocker": None if role == "not_a_market_trial" else INSUFFICIENT_TRIAL_CENSUS,
        "p_values_present": False,
    }


def _tuple_length(node: ast.AST) -> int | None:
    if isinstance(node, (ast.Tuple, ast.List)):
        return len(node.elts)
    return None


def declared_source_grids(root: Path) -> tuple[dict[str, object], ...]:
    """Parameter tuples written in research source. They are not executions."""
    research = root / "src" / "fmp" / "research"
    found = []
    if not research.is_dir():
        return ()
    for path in sorted(research.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            if not isinstance(node, ast.Assign):
                continue
            length = _tuple_length(node.value)
            if length is None:
                continue
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.endswith("_GRID"):
                    found.append({
                        "name": target.id,
                        "source": str(path.relative_to(root)),
                        "declared_parameter_count": length,
                        "status": "source_declared_not_an_execution_count",
                    })
    return tuple(found)


def family_correction_status(
    *,
    family_id: str,
    closed: bool,
    members: tuple[Mapping[str, object], ...] | list[Mapping[str, object]],
) -> dict[str, object]:
    """Decide whether a caller-supplied family may use the BY adjustment.

    Historical inventory construction passes ``closed=False``. A synthetic
    test may pass a closed family. This function does not read protected data.
    """
    if not isinstance(family_id, str) or not family_id.strip():
        return {
            "family_id": family_id,
            "status": INSUFFICIENT_TRIAL_CENSUS,
            "eligible_for_statistical_correction": "no",
            "adjustment": None,
        }
    identities = [str(member.get("hypothesis_id") or "") for member in members]
    if (
        not closed
        or not members
        or any(member.get("count_status") != VERIFIED for member in members)
        or len(set(identities)) != len(identities)
        or any(not identity.strip() for identity in identities)
    ):
        return {
            "family_id": family_id,
            "status": INSUFFICIENT_TRIAL_CENSUS,
            "eligible_for_statistical_correction": "no",
            "adjustment": None,
        }
    p_values: dict[str, float] = {}
    for member in members:
        value = member.get("p_value")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return {
                "family_id": family_id,
                "status": INSUFFICIENT_STATISTICAL_EVIDENCE,
                "eligible_for_statistical_correction": "no",
                "adjustment": None,
            }
        p_values[str(member["hypothesis_id"])] = float(value)
    try:
        assessment = benjamini_yekutieli(
            p_values,
            family_id=family_id,
            total_hypotheses=len(p_values),
        )
    except ValueError:
        return {
            "family_id": family_id,
            "status": INSUFFICIENT_STATISTICAL_EVIDENCE,
            "eligible_for_statistical_correction": "no",
            "adjustment": None,
        }
    return {
        "family_id": family_id,
        "status": ELIGIBLE_FOR_BY_ADJUSTMENT,
        "eligible_for_statistical_correction": "yes",
        "adjustment": {
            "method": assessment.method,
            "total_hypotheses": assessment.total_hypotheses,
            "rejected_hypotheses": list(assessment.rejected_hypotheses),
            "adjusted_p_values": [
                {"hypothesis_id": hypothesis_id, "adjusted_p": adjusted}
                for hypothesis_id, adjusted in assessment.adjusted_p_values
            ],
        },
    }


def build_inventory(
    root: Path,
    *,
    experiment_log: Path | None = None,
    ledger_path: Path | None = None,
) -> dict[str, object]:
    """Read unprotected documents. Does not write the ledger or the log."""
    log_path = experiment_log or (root / "docs" / "experiment-log.md")
    ledger = ledger_path or (root / "docs" / "trial-ledger.jsonl")
    before = ledger.read_bytes() if ledger.is_file() else None
    log_text = log_path.read_text(encoding="utf-8") if log_path.is_file() else ""
    try:
        source_name = str(log_path.resolve().relative_to(root.resolve()))
    except ValueError:
        source_name = log_path.name
    sections = _sections(log_text, source_name)
    trials = load_trials(ledger) if ledger.is_file() else ()
    if before is not None and ledger.read_bytes() != before:
        raise RuntimeError("inventory read changed the trial ledger")
    by_id: dict[str, Mapping[str, object]] = {}
    duplicate_ledger = False
    for trial in trials:
        trial_id = str(trial["trial_id"])
        if trial_id in by_id:
            duplicate_ledger = True
        by_id[trial_id] = trial
    counts: dict[str, int] = {}
    for section in sections:
        experiment_id = str(section["experiment_id"])
        counts[experiment_id] = counts.get(experiment_id, 0) + 1
    seen_counts: dict[str, int] = {}
    records = []
    for section in sections:
        experiment_id = str(section["experiment_id"])
        seen_counts[experiment_id] = seen_counts.get(experiment_id, 0) + 1
        records.append(_record_from_section(
            section,
            by_id.get(experiment_id),
            occurrence_index=seen_counts[experiment_id],
            occurrence_count=counts[experiment_id],
        ))
    seen = {str(section["experiment_id"]) for section in sections}
    for trial_id in sorted(by_id):
        if trial_id not in seen:
            records.append(_ledger_only(by_id[trial_id]))
    records.sort(key=lambda row: (str(row["experiment_id"]), int(row["occurrence_index"])))
    verified = [
        {
            "experiment_id": row["experiment_id"],
            "record_id": row["record_id"],
            "configuration_count": row["configuration_count"]["value"],
            "configuration_meaning": row["configuration_meaning"],
            "executed_trial_count": row["executed_trial_count"]["value"],
            "result_row_count": row["result_row_count"]["value"],
        }
        for row in records
        if row["configuration_count"]["status"] == VERIFIED
    ]
    duplicate_ids = sorted(experiment_id for experiment_id, count in counts.items() if count > 1)
    families = family_correction_status(
        family_id="historical-repository",
        closed=False,
        members=(),
    )
    return {
        "counting_rules": list(counting_rules()),
        "programme_trial_count": None,
        "programme_trial_count_status": UNAVAILABLE,
        "programme_trial_count_reason": (
            "The ledger census leaves the programme-wide trial count null. "
            "Heading counts, pull requests, and verified local grids are not that total."
        ),
        "experiment_heading_count": len(sections),
        "unique_experiment_ids_in_log": len(counts),
        "duplicate_experiment_ids": duplicate_ids,
        "ledger_duplicate_trial_id": duplicate_ledger,
        "verified_local_configuration_counts": verified,
        "verified_local_counts_are_not_a_programme_total": True,
        "records": records,
        "source_declared_grids": list(declared_source_grids(root)),
        "historical_family_correction": families,
        "ledger_sha256": hashlib.sha256(before).hexdigest() if before is not None else None,
    }


def inventory_json(inventory: Mapping[str, object]) -> str:
    return json.dumps(inventory, indent=2, sort_keys=True) + "\n"


def _exposure_lines(records: object) -> list[str]:
    """State exposure only for records whose own fields support the claim."""
    if not isinstance(records, list):
        return ["Exposure records are unavailable."]
    market_roles = {
        "strategy_configuration_search",
        "declared_search_not_executed",
        "frozen_candidate_reevaluation",
        "unclassified",
    }
    overlapped = [
        str(row["record_id"])
        for row in records
        if isinstance(row, Mapping)
        and row.get("role") in market_roles
        and isinstance(row.get("data_exposure"), Mapping)
        and row["data_exposure"].get("overlaps_2015_2022") is True
    ]
    scored = [
        str(row["record_id"])
        for row in records
        if isinstance(row, Mapping)
        and isinstance(row.get("data_exposure"), Mapping)
        and row["data_exposure"].get("scored_2024_through_2026") is True
    ]
    rejected = []
    for row in records:
        if not isinstance(row, Mapping):
            continue
        configuration = row.get("configuration_count")
        if not isinstance(configuration, Mapping):
            continue
        for item in configuration.get("provenance") or []:
            if not isinstance(item, Mapping):
                continue
            quote = str(item.get("quote") or "")
            if "not the earlier" in quote.lower():
                rejected.append(f"{row['record_id']}: {quote}")
    lines = []
    if overlapped:
        lines.append(
            "These market-trial records name a year from 2015 through 2022 in the "
            "data-range, train, or validation line, or the ledger marks that overlap. "
            "Those years are not untouched validation: "
            + ", ".join(overlapped)
            + "."
        )
    else:
        lines.append("No market-trial record in this reading states a 2015-2022 overlap.")
    if scored:
        lines.append(
            "These records name both 2024 and 2025 in the data-range, train, or validation line. "
            "That window is not untouched validation: "
            + ", ".join(scored)
            + "."
        )
    else:
        lines.append("No record in this reading states both 2024 and 2025 in those period lines.")
    if rejected:
        lines.append(
            "A ledger trial count was present and was not stored as a configuration total:"
        )
        lines.extend(f"- {item}" for item in rejected)
    lines.append(
        "A missing period line stays unavailable. Protected historical artifacts were not opened."
    )
    return lines


def inventory_summary(inventory: Mapping[str, object]) -> str:
    """Concise reading of the same object the JSON writer emits."""
    lines = [
        "# Historical trial inventory",
        "",
        "The programme-wide trial count is unknown.",
        "",
        inventory["programme_trial_count_reason"],
        "",
        f"Experiment-log headings: {inventory['experiment_heading_count']}.",
        f"Distinct experiment IDs in those headings: {inventory['unique_experiment_ids_in_log']}.",
        "The heading count is not a trial count.",
        "",
        "## Counting rules",
        "",
    ]
    for rule in inventory["counting_rules"]:
        lines.append(f"- {rule}")
    lines.extend(["", "## Duplicate experiment IDs", ""])
    duplicates = inventory["duplicate_experiment_ids"]
    if not duplicates:
        lines.append("None in this reading.")
    else:
        lines.append(", ".join(str(item) for item in duplicates) + ".")
        lines.append("Repeated IDs stay as separate records. Their counts are not added together.")
    lines.extend(["", "## Printed local counts", ""])
    lines.append("A number below is copied from the cited record. Adding these numbers does not produce an FMP-wide total.")
    lines.append("")
    executed = [
        row for row in inventory["records"]
        if row["executed_trial_count"]["status"] == "verified"
    ]
    rows_only = [
        row for row in inventory["records"]
        if row["result_row_count"]["status"] == "verified"
        and row["executed_trial_count"]["status"] != "verified"
    ]
    declared = [
        row for row in inventory["records"]
        if row["configuration_count"]["status"] == "verified"
        and row["executed_trial_count"]["status"] != "verified"
    ]
    lines.append("Executed grids, where both a configuration total and a result-row total are printed:")
    lines.append("")
    for row in executed:
        lines.append(
            f"- {row['record_id']}: {row['executed_trial_count']['value']} configurations, "
            f"{row['result_row_count']['value']} result rows."
        )
    lines.extend(["", "Result rows printed without a configuration total:", ""])
    for row in rows_only:
        factor = row["configurations_per_pair_timeframe"]
        factor_text = ""
        if factor["status"] == "partially_supported":
            factor_text = (
                f" A per-cell factor of {factor['value']} is printed and is not a total."
            )
        lines.append(
            f"- {row['record_id']}: {row['result_row_count']['value']} result rows. "
            "The configuration total is not printed."
            + factor_text
        )
    lines.extend(["", "Configuration totals printed for a search that the same record does not show as executed:", ""])
    for row in declared:
        lines.append(
            f"- {row['record_id']}: {row['configuration_count']['value']} declared configurations. "
            "No executed trial count is stored."
        )
    lines.extend(["", "## Data exposure", ""])
    lines.extend(_exposure_lines(inventory["records"]))
    lines.extend([
        "",
        "## Multiple-testing readiness",
        "",
        f"Historical family status: {inventory['historical_family_correction']['status']}.",
        "No historical p-value family is sent to the Benjamini-Yekutieli tool.",
        "A verified local grid is one experiment's printed total. It is not a closed hypothesis family.",
        "A later closed family can be assessed only by `family_correction_status` with its own members.",
        "",
        "## Source-declared grids",
        "",
        "A tuple in source is a declared parameter list. It is not evidence that the search was executed.",
        "",
    ])
    for grid in inventory["source_declared_grids"]:
        lines.append(
            f"- {grid['name']} in {grid['source']}: {grid['declared_parameter_count']} declared parameters."
        )
    lines.append("")
    return "\n".join(lines)
