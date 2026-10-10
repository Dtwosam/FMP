from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
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

    def test_same_bytes_different_inode_blocks_without_any_event_claim(self):
        r = module._evaluate(b'same', b'same', b'', 9, True, False,
                             inode_stable=False)
        self.assertEqual(r['status'], 'BLOCKED')
        self.assertTrue(r['observed_checks']['final_digest_equal'])
        self.assertFalse(r['observed_checks']['watched_inode_matches_final_path'])
        self.assertFalse(r['can_authorize_dispatch'])

    def test_ambiguous_or_truthy_inode_identity_blocks(self):
        for value in (False, None, 1, 'true', []):
            with self.subTest(value=repr(value)):
                r = module._evaluate(b'same', b'same', b'', 9, True, False,
                                     inode_stable=value)
                self.assertEqual(r['status'], 'BLOCKED')

    def test_replacement_control_not_detected_is_still_blocked(self):
        r = module._evaluate(b'same', b'same', b'', 9, True, False,
                             inode_stable=True, replacement_negative=True)
        self.assertEqual(r['status'], 'BLOCKED')
        self.assertIn('synthetic inode-replacement negative control not detected', r['findings'])

    def test_pinned_regular_inode_and_exact_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'sample'
            path.write_bytes(b'PUBLIC')
            ident, data = module._snapshot_regular(path)
            st = path.stat()
            self.assertEqual(ident, (st.st_dev, st.st_ino))
            self.assertEqual(data, b'PUBLIC')

    @unittest.skipUnless(hasattr(os, 'O_NOFOLLOW'), 'POSIX nofollow required')
    def test_symlink_snapshot_is_not_followed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            target = root / 'public-target'
            target.write_bytes(b'PUBLIC')
            (root / 'sample').symlink_to(target)
            with self.assertRaises(OSError):
                module._snapshot_regular(root / 'sample')
            self.assertEqual(target.read_bytes(), b'PUBLIC')

    @unittest.skipUnless(hasattr(os, 'mkfifo') and hasattr(os, 'O_NOFOLLOW'),
                         'POSIX named pipes required')
    def test_fifo_replacement_snapshot_is_bounded(self):
        # A FIFO substitution must not block indefinitely before fstat.
        with tempfile.TemporaryDirectory() as folder:
            sample = Path(folder) / 'sample'
            os.mkfifo(sample)
            code = ("import importlib.util,sys;"
                    "spec=importlib.util.spec_from_file_location('m',sys.argv[1]);"
                    "m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);"
                    "m._snapshot_regular(__import__('pathlib').Path(sys.argv[2]))")
            p = subprocess.run([sys.executable, '-B', '-c', code, str(SCRIPT), str(sample)],
                               capture_output=True, text=True, timeout=3)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn('bounded regular inode', p.stderr)

    def test_conflicting_manual_negative_controls_never_run(self):
        r = module.run_demo(negative=True, replace_watched_inode=True)
        self.assertEqual(r['status'], 'BLOCKED')
        self.assertFalse(r['can_authorize_dispatch'])

    def test_mutually_exclusive_inotify_cli_options(self):
        p = subprocess.run([sys.executable, '-B', str(SCRIPT),
                            '--execute-inode-replacement-negative',
                            '--execute-reverted-write-negative'],
                           capture_output=True, text=True, timeout=4)
        self.assertNotEqual(p.returncode, 0)

    @unittest.skipUnless(os.environ.get('DEC677_EXECUTE_INOTIFY_TEST') == '1',
                         'manual opt-in; not annual runner identity proof')
    def test_real_identical_bytes_new_inode_negative_blocks(self):
        r = module.run_demo(replace_watched_inode=True)
        self.assertEqual(r['status'], 'BLOCKED', r)
        self.assertTrue(r['observed_checks']['final_digest_equal'])
        self.assertFalse(r['observed_checks']['watched_inode_matches_final_path'])
        self.assertFalse(r['can_authorize_dispatch'])
        self.assertFalse(r['independent_os_proof_verified'])

    def test_directory_create_event_is_separately_accounted(self):
        data = ev(wd=10, mask=module.IN_CREATE, data=b'new-file\\x00')
        observed = module._classify_stream(data, 9, directory_watch=10)
        self.assertTrue(observed['well_formed'])
        self.assertEqual(observed['directory_changes'], 1)
        self.assertEqual(observed['write_events'], 0)

    def test_all_synthetic_directory_mutations_block(self):
        for mask in (module.IN_CREATE, module.IN_DELETE,
                     module.IN_MOVED_FROM, module.IN_MOVED_TO):
            with self.subTest(mask=mask):
                data = ev(wd=10, mask=mask)
                verdict = module._evaluate(b'a', b'a', data, 9, True, False,
                                           directory_watch=10)
                self.assertEqual(verdict['status'], 'BLOCKED')
                self.assertFalse(verdict['observed_checks']['no_directory_entry_mutations'])

    def test_final_directory_inventory_catches_silent_extra_leaf(self):
        verdict = module._evaluate(b'a', b'a', b'', 9, True, False,
                                   directory_watch=10, directory_inventory_ok=False)
        self.assertEqual(verdict['status'], 'BLOCKED')
        self.assertTrue(verdict['observed_checks']['final_digest_equal'])
        self.assertFalse(verdict['observed_checks']['no_directory_entry_mutations'])

    def test_unknown_fd_watch_with_directory_watch_still_blocks(self):
        verdict = module._evaluate(b'a', b'a', ev(wd=11, mask=module.IN_CREATE),
                                   9, True, False, directory_watch=10)
        self.assertEqual(verdict['status'], 'BLOCKED')
        self.assertFalse(verdict['observed_checks']['event_stream_complete'])

    def test_unverified_sibling_negative_is_always_blocked(self):
        verdict = module._evaluate(b'a', b'a', b'', 9, True, False,
                                   directory_watch=10, directory_inventory_ok=True,
                                   sibling_negative=True)
        self.assertEqual(verdict['status'], 'BLOCKED')
        self.assertIn('synthetic directory-event negative control not detected',
                      verdict['findings'])
        self.assertFalse(verdict['can_authorize_dispatch'])

    def test_fake_sibling_creation_conflicts_with_other_injections(self):
        self.assertEqual(module.run_demo(negative=True, create_sibling=True)['status'],
                         'BLOCKED')
        self.assertEqual(module.run_demo(replace_watched_inode=True,
                                         create_sibling=True)['status'], 'BLOCKED')

    def test_cli_disallows_multiple_negative_inotify_modes(self):
        p = subprocess.run([sys.executable, '-B', str(SCRIPT),
                            '--execute-sibling-creation-negative',
                            '--execute-inode-replacement-negative'],
                           capture_output=True, text=True, timeout=4)
        self.assertNotEqual(p.returncode, 0)

    @unittest.skipUnless(os.environ.get('DEC677_EXECUTE_INOTIFY_TEST') == '1',
                         'manual disposable directory watch, not annual runner proof')
    def test_real_sibling_creation_blocks_despite_sample_unchanged(self):
        result = module.run_demo(create_sibling=True)
        self.assertEqual(result['status'], 'BLOCKED', result)
        self.assertTrue(result['observed_checks']['final_digest_equal'])
        self.assertTrue(result['observed_checks']['watched_inode_matches_final_path'])
        self.assertFalse(result['observed_checks']['no_directory_entry_mutations'])
        self.assertFalse(result['can_authorize_dispatch'])

    def test_create_then_remove_events_detected_despite_final_inventory_match(self):
        stream = ev(wd=10, mask=module.IN_CREATE) + ev(wd=10, mask=module.IN_DELETE)
        result = module._evaluate(b'unchanged', b'unchanged', stream, 9, True, False,
                                  directory_watch=10, directory_inventory_ok=True,
                                  transient_sibling_negative=True)
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertTrue(result['observed_checks']['final_digest_equal'])
        self.assertTrue(result['observed_checks']['watched_inode_matches_final_path'])
        self.assertFalse(result['observed_checks']['no_directory_entry_mutations'])
        self.assertTrue(result['observed_checks']['transient_directory_control_detected'])
        self.assertFalse(result['can_authorize_dispatch'])

    def test_undetected_transient_directory_negative_blocks(self):
        result = module._evaluate(b'a', b'a', b'', 9, True, False,
                                  directory_watch=10, directory_inventory_ok=True,
                                  transient_sibling_negative=True)
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertFalse(result['observed_checks']['transient_directory_control_detected'])
        self.assertIn('synthetic transient directory negative control not observed',
                      result['findings'])

    def test_one_event_cannot_validate_two_event_negative(self):
        result = module._evaluate(b'a', b'a', ev(wd=10, mask=module.IN_CREATE),
                                  9, True, False, directory_watch=10,
                                  transient_sibling_negative=True)
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertFalse(result['observed_checks']['transient_directory_control_detected'])

    def test_transient_event_parser_counts_two_distinct_directory_events(self):
        stream = ev(wd=10, mask=module.IN_CREATE) + ev(wd=10, mask=module.IN_DELETE)
        parsed = module._classify_stream(stream, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['directory_changes'], 2)

    def test_transient_directory_mode_conflicts_with_other_negative_modes(self):
        for args in ({'negative': True}, {'replace_watched_inode': True},
                     {'create_sibling': True}):
            with self.subTest(args=args):
                result = module.run_demo(transient_sibling=True, **args)
                self.assertEqual(result['status'], 'BLOCKED')

    def test_conflicting_transient_directory_cli_modes_fail_closed(self):
        p = subprocess.run([sys.executable, '-B', str(SCRIPT),
                            '--execute-transient-directory-negative',
                            '--execute-sibling-creation-negative'],
                           capture_output=True, text=True, timeout=4)
        self.assertNotEqual(p.returncode, 0)

    @unittest.skipUnless(os.environ.get('DEC677_EXECUTE_INOTIFY_TEST') == '1',
                         'manual Linux temporary create/delete events, NOT annual proof')
    def test_real_disposable_transient_sibling_event_negative_blocks(self):
        result = module.run_demo(transient_sibling=True)
        self.assertEqual(result['status'], 'BLOCKED', result)
        self.assertTrue(result['observed_checks']['final_digest_equal'])
        self.assertTrue(result['observed_checks']['watched_inode_matches_final_path'])
        self.assertTrue(result['observed_checks']['transient_directory_control_detected'])
        self.assertFalse(result['observed_checks']['no_directory_entry_mutations'])
        self.assertFalse(result['can_authorize_dispatch'])
        self.assertFalse(result['independent_os_proof_verified'])

    def test_synthetic_drain_rejects_unread_queue_at_bounded_limit(self):
        class AlwaysReady:
            def register(self, *_args): pass
            def poll(self, _timeout): return [(17, module.select.POLLIN)]
        with patch.object(module.select, 'poll', return_value=AlwaysReady()):
            with patch.object(module.os, 'read', return_value=b'X' * 4096):
                with self.assertRaisesRegex(OSError, 'still pending'):
                    module._read_pending(17)

    def test_synthetic_drain_accepts_exact_limit_only_when_empty(self):
        class ReadySixteen:
            def __init__(self): self.calls = 0
            def register(self, *_args): pass
            def poll(self, _timeout):
                self.calls += 1
                return [(17, module.select.POLLIN)] if self.calls <= 16 else []
        with patch.object(module.select, 'poll', return_value=ReadySixteen()):
            with patch.object(module.os, 'read', return_value=b'Y' * 4096):
                self.assertEqual(len(module._read_pending(17)), 65536)

    def test_poll_error_hup_or_nval_must_fail_closed(self):
        for status in (module.select.POLLERR, module.select.POLLHUP,
                       module.select.POLLNVAL):
            with self.subTest(status=status):
                class BadPoll:
                    def register(self, *_args): pass
                    def poll(self, _timeout): return [(17, status)]
                with patch.object(module.select, 'poll', return_value=BadPoll()):
                    with self.assertRaises(OSError):
                        module._read_pending(17)

    def test_event_collector_unexpected_descriptor_blocks(self):
        class Wrong:
            def register(self, *_args): pass
            def poll(self, _timeout): return [(999, module.select.POLLIN)]
        with patch.object(module.select, 'poll', return_value=Wrong()):
            with self.assertRaises(OSError):
                module._read_pending(17)

    def test_watched_event_collector_eof_after_readable_blocks(self):
        class Ready:
            def register(self, *_args): pass
            def poll(self, _timeout): return [(17, module.select.POLLIN)]
        with patch.object(module.select, 'poll', return_value=Ready()):
            with patch.object(module.os, 'read', return_value=b''):
                with self.assertRaisesRegex(OSError, 'EOF'):
                    module._read_pending(17)

    def test_inotify_poll_readiness_disagreement_fails_closed(self):
        class Ready:
            def register(self, *_args): pass
            def poll(self, _timeout): return [(17, module.select.POLLIN)]
        with patch.object(module.select, 'poll', return_value=Ready()):
            with patch.object(module.os, 'read', side_effect=BlockingIOError()):
                with self.assertRaisesRegex(OSError, 'raced an empty event queue'):
                    module._read_pending(17)

    def test_clean_one_chunk_and_no_more_events_is_collected(self):
        event = ev(wd=9, mask=module.IN_CLOSE_WRITE)
        class Single:
            def __init__(self): self.calls = 0
            def register(self, *_args): pass
            def poll(self, _timeout):
                self.calls += 1
                return [(17, module.select.POLLIN)] if self.calls == 1 else []
        with patch.object(module.select, 'poll', return_value=Single()):
            with patch.object(module.os, 'read', return_value=event):
                self.assertEqual(module._read_pending(17), event)

    def test_zero_mask_event_is_not_a_quiet_observation(self):
        raw = ev(wd=9, mask=0)
        parsed = module._classify_stream(raw, 9)
        self.assertFalse(parsed['well_formed'])
        self.assertEqual(module._evaluate(b'a', b'a', raw, 9, True, False)['status'], 'BLOCKED')

    def test_unknown_high_event_flag_blocks(self):
        raw = ev(wd=9, mask=module.IN_MODIFY | 0x80000000)
        self.assertFalse(module._classify_stream(raw, 9)['well_formed'])

    def test_unhandled_unmount_event_flag_blocks(self):
        raw = ev(wd=9, mask=0x00002000)
        self.assertFalse(module._classify_stream(raw, 9)['well_formed'])

    def test_directory_marker_without_action_blocks(self):
        raw = ev(wd=10, mask=module.IN_ISDIR)
        self.assertFalse(module._classify_stream(raw, 9, directory_watch=10)['well_formed'])

    def test_directory_marker_with_valid_create_action_is_supported(self):
        raw = ev(wd=10, mask=module.IN_ISDIR | module.IN_CREATE)
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['directory_changes'], 1)
        self.assertEqual(module._evaluate(b'a', b'a', raw, 9, True, False,
                                          directory_watch=10)['status'], 'BLOCKED')

    def test_overflow_event_with_unexpected_watch_number_blocks(self):
        raw = ev(wd=9, mask=module.IN_Q_OVERFLOW)
        parsed = module._classify_stream(raw, 9)
        self.assertTrue(parsed['overflow'])
        self.assertFalse(parsed['well_formed'])

    def test_overflow_with_extra_action_mask_is_malformed(self):
        raw = ev(wd=-1, mask=module.IN_Q_OVERFLOW | module.IN_CREATE)
        parsed = module._classify_stream(raw, 9)
        self.assertTrue(parsed['overflow'])
        self.assertFalse(parsed['well_formed'])

    def test_known_single_file_event_remains_well_formed(self):
        raw = ev(wd=9, mask=module.IN_CLOSE_WRITE)
        parsed = module._classify_stream(raw, 9)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['write_events'], 1)

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
