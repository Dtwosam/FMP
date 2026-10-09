from __future__ import annotations

import copy
import hashlib
import json
import unittest

from fmp.discovery.annual_pattern_catalogue_2023_checkout_log_trace_preview import (
    BASE, HEAD, MERGE, PR, _counterexamples, build_preview,
    classify_pair, fixture, fixture_log, trace_matches, validate_preview,
)


class OfflineCheckoutTraceTests(unittest.TestCase):
    def test_positive_two_log_fixture_is_never_approval(self):
        self.assertEqual(classify_pair(fixture()), 'REPORTED_TWO_LOG_CHECKOUT_MATCH')
        report = build_preview()
        validate_preview(report)
        self.assertEqual(report['negative_case_count'], 32)
        for key in ('github_log_authenticity_proven', 'runner_identity_attested',
                    'independent_review_proven', 'merge_authorized',
                    'annual_dispatch_authorized', 'run385_authorized', 'trading_authorized'):
            with self.subTest(key=key):
                self.assertIs(report[key], False)
        self.assertTrue(report['dispatch_blocked'])

    def test_every_negative_case_is_rejected(self):
        cases = _counterexamples()
        self.assertEqual(len(cases), 32)
        self.assertEqual(len({n for n, _ in cases}), len(cases))
        for name, record in cases:
            with self.subTest(name=name):
                self.assertEqual(classify_pair(record), 'REJECTED')

    def test_log_parser_is_strict_on_identity_and_order(self):
        self.assertTrue(trace_matches(fixture_log(), PR, HEAD, BASE, MERGE))
        for pr, head, base, merge in ((99998, HEAD, BASE, MERGE),
                                       (PR, 'f' * 40, BASE, MERGE),
                                       (PR, HEAD, 'f' * 40, MERGE),
                                       (PR, HEAD, BASE, 'f' * 40)):
            with self.subTest(pr=pr, head=head, base=base, merge=merge):
                self.assertFalse(trace_matches(fixture_log(), pr, head, base, merge))
        self.assertFalse(trace_matches(fixture_log().replace('2026-10-09T00:00:00.0000000Z ' + MERGE, 'tampered'), PR, HEAD, BASE, MERGE))

    def test_observed_pr796_checkout_log_format_with_real_commit_ids(self):
        # Exact checkout identity lines observed in GitHub's run 37871891308.
        # This is a fixed format fixture, NOT a signed or authenticated log.
        head = 'cd400c6ce3383753bb583cf544b4fa93df6c6850'
        base = '53e203133bbc141b2f48c7b8b8241d56b35166a3'
        merge = '8c4dbf08f3456558ad616beb94dab849e87268ff'
        log = """2026-10-09T01:52:59.8911494Z ##[group]Fetching the repository
2026-10-09T01:52:59.8920399Z [command]/usr/bin/git -c protocol.version=2 fetch --no-tags --prune --no-recurse-submodules --depth=1 origin +8c4dbf08f3456558ad616beb94dab849e87268ff:refs/remotes/pull/796/merge
2026-10-09T01:53:01.4362360Z From https://github.com/Dtwosam/FMP
2026-10-09T01:53:01.4454418Z ##[group]Checking out the ref
2026-10-09T01:53:01.4456211Z [command]/usr/bin/git checkout --progress --force refs/remotes/pull/796/merge
2026-10-09T01:53:01.5808482Z HEAD is now at 8c4dbf0 Merge cd400c6ce3383753bb583cf544b4fa93df6c6850 into 53e203133bbc141b2f48c7b8b8241d56b35166a3
2026-10-09T01:53:01.5847529Z [command]/usr/bin/git log -1 --format=%H
2026-10-09T01:53:01.5871164Z 8c4dbf08f3456558ad616beb94dab849e87268ff
"""
        self.assertTrue(trace_matches(log, 796, head, base, merge))
        self.assertFalse(trace_matches(log, 796, merge, base, head))
        self.assertFalse(trace_matches(log, 797, head, base, merge))

    def test_bom_supported_but_truncated_or_nontext_fail(self):
        self.assertTrue(trace_matches('\ufeff' + fixture_log(), PR, HEAD, BASE, MERGE))
        for bad in ('', None, False, 12, [], 'fake timestamp: ' + fixture_log()):
            with self.subTest(bad=repr(bad)[:50]):
                self.assertFalse(trace_matches(bad, PR, HEAD, BASE, MERGE))

    def test_report_forged_authorization_with_valid_sha_rejected(self):
        for key in ('merge_authorized', 'annual_dispatch_authorized',
                    'run385_authorized', 'trading_authorized', 'dispatch_blocked'):
            with self.subTest(key=key):
                v = copy.deepcopy(build_preview())
                v[key] = key != 'dispatch_blocked'
                original = dict(v)
                original.pop('report_sha256')
                v['report_sha256'] = hashlib.sha256((json.dumps(original, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()).hexdigest()
                with self.assertRaisesRegex(ValueError, 'source-bound report mismatch'):
                    validate_preview(v)

    def test_report_missing_sha_and_invalid_shape_rejected(self):
        v = build_preview()
        v.pop('report_sha256')
        with self.assertRaisesRegex(ValueError, 'SHA-256 mismatch'):
            validate_preview(v)
        with self.assertRaisesRegex(ValueError, 'must be mapping'):
            validate_preview(None)


if __name__ == '__main__':
    unittest.main()
