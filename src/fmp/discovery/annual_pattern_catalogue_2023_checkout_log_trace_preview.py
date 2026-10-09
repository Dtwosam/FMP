from __future__ import annotations

"""DEC-634: inert offline classifier of supplied GitHub checkout log text.

It cannot download GitHub logs or attest their authenticity. Never a live gate.
"""

import copy
import hashlib
import json
import re
from collections.abc import Mapping

DECISION = 'DEC-634'
REPO = 'Dtwosam/FMP'
BASE = 'a' * 40
HEAD = 'b' * 40
MERGE = 'c' * 40
PR = 99999  # nonexistent synthetic PR
WORKFLOWS = ('.github/workflows/tests.yml', '.github/workflows/phase3-acceptance.yml')
REQUIRED = frozenset({'repository', 'pr_number', 'head_sha', 'base_sha', 'merge_sha', 'run_evidence'})
RUN_FIELDS = frozenset({'workflow_path', 'event', 'pr_number', 'head_sha', 'base_sha',
                        'status', 'conclusion', 'attempt', 'checkout_log'})
STAMP = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z '
SHA = r'[0-9a-f]{40}'


def fixture_log(*, pr: int = PR, head: str = HEAD, base: str = BASE, merge: str = MERGE) -> str:
    """Fabricated minimal GitHub Actions log, never evidence of a real run."""
    stamp = '2026-10-09T00:00:00.0000000Z '
    ref = f'refs/remotes/pull/{pr}/merge'
    return '\n'.join((
        stamp + '##[group]Fetching the repository',
        stamp + '[command]/usr/bin/git -c protocol.version=2 fetch --no-tags --prune --no-recurse-submodules --depth=1 origin +' + merge + ':' + ref,
        stamp + 'From https://github.com/Dtwosam/FMP',
        stamp + '##[group]Checking out the ref',
        stamp + '[command]/usr/bin/git checkout --progress --force ' + ref,
        stamp + 'HEAD is now at ' + merge[:7] + ' Merge ' + head + ' into ' + base,
        stamp + '[command]/usr/bin/git log -1 --format=%H',
        stamp + merge,
        stamp + '##[group]Run actions/setup-python@v5',
    )) + '\n'


def fixture() -> dict[str, object]:
    return {
        'repository': REPO, 'pr_number': PR, 'head_sha': HEAD,
        'base_sha': BASE, 'merge_sha': MERGE,
        'run_evidence': [
            {'workflow_path': workflow, 'event': 'pull_request', 'pr_number': PR,
             'head_sha': HEAD, 'base_sha': BASE, 'status': 'completed',
             'conclusion': 'success', 'attempt': 1, 'checkout_log': fixture_log()}
            for workflow in WORKFLOWS
        ],
    }


def _sha(value: object) -> bool:
    return type(value) is str and re.fullmatch(SHA, value) is not None


def trace_matches(log: object, pr: int, head: str, base: str, merge: str) -> bool:
    """Consistent *text*, not authenticated checkout / signed log proof."""
    if type(pr) is not int or pr <= 0 or any(not _sha(x) for x in (head, base, merge)):
        return False
    if len({head, base, merge}) != 3 or type(log) is not str or len(log.encode('utf-8')) > 4 * 1024 * 1024:
        return False
    # Match complete timestamp-prefixed lines, not echoed shell fragments or substrings.
    log = log.lstrip('\ufeff')
    ref = f'refs/remotes/pull/{pr}/merge'
    expressions = (
        r'\[command\]/usr/bin/git -c protocol\.version=2 fetch --no-tags --prune --no-recurse-submodules --depth=1 origin \+' + re.escape(merge) + ':' + re.escape(ref),
        r'\[command\]/usr/bin/git checkout --progress --force ' + re.escape(ref),
        r'HEAD is now at ' + re.escape(merge[:7]) + ' Merge ' + re.escape(head) + ' into ' + re.escape(base),
        r'\[command\]/usr/bin/git log -1 --format=%H',
        re.escape(merge),
    )
    lines = log.splitlines()
    # Reject unframed preambles that could falsely imply a captured runner log.
    if not lines or not re.match(r'^' + STAMP, lines[0]):
        return False
    if len(lines) > 30000:
        return False
    hits: list[int] = []
    for expression in expressions:
        pattern = re.compile(r'^' + STAMP + expression + r'$')
        matches = [i for i, line in enumerate(lines) if pattern.fullmatch(line)]
        if len(matches) != 1:
            return False
        hits.append(matches[0])
    if hits != sorted(hits) or len(set(hits)) != len(hits):
        return False
    # The log command's full 40-hex SHA must be its immediately following output.
    if hits[4] != hits[3] + 1:
        return False
    # Require one matching fetch-source line between fetch and checkout.
    remote_lines = [(i, line) for i, line in enumerate(lines)
                    if re.fullmatch(r'^' + STAMP + r'From https://github\.com/.*', line)]
    if len(remote_lines) != 1 or not (hits[0] < remote_lines[0][0] < hits[1]):
        return False
    if not re.fullmatch(r'^' + STAMP + r'From https://github\.com/Dtwosam/FMP', remote_lines[0][1]):
        return False
    # A second HEAD or git-log query is conflicting runner evidence.
    head_lines = [i for i, line in enumerate(lines)
                  if re.match(r'^' + STAMP + r'HEAD is now at ', line)]
    log_queries = [i for i, line in enumerate(lines)
                   if re.match(r'^' + STAMP + r'\[command\]/usr/bin/git log -1 --format=', line)]
    if head_lines != [hits[2]] or log_queries != [hits[3]]:
        return False
    # An unexpected checkout to a different PR/branch is an ambiguity, not proof.
    all_checkout = [i for i, line in enumerate(lines) if re.search(r'^' + STAMP + r'\[command\]/usr/bin/git checkout --progress --force ', line)]
    all_fetch = [i for i, line in enumerate(lines) if re.search(r'^' + STAMP + r'\[command\]/usr/bin/git -c protocol\.version=2 fetch --no-tags', line)]
    return all_checkout == [hits[1]] and all_fetch == [hits[0]]


def classify_pair(record: object) -> str:
    """Reject missing/ambiguous/failed inputs. An apparent match still gives no authority."""
    if not isinstance(record, Mapping) or set(record) != REQUIRED:
        return 'REJECTED'
    if type(record['repository']) is not str or record['repository'] != REPO:
        return 'REJECTED'
    pr, head, base, merge = (record[k] for k in ('pr_number', 'head_sha', 'base_sha', 'merge_sha'))
    if type(pr) is not int or pr <= 0 or not all(_sha(v) for v in (head, base, merge)):
        return 'REJECTED'
    if len({head, base, merge}) != 3:
        return 'REJECTED'
    runs = record['run_evidence']
    if type(runs) is not list or len(runs) != 2:
        return 'REJECTED'
    seen: set[str] = set()
    for run in runs:
        if not isinstance(run, Mapping) or set(run) != RUN_FIELDS:
            return 'REJECTED'
        workflow = run['workflow_path']
        if type(workflow) is not str or workflow not in WORKFLOWS or workflow in seen:
            return 'REJECTED'
        seen.add(workflow)
        if (type(run['event']) is not str or run['event'] != 'pull_request'
            or type(run['pr_number']) is not int or run['pr_number'] != pr
            or type(run['head_sha']) is not str or run['head_sha'] != head
            or type(run['base_sha']) is not str or run['base_sha'] != base
            or type(run['status']) is not str or run['status'] != 'completed'
            or type(run['conclusion']) is not str or run['conclusion'] != 'success'
            or type(run['attempt']) is not int or run['attempt'] != 1
            or not trace_matches(run['checkout_log'], pr, head, base, merge)):
            return 'REJECTED'
    return 'REPORTED_TWO_LOG_CHECKOUT_MATCH' if seen == set(WORKFLOWS) else 'REJECTED'


def _counterexamples() -> tuple[tuple[str, dict[str, object]], ...]:
    changes: list[tuple[str, dict[str, object]]] = []
    def add(label: str, mutate) -> None:
        record = fixture()
        mutate(record)
        changes.append((label, record))
    add('wrong_repository', lambda r: r.__setitem__('repository', 'other/FMP'))
    add('missing_source_head', lambda r: r.pop('head_sha'))
    add('head_changed', lambda r: r.__setitem__('head_sha', 'f' * 40))
    add('base_changed', lambda r: r.__setitem__('base_sha', 'f' * 40))
    add('merge_changed', lambda r: r.__setitem__('merge_sha', 'f' * 40))
    add('bad_pr_type', lambda r: r.__setitem__('pr_number', True))
    add('no_second_workflow', lambda r: r['run_evidence'].pop())
    add('duplicate_tests', lambda r: r['run_evidence'][1].__setitem__('workflow_path', WORKFLOWS[0]))
    add('skipped', lambda r: r['run_evidence'][0].__setitem__('conclusion', 'skipped'))
    add('failed', lambda r: r['run_evidence'][0].__setitem__('conclusion', 'failure'))
    add('running', lambda r: r['run_evidence'][1].__setitem__('status', 'in_progress'))
    add('rerun', lambda r: r['run_evidence'][1].__setitem__('attempt', 2))
    add('boolean_attempt', lambda r: r['run_evidence'][1].__setitem__('attempt', True))
    add('wrong_run_pr', lambda r: r['run_evidence'][0].__setitem__('pr_number', 99998))
    add('stale_run_head', lambda r: r['run_evidence'][0].__setitem__('head_sha', 'f' * 40))
    add('run_wrong_base', lambda r: r['run_evidence'][0].__setitem__('base_sha', 'f' * 40))
    add('not_pr_event', lambda r: r['run_evidence'][1].__setitem__('event', 'push'))
    add('fake_authority', lambda r: r.__setitem__('dispatch_authorized', True))
    add('duplicate_checkout_command', lambda r: r['run_evidence'][0].__setitem__('checkout_log', fixture_log() + fixture_log()))
    add('missing_result', lambda r: r['run_evidence'][0].__setitem__('checkout_log', fixture_log().replace('Z ' + MERGE + '\n', 'Z <omitted>\n')))
    add('moved_result', lambda r: r['run_evidence'][0].__setitem__('checkout_log', fixture_log().replace('Z ' + MERGE + '\n', 'Z skipped\n' + '2026-10-09T00:00:00.0000000Z ' + MERGE + '\n')))
    add('wrong_checkout_ref', lambda r: r['run_evidence'][0].__setitem__('checkout_log', fixture_log().replace('checkout --progress --force refs/remotes/pull/99999/merge', 'checkout --progress --force refs/heads/main')))
    add('wrong_fetch_ref', lambda r: r['run_evidence'][0].__setitem__('checkout_log', fixture_log().replace('origin +' + MERGE + ':refs/remotes/pull/99999/merge', 'origin +' + MERGE + ':refs/remotes/pull/99998/merge')))
    add('tampered_head_message', lambda r: r['run_evidence'][0].__setitem__('checkout_log', fixture_log().replace('Merge ' + HEAD, 'Merge ' + 'f' * 40)))
    add('wrong_fetched_sha', lambda r: r['run_evidence'][0].__setitem__('checkout_log', fixture_log().replace('origin +' + MERGE, 'origin +' + 'f' * 40)))
    add('no_timestamp', lambda r: r['run_evidence'][0].__setitem__('checkout_log', fixture_log().replace('Z [command]/usr/bin/git log -1 --format=%H', 'Z fake [command]/usr/bin/git log -1 --format=%H')))
    add('echo_injection', lambda r: r['run_evidence'][0].__setitem__('checkout_log', 'echo checkout\n' + fixture_log().replace('Z [command]/usr/bin/git checkout --progress', 'Z echo [command]/usr/bin/git checkout --progress')))
    add('wrong_remote', lambda r: r['run_evidence'][0].__setitem__('checkout_log', fixture_log().replace('From https://github.com/Dtwosam/FMP', 'From https://github.com/other/FMP')))
    add('duplicate_remote', lambda r: r['run_evidence'][0].__setitem__('checkout_log', fixture_log().replace('From https://github.com/Dtwosam/FMP', 'From https://github.com/Dtwosam/FMP\n2026-10-09T00:00:00.0000000Z From https://github.com/Dtwosam/FMP')))
    add('extra_head_message', lambda r: r['run_evidence'][0].__setitem__('checkout_log', fixture_log() + '2026-10-09T00:00:00.0000000Z HEAD is now at fffffff Merge unexpected into unexpected\n'))
    add('extra_log_query', lambda r: r['run_evidence'][0].__setitem__('checkout_log', fixture_log() + '2026-10-09T00:00:00.0000000Z [command]/usr/bin/git log -1 --format=%H\n'))
    add('oversized_log', lambda r: r['run_evidence'][0].__setitem__('checkout_log', fixture_log() + ('x' * (4 * 1024 * 1024))))
    return tuple(changes)


def _digest(obj: object) -> str:
    return hashlib.sha256((json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()).hexdigest()


def _payload() -> dict[str, object]:
    rows = [{'name': 'synthetic_complete_pair', 'classification': classify_pair(fixture())}]
    rows.extend({'name': n, 'classification': classify_pair(r)} for n, r in _counterexamples())
    if rows[0]['classification'] != 'REPORTED_TWO_LOG_CHECKOUT_MATCH' or any(r['classification'] != 'REJECTED' for r in rows[1:]):
        raise ValueError('DEC-634 regression fixture drift')
    return {
        'decision': DECISION, 'stage': 'OFFLINE_UNAUTHENTICATED_CHECKOUT_LOG_TRACE_PREVIEW',
        'cases': rows, 'negative_case_count': len(rows) - 1,
        'synthetic_evidence_only': True, 'github_log_authenticity_proven': False,
        'runner_identity_attested': False, 'independent_review_proven': False,
        'merge_authorized': False, 'annual_dispatch_authorized': False,
        'run385_authorized': False, 'trading_authorized': False,
        'dispatch_blocked': True,
    }


def build_preview() -> dict[str, object]:
    payload = _payload()
    return {**payload, 'report_sha256': _digest(payload)}


def validate_preview(obj: object) -> None:
    if not isinstance(obj, Mapping):
        raise ValueError('DEC-634 report must be mapping')
    value = dict(obj)
    sha = value.pop('report_sha256', None)
    if type(sha) is not str or sha != _digest(value):
        raise ValueError('DEC-634 report SHA-256 mismatch')
    if value != _payload():
        raise ValueError('DEC-634 source-bound report mismatch')
