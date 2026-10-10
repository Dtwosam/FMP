from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def ev(wd=9, mask=None, data=b''):
    if mask is None:
        mask = module.IN_CLOSE_WRITE
    return module.EVENT.pack(wd, mask, 0, len(data)) + data


class DisposableInotifyTests(unittest.TestCase):
    def test_empty_stream_has_no_events_but_never_authorizes(self):
        r = module._evaluate(b'same', b'same', b'', 9, True, False)
        self.assertEqual(r['status'], 'LOCAL_DISPOSABLE_WITNESS_UNVERIFIED')
        self.assertFalse(r['can_authorize_dispatch'])
        self.assertFalse(r['independent_os_proof_verified'])

    def test_two_writes_and_revert_always_block(self):
        r = module._evaluate(b'same', b'same', ev()+ev(), 9, True, True)
        self.assertEqual(r['status'], 'BLOCKED')
        self.assertTrue(r['observed_checks']['final_digest_equal'])
        self.assertTrue(r['observed_checks']['negative_control_detected'])
        self.assertFalse(r['observed_checks']['no_observed_writes'])

    def test_single_write_blocks_even_in_control(self):
        r = module._evaluate(b'a', b'a', ev(), 9, True, False)
        self.assertEqual(r['status'], 'BLOCKED')

    def test_inotify_queue_overflow_never_passes(self):
        r = module._evaluate(b'a', b'a', ev(-1, module.IN_Q_OVERFLOW), 9, True, False)
        self.assertEqual(r['status'], 'BLOCKED')
        self.assertFalse(r['observed_checks']['event_stream_complete'])

    def test_watch_removed_never_passes(self):
        for mask in (module.IN_IGNORED, module.IN_DELETE_SELF, module.IN_MOVE_SELF):
            with self.subTest(mask=mask):
                r = module._evaluate(b'a', b'a', ev(mask=mask), 9, True, False)
                self.assertEqual(r['status'], 'BLOCKED')

    def test_wrong_watch_id_blocks(self):
        self.assertEqual(module._evaluate(b'a', b'a', ev(wd=11), 9, True, False)['status'], 'BLOCKED')

    def test_truncated_event_header_blocks(self):
        self.assertEqual(module._evaluate(b'a', b'a', b'\x00'*7, 9, True, False)['status'], 'BLOCKED')

    def test_mismatched_name_length_blocks(self):
        bad = module.EVENT.pack(9, module.IN_CLOSE_WRITE, 0, 100) + b'X'
        self.assertEqual(module._evaluate(b'a', b'a', bad, 9, True, False)['status'], 'BLOCKED')

    def test_unbounded_event_stream_blocks(self):
        self.assertFalse(module._classify_stream(b'X'*65537, 9)['well_formed'])

    def test_unsupported_monitor_data_blocks(self):
        for data in ('text', None, [], 33):
            with self.subTest(value=repr(data)):
                self.assertFalse(module._classify_stream(data, 9)['well_formed'])

    def test_invalid_watch_identity_blocks(self):
        self.assertFalse(module._classify_stream(ev(), -1)['well_formed'])

    def test_changed_final_digest_blocks_without_events(self):
        self.assertEqual(module._evaluate(b'a', b'b', b'', 9, True, False)['status'], 'BLOCKED')

    def test_untrusted_watcher_status_blocks(self):
        self.assertEqual(module._evaluate(b'a', b'a', b'', 9, False, False)['status'], 'BLOCKED')

    def test_default_cli_inert(self):
        p = subprocess.run([sys.executable, '-B', str(SCRIPT)], capture_output=True, text=True, timeout=4)
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)['can_authorize_dispatch'])

    def test_cli_rejects_caller_source_path(self):
        p = subprocess.run([sys.executable, '-B', str(SCRIPT), '--source', '/protected'],
                           capture_output=True, text=True, timeout=4)
        self.assertNotEqual(p.returncode, 0)

    def test_nonlinux_blocks(self):
        with patch.object(module.sys, 'platform', 'win32'):
            self.assertEqual(module.run_demo()['status'], 'BLOCKED')

    @unittest.skipUnless(os.environ.get('DEC677_EXECUTE_INOTIFY_TEST') == '1',
                         'manual Linux inotify observation, NOT annual runner proof')
    def test_real_disposable_control_only_locally_unverified(self):
        r = module.run_demo(False)
        self.assertEqual(r['status'], 'LOCAL_DISPOSABLE_WITNESS_UNVERIFIED', r)
        self.assertFalse(r['can_authorize_dispatch'])

    @unittest.skipUnless(os.environ.get('DEC677_EXECUTE_INOTIFY_TEST') == '1',
                         'manual Linux inotify observation, NOT annual runner proof')
    def test_real_disposable_write_revert_is_detected(self):
        r = module.run_demo(True)
        self.assertEqual(r['status'], 'BLOCKED', r)
        self.assertTrue(r['observed_checks']['final_digest_equal'])
        self.assertTrue(r['observed_checks']['negative_control_detected'])
        self.assertFalse(r['can_authorize_dispatch'])


if __name__ == '__main__':
    unittest.main()
