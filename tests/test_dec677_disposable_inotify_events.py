from __future__ import annotations

import importlib.util
import json
import os
import random
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


def named(basename: bytes) -> bytes:
    # Linux inotify pads the NUL-terminated name to the 16-byte event header.
    return basename + b"\x00" * (module.EVENT.size - len(basename) % module.EVENT.size)


def ev(wd=9, mask=None, data=b'', cookie=0):
    if mask is None:
        mask = module.IN_CLOSE_WRITE
    # A real directory-entry event includes a NUL-terminated, padded name.
    # Preserve the explicit data argument for adversarial malformed records.
    if wd == 10 and mask & module.DIRECTORY_CHANGES and not data:
        data = named(b"public")
    return module.EVENT.pack(wd, mask, cookie, len(data)) + data


class DisposableInotifyTests(unittest.TestCase):
    def test_empty_stream_has_no_events_but_never_authorizes(self):
        r = module._evaluate(b'same', b'same', b'', 9, True, False,
                             directory_watch=10)
        self.assertEqual(r['status'], 'LOCAL_DISPOSABLE_WITNESS_UNVERIFIED')
        self.assertFalse(r['can_authorize_dispatch'])
        self.assertFalse(r['independent_os_proof_verified'])

    def test_two_writes_and_revert_always_block(self):
        r = module._evaluate(b'same', b'same',
                             ev(mask=module.IN_MODIFY) * 2, 9, True, True)
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
        data = ev(wd=10, mask=module.IN_CREATE, data=named(b'new-file'))
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

    def test_file_watch_cannot_claim_a_directory_create_or_delete(self):
        for mask in (module.IN_CREATE, module.IN_DELETE,
                     module.IN_MOVED_FROM, module.IN_MOVED_TO):
            with self.subTest(mask=mask):
                raw = ev(wd=9, mask=mask)
                parsed = module._classify_stream(raw, 9, directory_watch=10)
                self.assertFalse(parsed['well_formed'])
                verdict = module._evaluate(b'PUBLIC', b'PUBLIC', raw, 9, True, False,
                                           directory_watch=10)
                self.assertEqual(verdict['status'], 'BLOCKED')
                self.assertTrue(verdict['observed_checks']['final_digest_equal'])
                self.assertFalse(verdict['observed_checks']['event_stream_complete'])

    def test_file_watch_cannot_claim_isdir_modifier(self):
        for mask in (module.IN_MODIFY | module.IN_ISDIR, module.IN_ISDIR | module.IN_CREATE):
            with self.subTest(mask=mask):
                self.assertFalse(module._classify_stream(ev(wd=9, mask=mask), 9,
                                                        directory_watch=10)['well_formed'])

    def test_single_file_watch_directory_change_is_never_quiet(self):
        raw = ev(wd=9, mask=module.IN_CREATE)
        verdict = module._evaluate(b'a', b'a', raw, 9, True, False)
        self.assertEqual(verdict['status'], 'BLOCKED')
        self.assertFalse(verdict['observed_checks']['event_stream_complete'])

    def test_directory_identity_cannot_equal_file_identity(self):
        parsed = module._classify_stream(b'', 9, directory_watch=9)
        self.assertFalse(parsed['well_formed'])
        verdict = module._evaluate(b'a', b'a', b'', 9, True, False, directory_watch=9)
        self.assertEqual(verdict['status'], 'BLOCKED')

    def test_invalid_directory_watch_id_fail_closed(self):
        for directory_watch in (True, False, -1, '10', 3.0, [], {}):
            with self.subTest(directory_watch=repr(directory_watch)):
                self.assertFalse(module._classify_stream(b'', 9, directory_watch)['well_formed'])

    def test_legitimate_directory_event_and_file_write_still_count(self):
        data = ev(wd=10, mask=module.IN_CREATE) + ev(wd=9, mask=module.IN_CLOSE_WRITE)
        result = module._classify_stream(data, 9, directory_watch=10)
        self.assertTrue(result['well_formed'])
        self.assertEqual(result['directory_changes'], 1)
        self.assertEqual(result['write_events'], 1)

    def test_file_only_known_write_event_still_recognized(self):
        result = module._classify_stream(ev(wd=9, mask=module.IN_CLOSE_WRITE), 9)
        self.assertTrue(result['well_formed'])
        self.assertEqual(result['write_events'], 1)

    def test_directory_child_event_requires_filename(self):
        raw = module.EVENT.pack(10, module.IN_CREATE, 0, 0)
        self.assertFalse(module._classify_stream(raw, 9, directory_watch=10)['well_formed'])

    def test_directory_name_without_nul_terminator_blocks(self):
        raw = ev(wd=10, mask=module.IN_CREATE, data=b"A" * 16)
        self.assertFalse(module._classify_stream(raw, 9, directory_watch=10)['well_formed'])

    def test_directory_name_without_zero_padding_blocks(self):
        raw = ev(wd=10, mask=module.IN_CREATE, data=b"a\x00X" + b"\x00" * 13)
        self.assertFalse(module._classify_stream(raw, 9, directory_watch=10)['well_formed'])

    def test_empty_directory_child_name_blocks(self):
        raw = ev(wd=10, mask=module.IN_CREATE, data=b"\x00" * 16)
        self.assertFalse(module._classify_stream(raw, 9, directory_watch=10)['well_formed'])

    def test_directory_leaf_name_cannot_include_path_separator(self):
        raw = ev(wd=10, mask=module.IN_CREATE, data=named(b"a/b"))
        self.assertFalse(module._classify_stream(raw, 9, directory_watch=10)['well_formed'])

    def test_file_watch_event_cannot_have_name_payload(self):
        raw = ev(wd=9, mask=module.IN_CLOSE_WRITE, data=named(b"fake"))
        self.assertFalse(module._classify_stream(raw, 9, directory_watch=10)['well_formed'])
        self.assertEqual(module._evaluate(b'x', b'x', raw, 9, True, False,
                                          directory_watch=10)['status'], 'BLOCKED')

    def test_misaligned_directory_name_field_blocks(self):
        raw = ev(wd=10, mask=module.IN_CREATE, data=b"a\x00\x00")
        self.assertFalse(module._classify_stream(raw, 9, directory_watch=10)['well_formed'])

    def test_valid_zero_padded_directory_basename_is_accepted_structurally(self):
        raw = ev(wd=10, mask=module.IN_CREATE, data=named(b"abc"))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['directory_changes'], 1)

    def test_special_overflow_event_cannot_carry_child_name(self):
        raw = ev(wd=-1, mask=module.IN_Q_OVERFLOW, data=named(b"abc"))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['overflow'])
        self.assertFalse(parsed['well_formed'])

    def test_short_regular_source_read_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            sample = Path(folder) / "sample"
            sample.write_bytes(b"LONGER-PUBLIC-FILE")
            with patch.object(module.os, "read", return_value=b"X"):
                with self.assertRaisesRegex(OSError, "incompletely"):
                    module._snapshot_regular(sample)

    def test_source_grows_during_open_fd_read_and_blocks(self):
        with tempfile.TemporaryDirectory() as folder:
            sample = Path(folder) / "sample"
            sample.write_bytes(b"PUBLIC")
            original_read = os.read
            def concurrent_append(fd, n):
                with open(sample, "ab") as writer:
                    writer.write(b"-SYNTHETIC-APPEND")
                    writer.flush()
                    os.fsync(writer.fileno())
                return original_read(fd, n)
            with patch.object(module.os, "read", side_effect=concurrent_append):
                with self.assertRaisesRegex(OSError, "changed or was read incompletely"):
                    module._snapshot_regular(sample)

    def test_same_length_source_rewrite_during_snapshot_blocks(self):
        with tempfile.TemporaryDirectory() as folder:
            sample = Path(folder) / "sample"
            sample.write_bytes(b"ORIGINAL")
            original_read = os.read
            def concurrent_update(fd, n):
                # Changed bytes/mtime and ctime, without changing length.
                with open(sample, "r+b") as writer:
                    writer.write(b"REPLACED")
                    writer.flush()
                    os.fsync(writer.fileno())
                return original_read(fd, n)
            with patch.object(module.os, "read", side_effect=concurrent_update):
                with self.assertRaises(OSError):
                    module._snapshot_regular(sample)

    def test_source_metadata_change_during_snapshot_blocks(self):
        with tempfile.TemporaryDirectory() as folder:
            sample = Path(folder) / "sample"
            sample.write_bytes(b"PUBLIC")
            original_read = os.read
            def modified_metadata(fd, n):
                os.utime(sample, ns=(1_600_000_000_000_000_000, 1_600_000_000_000_000_000))
                return original_read(fd, n)
            with patch.object(module.os, "read", side_effect=modified_metadata):
                with self.assertRaises(OSError):
                    module._snapshot_regular(sample)

    def test_oversized_synthetic_sample_is_rejected_without_read(self):
        with tempfile.TemporaryDirectory() as folder:
            sample = Path(folder) / "sample"
            sample.write_bytes(b"X" * 4097)
            with patch.object(module.os, "read") as read:
                with self.assertRaisesRegex(OSError, "bounded regular inode"):
                    module._snapshot_regular(sample)
                read.assert_not_called()

    def test_empty_regular_file_snapshot_is_bounded(self):
        with tempfile.TemporaryDirectory() as folder:
            sample = Path(folder) / "sample"
            sample.write_bytes(b"")
            _inode, data = module._snapshot_regular(sample)
            self.assertEqual(data, b"")

    def test_file_only_quiet_watch_cannot_be_reported_complete(self):
        r = module._evaluate(b'public', b'public', b'', 9, True, False)
        self.assertEqual(r['status'], 'BLOCKED')
        self.assertFalse(r['observed_checks']['both_watches_identified'])
        self.assertFalse(r['can_authorize_dispatch'])

    def test_file_and_directory_watches_quiet_is_only_locally_unverified(self):
        r = module._evaluate(b'public', b'public', b'', 9, True, False,
                             directory_watch=10)
        self.assertEqual(r['status'], 'LOCAL_DISPOSABLE_WITNESS_UNVERIFIED')
        self.assertTrue(r['observed_checks']['both_watches_identified'])
        self.assertFalse(r['independent_os_proof_verified'])

    def test_fake_aliased_watch_pair_blocks(self):
        r = module._evaluate(b'a', b'a', b'', 9, True, False,
                             directory_watch=9)
        self.assertEqual(r['status'], 'BLOCKED')
        self.assertFalse(r['observed_checks']['both_watches_identified'])

    def test_invalid_watch_identity_cannot_be_a_clean_receipt(self):
        for watch in (True, False, -1, '9', None):
            with self.subTest(watch=repr(watch)):
                r = module._evaluate(b'a', b'a', b'', watch, True, False,
                                     directory_watch=10)
                self.assertEqual(r['status'], 'BLOCKED')

    def test_noninteger_directory_watch_cannot_be_clean(self):
        for directory_watch in (None, False, True, -1, 9, '10'):
            with self.subTest(directory_watch=repr(directory_watch)):
                r = module._evaluate(b'a', b'a', b'', 9, True, False,
                                     directory_watch=directory_watch)
                self.assertEqual(r['status'], 'BLOCKED')


    def test_oversized_file_watch_id_cannot_make_a_quiet_receipt(self):
        for wd in (1 << 31, 1 << 32, 1 << 63):
            with self.subTest(wd=wd):
                self.assertFalse(module._classify_stream(b'', wd, directory_watch=10)['well_formed'])
                result = module._evaluate(b'a', b'a', b'', wd, True, False,
                                          directory_watch=10)
                self.assertEqual(result['status'], 'BLOCKED')
                self.assertFalse(result['observed_checks']['both_watches_identified'])

    def test_oversized_directory_watch_id_cannot_make_a_quiet_receipt(self):
        for wd in (1 << 31, 1 << 32, 1 << 63):
            with self.subTest(wd=wd):
                self.assertFalse(module._classify_stream(b'', 9, directory_watch=wd)['well_formed'])
                result = module._evaluate(b'a', b'a', b'', 9, True, False,
                                          directory_watch=wd)
                self.assertEqual(result['status'], 'BLOCKED')
                self.assertFalse(result['observed_checks']['both_watches_identified'])

    def test_signed_32_bit_watch_upper_boundary_remains_structurally_valid(self):
        largest = (1 << 31) - 1
        adjacent = largest - 1
        self.assertTrue(module._classify_stream(b'', largest, directory_watch=adjacent)['well_formed'])
        result = module._evaluate(b'a', b'a', b'', largest, True, False,
                                  directory_watch=adjacent)
        self.assertEqual(result['status'], 'LOCAL_DISPOSABLE_WITNESS_UNVERIFIED')
        self.assertFalse(result['can_authorize_dispatch'])

    def test_oversized_directory_identity_blocks_even_with_valid_file_event(self):
        raw = ev(wd=9, mask=module.IN_CLOSE_WRITE)
        result = module._classify_stream(raw, 9, directory_watch=1 << 31)
        self.assertFalse(result['well_formed'])
        verdict = module._evaluate(b'a', b'a', raw, 9, True, False,
                                   directory_watch=1 << 31)
        self.assertEqual(verdict['status'], 'BLOCKED')


    def test_two_creates_cannot_validate_a_create_remove_negative(self):
        stream = ev(wd=10, mask=module.IN_CREATE) * 2
        parsed = module._classify_stream(stream, 9, directory_watch=10)
        self.assertEqual(parsed['directory_changes'], 2)
        self.assertEqual(parsed['transient_create_delete_pairs'], 0)
        result = module._evaluate(b'a', b'a', stream, 9, True, False,
                                  directory_watch=10, transient_sibling_negative=True)
        self.assertFalse(result['observed_checks']['transient_directory_control_detected'])
        self.assertEqual(result['status'], 'BLOCKED')

    def test_two_deletes_cannot_validate_a_create_remove_negative(self):
        stream = ev(wd=10, mask=module.IN_DELETE) * 2
        parsed = module._classify_stream(stream, 9, directory_watch=10)
        self.assertEqual(parsed['transient_create_delete_pairs'], 0)
        result = module._evaluate(b'a', b'a', stream, 9, True, False,
                                  directory_watch=10, transient_sibling_negative=True)
        self.assertFalse(result['observed_checks']['transient_directory_control_detected'])

    def test_create_then_delete_of_different_leaf_is_not_matched(self):
        stream = (ev(wd=10, mask=module.IN_CREATE, data=named(b'a'))
                  + ev(wd=10, mask=module.IN_DELETE, data=named(b'b')))
        parsed = module._classify_stream(stream, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['transient_create_delete_pairs'], 0)

    def test_delete_then_create_is_not_a_transient_completion(self):
        stream = ev(wd=10, mask=module.IN_DELETE) + ev(wd=10, mask=module.IN_CREATE)
        result = module._evaluate(b'a', b'a', stream, 9, True, False,
                                  directory_watch=10, transient_sibling_negative=True)
        self.assertFalse(result['observed_checks']['transient_directory_control_detected'])
        self.assertIn('synthetic transient directory negative control not observed',
                      result['findings'])

    def test_named_create_delete_pair_survives_interleaved_unrelated_event(self):
        stream = (ev(wd=10, mask=module.IN_CREATE, data=named(b'a'))
                  + ev(wd=10, mask=module.IN_CREATE, data=named(b'b'))
                  + ev(wd=10, mask=module.IN_DELETE, data=named(b'a')))
        parsed = module._classify_stream(stream, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['transient_create_delete_pairs'], 1)
        result = module._evaluate(b'a', b'a', stream, 9, True, False,
                                  directory_watch=10, transient_sibling_negative=True)
        self.assertTrue(result['observed_checks']['transient_directory_control_detected'])
        self.assertEqual(result['status'], 'BLOCKED')

    def test_combined_create_delete_mask_cannot_forge_a_pair(self):
        raw = ev(wd=10, mask=module.IN_CREATE | module.IN_DELETE)
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertEqual(parsed['transient_create_delete_pairs'], 0)
        result = module._evaluate(b'a', b'a', raw, 9, True, False,
                                  directory_watch=10, transient_sibling_negative=True)
        self.assertFalse(result['observed_checks']['transient_directory_control_detected'])


    def test_directory_write_events_cannot_impersonate_source_rewrite_control(self):
        stream = ev(wd=10, mask=module.IN_MODIFY) * 2
        parsed = module._classify_stream(stream, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['write_events'], 2)
        self.assertEqual(parsed['source_content_write_events'], 0)
        result = module._evaluate(b'a', b'a', stream, 9, True, True,
                                  directory_watch=10)
        self.assertFalse(result['observed_checks']['negative_control_detected'])
        self.assertFalse(result['observed_checks']['no_observed_writes'])
        self.assertEqual(result['status'], 'BLOCKED')

    def test_file_attrib_events_cannot_impersonate_content_rewrite_control(self):
        stream = ev(wd=9, mask=module.IN_ATTRIB) * 2
        parsed = module._classify_stream(stream, 9, directory_watch=10)
        self.assertEqual(parsed['write_events'], 2)
        self.assertEqual(parsed['source_content_write_events'], 0)
        result = module._evaluate(b'a', b'a', stream, 9, True, True,
                                  directory_watch=10)
        self.assertFalse(result['observed_checks']['negative_control_detected'])

    def test_one_source_write_plus_directory_write_is_not_two_source_writes(self):
        stream = ev(wd=9, mask=module.IN_MODIFY) + ev(wd=10, mask=module.IN_MODIFY)
        parsed = module._classify_stream(stream, 9, directory_watch=10)
        self.assertEqual(parsed['source_content_write_events'], 1)
        result = module._evaluate(b'a', b'a', stream, 9, True, True,
                                  directory_watch=10)
        self.assertFalse(result['observed_checks']['negative_control_detected'])

    def test_two_valid_source_content_events_still_witness_negative_control(self):
        stream = ev(wd=9, mask=module.IN_MODIFY) * 2
        parsed = module._classify_stream(stream, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['source_content_write_events'], 2)
        self.assertEqual(parsed['source_modify_events'], 2)
        result = module._evaluate(b'a', b'a', stream, 9, True, True,
                                  directory_watch=10)
        self.assertTrue(result['observed_checks']['negative_control_detected'])
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertFalse(result['can_authorize_dispatch'])


    def test_poll_zero_pri_and_unknown_flags_are_not_valid_readiness(self):
        for flags in (0, module.select.POLLPRI,
                      module.select.POLLIN | module.select.POLLPRI,
                      module.select.POLLIN | 0x8000):
            with self.subTest(flags=flags):
                class InvalidReady:
                    def register(self, *_args): pass
                    def poll(self, _timeout): return [(17, flags)]
                with patch.object(module.select, 'poll', return_value=InvalidReady()):
                    with patch.object(module.os, 'read') as read:
                        with self.assertRaisesRegex(OSError, 'lost readable status'):
                            module._read_pending(17)
                        read.assert_not_called()

    def test_duplicate_readiness_records_do_not_trigger_an_unverified_read(self):
        class DuplicateReady:
            def register(self, *_args): pass
            def poll(self, _timeout):
                return [(17, module.select.POLLIN), (17, module.select.POLLIN)]
        with patch.object(module.select, 'poll', return_value=DuplicateReady()):
            with patch.object(module.os, 'read') as read:
                with self.assertRaisesRegex(OSError, 'lost readable status'):
                    module._read_pending(17)
                read.assert_not_called()

    def test_valid_single_pollin_event_drains_once_without_special_flags(self):
        record = ev(wd=9, mask=module.IN_CLOSE_WRITE)
        class Normal:
            def __init__(self): self.calls = 0
            def register(self, *_args): pass
            def poll(self, _timeout):
                self.calls += 1
                return [(17, module.select.POLLIN)] if self.calls == 1 else []
        with patch.object(module.select, 'poll', return_value=Normal()):
            with patch.object(module.os, 'read', return_value=record):
                self.assertEqual(module._read_pending(17), record)


    def test_nonmove_file_content_event_cannot_carry_rename_cookie(self):
        for mask in (module.IN_MODIFY, module.IN_CLOSE_WRITE, module.IN_ATTRIB):
            with self.subTest(mask=mask):
                raw = ev(wd=9, mask=mask, cookie=1234)
                parsed = module._classify_stream(raw, 9, directory_watch=10)
                self.assertFalse(parsed['well_formed'])
                result = module._evaluate(b'a', b'a', raw, 9, True, False,
                                          directory_watch=10)
                self.assertFalse(result['observed_checks']['event_stream_complete'])
                self.assertEqual(result['status'], 'BLOCKED')

    def test_nonmove_directory_child_event_cannot_carry_rename_cookie(self):
        for mask in (module.IN_CREATE, module.IN_DELETE):
            with self.subTest(mask=mask):
                raw = ev(wd=10, mask=mask, cookie=1234)
                self.assertFalse(module._classify_stream(raw, 9, directory_watch=10)['well_formed'])

    def test_move_from_and_to_cookie_is_retained_without_claiming_pairing(self):
        raw = (ev(wd=10, mask=module.IN_MOVED_FROM, cookie=1234)
               + ev(wd=10, mask=module.IN_MOVED_TO, cookie=1234))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['directory_changes'], 2)
        verdict = module._evaluate(b'a', b'a', raw, 9, True, False, directory_watch=10)
        self.assertEqual(verdict['status'], 'BLOCKED')

    def test_quiet_control_preserves_zero_cookie_file_event(self):
        parsed = module._classify_stream(ev(wd=9, mask=module.IN_CLOSE_WRITE), 9,
                                         directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['source_content_write_events'], 1)


    def test_multiple_source_action_bits_are_not_one_credible_event(self):
        for mask in (module.IN_MODIFY | module.IN_CLOSE_WRITE,
                     module.IN_MODIFY | module.IN_ATTRIB):
            with self.subTest(mask=mask):
                raw = ev(wd=9, mask=mask)
                parsed = module._classify_stream(raw, 9, directory_watch=10)
                self.assertFalse(parsed['well_formed'])
                result = module._evaluate(b'a', b'a', raw, 9, True, True,
                                          directory_watch=10)
                self.assertFalse(result['observed_checks']['negative_control_detected'])
                self.assertEqual(result['status'], 'BLOCKED')

    def test_multiple_directory_primary_bits_are_malformed(self):
        for mask in (module.IN_CREATE | module.IN_DELETE,
                     module.IN_CREATE | module.IN_MODIFY,
                     module.IN_MOVED_FROM | module.IN_MOVED_TO):
            with self.subTest(mask=mask):
                raw = ev(wd=10, mask=mask)
                self.assertFalse(module._classify_stream(raw, 9,
                                                         directory_watch=10)['well_formed'])

    def test_directory_isdir_modifier_still_allows_one_primary_action(self):
        raw = ev(wd=10, mask=module.IN_CREATE | module.IN_ISDIR)
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['directory_changes'], 1)
        result = module._evaluate(b'a', b'a', raw, 9, True, False, directory_watch=10)
        self.assertEqual(result['status'], 'BLOCKED')

    def test_distinct_single_action_source_records_remain_valid(self):
        raw = ev(wd=9, mask=module.IN_MODIFY) + ev(wd=9, mask=module.IN_CLOSE_WRITE)
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['source_content_write_events'], 2)


    def test_directory_create_never_names_dot_or_dotdot_entries(self):
        for name in (named(b'.'), named(b'..')):
            with self.subTest(name=name):
                raw = ev(wd=10, mask=module.IN_CREATE, data=name)
                parsed = module._classify_stream(raw, 9, directory_watch=10)
                self.assertFalse(parsed['well_formed'])
                verdict = module._evaluate(b'a', b'a', raw, 9, True, False,
                                           directory_watch=10)
                self.assertEqual(verdict['status'], 'BLOCKED')

    def test_impossible_dot_segments_cannot_validate_transient_control(self):
        for name in (named(b'.'), named(b'..')):
            with self.subTest(name=name):
                raw = (ev(wd=10, mask=module.IN_CREATE, data=name)
                       + ev(wd=10, mask=module.IN_DELETE, data=name))
                result = module._evaluate(b'a', b'a', raw, 9, True, False,
                                          directory_watch=10,
                                          transient_sibling_negative=True)
                self.assertFalse(result['observed_checks']['transient_directory_control_detected'])
                self.assertFalse(result['observed_checks']['event_stream_complete'])
                self.assertEqual(result['status'], 'BLOCKED')

    def test_dot_prefixed_real_leaf_remains_valid_structure(self):
        raw = ev(wd=10, mask=module.IN_CREATE, data=named(b'.env'))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['directory_changes'], 1)


    def test_nonlist_poll_return_cannot_be_treated_as_quiet(self):
        for value in (None, (), {}, False):
            with self.subTest(value=repr(value)):
                class BrokenPoll:
                    def register(self, *_args): pass
                    def poll(self, _timeout): return value
                with patch.object(module.select, 'poll', return_value=BrokenPoll()):
                    with patch.object(module.os, 'read') as read:
                        with self.assertRaisesRegex(OSError, 'malformed readiness'):
                            module._read_pending(17)
                        read.assert_not_called()

    def test_impossible_inotify_read_chunk_larger_than_requested_blocks(self):
        class Ready:
            def register(self, *_args): pass
            def poll(self, _timeout): return [(17, module.select.POLLIN)]
        with patch.object(module.select, 'poll', return_value=Ready()):
            with patch.object(module.os, 'read', return_value=b'X' * 4097):
                with self.assertRaisesRegex(OSError, 'impossible chunk shape'):
                    module._read_pending(17)

    def test_nonbytes_inotify_read_result_fails_closed(self):
        for value in ('bytes-looking', bytearray(b'X'), [88], 0):
            with self.subTest(value=repr(value)):
                class Ready:
                    def register(self, *_args): pass
                    def poll(self, _timeout): return [(17, module.select.POLLIN)]
                with patch.object(module.select, 'poll', return_value=Ready()):
                    with patch.object(module.os, 'read', return_value=value):
                        with self.assertRaisesRegex(OSError, 'impossible chunk shape'):
                            module._read_pending(17)


    def test_transient_pair_with_trailing_malformed_event_does_not_claim_detection(self):
        matched = ev(wd=10, mask=module.IN_CREATE) + ev(wd=10, mask=module.IN_DELETE)
        raw = matched + b'\x00' * 7
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertEqual(parsed['transient_create_delete_pairs'], 1)
        self.assertFalse(parsed['well_formed'])
        result = module._evaluate(b'a', b'a', raw, 9, True, False,
                                  directory_watch=10, transient_sibling_negative=True)
        self.assertFalse(result['observed_checks']['transient_directory_control_detected'])
        self.assertIn('synthetic transient directory negative control not observed',
                      result['findings'])

    def test_transient_pair_with_queue_overflow_does_not_claim_detection(self):
        matched = ev(wd=10, mask=module.IN_CREATE) + ev(wd=10, mask=module.IN_DELETE)
        raw = matched + ev(wd=-1, mask=module.IN_Q_OVERFLOW)
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['overflow'])
        self.assertEqual(parsed['transient_create_delete_pairs'], 1)
        result = module._evaluate(b'a', b'a', raw, 9, True, False,
                                  directory_watch=10, transient_sibling_negative=True)
        self.assertFalse(result['observed_checks']['transient_directory_control_detected'])
        self.assertEqual(result['status'], 'BLOCKED')

    def test_transient_pair_with_removed_watch_does_not_claim_detection(self):
        matched = ev(wd=10, mask=module.IN_CREATE) + ev(wd=10, mask=module.IN_DELETE)
        raw = matched + ev(wd=9, mask=module.IN_IGNORED)
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['invalidated'])
        result = module._evaluate(b'a', b'a', raw, 9, True, False,
                                  directory_watch=10, transient_sibling_negative=True)
        self.assertFalse(result['observed_checks']['transient_directory_control_detected'])

    def test_transient_pair_without_live_collector_does_not_claim_detection(self):
        raw = ev(wd=10, mask=module.IN_CREATE) + ev(wd=10, mask=module.IN_DELETE)
        result = module._evaluate(b'a', b'a', raw, 9, False, False,
                                  directory_watch=10, transient_sibling_negative=True)
        self.assertFalse(result['observed_checks']['transient_directory_control_detected'])
        self.assertEqual(result['status'], 'BLOCKED')


    def test_four_eight_and_twelve_byte_named_fields_rejected(self):
        for n in (4, 8, 12):
            with self.subTest(name_field_length=n):
                raw = ev(wd=10, mask=module.IN_CREATE,
                         data=b'x' + b'\x00' * (n - 1))
                parsed = module._classify_stream(raw, 9, directory_watch=10)
                self.assertFalse(parsed['well_formed'])
                result = module._evaluate(b'a', b'a', raw, 9, True, False,
                                          directory_watch=10)
                self.assertFalse(result['observed_checks']['event_stream_complete'])
                self.assertEqual(result['status'], 'BLOCKED')

    def test_minimum_native_sixteen_byte_named_field_supported(self):
        raw = ev(wd=10, mask=module.IN_CREATE, data=named(b'abc'))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['directory_changes'], 1)
        self.assertEqual(len(raw), module.EVENT.size * 2)

    def test_longer_native_thirty_two_byte_padded_name_supported(self):
        raw = ev(wd=10, mask=module.IN_CREATE, data=named(b'a' * 17))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['directory_changes'], 1)
        self.assertEqual(len(raw), module.EVENT.size * 3)

    def test_named_directory_metadata_requires_native_name_alignment(self):
        raw = ev(wd=10, mask=module.IN_MODIFY, data=b'x\x00\x00\x00')
        self.assertFalse(module._classify_stream(raw, 9, directory_watch=10)['well_formed'])
        valid = ev(wd=10, mask=module.IN_MODIFY, data=named(b'x'))
        parsed = module._classify_stream(valid, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['write_events'], 1)


    def test_short_child_name_cannot_claim_extra_thirty_two_byte_padding(self):
        raw = ev(wd=10, mask=module.IN_CREATE,
                 data=named(b'a') + b'\x00' * module.EVENT.size)
        self.assertEqual(len(raw) - module.EVENT.size, 32)
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertFalse(parsed['well_formed'])
        result = module._evaluate(b'a', b'a', raw, 9, True, False,
                                  directory_watch=10)
        self.assertFalse(result['observed_checks']['event_stream_complete'])
        self.assertEqual(result['status'], 'BLOCKED')

    def test_fifteen_byte_basename_with_unnecessary_extra_padding_is_invalid(self):
        raw = ev(wd=10, mask=module.IN_DELETE,
                 data=named(b'x' * 15) + b'\x00' * 32)
        self.assertEqual(len(raw) - module.EVENT.size, 48)
        self.assertFalse(module._classify_stream(raw, 9, directory_watch=10)['well_formed'])

    def test_exact_native_roundup_at_fifteen_and_sixteen_character_boundary(self):
        for size, expected in ((15, 16), (16, 32)):
            with self.subTest(name_length=size):
                data = named(b'x' * size)
                self.assertEqual(len(data), expected)
                parsed = module._classify_stream(
                    ev(wd=10, mask=module.IN_CREATE, data=data),
                    9, directory_watch=10)
                self.assertTrue(parsed['well_formed'])
                self.assertEqual(parsed['directory_changes'], 1)

    def test_named_directory_metadata_cannot_claim_arbitrary_extra_padding(self):
        raw = ev(wd=10, mask=module.IN_MODIFY,
                 data=named(b'leaf') + b'\x00' * 16)
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertFalse(parsed['well_formed'])
        result = module._evaluate(b'a', b'a', raw, 9, True, False,
                                  directory_watch=10)
        self.assertFalse(result['observed_checks']['event_stream_complete'])


    def test_max_linux_255_byte_basename_remains_structurally_possible(self):
        raw = ev(wd=10, mask=module.IN_CREATE, data=named(b'a' * 255))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['directory_changes'], 1)
        self.assertEqual(len(raw) - module.EVENT.size, 256)

    def test_overlong_256_byte_basename_fails_closed_even_when_padded(self):
        raw = ev(wd=10, mask=module.IN_CREATE, data=named(b'a' * 256))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertFalse(parsed['well_formed'])
        result = module._evaluate(b'a', b'a', raw, 9, True, False,
                                  directory_watch=10)
        self.assertFalse(result['observed_checks']['event_stream_complete'])
        self.assertEqual(result['status'], 'BLOCKED')

    def test_impossible_long_name_does_not_validate_transient_control(self):
        data = named(b'z' * 300)
        raw = (ev(wd=10, mask=module.IN_CREATE, data=data)
               + ev(wd=10, mask=module.IN_DELETE, data=data))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertFalse(parsed['well_formed'])
        self.assertEqual(parsed['transient_create_delete_pairs'], 0)
        verdict = module._evaluate(b'a', b'a', raw, 9, True, False,
                                   directory_watch=10, transient_sibling_negative=True)
        self.assertFalse(verdict['observed_checks']['transient_directory_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')


    def test_deterministic_malformed_byte_corpus_cannot_authorize(self):
        rng = random.Random(0xDEC699)
        for index in range(512):
            raw = bytes(rng.getrandbits(8) for _ in range(rng.randrange(160)))
            with self.subTest(case=index, length=len(raw)):
                parsed = module._classify_stream(raw, 9, directory_watch=10)
                self.assertIs(type(parsed['well_formed']), bool)
                self.assertGreaterEqual(parsed['write_events'], 0)
                self.assertGreaterEqual(parsed['directory_changes'], 0)
                verdict = module._evaluate(b'public', b'public', raw, 9, True, False,
                                           directory_watch=10)
                self.assertIn(verdict['status'],
                              ('BLOCKED', 'LOCAL_DISPOSABLE_WITNESS_UNVERIFIED'))
                self.assertFalse(verdict['can_authorize_dispatch'])
                self.assertFalse(verdict['independent_os_proof_verified'])

    def test_deterministic_forged_kernel_headers_always_block(self):
        rng = random.Random(0xDEC69A)
        for index in range(512):
            watch = rng.choice((9, 10, 11, -1))
            mask = rng.getrandbits(32)
            cookie = rng.getrandbits(32)
            declared = rng.randrange(5000)
            name = bytes(rng.getrandbits(8) for _ in range(rng.randrange(64)))
            raw = module.EVENT.pack(watch, mask, cookie, declared) + name
            with self.subTest(case=index):
                verdict = module._evaluate(b'public', b'public', raw, 9, True, False,
                                           directory_watch=10)
                self.assertEqual(verdict['status'], 'BLOCKED')
                self.assertFalse(verdict['can_authorize_dispatch'])
                self.assertFalse(verdict['independent_os_proof_verified'])

    def test_bounded_bit_flip_mutations_never_promote_local_evidence(self):
        base = (ev(wd=9, mask=module.IN_MODIFY)
                + ev(wd=10, mask=module.IN_CREATE))
        for offset in range(len(base)):
            for bit in (1, 8, 128):
                mutated = bytearray(base)
                mutated[offset] ^= bit
                verdict = module._evaluate(
                    b'public', b'public', bytes(mutated), 9, True, False,
                    directory_watch=10)
                self.assertIn(verdict['status'],
                              ('BLOCKED', 'LOCAL_DISPOSABLE_WITNESS_UNVERIFIED'))
                self.assertFalse(verdict['can_authorize_dispatch'])
                self.assertFalse(verdict['independent_os_proof_verified'])


    def test_transient_directory_creation_and_removal_not_file_witness(self):
        raw = (ev(wd=10, mask=module.IN_CREATE | module.IN_ISDIR)
               + ev(wd=10, mask=module.IN_DELETE | module.IN_ISDIR))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['directory_changes'], 2)
        self.assertEqual(parsed['transient_create_delete_pairs'], 0)
        verdict = module._evaluate(b'same', b'same', raw, 9, True, False,
                                   directory_watch=10, transient_sibling_negative=True)
        self.assertFalse(verdict['observed_checks']['transient_directory_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')

    def test_file_create_followed_by_directory_delete_not_matched(self):
        raw = (ev(wd=10, mask=module.IN_CREATE)
               + ev(wd=10, mask=module.IN_DELETE | module.IN_ISDIR))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertEqual(parsed['transient_create_delete_pairs'], 0)
        verdict = module._evaluate(b'same', b'same', raw, 9, True, False,
                                   directory_watch=10, transient_sibling_negative=True)
        self.assertFalse(verdict['observed_checks']['transient_directory_control_detected'])

    def test_directory_create_then_regular_file_delete_not_matched(self):
        raw = (ev(wd=10, mask=module.IN_CREATE | module.IN_ISDIR)
               + ev(wd=10, mask=module.IN_DELETE))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertEqual(parsed['transient_create_delete_pairs'], 0)

    def test_directory_recreation_clears_prior_regular_creation(self):
        raw = (ev(wd=10, mask=module.IN_CREATE)
               + ev(wd=10, mask=module.IN_CREATE | module.IN_ISDIR)
               + ev(wd=10, mask=module.IN_DELETE))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertEqual(parsed['transient_create_delete_pairs'], 0)

    def test_regular_file_create_delete_still_counts_once(self):
        raw = ev(wd=10, mask=module.IN_CREATE) + ev(wd=10, mask=module.IN_DELETE)
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['transient_create_delete_pairs'], 1)
        verdict = module._evaluate(b'same', b'same', raw, 9, True, False,
                                   directory_watch=10, transient_sibling_negative=True)
        self.assertTrue(verdict['observed_checks']['transient_directory_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')


    def test_two_close_write_events_do_not_claim_two_content_modifications(self):
        stream = ev(wd=9, mask=module.IN_CLOSE_WRITE) * 2
        parsed = module._classify_stream(stream, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['source_content_write_events'], 2)
        self.assertEqual(parsed['source_modify_events'], 0)
        result = module._evaluate(b'same', b'same', stream, 9, True, True,
                                  directory_watch=10)
        self.assertFalse(result['observed_checks']['negative_control_detected'])
        self.assertFalse(result['observed_checks']['no_observed_writes'])
        self.assertEqual(result['status'], 'BLOCKED')

    def test_one_modify_and_one_close_write_cannot_prove_two_modifications(self):
        stream = ev(wd=9, mask=module.IN_MODIFY) + ev(wd=9, mask=module.IN_CLOSE_WRITE)
        parsed = module._classify_stream(stream, 9, directory_watch=10)
        self.assertEqual(parsed['source_modify_events'], 1)
        result = module._evaluate(b'same', b'same', stream, 9, True, True,
                                  directory_watch=10)
        self.assertFalse(result['observed_checks']['negative_control_detected'])

    def test_two_modify_events_with_interleaved_close_still_detect_control(self):
        stream = (ev(wd=9, mask=module.IN_MODIFY)
                  + ev(wd=9, mask=module.IN_CLOSE_WRITE)
                  + ev(wd=9, mask=module.IN_MODIFY))
        parsed = module._classify_stream(stream, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['source_modify_events'], 2)
        self.assertEqual(parsed['source_content_write_events'], 3)
        result = module._evaluate(b'same', b'same', stream, 9, True, True,
                                  directory_watch=10)
        self.assertTrue(result['observed_checks']['negative_control_detected'])
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertFalse(result['can_authorize_dispatch'])

    def test_directory_modify_does_not_count_as_source_modification(self):
        stream = ev(wd=10, mask=module.IN_MODIFY) * 2
        parsed = module._classify_stream(stream, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['source_modify_events'], 0)
        result = module._evaluate(b'same', b'same', stream, 9, True, True,
                                  directory_watch=10)
        self.assertFalse(result['observed_checks']['negative_control_detected'])


    def test_malformed_source_snapshot_inputs_are_blocked_without_exception(self):
        for before, after in (('text', b'public'), (b'public', 'text'),
                              (None, b'public'), (b'public', None),
                              (bytearray(b'public'), b'public'),
                              (b'public', memoryview(b'public')),
                              ([], b'public'), (True, b'public')):
            with self.subTest(before=repr(before), after=repr(after)):
                verdict = module._evaluate(before, after, b'', 9, True, False,
                                           directory_watch=10)
                self.assertEqual(verdict['status'], 'BLOCKED')
                self.assertFalse(verdict['can_authorize_dispatch'])
                self.assertFalse(verdict['independent_os_proof_verified'])
                self.assertIn('disposable source snapshot must be bounded bytes',
                              verdict['findings'])

    def test_source_snapshots_larger_than_4096_bytes_fail_closed(self):
        for before, after in ((b'x' * 4097, b'x'),
                              (b'x', b'x' * 4097)):
            with self.subTest(initial_length=len(before), final_length=len(after)):
                verdict = module._evaluate(before, after, b'', 9, True, False,
                                           directory_watch=10)
                self.assertEqual(verdict['status'], 'BLOCKED')
                self.assertIn('disposable source snapshot must be bounded bytes',
                              verdict['findings'])

    def test_maximum_bounded_snapshot_is_locally_unverified_not_authorized(self):
        payload = b'X' * 4096
        verdict = module._evaluate(payload, payload, b'', 9, True, False,
                                   directory_watch=10)
        self.assertEqual(verdict['status'], 'LOCAL_DISPOSABLE_WITNESS_UNVERIFIED')
        self.assertFalse(verdict['can_authorize_dispatch'])
        self.assertFalse(verdict['independent_os_proof_verified'])


    def test_unrelated_created_leaf_does_not_validate_expected_sibling_control(self):
        raw = ev(wd=10, mask=module.IN_CREATE, data=named(b'unrelated'))
        verdict = module._evaluate(b'public', b'public', raw, 9, True, False,
                                   directory_watch=10, directory_inventory_ok=False,
                                   sibling_negative=True)
        self.assertEqual(verdict['status'], 'BLOCKED')
        self.assertFalse(verdict['observed_checks']['sibling_creation_control_detected'])
        self.assertIn('synthetic directory-event negative control not detected',
                      verdict['findings'])

    def test_expected_regular_file_creation_and_inventory_drift_detect_control(self):
        raw = ev(wd=10, mask=module.IN_CREATE,
                 data=named(b'unexpected-public-sibling'))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertTrue(parsed['expected_sibling_created'])
        verdict = module._evaluate(b'public', b'public', raw, 9, True, False,
                                   directory_watch=10, directory_inventory_ok=False,
                                   directory_inventory_names=("sample", "unexpected-public-sibling"),
                                   sibling_snapshot_stable=True,
                                   sibling_negative=True)
        self.assertTrue(verdict['observed_checks']['sibling_creation_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')
        self.assertFalse(verdict['can_authorize_dispatch'])

    def test_matching_directory_creation_is_not_regular_sibling_witness(self):
        raw = ev(wd=10, mask=module.IN_CREATE | module.IN_ISDIR,
                 data=named(b'unexpected-public-sibling'))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertFalse(parsed['expected_sibling_created'])
        verdict = module._evaluate(b'public', b'public', raw, 9, True, False,
                                   directory_watch=10, directory_inventory_ok=False,
                                   sibling_negative=True)
        self.assertFalse(verdict['observed_checks']['sibling_creation_control_detected'])

    def test_expected_sibling_with_quiet_final_inventory_not_confirmed(self):
        raw = ev(wd=10, mask=module.IN_CREATE,
                 data=named(b'unexpected-public-sibling'))
        verdict = module._evaluate(b'public', b'public', raw, 9, True, False,
                                   directory_watch=10, directory_inventory_ok=True,
                                   sibling_negative=True)
        self.assertFalse(verdict['observed_checks']['sibling_creation_control_detected'])

    def test_expected_sibling_followed_by_overflow_cannot_claim_detection(self):
        raw = (ev(wd=10, mask=module.IN_CREATE,
                  data=named(b'unexpected-public-sibling'))
               + ev(wd=-1, mask=module.IN_Q_OVERFLOW))
        verdict = module._evaluate(b'public', b'public', raw, 9, True, False,
                                   directory_watch=10, directory_inventory_ok=False,
                                   sibling_negative=True)
        self.assertFalse(verdict['observed_checks']['sibling_creation_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')


    def test_dirty_inventory_with_only_other_sibling_is_not_expected_file(self):
        raw = ev(wd=10, mask=module.IN_CREATE,
                 data=named(b'unexpected-public-sibling'))
        verdict = module._evaluate(
            b'public', b'public', raw, 9, True, False,
            directory_watch=10, directory_inventory_ok=False,
            directory_inventory_names=("sample", "unrelated"),
            sibling_negative=True)
        self.assertFalse(verdict['observed_checks']['sibling_creation_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')

    def test_missing_or_untrusted_final_inventory_is_not_a_control_witness(self):
        raw = ev(wd=10, mask=module.IN_CREATE,
                 data=named(b'unexpected-public-sibling'))
        for names in (None, [], ["sample", "unexpected-public-sibling"],
                      ("unexpected-public-sibling", "sample"),
                      ("sample",), ("sample", "unrelated")):
            with self.subTest(names=repr(names)):
                verdict = module._evaluate(
                    b'public', b'public', raw, 9, True, False,
                    directory_watch=10, directory_inventory_ok=False,
                    directory_inventory_names=names,
                    sibling_negative=True)
                self.assertFalse(verdict['observed_checks']['sibling_creation_control_detected'])
                self.assertEqual(verdict['status'], 'BLOCKED')

    def test_expected_inventory_without_create_event_does_not_witness_control(self):
        verdict = module._evaluate(
            b'public', b'public', b'', 9, True, False,
            directory_watch=10, directory_inventory_ok=False,
            directory_inventory_names=("sample", "unexpected-public-sibling"),
            sibling_negative=True)
        self.assertFalse(verdict['observed_checks']['sibling_creation_control_detected'])
        self.assertIn('synthetic directory-event negative control not detected',
                      verdict['findings'])


    def test_matching_sibling_event_and_names_need_stable_inode_bytes(self):
        raw = ev(wd=10, mask=module.IN_CREATE,
                 data=named(b'unexpected-public-sibling'))
        for stable in (None, False, 1, 'true', [], {}):
            with self.subTest(stable=repr(stable)):
                verdict = module._evaluate(
                    b'public', b'public', raw, 9, True, False,
                    directory_watch=10, directory_inventory_ok=False,
                    directory_inventory_names=("sample", "unexpected-public-sibling"),
                    sibling_snapshot_stable=stable, sibling_negative=True)
                self.assertFalse(verdict['observed_checks']['sibling_creation_control_detected'])
                self.assertEqual(verdict['status'], 'BLOCKED')

    def test_disposable_sibling_pin_refuses_different_inode_and_symlink(self):
        with tempfile.TemporaryDirectory() as folder:
            parent = Path(folder)
            sibling = parent / 'unexpected-public-sibling'
            sibling.write_bytes(b'PUBLIC-EXTRA')
            inode, payload = module._snapshot_regular(sibling)
            self.assertEqual(payload, b'PUBLIC-EXTRA')
            sibling.unlink()
            substitute = parent / 'new-public-target'
            substitute.write_bytes(b'PUBLIC-EXTRA')
            sibling.symlink_to(substitute)
            with self.assertRaises(OSError):
                module._snapshot_regular(sibling)

    def test_disposable_sibling_same_inode_rewritten_bytes_are_detected(self):
        with tempfile.TemporaryDirectory() as folder:
            sibling = Path(folder) / 'unexpected-public-sibling'
            sibling.write_bytes(b'PUBLIC-EXTRA')
            inode, payload = module._snapshot_regular(sibling)
            sibling.write_bytes(b'CHANGED')
            next_inode, next_payload = module._snapshot_regular(sibling)
            self.assertEqual(inode, next_inode)
            self.assertNotEqual(payload, next_payload)
            self.assertFalse(inode == next_inode and payload == next_payload == b'PUBLIC-EXTRA')

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
