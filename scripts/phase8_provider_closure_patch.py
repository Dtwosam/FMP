from __future__ import annotations

from pathlib import Path


campaign = Path("src/fmp/shadow/campaign.py")
text = campaign.read_text(encoding="utf-8")
if "import os\n" not in text:
    text = text.replace("import json\n", "import json\nimport os\n", 1)
if "PROVIDER_CLOSURE_PROTOCOL" not in text:
    text = text.replace(
        'FULL_MARKET_CLOSURE_REASON = "PROVIDER_DOCUMENTED_FULL_MARKET_CLOSURE"\n',
        'FULL_MARKET_CLOSURE_REASON = "PROVIDER_DOCUMENTED_FULL_MARKET_CLOSURE"\n'
        'PROVIDER_CLOSURE_PROTOCOL = "fmp-phase8-provider-closure-v1"\n'
        'PROVIDER_CLOSURE_FILENAME = "provider-closures.jsonl"\n',
        1,
    )
marker = "\n\ndef denominator_london_dates(\n"
if marker not in text:
    raise SystemExit("campaign denominator marker not found")
if "def load_provider_closures(" not in text:
    block = '''\n\ndef _provider_closure_record(closure: ProviderClosure, *, code_commit: str) -> dict[str, object]:\n    return {\n        "protocol": PROVIDER_CLOSURE_PROTOCOL,\n        "code_commit": code_commit,\n        "london_date": closure.london_date.isoformat(),\n        "reason": closure.reason,\n        "documentation": closure.documentation,\n        "recorded_at_utc": _iso_utc(closure.recorded_at_utc),\n    }\n\n\ndef load_provider_closures(\n    campaign_dir: Path,\n    *,\n    code_commit: str,\n) -> tuple[ProviderClosure, ...]:\n    registration = load_campaign_registration(Path(campaign_dir), code_commit=code_commit)\n    first_date_raw = registration.get("first_london_date")\n    if not isinstance(first_date_raw, str):\n        raise ValueError("Phase 8 campaign registration first_london_date is invalid")\n    first_date = date.fromisoformat(first_date_raw)\n    path = Path(campaign_dir) / PROVIDER_CLOSURE_FILENAME\n    if not path.exists():\n        return ()\n    try:\n        payload = path.read_bytes()\n    except OSError as exc:\n        raise ValueError("Phase 8 provider closure evidence is unreadable") from exc\n\n    closures: list[ProviderClosure] = []\n    seen_dates: set[date] = set()\n    for line_number, raw in enumerate(payload.splitlines(keepends=True), start=1):\n        try:\n            value = json.loads(raw)\n        except json.JSONDecodeError as exc:\n            raise ValueError(\n                f"Phase 8 provider closure evidence is invalid at line {line_number}"\n            ) from exc\n        if not isinstance(value, dict):\n            raise ValueError("Phase 8 provider closure evidence record must be an object")\n        record: dict[str, object] = dict(value)\n        if raw != _canonical_bytes(record):\n            raise ValueError("Phase 8 provider closure evidence must use canonical bytes")\n        expected_keys = {\n            "protocol",\n            "code_commit",\n            "london_date",\n            "reason",\n            "documentation",\n            "recorded_at_utc",\n        }\n        if set(record) != expected_keys:\n            raise ValueError("Phase 8 provider closure evidence fields mismatch")\n        if record.get("protocol") != PROVIDER_CLOSURE_PROTOCOL:\n            raise ValueError("Phase 8 provider closure protocol mismatch")\n        if record.get("code_commit") != code_commit:\n            raise ValueError("Phase 8 provider closure code commit mismatch")\n        london_date_raw = record.get("london_date")\n        if not isinstance(london_date_raw, str):\n            raise ValueError("Phase 8 provider closure London date is invalid")\n        try:\n            london_date = date.fromisoformat(london_date_raw)\n        except ValueError as exc:\n            raise ValueError("Phase 8 provider closure London date is invalid") from exc\n        if london_date.isoformat() != london_date_raw:\n            raise ValueError("Phase 8 provider closure London date must be canonical")\n        if london_date.weekday() >= 5:\n            raise ValueError("provider full-market closure must be a London weekday")\n        if london_date < first_date:\n            raise ValueError("provider full-market closure cannot precede campaign start")\n        recorded_raw = record.get("recorded_at_utc")\n        if not isinstance(recorded_raw, str) or not recorded_raw.endswith("Z"):\n            raise ValueError("Phase 8 provider closure recorded_at_utc is invalid")\n        try:\n            recorded_at = datetime.fromisoformat(recorded_raw[:-1] + "+00:00")\n        except ValueError as exc:\n            raise ValueError("Phase 8 provider closure recorded_at_utc is invalid") from exc\n        _require_utc(recorded_at, field="recorded_at_utc")\n        if _iso_utc(recorded_at) != recorded_raw:\n            raise ValueError("Phase 8 provider closure recorded_at_utc must be canonical")\n        documentation = record.get("documentation")\n        if not isinstance(documentation, str):\n            raise ValueError("Phase 8 provider closure documentation is invalid")\n        closure = ProviderClosure(\n            london_date=london_date,\n            reason=str(record.get("reason")),\n            documentation=documentation,\n            recorded_at_utc=recorded_at,\n        )\n        london_midnight = datetime.combine(\n            closure.london_date, time.min, tzinfo=LONDON\n        ).astimezone(timezone.utc)\n        if closure.recorded_at_utc >= london_midnight:\n            raise ValueError(\n                "provider full-market closure must be recorded before the London date begins"\n            )\n        if closure.london_date in seen_dates:\n            raise ValueError("duplicate provider full-market closure date")\n        seen_dates.add(closure.london_date)\n        closures.append(closure)\n    return tuple(closures)\n\n\ndef record_provider_closure(\n    *,\n    campaign_dir: Path,\n    code_commit: str,\n    london_date: date,\n    documentation: str,\n    recorded_at_utc: datetime,\n) -> ProviderClosure:\n    registration = load_campaign_registration(Path(campaign_dir), code_commit=code_commit)\n    if not isinstance(london_date, date) or isinstance(london_date, datetime):\n        raise TypeError("london_date must be a date")\n    if london_date.weekday() >= 5:\n        raise ValueError("provider full-market closure must be a London weekday")\n    first_date_raw = registration.get("first_london_date")\n    if not isinstance(first_date_raw, str):\n        raise ValueError("Phase 8 campaign registration first_london_date is invalid")\n    if london_date < date.fromisoformat(first_date_raw):\n        raise ValueError("provider full-market closure cannot precede campaign start")\n    closure = ProviderClosure(\n        london_date=london_date,\n        reason=FULL_MARKET_CLOSURE_REASON,\n        documentation=documentation,\n        recorded_at_utc=recorded_at_utc,\n    )\n    london_midnight = datetime.combine(\n        closure.london_date, time.min, tzinfo=LONDON\n    ).astimezone(timezone.utc)\n    if closure.recorded_at_utc >= london_midnight:\n        raise ValueError(\n            "provider full-market closure must be recorded before the London date begins"\n        )\n    existing = load_provider_closures(Path(campaign_dir), code_commit=code_commit)\n    if any(item.london_date == closure.london_date for item in existing):\n        raise ValueError("duplicate provider full-market closure date")\n\n    record = _provider_closure_record(closure, code_commit=code_commit)\n    path = Path(campaign_dir) / PROVIDER_CLOSURE_FILENAME\n    with path.open("ab") as handle:\n        handle.write(_canonical_bytes(record))\n        handle.flush()\n        os.fsync(handle.fileno())\n    return closure\n'''
    text = text.replace(marker, block + marker, 1)
for old, new in (
    ('    "ProviderClosure",\n', '    "ProviderClosure",\n    "PROVIDER_CLOSURE_FILENAME",\n    "PROVIDER_CLOSURE_PROTOCOL",\n'),
    ('    "load_campaign_registration",\n', '    "load_campaign_registration",\n    "load_provider_closures",\n'),
    ('    "register_campaign",\n', '    "record_provider_closure",\n    "register_campaign",\n'),
):
    if old in text and new not in text:
        text = text.replace(old, new, 1)
campaign.write_text(text, encoding="utf-8")


cli = Path("src/fmp/shadow/cli.py")
text = cli.read_text(encoding="utf-8")
text = text.replace(
    "from datetime import datetime, timezone\n",
    "from datetime import date, datetime, timezone\n",
    1,
)
text = text.replace(
    "from .campaign import register_campaign\n",
    "from .campaign import record_provider_closure, register_campaign\n",
    1,
)
parser_marker = '''    register.add_argument("--reference", required=True, type=Path)\n    register.add_argument("--campaign-dir", required=True, type=Path)\n'''
parser_insert = parser_marker + '''    record_closure = subparsers.add_parser(\n        "record-closure",\n        help="record a provider-documented full-market closure before its London date",\n    )\n    record_closure.add_argument("--campaign-dir", required=True, type=Path)\n    record_closure.add_argument("--london-date", required=True, type=date.fromisoformat)\n    record_closure.add_argument("--documentation", required=True)\n'''
if '"record-closure"' not in text:
    if parser_marker not in text:
        raise SystemExit("CLI registration parser marker not found")
    text = text.replace(parser_marker, parser_insert, 1)
text = text.replace(
    "    register_command: Callable[..., Mapping[str, object]] = register_campaign,\n",
    "    register_command: Callable[..., Mapping[str, object]] = register_campaign,\n"
    "    record_closure_command: Callable[..., object] = record_provider_closure,\n",
    1,
)
main_marker = '''    if args.command == "review":\n        outcome = review_command(Path(args.campaign_dir))\n'''
main_insert = '''    if args.command == "record-closure":\n        now = utc_now or (lambda: datetime.now(timezone.utc))\n        record_closure_command(\n            campaign_dir=Path(args.campaign_dir),\n            code_commit=code_commit_resolver(),\n            london_date=args.london_date,\n            documentation=args.documentation,\n            recorded_at_utc=now(),\n        )\n        return 0\n\n''' + main_marker
if 'if args.command == "record-closure":' not in text:
    if main_marker not in text:
        raise SystemExit("CLI review marker not found")
    text = text.replace(main_marker, main_insert, 1)
cli.write_text(text, encoding="utf-8")


review = Path("src/fmp/shadow/review_compiler.py")
text = review.read_text(encoding="utf-8")
if "    load_provider_closures,\n" not in text:
    text = text.replace(
        "    load_campaign_registration,\n",
        "    load_campaign_registration,\n    load_provider_closures,\n",
        1,
    )
signature = '''def _compile_segments(\n    segment_dirs: Sequence[Path],\n    *,\n    registration: Mapping[str, object],\n    code_commit: str,\n    qualification_fingerprint: str | None,\n) -> dict[str, object]:\n'''
replacement = '''def _compile_segments(\n    segment_dirs: Sequence[Path],\n    *,\n    registration: Mapping[str, object],\n    code_commit: str,\n    qualification_fingerprint: str | None,\n    provider_closures: Sequence[object],\n) -> dict[str, object]:\n'''
if signature in text:
    text = text.replace(signature, replacement, 1)
elif "    provider_closures: Sequence[object],\n) -> dict[str, object]:\n" not in text:
    raise SystemExit("review _compile_segments signature not found")
denominator = '''    denominator = denominator_london_dates(\n        first_london_date=first_date,\n        review_cutoff_utc=review_cutoff,\n    )\n'''
if denominator in text:
    text = text.replace(
        denominator,
        '''    denominator = denominator_london_dates(\n        first_london_date=first_date,\n        review_cutoff_utc=review_cutoff,\n        provider_closures=provider_closures,\n    )\n''',
        1,
    )
caller_marker = '''    segment_dirs = tuple(\n        path for path in sorted(campaign_dir.glob("segment-*")) if path.is_dir()\n    )\n'''
if "    provider_closures = load_provider_closures(\n" not in text:
    if caller_marker not in text:
        raise SystemExit("review segment marker not found")
    text = text.replace(
        caller_marker,
        '''    provider_closures = load_provider_closures(\n        campaign_dir,\n        code_commit=code_commit,\n    )\n''' + caller_marker,
        1,
    )
call_marker = '''            qualification_fingerprint=qualification_fingerprint,\n        )\n'''
if "            provider_closures=provider_closures,\n" not in text:
    if call_marker not in text:
        raise SystemExit("review _compile_segments call marker not found")
    text = text.replace(
        call_marker,
        '''            qualification_fingerprint=qualification_fingerprint,\n            provider_closures=provider_closures,\n        )\n''',
        1,
    )
review.write_text(text, encoding="utf-8")
