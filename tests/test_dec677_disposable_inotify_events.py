from __future__ import annotations

import contextlib
import importlib.util
import io
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


def native_created_sample_snapshot(path, data=module.BEFORE):
    """Keep synthetic snapshot bytes but bind to a real generated inode."""
    record = os.lstat(path)
    return ((record.st_dev, record.st_ino), data)


def native_created_sample_sequence(*observations):
    """Keep a real initial inode before injected second-snapshot failures."""
    pending = iter(observations)

    def snapshot(path):
        item = next(pending)
        if isinstance(item, Exception):
            raise item
        return native_created_sample_snapshot(path, item)

    return snapshot


class DisposableInotifyTests(unittest.TestCase):
    def test_empty_stream_has_no_events_but_never_authorizes(self):
        r = module._evaluate(b'same', b'same', b'', 9, True, False,
                             directory_watch=10, directory_inventory_names=("sample",))
        self.assertEqual(r['status'], 'LOCAL_DISPOSABLE_WITNESS_UNVERIFIED')
        self.assertFalse(r['can_authorize_dispatch'])
        self.assertFalse(r['independent_os_proof_verified'])

    def test_two_writes_and_revert_always_block(self):
        r = module._evaluate(b'same', b'same',
                             ev(mask=module.IN_MODIFY) * 2, 9, True, True,
                             directory_watch=10,
                             midpoint_snapshot_matches_expected=True,
                                  directory_inventory_names=("sample",))
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
        stream = (ev(wd=10, mask=module.IN_CREATE, data=named(b'temporary-public-sibling'))
                  + ev(wd=10, mask=module.IN_DELETE, data=named(b'temporary-public-sibling')))
        result = module._evaluate(b'unchanged', b'unchanged', stream, 9, True, False,
                                  directory_watch=10, directory_inventory_ok=True,
                                  directory_inventory_names=("sample",),
                                  transient_sibling_negative=True, transient_midpoint_verified=True)
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
                             directory_watch=10, directory_inventory_names=("sample",))
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
                                  directory_watch=adjacent, directory_inventory_names=("sample",))
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
        stream = (ev(wd=10, mask=module.IN_CREATE, data=named(b'temporary-public-sibling'))
                  + ev(wd=10, mask=module.IN_CREATE, data=named(b'b'))
                  + ev(wd=10, mask=module.IN_DELETE, data=named(b'temporary-public-sibling'))
                  + ev(wd=10, mask=module.IN_DELETE, data=named(b'b')))
        parsed = module._classify_stream(stream, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['transient_create_delete_pairs'], 2)
        self.assertEqual(parsed['expected_transient_pairs'], 1)
        result = module._evaluate(b'a', b'a', stream, 9, True, False,
                                  directory_watch=10, directory_inventory_names=("sample",),
                                  transient_sibling_negative=True, transient_midpoint_verified=True)
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
                                  directory_watch=10,
                                  midpoint_snapshot_matches_expected=True,
                                  directory_inventory_names=("sample",))
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
        raw = (ev(wd=10, mask=module.IN_CREATE, data=named(b'temporary-public-sibling'))
               + ev(wd=10, mask=module.IN_DELETE, data=named(b'temporary-public-sibling')))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['transient_create_delete_pairs'], 1)
        verdict = module._evaluate(b'same', b'same', raw, 9, True, False,
                                   directory_watch=10, directory_inventory_names=("sample",),
                                  transient_sibling_negative=True, transient_midpoint_verified=True)
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
                                  directory_watch=10,
                                  midpoint_snapshot_matches_expected=True,
                                  directory_inventory_names=("sample",))
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
                                   directory_watch=10, directory_inventory_names=("sample",))
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

    @unittest.skipUnless(hasattr(os, 'O_NOFOLLOW') and hasattr(os, 'symlink'),
                         'POSIX no-follow symlinks required')
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

    @unittest.skipUnless(hasattr(os, 'O_NOFOLLOW'),
                         'POSIX no-follow snapshot required')
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


    def test_malformed_event_decoder_early_returns_have_complete_dicts(self):
        oversized = b'Z' * 65537
        for data, watch, directory_watch in (
            ('not-bytes', 9, 10),
            (b'', -1, 10),
            (b'', 1 << 31, 10),
            (oversized, 9, 10),
            (b'', 9, 9),
            (b'', 9, 'bad-directory-watch'),
        ):
            with self.subTest(data_type=type(data).__name__, watch=watch,
                              directory_watch=directory_watch):
                parsed = module._classify_stream(data, watch, directory_watch)
                self.assertFalse(parsed['well_formed'])
                self.assertTrue(parsed['overflow'])
                self.assertTrue(parsed['invalidated'])
                self.assertEqual(parsed['source_modify_events'], 0)
                self.assertFalse(parsed['expected_sibling_created'])
                self.assertEqual(parsed['transient_create_delete_pairs'], 0)

    def test_malformed_watch_identity_still_returns_blocked_evaluation(self):
        verdict = module._evaluate(b'public', b'public', b'', 9, True, False,
                                   directory_watch=9)
        self.assertEqual(verdict['status'], 'BLOCKED')
        self.assertFalse(verdict['can_authorize_dispatch'])
        self.assertFalse(verdict['independent_os_proof_verified'])
        self.assertFalse(verdict['observed_checks']['event_stream_complete'])


    def test_sorted_directory_enumeration_recognizes_correct_persistent_sibling(self):
        with tempfile.TemporaryDirectory() as folder:
            parent = Path(folder)
            (parent / "sample").write_bytes(b"public")
            (parent / module.PERSISTENT_SIBLING_NAME).write_bytes(b"PUBLIC-EXTRA")
            names = tuple(sorted(path.name for path in parent.iterdir()))
            self.assertEqual(names, ("sample", "unexpected-public-sibling"))
            raw = ev(wd=10, mask=module.IN_CREATE,
                     data=named(b"unexpected-public-sibling"))
            verdict = module._evaluate(
                b"public", b"public", raw, 9, True, False,
                directory_watch=10, directory_inventory_ok=False,
                directory_inventory_names=names, sibling_snapshot_stable=True,
                sibling_negative=True)
            self.assertTrue(verdict['observed_checks']['sibling_creation_control_detected'])
            self.assertEqual(verdict['status'], 'BLOCKED')

    def test_unsorted_input_tuple_cannot_claim_persistent_sibling_witness(self):
        raw = ev(wd=10, mask=module.IN_CREATE,
                 data=named(b"unexpected-public-sibling"))
        verdict = module._evaluate(
            b"public", b"public", raw, 9, True, False,
            directory_watch=10, directory_inventory_ok=False,
            directory_inventory_names=("unexpected-public-sibling", "sample"),
            sibling_snapshot_stable=True, sibling_negative=True)
        self.assertFalse(verdict['observed_checks']['sibling_creation_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')


    def test_source_modify_events_without_midpoint_do_not_prove_revert(self):
        raw = ev(wd=9, mask=module.IN_MODIFY) * 2
        for midway in (None, False, 1, "true", b'AFTER'):
            with self.subTest(midway=repr(midway)):
                verdict = module._evaluate(
                    b'public', b'public', raw, 9, True, True,
                    directory_watch=10,
                    midpoint_snapshot_matches_expected=midway)
                self.assertFalse(verdict['observed_checks']['negative_control_detected'])
                self.assertFalse(verdict['observed_checks']['midpoint_source_snapshot_matches_expected'])
                self.assertEqual(verdict['status'], 'BLOCKED')

    def test_exact_midpoint_and_two_file_modifications_witness_control(self):
        raw = ev(wd=9, mask=module.IN_MODIFY) * 2
        verdict = module._evaluate(
            b'public', b'public', raw, 9, True, True,
            directory_watch=10, midpoint_snapshot_matches_expected=True,
                                  directory_inventory_names=("sample",))
        self.assertTrue(verdict['observed_checks']['midpoint_source_snapshot_matches_expected'])
        self.assertTrue(verdict['observed_checks']['negative_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')
        self.assertFalse(verdict['can_authorize_dispatch'])

    def test_midpoint_proof_without_two_source_modifies_not_witness(self):
        raw = ev(wd=9, mask=module.IN_CLOSE_WRITE) * 2
        verdict = module._evaluate(
            b'public', b'public', raw, 9, True, True,
            directory_watch=10, midpoint_snapshot_matches_expected=True)
        self.assertTrue(verdict['observed_checks']['midpoint_source_snapshot_matches_expected'])
        self.assertFalse(verdict['observed_checks']['negative_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')

    def test_midpoint_proof_with_invalid_event_stream_not_witness(self):
        raw = ev(wd=9, mask=module.IN_MODIFY) * 2 + b'BROKEN'
        verdict = module._evaluate(
            b'public', b'public', raw, 9, True, True,
            directory_watch=10, midpoint_snapshot_matches_expected=True)
        self.assertFalse(verdict['observed_checks']['event_stream_complete'])
        self.assertFalse(verdict['observed_checks']['negative_control_detected'])


    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux watch test')
    def test_baseline_snapshot_is_taken_after_both_watches_registered(self):
        rd, wr = os.pipe()
        order = []
        try:
            def fake_watch(_path):
                order.append('watch-file-and-directory')
                return rd, 9, 10
            def fake_snapshot(_path):
                order.append('bounded-snapshot')
                return native_created_sample_snapshot(_path)
            def fake_drain(_fd):
                order.append('event-drain')
                return b''
            with patch.object(module, '_start_watch', side_effect=fake_watch):
                with patch.object(module, '_snapshot_regular', side_effect=fake_snapshot):
                    with patch.object(module, '_read_pending', side_effect=fake_drain):
                        verdict = module.run_demo()
            self.assertEqual(order[0:2], ['watch-file-and-directory', 'bounded-snapshot'])
            self.assertEqual(verdict['status'], 'LOCAL_DISPOSABLE_WITNESS_UNVERIFIED')
            self.assertFalse(verdict['can_authorize_dispatch'])
        finally:
            os.close(wr)

    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux watch test')
    def test_initial_snapshot_failure_closes_installed_watch_fd(self):
        rd, wr = os.pipe()
        try:
            with patch.object(module, '_start_watch', return_value=(rd, 9, 10)):
                with patch.object(module, '_snapshot_regular',
                                  side_effect=OSError('failed initial snapshot')):
                    with patch.object(module, '_read_pending') as drain:
                        verdict = module.run_demo()
                        drain.assert_not_called()
            self.assertEqual(verdict['status'], 'BLOCKED')
            self.assertFalse(verdict['can_authorize_dispatch'])
            with self.assertRaises(OSError):
                os.fstat(rd)
        finally:
            os.close(wr)


    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux watch test')
    def test_end_of_observation_event_drain_is_after_final_snapshot(self):
        rd, wr = os.pipe()
        order = []
        try:
            def fake_snapshot(_path):
                order.append('snapshot')
                return native_created_sample_snapshot(_path)
            def fake_drain(_fd):
                order.append('drain')
                return b''
            with patch.object(module, '_start_watch', return_value=(rd, 9, 10)):
                with patch.object(module, '_snapshot_regular', side_effect=fake_snapshot):
                    with patch.object(module, '_read_pending', side_effect=fake_drain):
                        result = module.run_demo()
            # DEC-845 intentionally takes a third no-follow sample snapshot
            # after draining: the predrain snapshot still precedes the drain.
            self.assertEqual(order, ['snapshot', 'snapshot', 'drain', 'snapshot'])
            self.assertEqual(result['status'], 'LOCAL_DISPOSABLE_WITNESS_UNVERIFIED')
        finally:
            os.close(wr)

    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux watch test')
    def test_modification_during_final_snapshot_is_drained_before_verdict(self):
        rd, wr = os.pipe()
        pending = []
        snapshot_calls = []
        try:
            def fake_snapshot(_path):
                snapshot_calls.append(1)
                if len(snapshot_calls) == 2:
                    pending.append(ev(wd=9, mask=module.IN_MODIFY))
                return native_created_sample_snapshot(_path)
            def fake_drain(_fd):
                observed = b''.join(pending)
                pending.clear()
                return observed
            with patch.object(module, '_start_watch', return_value=(rd, 9, 10)):
                with patch.object(module, '_snapshot_regular', side_effect=fake_snapshot):
                    with patch.object(module, '_read_pending', side_effect=fake_drain):
                        result = module.run_demo()
            # One additional postdrain sample read must not make the earlier
            # observed IN_MODIFY event disappear from the final verdict.
            self.assertEqual(len(snapshot_calls), 3)
            self.assertEqual(result['status'], 'BLOCKED')
            self.assertFalse(result['observed_checks']['no_observed_writes'])
            self.assertFalse(result['can_authorize_dispatch'])
        finally:
            os.close(wr)


    def test_unrelated_regular_create_delete_pair_is_not_expected_control(self):
        raw = (ev(wd=10, mask=module.IN_CREATE, data=named(b'unrelated'))
               + ev(wd=10, mask=module.IN_DELETE, data=named(b'unrelated')))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['transient_create_delete_pairs'], 1)
        self.assertEqual(parsed['expected_transient_pairs'], 0)
        verdict = module._evaluate(b'a', b'a', raw, 9, True, False,
                                   directory_watch=10, transient_sibling_negative=True)
        self.assertFalse(verdict['observed_checks']['transient_directory_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')

    def test_specific_regular_transient_pair_counts_one_expected_control(self):
        name = named(b'temporary-public-sibling')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=name)
               + ev(wd=10, mask=module.IN_DELETE, data=name))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['expected_transient_pairs'], 1)
        self.assertEqual(parsed['transient_create_delete_pairs'], 1)
        verdict = module._evaluate(b'a', b'a', raw, 9, True, False,
                                   directory_watch=10, directory_inventory_names=("sample",),
                                  transient_sibling_negative=True, transient_midpoint_verified=True)
        self.assertTrue(verdict['observed_checks']['transient_directory_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')

    def test_expected_name_directory_events_do_not_count_as_file_control(self):
        name = named(b'temporary-public-sibling')
        raw = (ev(wd=10, mask=module.IN_CREATE | module.IN_ISDIR, data=name)
               + ev(wd=10, mask=module.IN_DELETE | module.IN_ISDIR, data=name))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertEqual(parsed['expected_transient_pairs'], 0)
        verdict = module._evaluate(b'a', b'a', raw, 9, True, False,
                                   directory_watch=10, transient_sibling_negative=True)
        self.assertFalse(verdict['observed_checks']['transient_directory_control_detected'])

    def test_expected_create_and_other_leaf_delete_does_not_count(self):
        raw = (ev(wd=10, mask=module.IN_CREATE,
                  data=named(b'temporary-public-sibling'))
               + ev(wd=10, mask=module.IN_DELETE, data=named(b'other')))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertEqual(parsed['expected_transient_pairs'], 0)
        self.assertEqual(parsed['transient_create_delete_pairs'], 0)

    def test_expected_pair_with_overflow_cannot_claim_transient_control(self):
        name = named(b'temporary-public-sibling')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=name)
               + ev(wd=10, mask=module.IN_DELETE, data=name)
               + ev(wd=-1, mask=module.IN_Q_OVERFLOW))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertEqual(parsed['expected_transient_pairs'], 1)
        self.assertTrue(parsed['overflow'])
        verdict = module._evaluate(b'a', b'a', raw, 9, True, False,
                                   directory_watch=10, transient_sibling_negative=True)
        self.assertFalse(verdict['observed_checks']['transient_directory_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')


    def test_correct_transient_pair_with_other_surviving_entry_not_complete(self):
        name = named(b'temporary-public-sibling')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=name)
               + ev(wd=10, mask=module.IN_DELETE, data=name))
        verdict = module._evaluate(
            b'public', b'public', raw, 9, True, False,
            directory_watch=10, directory_inventory_ok=False,
            directory_inventory_names=("other", "sample"),
            transient_sibling_negative=True)
        self.assertFalse(verdict['observed_checks']['transient_directory_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')

    def test_correct_transient_pair_requires_bounded_final_names(self):
        name = named(b'temporary-public-sibling')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=name)
               + ev(wd=10, mask=module.IN_DELETE, data=name))
        for names in (None, [], ["sample"], ("sample", "other"), ("other",)):
            with self.subTest(names=repr(names)):
                verdict = module._evaluate(
                    b'public', b'public', raw, 9, True, False,
                    directory_watch=10, directory_inventory_ok=True,
                    directory_inventory_names=names,
                    transient_sibling_negative=True)
                self.assertFalse(verdict['observed_checks']['transient_directory_control_detected'])

    def test_correct_transient_pair_with_final_single_leaf_counts_as_detected(self):
        name = named(b'temporary-public-sibling')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=name)
               + ev(wd=10, mask=module.IN_DELETE, data=name))
        verdict = module._evaluate(
            b'public', b'public', raw, 9, True, False,
            directory_watch=10, directory_inventory_ok=True,
            directory_inventory_names=("sample",),
            transient_sibling_negative=True, transient_midpoint_verified=True)
        self.assertTrue(verdict['observed_checks']['transient_directory_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')
        self.assertFalse(verdict['can_authorize_dispatch'])

    def test_transient_pair_with_correct_names_but_false_inventory_flag_is_rejected(self):
        name = named(b'temporary-public-sibling')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=name)
               + ev(wd=10, mask=module.IN_DELETE, data=name))
        verdict = module._evaluate(
            b'public', b'public', raw, 9, True, False,
            directory_watch=10, directory_inventory_ok=False,
            directory_inventory_names=("sample",),
            transient_sibling_negative=True)
        self.assertFalse(verdict['observed_checks']['transient_directory_control_detected'])


    def test_quiet_stream_without_final_names_cannot_claim_clean_inventory(self):
        verdict = module._evaluate(b'public', b'public', b'', 9, True, False,
                                   directory_watch=10, directory_inventory_ok=True)
        self.assertFalse(verdict['observed_checks']['no_directory_entry_mutations'])
        self.assertEqual(verdict['status'], 'BLOCKED')
        self.assertFalse(verdict['can_authorize_dispatch'])

    def test_wrong_final_names_or_type_cannot_claim_clean_directory(self):
        for names in (None, ['sample'], ('other',), ('other', 'sample'),
                      ('sample', 'extra')):
            with self.subTest(names=repr(names)):
                verdict = module._evaluate(
                    b'public', b'public', b'', 9, True, False,
                    directory_watch=10, directory_inventory_ok=True,
                    directory_inventory_names=names)
                self.assertFalse(verdict['observed_checks']['no_directory_entry_mutations'])
                self.assertEqual(verdict['status'], 'BLOCKED')

    def test_exact_final_single_source_and_quiet_stream_remain_only_local(self):
        verdict = module._evaluate(
            b'public', b'public', b'', 9, True, False,
            directory_watch=10, directory_inventory_ok=True,
            directory_inventory_names=('sample',))
        self.assertTrue(verdict['observed_checks']['no_directory_entry_mutations'])
        self.assertEqual(verdict['status'], 'LOCAL_DISPOSABLE_WITNESS_UNVERIFIED')
        self.assertFalse(verdict['independent_os_proof_verified'])
        self.assertFalse(verdict['can_authorize_dispatch'])

    def test_sibling_sort_uses_python_lexical_order_in_contract_and_fixture(self):
        # The contract and fixture must agree with Python's actual ordering:
        # lowercase 's' precedes lowercase 'u'.
        expected = ("sample", module.PERSISTENT_SIBLING_NAME)
        self.assertEqual(tuple(sorted(expected)), expected)
        self.assertEqual(tuple(sorted(reversed(expected))), expected)
        raw = ev(wd=10, mask=module.IN_CREATE,
                 data=named(module.PERSISTENT_SIBLING_NAME.encode('ascii')))
        observed = module._evaluate(
            b'public', b'public', raw, 9, True, False,
            directory_watch=10, directory_inventory_ok=False,
            directory_inventory_names=expected,
            sibling_snapshot_stable=True, sibling_negative=True)
        self.assertTrue(observed['observed_checks']['sibling_creation_control_detected'])
        self.assertEqual(observed['status'], 'BLOCKED')
        self.assertFalse(observed['can_authorize_dispatch'])


    def test_move_away_cancels_pending_transient_create_claim(self):
        name = named(b'temporary-public-sibling')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=name)
               + ev(wd=10, mask=module.IN_MOVED_FROM, data=name, cookie=3)
               + ev(wd=10, mask=module.IN_DELETE, data=name))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        # No IN_CREATE / IN_MOVED_TO after move-out can justify the delete.
        self.assertFalse(parsed['well_formed'])
        self.assertEqual(parsed['transient_create_delete_pairs'], 0)
        self.assertEqual(parsed['expected_transient_pairs'], 0)
        verdict = module._evaluate(
            b'public', b'public', raw, 9, True, False,
            directory_watch=10, directory_inventory_ok=True,
            directory_inventory_names=("sample",),
            transient_sibling_negative=True)
        self.assertFalse(verdict['observed_checks']['transient_directory_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')

    def test_move_into_same_basename_cancels_original_create_claim(self):
        name = named(b'temporary-public-sibling')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=name)
               + ev(wd=10, mask=module.IN_MOVED_TO, data=name, cookie=7)
               + ev(wd=10, mask=module.IN_DELETE, data=name))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['transient_create_delete_pairs'], 0)
        self.assertEqual(parsed['expected_transient_pairs'], 0)

    def test_unrelated_move_does_not_invalidate_expected_regular_file_pair(self):
        target = named(b'temporary-public-sibling')
        unrelated = named(b'another-public-child')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=target)
               + ev(wd=10, mask=module.IN_MOVED_FROM, data=unrelated, cookie=5)
               + ev(wd=10, mask=module.IN_DELETE, data=target))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['expected_transient_pairs'], 1)
        verdict = module._evaluate(
            b'public', b'public', raw, 9, True, False,
            directory_watch=10, directory_inventory_ok=True,
            directory_inventory_names=("sample",),
            transient_sibling_negative=True, transient_midpoint_verified=True)
        self.assertTrue(verdict['observed_checks']['transient_directory_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')

    def test_new_create_after_name_move_can_form_its_own_pair(self):
        name = named(b'temporary-public-sibling')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=name)
               + ev(wd=10, mask=module.IN_MOVED_FROM, data=name, cookie=4)
               + ev(wd=10, mask=module.IN_CREATE, data=name)
               + ev(wd=10, mask=module.IN_DELETE, data=name))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['expected_transient_pairs'], 1)


    def test_transient_pair_with_unobserved_intermediate_file_cannot_claim_control(self):
        name = named(b'temporary-public-sibling')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=name)
               + ev(wd=10, mask=module.IN_DELETE, data=name))
        for value in (None, False, 1, 'true', (), []):
            with self.subTest(value=repr(value)):
                verdict = module._evaluate(
                    b'public', b'public', raw, 9, True, False,
                    directory_watch=10, directory_inventory_ok=True,
                    directory_inventory_names=("sample",),
                    transient_sibling_negative=True, transient_midpoint_verified=value)
                self.assertFalse(verdict['observed_checks']['transient_midpoint_regular_file_verified'])
                self.assertFalse(verdict['observed_checks']['transient_directory_control_detected'])
                self.assertEqual(verdict['status'], 'BLOCKED')

    def test_transient_midpoint_without_expected_kernel_pair_does_not_claim_control(self):
        raw = (ev(wd=10, mask=module.IN_CREATE, data=named(b'other'))
               + ev(wd=10, mask=module.IN_DELETE, data=named(b'other')))
        verdict = module._evaluate(
            b'public', b'public', raw, 9, True, False,
            directory_watch=10, directory_inventory_names=("sample",),
            transient_sibling_negative=True, transient_midpoint_verified=True)
        self.assertTrue(verdict['observed_checks']['transient_midpoint_regular_file_verified'])
        self.assertFalse(verdict['observed_checks']['transient_directory_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')

    @unittest.skipUnless(hasattr(os, 'O_NOFOLLOW'), 'POSIX no-follow snapshot required')
    def test_generated_transient_midpoint_is_bounded_regular_public_file(self):
        with tempfile.TemporaryDirectory() as folder:
            transient = Path(folder) / module.TRANSIENT_SIBLING_NAME
            transient.write_bytes(b'PUBLIC-TEMPORARY')
            inode, content = module._snapshot_regular(transient)
            self.assertIs(type(inode), tuple)
            self.assertEqual(len(inode), 2)
            self.assertEqual(content, b'PUBLIC-TEMPORARY')
            transient.unlink()
            self.assertFalse(transient.exists())
            with self.assertRaises(OSError):
                module._snapshot_regular(transient)


    def test_source_write_without_restored_final_bytes_is_not_revert_control(self):
        raw = ev(wd=9, mask=module.IN_MODIFY) * 2
        verdict = module._evaluate(
            b'baseline', b'changed', raw, 9, True, True,
            directory_watch=10, midpoint_snapshot_matches_expected=True)
        self.assertFalse(verdict['observed_checks']['final_digest_equal'])
        self.assertTrue(verdict['observed_checks']['midpoint_source_snapshot_matches_expected'])
        self.assertFalse(verdict['observed_checks']['negative_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')
        self.assertFalse(verdict['can_authorize_dispatch'])

    def test_source_inode_swap_with_same_final_bytes_is_not_revert_control(self):
        raw = ev(wd=9, mask=module.IN_MODIFY) * 2
        verdict = module._evaluate(
            b'baseline', b'baseline', raw, 9, True, True, inode_stable=False,
            directory_watch=10, midpoint_snapshot_matches_expected=True)
        self.assertTrue(verdict['observed_checks']['final_digest_equal'])
        self.assertFalse(verdict['observed_checks']['watched_inode_matches_final_path'])
        self.assertFalse(verdict['observed_checks']['negative_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')

    def test_restored_source_inode_and_bytes_preserve_observed_negative(self):
        raw = ev(wd=9, mask=module.IN_MODIFY) * 2
        verdict = module._evaluate(
            b'baseline', b'baseline', raw, 9, True, True, inode_stable=True,
            directory_watch=10, midpoint_snapshot_matches_expected=True,
                                  directory_inventory_names=("sample",))
        self.assertTrue(verdict['observed_checks']['negative_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')


    def test_expected_persistent_sibling_create_then_delete_not_current(self):
        name = named(b'unexpected-public-sibling')
        stream = (ev(wd=10, mask=module.IN_CREATE, data=name)
                  + ev(wd=10, mask=module.IN_DELETE, data=name))
        parsed = module._classify_stream(stream, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertFalse(parsed['expected_sibling_created'])
        result = module._evaluate(
            b'public', b'public', stream, 9, True, False,
            directory_watch=10, directory_inventory_ok=False,
            directory_inventory_names=("sample", "unexpected-public-sibling"),
            sibling_snapshot_stable=True, sibling_negative=True)
        self.assertFalse(result['observed_checks']['sibling_creation_control_detected'])
        self.assertEqual(result['status'], 'BLOCKED')

    def test_expected_persistent_sibling_move_away_cancels_claim(self):
        name = named(b'unexpected-public-sibling')
        stream = (ev(wd=10, mask=module.IN_CREATE, data=name)
                  + ev(wd=10, mask=module.IN_MOVED_FROM, data=name, cookie=101))
        parsed = module._classify_stream(stream, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertFalse(parsed['expected_sibling_created'])

    def test_same_name_move_in_does_not_preserve_prior_create_claim(self):
        name = named(b'unexpected-public-sibling')
        stream = (ev(wd=10, mask=module.IN_CREATE, data=name)
                  + ev(wd=10, mask=module.IN_MOVED_TO, data=name, cookie=102))
        parsed = module._classify_stream(stream, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertFalse(parsed['expected_sibling_created'])

    def test_unrelated_child_does_not_invalidate_expected_persistent_sibling(self):
        target = named(b'unexpected-public-sibling')
        other = named(b'unrelated')
        stream = (ev(wd=10, mask=module.IN_CREATE, data=target)
                  + ev(wd=10, mask=module.IN_CREATE, data=other)
                  + ev(wd=10, mask=module.IN_DELETE, data=other))
        parsed = module._classify_stream(stream, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertTrue(parsed['expected_sibling_created'])
        result = module._evaluate(
            b'public', b'public', stream, 9, True, False,
            directory_watch=10, directory_inventory_ok=False,
            directory_inventory_names=("sample", "unexpected-public-sibling"),
            sibling_snapshot_stable=True, sibling_negative=True)
        self.assertTrue(result['observed_checks']['sibling_creation_control_detected'])
        self.assertEqual(result['status'], 'BLOCKED')


    def test_duplicate_create_then_delete_same_leaf_fails_closed(self):
        name = named(b'temporary-public-sibling')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=name)
               + ev(wd=10, mask=module.IN_CREATE, data=name)
               + ev(wd=10, mask=module.IN_DELETE, data=name))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertFalse(parsed['well_formed'])
        verdict = module._evaluate(
            b'public', b'public', raw, 9, True, False,
            directory_watch=10, directory_inventory_ok=True,
            directory_inventory_names=("sample",),
            transient_sibling_negative=True, transient_midpoint_verified=True)
        self.assertFalse(verdict['observed_checks']['event_stream_complete'])
        self.assertFalse(verdict['observed_checks']['transient_directory_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')

    def test_duplicate_create_unrelated_leaf_fails_stream_closed(self):
        target = named(b'temporary-public-sibling')
        other = named(b'other')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=target)
               + ev(wd=10, mask=module.IN_CREATE, data=other)
               + ev(wd=10, mask=module.IN_CREATE, data=other)
               + ev(wd=10, mask=module.IN_DELETE, data=target))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertFalse(parsed['well_formed'])
        verdict = module._evaluate(
            b'public', b'public', raw, 9, True, False,
            directory_watch=10, directory_inventory_ok=True,
            directory_inventory_names=("sample",),
            transient_sibling_negative=True, transient_midpoint_verified=True)
        self.assertFalse(verdict['observed_checks']['transient_directory_control_detected'])

    def test_create_delete_create_delete_same_leaf_remains_two_witnesses(self):
        name = named(b'temporary-public-sibling')
        pair = (ev(wd=10, mask=module.IN_CREATE, data=name)
                + ev(wd=10, mask=module.IN_DELETE, data=name))
        parsed = module._classify_stream(pair + pair, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['expected_transient_pairs'], 2)
        self.assertEqual(parsed['transient_create_delete_pairs'], 2)

    def test_create_move_out_then_create_same_leaf_is_not_duplicate(self):
        name = named(b'temporary-public-sibling')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=name)
               + ev(wd=10, mask=module.IN_MOVED_FROM, data=name, cookie=71)
               + ev(wd=10, mask=module.IN_CREATE, data=name)
               + ev(wd=10, mask=module.IN_DELETE, data=name))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['expected_transient_pairs'], 1)


    def test_disposable_mode_values_require_exact_bool_type(self):
        for invalid in (None, 1, 0, "true", "false", [], {}, 0.5, float('nan')):
            for mode in range(4):
                with self.subTest(invalid=repr(invalid), mode=mode):
                    args = [False, False, False, False]
                    args[mode] = invalid
                    result = module.run_demo(*args)
                    self.assertEqual(result['status'], 'BLOCKED')
                    self.assertIn('disposable negative-control modes must be booleans',
                                  result['findings'])
                    self.assertFalse(result['can_authorize_dispatch'])

    def test_conflicting_real_boolean_negative_modes_still_block(self):
        for indices in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)):
            with self.subTest(indices=indices):
                args = [False, False, False, False]
                for index in indices:
                    args[index] = True
                result = module.run_demo(*args)
                self.assertEqual(result['status'], 'BLOCKED')
                self.assertIn('conflicting synthetic negative-control modes',
                              result['findings'])
                self.assertFalse(result['can_authorize_dispatch'])

    def test_invalid_mode_type_precedes_linux_and_filesystem_setup(self):
        with patch.object(module.sys, 'platform', 'linux'):
            with patch.object(module.tempfile, 'TemporaryDirectory') as directory:
                result = module.run_demo(negative="nonboolean")
                directory.assert_not_called()
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertFalse(result['can_authorize_dispatch'])

    def test_valid_bool_modes_on_unsupported_host_fail_closed(self):
        with patch.object(module.sys, 'platform', 'win32'):
            for args in ((False, False, False, False),
                         (True, False, False, False),
                         (False, True, False, False),
                         (False, False, True, False),
                         (False, False, False, True)):
                with self.subTest(args=args):
                    result = module.run_demo(*args)
                    self.assertEqual(result['status'], 'BLOCKED')
                    self.assertIn('Linux disposable kernel event monitor unavailable',
                                  result['findings'])


    def test_two_deletes_of_same_child_make_stream_incomplete(self):
        name = named(b'temporary-public-sibling')
        stream = ev(wd=10, mask=module.IN_DELETE, data=name) * 2
        parsed = module._classify_stream(stream, 9, directory_watch=10)
        self.assertFalse(parsed['well_formed'])
        verdict = module._evaluate(
            b'a', b'a', stream, 9, True, False, directory_watch=10,
            directory_inventory_ok=True, directory_inventory_names=("sample",),
            transient_sibling_negative=True, transient_midpoint_verified=True)
        self.assertFalse(verdict['observed_checks']['event_stream_complete'])
        self.assertFalse(verdict['observed_checks']['transient_directory_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')

    def test_duplicate_unrelated_delete_contaminates_valid_transient_pair(self):
        target = named(b'temporary-public-sibling')
        other = named(b'other')
        stream = (ev(wd=10, mask=module.IN_CREATE, data=target)
                  + ev(wd=10, mask=module.IN_DELETE, data=other)
                  + ev(wd=10, mask=module.IN_DELETE, data=other)
                  + ev(wd=10, mask=module.IN_DELETE, data=target))
        parsed = module._classify_stream(stream, 9, directory_watch=10)
        self.assertFalse(parsed['well_formed'])
        verdict = module._evaluate(
            b'a', b'a', stream, 9, True, False, directory_watch=10,
            directory_inventory_ok=True, directory_inventory_names=("sample",),
            transient_sibling_negative=True, transient_midpoint_verified=True)
        self.assertFalse(verdict['observed_checks']['transient_directory_control_detected'])

    def test_delete_create_delete_same_child_is_valid_timeline(self):
        name = named(b'temporary-public-sibling')
        stream = (ev(wd=10, mask=module.IN_DELETE, data=name)
                  + ev(wd=10, mask=module.IN_CREATE, data=name)
                  + ev(wd=10, mask=module.IN_DELETE, data=name))
        parsed = module._classify_stream(stream, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['expected_transient_pairs'], 1)

    def test_delete_move_into_name_delete_is_valid_timeline(self):
        name = named(b'temporary-public-sibling')
        stream = (ev(wd=10, mask=module.IN_DELETE, data=name)
                  + ev(wd=10, mask=module.IN_MOVED_TO, data=name, cookie=19)
                  + ev(wd=10, mask=module.IN_DELETE, data=name))
        parsed = module._classify_stream(stream, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['expected_transient_pairs'], 0)


    def test_inotify_decoder_rejects_hostile_bytes_subclass_before_len(self):
        class HostileBytes(bytes):
            def __len__(self):
                raise RuntimeError('injected len side effect')

        parsed = module._classify_stream(HostileBytes(b''), 9, directory_watch=10)
        self.assertFalse(parsed['well_formed'])
        self.assertTrue(parsed['overflow'])
        self.assertTrue(parsed['invalidated'])
        verdict = module._evaluate(
            b'public', b'public', HostileBytes(b''), 9, True, False,
            directory_watch=10, directory_inventory_names=('sample',))
        self.assertEqual(verdict['status'], 'BLOCKED')
        self.assertFalse(verdict['can_authorize_dispatch'])

    def test_inotify_decoder_rejects_bytes_subclass_with_spoofed_length(self):
        class PretendEmpty(bytes):
            def __len__(self):
                return 0

        raw = module.EVENT.pack(9, module.IN_MODIFY, 0, 0)
        parsed = module._classify_stream(PretendEmpty(raw), 9, directory_watch=10)
        self.assertFalse(parsed['well_formed'])
        self.assertEqual(parsed['source_modify_events'], 0)

    def test_inotify_decoder_plain_bytes_still_parse_normal_event(self):
        raw = bytes(module.EVENT.pack(9, module.IN_MODIFY, 0, 0))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['source_modify_events'], 1)
        self.assertFalse(parsed['overflow'])


    def test_forged_eq_readiness_object_cannot_fake_exact_pollin(self):
        class AlwaysEqual:
            def __eq__(self, _other):
                return True
        class Ready:
            def register(self, *_args): pass
            def poll(self, _timeout): return [AlwaysEqual()]
        with patch.object(module.select, 'poll', return_value=Ready()):
            with patch.object(module.os, 'read') as read:
                with self.assertRaisesRegex(OSError, 'lost readable status'):
                    module._read_pending(17)
                read.assert_not_called()

    def test_poll_tuple_subclass_with_forged_equality_is_refused(self):
        class ForgedTuple(tuple):
            def __eq__(self, _other):
                return True
        class Ready:
            def register(self, *_args): pass
            def poll(self, _timeout): return [ForgedTuple((18, 0))]
        with patch.object(module.select, 'poll', return_value=Ready()):
            with patch.object(module.os, 'read') as read:
                with self.assertRaisesRegex(OSError, 'lost readable status'):
                    module._read_pending(17)
                read.assert_not_called()

    def test_poll_tuple_with_boolean_or_int_subclass_is_refused(self):
        class SpoofInt(int):
            def __eq__(self, _other):
                return True
        class Ready:
            def __init__(self, record): self.record = record
            def register(self, *_args): pass
            def poll(self, _timeout): return [self.record]
        for record in ((17, True), (True, module.select.POLLIN),
                       (SpoofInt(17), module.select.POLLIN),
                       (17, SpoofInt(module.select.POLLIN)), (17,),
                       (17, module.select.POLLIN, 3)):
            with self.subTest(record=record):
                with patch.object(module.select, 'poll', return_value=Ready(record)):
                    with patch.object(module.os, 'read') as read:
                        with self.assertRaisesRegex(OSError, 'lost readable status'):
                            module._read_pending(17)
                        read.assert_not_called()

    def test_collector_rejects_noninteger_fd_before_poll_registration(self):
        with patch.object(module.select, 'poll') as factory:
            for fd in (None, True, False, '17', -1, 17.0):
                with self.subTest(fd=repr(fd)):
                    with self.assertRaisesRegex(OSError, 'requires a nonstdio integer fd'):
                        module._read_pending(fd)
            factory.assert_not_called()


    @unittest.skipUnless(hasattr(os, 'O_NOFOLLOW'), 'POSIX no-follow snapshot required')
    def test_snapshot_nonbyte_read_results_raise_handled_oserror(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'sample'
            path.write_bytes(b'ABC')
            for value in (None, 'ABC', [], bytearray(b'ABC'), 123):
                with self.subTest(value=repr(value)):
                    with patch.object(module.os, 'read', return_value=value):
                        with self.assertRaisesRegex(OSError, 'impossible bytes'):
                            module._snapshot_regular(path)

    @unittest.skipUnless(hasattr(os, 'O_NOFOLLOW'), 'POSIX no-follow snapshot required')
    def test_snapshot_bytes_subclass_with_forged_length_is_refused(self):
        class Spoofed(bytes):
            def __len__(self):
                raise RuntimeError('spoofed buffer length')
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'sample'
            path.write_bytes(b'ABC')
            with patch.object(module.os, 'read', return_value=Spoofed(b'ABC')):
                with self.assertRaisesRegex(OSError, 'impossible bytes'):
                    module._snapshot_regular(path)

    @unittest.skipUnless(hasattr(os, 'O_NOFOLLOW'), 'POSIX no-follow snapshot required')
    def test_snapshot_oversized_read_result_is_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'sample'
            path.write_bytes(b'ABC')
            with patch.object(module.os, 'read', return_value=b'ABCDE'):
                with self.assertRaisesRegex(OSError, 'impossible bytes'):
                    module._snapshot_regular(path)

    @unittest.skipUnless(hasattr(os, 'O_NOFOLLOW'), 'POSIX no-follow snapshot required')
    def test_normal_public_snapshot_bytes_and_inode_still_work(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'sample'
            path.write_bytes(b'ABC')
            identity, data = module._snapshot_regular(path)
            self.assertEqual(data, b'ABC')
            self.assertEqual(identity, (path.stat().st_dev, path.stat().st_ino))


    def test_persistent_sibling_cannot_claim_isolated_negative_with_modified_source(self):
        name = named(b'unexpected-public-sibling')
        raw = ev(wd=10, mask=module.IN_CREATE, data=name)
        verdict = module._evaluate(
            b'public-before', b'public-after', raw, 9, True, False,
            directory_watch=10, directory_inventory_ok=False,
            directory_inventory_names=('sample', 'unexpected-public-sibling'),
            sibling_snapshot_stable=True, sibling_negative=True)
        self.assertFalse(verdict['observed_checks']['final_digest_equal'])
        self.assertFalse(verdict['observed_checks']['sibling_creation_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')

    def test_persistent_sibling_cannot_claim_isolated_negative_after_source_inode_swap(self):
        name = named(b'unexpected-public-sibling')
        raw = ev(wd=10, mask=module.IN_CREATE, data=name)
        verdict = module._evaluate(
            b'public', b'public', raw, 9, True, False, inode_stable=False,
            directory_watch=10, directory_inventory_ok=False,
            directory_inventory_names=('sample', 'unexpected-public-sibling'),
            sibling_snapshot_stable=True, sibling_negative=True)
        self.assertFalse(verdict['observed_checks']['watched_inode_matches_final_path'])
        self.assertFalse(verdict['observed_checks']['sibling_creation_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')

    def test_transient_sibling_cannot_claim_isolated_negative_with_modified_source(self):
        name = named(b'temporary-public-sibling')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=name)
               + ev(wd=10, mask=module.IN_DELETE, data=name))
        verdict = module._evaluate(
            b'public-before', b'public-after', raw, 9, True, False,
            directory_watch=10, directory_inventory_ok=True,
            directory_inventory_names=('sample',),
            transient_midpoint_verified=True, transient_sibling_negative=True)
        self.assertFalse(verdict['observed_checks']['final_digest_equal'])
        self.assertFalse(verdict['observed_checks']['transient_directory_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')

    def test_transient_sibling_cannot_claim_isolated_negative_after_source_inode_swap(self):
        name = named(b'temporary-public-sibling')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=name)
               + ev(wd=10, mask=module.IN_DELETE, data=name))
        verdict = module._evaluate(
            b'public', b'public', raw, 9, True, False, inode_stable=False,
            directory_watch=10, directory_inventory_ok=True,
            directory_inventory_names=('sample',),
            transient_midpoint_verified=True, transient_sibling_negative=True)
        self.assertFalse(verdict['observed_checks']['watched_inode_matches_final_path'])
        self.assertFalse(verdict['observed_checks']['transient_directory_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')


    def test_evaluator_rejects_nonboolean_negative_control_inputs(self):
        for invalid in (None, 0, 1, "true", "", [], {}, 1.0, float('nan')):
            for index in range(4):
                with self.subTest(value=repr(invalid), index=index):
                    flags = [False, False, False, False]
                    flags[index] = invalid
                    result = module._evaluate(
                        b'public', b'public', b'', 9, True, flags[0],
                        replacement_negative=flags[1],
                        sibling_negative=flags[2],
                        transient_sibling_negative=flags[3],
                        directory_watch=10, directory_inventory_names=('sample',))
                    self.assertEqual(result['status'], 'BLOCKED')
                    self.assertIn('disposable evaluator negative controls must be booleans',
                                  result['findings'])
                    self.assertFalse(result['can_authorize_dispatch'])

    def test_evaluator_rejects_all_pairwise_conflicting_negative_modes(self):
        for a in range(4):
            for b in range(a + 1, 4):
                flags = [False, False, False, False]
                flags[a] = flags[b] = True
                result = module._evaluate(
                    b'public', b'public', b'', 9, True, flags[0],
                    replacement_negative=flags[1], sibling_negative=flags[2],
                    transient_sibling_negative=flags[3],
                    directory_watch=10, directory_inventory_names=('sample',))
                self.assertEqual(result['status'], 'BLOCKED')
                self.assertIn('conflicting synthetic evaluator negative controls',
                              result['findings'])
                self.assertFalse(result['can_authorize_dispatch'])

    def test_evaluator_mode_gate_rejects_before_stream_parser(self):
        with patch.object(module, '_classify_stream') as classifier:
            result = module._evaluate(b'public', b'public', b'', 9, True, False,
                                      replacement_negative=True, sibling_negative=True,
                                      directory_watch=10)
            classifier.assert_not_called()
        self.assertEqual(result['status'], 'BLOCKED')

    def test_evaluator_valid_mode_free_path_remains_locally_unverified(self):
        result = module._evaluate(b'public', b'public', b'', 9, True, False,
                                  directory_watch=10, directory_inventory_names=('sample',))
        self.assertEqual(result['status'], 'LOCAL_DISPOSABLE_WITNESS_UNVERIFIED')
        self.assertFalse(result['can_authorize_dispatch'])
        self.assertFalse(result['independent_os_proof_verified'])


    def test_disposable_collector_never_registers_stdio_fds(self):
        with patch.object(module.select, 'poll') as factory:
            for fd in (0, 1, 2, -1, None, True):
                with self.subTest(fd=repr(fd)):
                    with self.assertRaisesRegex(OSError, 'nonstdio integer fd'):
                        module._read_pending(fd)
            factory.assert_not_called()

    def test_inotify_init1_stdio_fd_is_closed_before_watches(self):
        class CFunction:
            def __init__(self, value):
                self.value = value
                self.argtypes = None
                self.restype = None
                self.calls = 0
            def __call__(self, *_args):
                self.calls += 1
                return self.value
        for fd in (0, 1, 2):
            with self.subTest(fd=fd):
                init = CFunction(fd)
                add_watch = CFunction(9)
                class FakeLib:
                    inotify_init1 = init
                    inotify_add_watch = add_watch
                with patch.object(module.ctypes, 'CDLL', return_value=FakeLib()):
                    with patch.object(module.os, 'close') as close:
                        with self.assertRaisesRegex(OSError, 'standard descriptor'):
                            module._start_watch(Path('/tmp/public-fake-only'))
                        close.assert_called_once_with(fd)
                self.assertEqual(add_watch.calls, 0)

    def test_disposable_watcher_nonstdio_fd_still_registers_two_watches(self):
        class CFunction:
            def __init__(self, values):
                self.values = iter(values)
                self.argtypes = None
                self.restype = None
                self.calls = 0
            def __call__(self, *_args):
                self.calls += 1
                return next(self.values)
        init = CFunction([17])
        add = CFunction([9, 10])
        class FakeLib:
            inotify_init1 = init
            inotify_add_watch = add
        with patch.object(module.ctypes, 'CDLL', return_value=FakeLib()):
            result = module._start_watch(Path('/tmp/public-fake-only'))
        self.assertEqual(result, (17, 9, 10))
        self.assertEqual(add.calls, 2)

    def test_disposable_collector_exact_regular_fd_retains_quiet_poll(self):
        class Quiet:
            def register(self, *_args): pass
            def poll(self, _timeout): return []
        with patch.object(module.select, 'poll', return_value=Quiet()):
            with patch.object(module.os, 'read') as read:
                self.assertEqual(module._read_pending(17), b'')
                read.assert_not_called()


    def test_duplicate_same_directory_create_is_incomplete_stream(self):
        name = named(b'new-public-dir')
        raw = ev(wd=10, mask=module.IN_CREATE | module.IN_ISDIR, data=name) * 2
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertFalse(parsed['well_formed'])
        self.assertEqual(parsed['directory_changes'], 2)

    def test_file_create_followed_by_directory_create_same_name_is_incomplete(self):
        name = named(b'same-name')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=name)
               + ev(wd=10, mask=module.IN_CREATE | module.IN_ISDIR, data=name))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertFalse(parsed['well_formed'])

    def test_directory_create_followed_by_file_create_same_name_is_incomplete(self):
        name = named(b'same-name')
        raw = (ev(wd=10, mask=module.IN_CREATE | module.IN_ISDIR, data=name)
               + ev(wd=10, mask=module.IN_CREATE, data=name))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertFalse(parsed['well_formed'])

    def test_same_name_directory_delete_then_file_create_is_coherent(self):
        name = named(b'same-name')
        raw = (ev(wd=10, mask=module.IN_CREATE | module.IN_ISDIR, data=name)
               + ev(wd=10, mask=module.IN_DELETE | module.IN_ISDIR, data=name)
               + ev(wd=10, mask=module.IN_CREATE, data=name))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['directory_changes'], 3)

    def test_move_into_known_basename_blocks_unseparated_new_create(self):
        name = named(b'same-name')
        raw = (ev(wd=10, mask=module.IN_MOVED_TO, data=name, cookie=77)
               + ev(wd=10, mask=module.IN_CREATE, data=name))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertFalse(parsed['well_formed'])


    def test_created_file_cannot_be_removed_as_same_name_directory(self):
        name = named(b'public-child')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=name)
               + ev(wd=10, mask=module.IN_DELETE | module.IN_ISDIR, data=name))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertFalse(parsed['well_formed'])
        self.assertEqual(parsed['directory_changes'], 2)

    def test_created_directory_cannot_be_removed_as_same_name_file(self):
        name = named(b'public-child')
        raw = (ev(wd=10, mask=module.IN_CREATE | module.IN_ISDIR, data=name)
               + ev(wd=10, mask=module.IN_DELETE, data=name))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertFalse(parsed['well_formed'])

    def test_created_child_moved_out_with_wrong_kind_is_malformed(self):
        name = named(b'public-child')
        for first, second in (
            (module.IN_CREATE, module.IN_MOVED_FROM | module.IN_ISDIR),
            (module.IN_CREATE | module.IN_ISDIR, module.IN_MOVED_FROM),
        ):
            with self.subTest(first=first, second=second):
                raw = (ev(wd=10, mask=first, data=name)
                       + ev(wd=10, mask=second, data=name, cookie=10))
                parsed = module._classify_stream(raw, 9, directory_watch=10)
                self.assertFalse(parsed['well_formed'])

    def test_matching_file_and_directory_kind_deletions_remain_valid(self):
        name = named(b'public-child')
        for isdir in (0, module.IN_ISDIR):
            with self.subTest(isdir=isdir):
                raw = (ev(wd=10, mask=module.IN_CREATE | isdir, data=name)
                       + ev(wd=10, mask=module.IN_DELETE | isdir, data=name))
                parsed = module._classify_stream(raw, 9, directory_watch=10)
                self.assertTrue(parsed['well_formed'])

    def test_move_in_after_observed_move_out_can_change_entry_kind(self):
        name = named(b'public-child')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=name)
               + ev(wd=10, mask=module.IN_MOVED_FROM, data=name, cookie=41)
               + ev(wd=10, mask=module.IN_MOVED_TO | module.IN_ISDIR, data=name, cookie=42)
               + ev(wd=10, mask=module.IN_DELETE | module.IN_ISDIR, data=name))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['directory_changes'], 4)

    def test_preexisting_child_delete_with_untracked_kind_is_structurally_valid(self):
        name = named(b'preexisting')
        raw = ev(wd=10, mask=module.IN_DELETE | module.IN_ISDIR, data=name)
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['directory_changes'], 1)


    def test_moved_out_child_cannot_be_deleted_without_reentry(self):
        name = named(b'public-child')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=name)
               + ev(wd=10, mask=module.IN_MOVED_FROM, data=name, cookie=20)
               + ev(wd=10, mask=module.IN_DELETE, data=name))
        observed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertFalse(observed['well_formed'])
        verdict = module._evaluate(b'a', b'a', raw, 9, True, False,
                                   directory_watch=10, directory_inventory_names=('sample',))
        self.assertEqual(verdict['status'], 'BLOCKED')
        self.assertFalse(verdict['observed_checks']['event_stream_complete'])

    def test_deleted_child_cannot_move_out_without_reentry(self):
        name = named(b'public-child')
        raw = (ev(wd=10, mask=module.IN_DELETE, data=name)
               + ev(wd=10, mask=module.IN_MOVED_FROM, data=name, cookie=20))
        self.assertFalse(module._classify_stream(raw, 9, directory_watch=10)['well_formed'])

    def test_two_same_name_move_outs_without_reentry_are_incomplete(self):
        name = named(b'public-child')
        raw = (ev(wd=10, mask=module.IN_MOVED_FROM, data=name, cookie=20)
               + ev(wd=10, mask=module.IN_MOVED_FROM, data=name, cookie=21))
        self.assertFalse(module._classify_stream(raw, 9, directory_watch=10)['well_formed'])

    def test_move_out_move_in_delete_same_name_is_complete(self):
        name = named(b'public-child')
        raw = (ev(wd=10, mask=module.IN_MOVED_FROM, data=name, cookie=20)
               + ev(wd=10, mask=module.IN_MOVED_TO, data=name, cookie=21)
               + ev(wd=10, mask=module.IN_DELETE, data=name))
        observed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(observed['well_formed'])
        self.assertEqual(observed['directory_changes'], 3)

    def test_move_out_create_delete_same_name_is_complete(self):
        name = named(b'public-child')
        raw = (ev(wd=10, mask=module.IN_MOVED_FROM, data=name, cookie=20)
               + ev(wd=10, mask=module.IN_CREATE, data=name)
               + ev(wd=10, mask=module.IN_DELETE, data=name))
        observed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(observed['well_formed'])
        self.assertEqual(observed['transient_create_delete_pairs'], 1)


    def test_transient_control_rejects_surviving_unrelated_observed_child(self):
        target = named(b'temporary-public-sibling')
        other = named(b'unremoved-public-child')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=target)
               + ev(wd=10, mask=module.IN_CREATE, data=other)
               + ev(wd=10, mask=module.IN_DELETE, data=target))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['pending_new_child_names'], (b'unremoved-public-child',))
        verdict = module._evaluate(
            b'public', b'public', raw, 9, True, False,
            directory_watch=10, directory_inventory_ok=True,
            directory_inventory_names=('sample',),
            transient_midpoint_verified=True, transient_sibling_negative=True)
        self.assertFalse(verdict['observed_checks']['transient_directory_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')

    def test_persistent_control_rejects_surviving_unrelated_observed_child(self):
        target = named(b'unexpected-public-sibling')
        other = named(b'other-public-child')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=target)
               + ev(wd=10, mask=module.IN_CREATE, data=other))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertEqual(parsed['pending_new_child_names'],
                         (b'other-public-child', b'unexpected-public-sibling'))
        verdict = module._evaluate(
            b'public', b'public', raw, 9, True, False,
            directory_watch=10, directory_inventory_ok=False,
            directory_inventory_names=('sample', 'unexpected-public-sibling'),
            sibling_snapshot_stable=True, sibling_negative=True)
        self.assertFalse(verdict['observed_checks']['sibling_creation_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')

    def test_transient_control_allows_fully_removed_unrelated_observed_child(self):
        target = named(b'temporary-public-sibling')
        other = named(b'other-public-child')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=target)
               + ev(wd=10, mask=module.IN_CREATE, data=other)
               + ev(wd=10, mask=module.IN_DELETE, data=target)
               + ev(wd=10, mask=module.IN_DELETE, data=other))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['pending_new_child_names'], ())
        verdict = module._evaluate(
            b'public', b'public', raw, 9, True, False,
            directory_watch=10, directory_inventory_ok=True,
            directory_inventory_names=('sample',),
            transient_midpoint_verified=True, transient_sibling_negative=True)
        self.assertTrue(verdict['observed_checks']['transient_directory_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')

    def test_sibling_control_single_expected_child_is_only_pending_name(self):
        name = named(b'unexpected-public-sibling')
        parsed = module._classify_stream(
            ev(wd=10, mask=module.IN_CREATE, data=name), 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['pending_new_child_names'], (b'unexpected-public-sibling',))

    def test_malformed_early_stream_has_no_observed_surviving_children(self):
        for data, wd, directory in (
            ('wrong-buffer', 9, 10),
            (b'', -1, 10),
            (b'', 9, 9),
        ):
            with self.subTest(wd=wd, directory=directory):
                parsed = module._classify_stream(data, wd, directory_watch=directory)
                self.assertFalse(parsed['well_formed'])
                self.assertEqual(parsed['pending_new_child_names'], ())


    def test_quiet_buffer_without_directory_watch_is_not_complete(self):
        result = module._evaluate(
            b'public', b'public', b'', 9, True, False,
            directory_watch=None, directory_inventory_names=('sample',))
        self.assertFalse(result['observed_checks']['both_watches_identified'])
        self.assertFalse(result['observed_checks']['event_stream_complete'])
        self.assertEqual(result['status'], 'BLOCKED')

    def test_two_source_modifications_without_directory_watch_are_not_full_control(self):
        raw = ev(wd=9, mask=module.IN_MODIFY) * 2
        result = module._evaluate(
            b'public', b'public', raw, 9, True, True,
            directory_watch=None, midpoint_snapshot_matches_expected=True)
        self.assertFalse(result['observed_checks']['both_watches_identified'])
        self.assertFalse(result['observed_checks']['event_stream_complete'])
        self.assertFalse(result['observed_checks']['negative_control_detected'])
        self.assertEqual(result['status'], 'BLOCKED')

    def test_aliased_watch_descriptors_do_not_claim_complete_stream(self):
        result = module._evaluate(
            b'public', b'public', b'', 9, True, False,
            directory_watch=9, directory_inventory_names=('sample',))
        self.assertFalse(result['observed_checks']['both_watches_identified'])
        self.assertFalse(result['observed_checks']['event_stream_complete'])
        self.assertEqual(result['status'], 'BLOCKED')

    def test_two_distinct_valid_watches_retain_quiet_local_unverified(self):
        result = module._evaluate(
            b'public', b'public', b'', 9, True, False,
            directory_watch=10, directory_inventory_names=('sample',))
        self.assertTrue(result['observed_checks']['both_watches_identified'])
        self.assertTrue(result['observed_checks']['event_stream_complete'])
        self.assertEqual(result['status'], 'LOCAL_DISPOSABLE_WITNESS_UNVERIFIED')
        self.assertFalse(result['can_authorize_dispatch'])


    def test_source_write_revert_with_unrelated_directory_creation_is_not_isolated(self):
        raw = (ev(wd=9, mask=module.IN_MODIFY) * 2
               + ev(wd=10, mask=module.IN_CREATE, data=named(b'unrelated-child')))
        verdict = module._evaluate(
            b'public', b'public', raw, 9, True, True,
            directory_watch=10, directory_inventory_ok=False,
            directory_inventory_names=('sample', 'unrelated-child'),
            midpoint_snapshot_matches_expected=True)
        self.assertTrue(verdict['observed_checks']['midpoint_source_snapshot_matches_expected'])
        self.assertFalse(verdict['observed_checks']['no_directory_entry_mutations'])
        self.assertFalse(verdict['observed_checks']['negative_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')

    def test_write_revert_with_unrelated_transient_directory_pair_is_not_isolated(self):
        name = named(b'other-child')
        raw = (ev(wd=9, mask=module.IN_MODIFY) * 2
               + ev(wd=10, mask=module.IN_CREATE, data=name)
               + ev(wd=10, mask=module.IN_DELETE, data=name))
        verdict = module._evaluate(
            b'public', b'public', raw, 9, True, True,
            directory_watch=10, directory_inventory_ok=True,
            directory_inventory_names=('sample',),
            midpoint_snapshot_matches_expected=True)
        self.assertTrue(verdict['observed_checks']['event_stream_complete'])
        self.assertFalse(verdict['observed_checks']['no_directory_entry_mutations'])
        self.assertFalse(verdict['observed_checks']['negative_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')

    def test_write_revert_requires_actual_typed_final_original_inventory(self):
        raw = ev(wd=9, mask=module.IN_MODIFY) * 2
        for names in (None, [], ('sample', 'unrelated'), ('other',), 'sample'):
            with self.subTest(names=repr(names)):
                verdict = module._evaluate(
                    b'public', b'public', raw, 9, True, True,
                    directory_watch=10, directory_inventory_ok=True,
                    directory_inventory_names=names,
                    midpoint_snapshot_matches_expected=True)
                self.assertFalse(verdict['observed_checks']['negative_control_detected'])
                self.assertEqual(verdict['status'], 'BLOCKED')

    def test_write_revert_original_directory_and_midpoint_preserve_control(self):
        raw = ev(wd=9, mask=module.IN_MODIFY) * 2
        verdict = module._evaluate(
            b'public', b'public', raw, 9, True, True,
            directory_watch=10, directory_inventory_ok=True,
            directory_inventory_names=('sample',),
            midpoint_snapshot_matches_expected=True)
        self.assertTrue(verdict['observed_checks']['negative_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')
        self.assertFalse(verdict['can_authorize_dispatch'])


    def test_persistent_directory_only_negative_refuses_source_modify_event(self):
        raw = (ev(wd=10, mask=module.IN_CREATE,
                  data=named(b'unexpected-public-sibling'))
               + ev(wd=9, mask=module.IN_MODIFY))
        verdict = module._evaluate(
            b'public', b'public', raw, 9, True, False,
            directory_watch=10, directory_inventory_ok=False,
            directory_inventory_names=('sample', 'unexpected-public-sibling'),
            sibling_snapshot_stable=True, sibling_negative=True)
        self.assertTrue(verdict['observed_checks']['final_digest_equal'])
        self.assertFalse(verdict['observed_checks']['sibling_creation_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')

    def test_persistent_directory_only_negative_refuses_source_close_write_event(self):
        raw = (ev(wd=10, mask=module.IN_CREATE,
                  data=named(b'unexpected-public-sibling'))
               + ev(wd=9, mask=module.IN_CLOSE_WRITE))
        verdict = module._evaluate(
            b'public', b'public', raw, 9, True, False,
            directory_watch=10, directory_inventory_ok=False,
            directory_inventory_names=('sample', 'unexpected-public-sibling'),
            sibling_snapshot_stable=True, sibling_negative=True)
        self.assertFalse(verdict['observed_checks']['sibling_creation_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')

    def test_transient_directory_only_negative_refuses_source_modify_event(self):
        name = named(b'temporary-public-sibling')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=name)
               + ev(wd=9, mask=module.IN_MODIFY)
               + ev(wd=10, mask=module.IN_DELETE, data=name))
        verdict = module._evaluate(
            b'public', b'public', raw, 9, True, False,
            directory_watch=10, directory_inventory_ok=True,
            directory_inventory_names=('sample',),
            transient_midpoint_verified=True, transient_sibling_negative=True)
        self.assertFalse(verdict['observed_checks']['transient_directory_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')

    def test_transient_directory_only_negative_allows_sibling_close_write(self):
        name = named(b'temporary-public-sibling')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=name)
               + ev(wd=10, mask=module.IN_CLOSE_WRITE, data=name)
               + ev(wd=10, mask=module.IN_DELETE, data=name))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['source_content_write_events'], 0)
        self.assertGreater(parsed['write_events'], 0)
        verdict = module._evaluate(
            b'public', b'public', raw, 9, True, False,
            directory_watch=10, directory_inventory_ok=True,
            directory_inventory_names=('sample',),
            transient_midpoint_verified=True, transient_sibling_negative=True)
        self.assertTrue(verdict['observed_checks']['transient_directory_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')


    def test_occupied_regular_child_cannot_directly_move_in_directory_same_name(self):
        name = named(b'public-child')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=name)
               + ev(wd=10, mask=module.IN_MOVED_TO | module.IN_ISDIR, data=name, cookie=91))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertFalse(parsed['well_formed'])
        verdict = module._evaluate(b'a', b'a', raw, 9, True, False,
                                   directory_watch=10, directory_inventory_names=('sample',))
        self.assertFalse(verdict['observed_checks']['event_stream_complete'])
        self.assertEqual(verdict['status'], 'BLOCKED')

    def test_occupied_directory_cannot_directly_move_in_file_same_name(self):
        name = named(b'public-child')
        raw = (ev(wd=10, mask=module.IN_CREATE | module.IN_ISDIR, data=name)
               + ev(wd=10, mask=module.IN_MOVED_TO, data=name, cookie=91))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertFalse(parsed['well_formed'])

    def test_move_in_over_known_same_kind_target_remains_coherent(self):
        name = named(b'public-child')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=name)
               + ev(wd=10, mask=module.IN_MOVED_TO, data=name, cookie=91)
               + ev(wd=10, mask=module.IN_DELETE, data=name))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['directory_changes'], 3)

    def test_kind_change_after_move_out_remains_coherent(self):
        name = named(b'public-child')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=name)
               + ev(wd=10, mask=module.IN_MOVED_FROM, data=name, cookie=91)
               + ev(wd=10, mask=module.IN_MOVED_TO | module.IN_ISDIR, data=name, cookie=92)
               + ev(wd=10, mask=module.IN_DELETE | module.IN_ISDIR, data=name))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['directory_changes'], 4)


    def test_hostile_inventory_tuple_element_cannot_fake_original_leaf(self):
        class AlwaysEqual:
            def __eq__(self, _other):
                return True
        self.assertTrue((AlwaysEqual(),) == ('sample',))
        verdict = module._evaluate(
            b'public', b'public', b'', 9, True, False,
            directory_watch=10, directory_inventory_ok=True,
            directory_inventory_names=(AlwaysEqual(),))
        self.assertFalse(verdict['observed_checks']['no_directory_entry_mutations'])
        self.assertEqual(verdict['status'], 'BLOCKED')
        self.assertFalse(verdict['can_authorize_dispatch'])

    def test_str_subclass_cannot_impersonate_original_leaf(self):
        class ForgedName(str):
            def __eq__(self, _other):
                return True
        self.assertTrue((ForgedName('malicious'),) == ('sample',))
        verdict = module._evaluate(
            b'public', b'public', b'', 9, True, False,
            directory_watch=10, directory_inventory_ok=True,
            directory_inventory_names=(ForgedName('malicious'),))
        self.assertFalse(verdict['observed_checks']['no_directory_entry_mutations'])
        self.assertEqual(verdict['status'], 'BLOCKED')

    def test_hostile_expected_sibling_inventory_member_cannot_fake_witness(self):
        class ForgedName:
            def __eq__(self, _other):
                return True
        forged = ('sample', ForgedName())
        self.assertTrue(forged == ('sample', 'unexpected-public-sibling'))
        raw = ev(wd=10, mask=module.IN_CREATE,
                 data=named(b'unexpected-public-sibling'))
        verdict = module._evaluate(
            b'public', b'public', raw, 9, True, False,
            directory_watch=10, directory_inventory_ok=False,
            directory_inventory_names=forged, sibling_snapshot_stable=True,
            sibling_negative=True)
        self.assertFalse(verdict['observed_checks']['sibling_creation_control_detected'])
        self.assertEqual(verdict['status'], 'BLOCKED')

    def test_plain_filename_tuple_preserves_positive_local_unverified_control(self):
        verdict = module._evaluate(
            b'public', b'public', b'', 9, True, False,
            directory_watch=10, directory_inventory_ok=True,
            directory_inventory_names=('sample',))
        self.assertTrue(verdict['observed_checks']['no_directory_entry_mutations'])
        self.assertEqual(verdict['status'], 'LOCAL_DISPOSABLE_WITNESS_UNVERIFIED')
        self.assertFalse(verdict['independent_os_proof_verified'])


    def test_regular_file_pair_counter_includes_unrelated_control_child(self):
        target = named(b'temporary-public-sibling')
        other = named(b'public-unrelated')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=target)
               + ev(wd=10, mask=module.IN_CREATE, data=other)
               + ev(wd=10, mask=module.IN_DELETE, data=target)
               + ev(wd=10, mask=module.IN_DELETE, data=other))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['transient_create_delete_pairs'], 2)
        self.assertEqual(parsed['expected_transient_pairs'], 1)
        self.assertEqual(parsed['pending_new_child_names'], ())

    def test_collector_invalid_fd_error_message_matches_stdin_safety_contract(self):
        for invalid_fd in (None, True, -1, 0, 1, 2, '12'):
            with self.subTest(fd=repr(invalid_fd)):
                with patch.object(module.select, 'poll') as poll_factory:
                    with self.assertRaisesRegex(OSError, 'requires a nonstdio integer fd'):
                        module._read_pending(invalid_fd)
                    poll_factory.assert_not_called()


    def test_truncated_local_event_buffer_cannot_claim_no_writes(self):
        result = module._evaluate(
            b'public', b'public', b'\x00' * 7, 9, True, False,
            directory_watch=10, directory_inventory_names=('sample',))
        self.assertFalse(result['observed_checks']['event_stream_complete'])
        self.assertFalse(result['observed_checks']['no_observed_writes'])
        self.assertEqual(result['status'], 'BLOCKED')

    def test_missing_parent_watch_cannot_claim_no_writes(self):
        result = module._evaluate(
            b'public', b'public', b'', 9, True, False,
            directory_watch=None, directory_inventory_names=('sample',))
        self.assertFalse(result['observed_checks']['both_watches_identified'])
        self.assertFalse(result['observed_checks']['no_observed_writes'])
        self.assertEqual(result['status'], 'BLOCKED')

    def test_dead_watcher_cannot_claim_unchanged_write_history(self):
        result = module._evaluate(
            b'public', b'public', b'', 9, False, False,
            directory_watch=10, directory_inventory_names=('sample',))
        self.assertFalse(result['observed_checks']['event_stream_complete'])
        self.assertFalse(result['observed_checks']['no_observed_writes'])
        self.assertEqual(result['status'], 'BLOCKED')

    def test_valid_quiet_dual_watch_buffer_still_reports_no_observed_writes(self):
        result = module._evaluate(
            b'public', b'public', b'', 9, True, False,
            directory_watch=10, directory_inventory_ok=True,
            directory_inventory_names=('sample',))
        self.assertTrue(result['observed_checks']['event_stream_complete'])
        self.assertTrue(result['observed_checks']['no_observed_writes'])
        self.assertEqual(result['status'], 'LOCAL_DISPOSABLE_WITNESS_UNVERIFIED')
        self.assertFalse(result['can_authorize_dispatch'])


    def test_snapshot_rejects_fd_allocated_on_stdio_before_fstat(self):
        for fd in (0, 1, 2):
            with self.subTest(fd=fd):
                with patch.object(module.os, 'open', return_value=fd):
                    with patch.object(module.os, 'close') as closed:
                        with patch.object(module.os, 'fstat') as stat_call:
                            with self.assertRaisesRegex(OSError, 'standard descriptor'):
                                module._snapshot_regular(Path('/tmp/public-synthetic'))
                            closed.assert_called_once_with(fd)
                            stat_call.assert_not_called()

    def test_snapshot_rejects_malformed_open_fd_before_fstat(self):
        for fd in (None, False, -1, '17', 17.0):
            with self.subTest(fd=repr(fd)):
                with patch.object(module.os, 'open', return_value=fd):
                    with patch.object(module.os, 'close') as close:
                        with patch.object(module.os, 'fstat') as stat_call:
                            with self.assertRaisesRegex(OSError, 'valid integer fd'):
                                module._snapshot_regular(Path('/tmp/public-synthetic'))
                            close.assert_not_called()
                            stat_call.assert_not_called()

    @unittest.skipUnless(hasattr(os, 'O_NOFOLLOW'), 'POSIX no-follow snapshot required')
    def test_generated_public_snapshot_uses_nonstdio_fd(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'sample'
            path.write_bytes(b'PUBLIC-DATA')
            inode, content = module._snapshot_regular(path)
            self.assertIs(type(inode), tuple)
            self.assertEqual(content, b'PUBLIC-DATA')


    def test_inotify_init_rejects_noninteger_ctypes_result_before_registering(self):
        class Callable:
            def __init__(self, result): self.result = result
            def __call__(self, *_args): return self.result
        for invalid in (None, True, '17', 17.0):
            with self.subTest(value=repr(invalid)):
                class FakeLib:
                    inotify_init1 = Callable(invalid)
                    inotify_add_watch = Callable(9)
                with patch.object(module.ctypes, 'CDLL', return_value=FakeLib()):
                    with patch.object(module.os, 'close') as close:
                        with self.assertRaisesRegex(OSError, 'noninteger descriptor'):
                            module._start_watch(Path('/tmp/public-fake-only'))
                        close.assert_not_called()

    def test_inotify_first_watch_rejects_noninteger_or_impossible_id(self):
        class Callable:
            def __init__(self, result): self.result = result; self.calls = 0
            def __call__(self, *_args): self.calls += 1; return self.result
        for invalid in (None, True, '9', 9.0, (1 << 31)):
            with self.subTest(value=repr(invalid)):
                add = Callable(invalid)
                class FakeLib:
                    inotify_init1 = Callable(17)
                    inotify_add_watch = add
                with patch.object(module.ctypes, 'CDLL', return_value=FakeLib()):
                    with patch.object(module.os, 'close') as close:
                        with self.assertRaisesRegex(OSError, 'inotify_add_watch failed'):
                            module._start_watch(Path('/tmp/public-fake-only'))
                        close.assert_called_once_with(17)
                        self.assertEqual(add.calls, 1)

    def test_inotify_directory_watch_rejects_noninteger_or_impossible_id(self):
        class Callable:
            def __init__(self, values): self.values = iter(values)
            def __call__(self, *_args): return next(self.values)
        for invalid in (None, False, '10', 10.0, (1 << 31), 9):
            with self.subTest(value=repr(invalid)):
                class FakeLib:
                    inotify_init1 = Callable([17])
                    inotify_add_watch = Callable([9, invalid])
                with patch.object(module.ctypes, 'CDLL', return_value=FakeLib()):
                    with patch.object(module.os, 'close') as close:
                        with self.assertRaisesRegex(OSError, 'directory inotify_add_watch failed'):
                            module._start_watch(Path('/tmp/public-fake-only'))
                        close.assert_called_once_with(17)

    def test_inotify_ctypes_plain_integer_ids_keep_normal_two_watch_result(self):
        class Callable:
            def __init__(self, values): self.values = iter(values)
            def __call__(self, *_args): return next(self.values)
        class FakeLib:
            inotify_init1 = Callable([17])
            inotify_add_watch = Callable([9, 10])
        with patch.object(module.ctypes, 'CDLL', return_value=FakeLib()):
            self.assertEqual(module._start_watch(Path('/tmp/public-fake-only')),
                             (17, 9, 10))


    def test_mode_free_quiet_receipt_does_not_claim_any_unexecuted_control(self):
        result = module._evaluate(
            b'public', b'public', b'', 9, True, False,
            directory_watch=10, directory_inventory_names=('sample',))
        for key in ('negative_control_detected',
                    'midpoint_source_snapshot_matches_expected',
                    'sibling_creation_control_detected',
                    'transient_midpoint_regular_file_verified',
                    'transient_directory_control_detected'):
            with self.subTest(key=key):
                self.assertFalse(result['observed_checks'][key])
                self.assertFalse(any(key in finding for finding in result['findings']))
        self.assertEqual(result['status'], 'LOCAL_DISPOSABLE_WITNESS_UNVERIFIED')
        self.assertFalse(result['can_authorize_dispatch'])

    def test_source_write_control_does_not_claim_inactive_directory_controls(self):
        result = module._evaluate(
            b'public', b'public', ev(wd=9, mask=module.IN_MODIFY) * 2,
            9, True, True, directory_watch=10,
            directory_inventory_names=('sample',),
            midpoint_snapshot_matches_expected=True)
        self.assertTrue(result['observed_checks']['negative_control_detected'])
        self.assertFalse(result['observed_checks']['sibling_creation_control_detected'])
        self.assertFalse(result['observed_checks']['transient_directory_control_detected'])
        self.assertEqual(result['status'], 'BLOCKED')

    def test_persistent_sibling_control_does_not_claim_other_modes(self):
        raw = ev(wd=10, mask=module.IN_CREATE, data=named(b'unexpected-public-sibling'))
        result = module._evaluate(
            b'public', b'public', raw, 9, True, False,
            directory_watch=10, directory_inventory_ok=False,
            directory_inventory_names=('sample', 'unexpected-public-sibling'),
            sibling_snapshot_stable=True, sibling_negative=True)
        self.assertTrue(result['observed_checks']['sibling_creation_control_detected'])
        self.assertFalse(result['observed_checks']['negative_control_detected'])
        self.assertFalse(result['observed_checks']['transient_directory_control_detected'])
        self.assertEqual(result['status'], 'BLOCKED')

    def test_transient_sibling_control_does_not_claim_inactive_persistent(self):
        name = named(b'temporary-public-sibling')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=name)
               + ev(wd=10, mask=module.IN_DELETE, data=name))
        result = module._evaluate(
            b'public', b'public', raw, 9, True, False,
            directory_watch=10, directory_inventory_names=('sample',),
            transient_midpoint_verified=True, transient_sibling_negative=True)
        self.assertTrue(result['observed_checks']['transient_midpoint_regular_file_verified'])
        self.assertTrue(result['observed_checks']['transient_directory_control_detected'])
        self.assertFalse(result['observed_checks']['sibling_creation_control_detected'])
        self.assertFalse(result['observed_checks']['negative_control_detected'])
        self.assertEqual(result['status'], 'BLOCKED')

    def test_replacement_control_does_not_claim_any_other_negative(self):
        result = module._evaluate(
            b'public', b'public', b'', 9, True, False,
            inode_stable=False, replacement_negative=True,
            directory_watch=10, directory_inventory_names=('sample',))
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertFalse(result['observed_checks']['negative_control_detected'])
        self.assertFalse(result['observed_checks']['sibling_creation_control_detected'])
        self.assertFalse(result['observed_checks']['transient_directory_control_detected'])
        self.assertFalse(result['can_authorize_dispatch'])


    def test_directory_only_persistent_negative_refuses_source_attrib(self):
        raw = (ev(wd=10, mask=module.IN_CREATE,
                  data=named(b'unexpected-public-sibling'))
               + ev(wd=9, mask=module.IN_ATTRIB))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['source_attribute_events'], 1)
        result = module._evaluate(
            b'public', b'public', raw, 9, True, False,
            directory_watch=10, directory_inventory_ok=False,
            directory_inventory_names=('sample', 'unexpected-public-sibling'),
            sibling_snapshot_stable=True, sibling_negative=True)
        self.assertFalse(result['observed_checks']['sibling_creation_control_detected'])
        self.assertEqual(result['status'], 'BLOCKED')

    def test_directory_only_transient_negative_refuses_source_attrib(self):
        target = named(b'temporary-public-sibling')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=target)
               + ev(wd=9, mask=module.IN_ATTRIB)
               + ev(wd=10, mask=module.IN_DELETE, data=target))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['source_attribute_events'], 1)
        result = module._evaluate(
            b'public', b'public', raw, 9, True, False,
            directory_watch=10, directory_inventory_names=('sample',),
            transient_midpoint_verified=True, transient_sibling_negative=True)
        self.assertFalse(result['observed_checks']['transient_directory_control_detected'])
        self.assertEqual(result['status'], 'BLOCKED')

    def test_directory_watch_attrib_does_not_impersonate_source_inode_attrib(self):
        target = named(b'temporary-public-sibling')
        raw = (ev(wd=10, mask=module.IN_CREATE, data=target)
               + ev(wd=10, mask=module.IN_ATTRIB, data=target)
               + ev(wd=10, mask=module.IN_DELETE, data=target))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['source_attribute_events'], 0)
        result = module._evaluate(
            b'public', b'public', raw, 9, True, False,
            directory_watch=10, directory_inventory_names=('sample',),
            transient_midpoint_verified=True, transient_sibling_negative=True)
        self.assertTrue(result['observed_checks']['transient_directory_control_detected'])
        self.assertEqual(result['status'], 'BLOCKED')

    def test_truncated_stream_defaults_source_attrib_counter_to_zero_but_blocks(self):
        parsed = module._classify_stream(b'', -1, directory_watch=10)
        self.assertFalse(parsed['well_formed'])
        self.assertEqual(parsed['source_attribute_events'], 0)
        result = module._evaluate(
            b'public', b'public', b'\x00' * 5, 9, True, False,
            directory_watch=10, directory_inventory_names=('sample',))
        self.assertFalse(result['observed_checks']['event_stream_complete'])
        self.assertFalse(result['can_authorize_dispatch'])


    def test_truncated_buffer_cannot_prove_quiet_directory_inventory(self):
        result = module._evaluate(
            b'public', b'public', b'\x00' * 7, 9, True, False,
            directory_watch=10, directory_inventory_ok=True,
            directory_inventory_names=('sample',))
        self.assertFalse(result['observed_checks']['event_stream_complete'])
        self.assertFalse(result['observed_checks']['no_directory_entry_mutations'])
        self.assertEqual(result['status'], 'BLOCKED')

    def test_dead_directory_watcher_cannot_prove_no_directory_mutations(self):
        result = module._evaluate(
            b'public', b'public', b'', 9, False, False,
            directory_watch=10, directory_inventory_ok=True,
            directory_inventory_names=('sample',))
        self.assertFalse(result['observed_checks']['event_stream_complete'])
        self.assertFalse(result['observed_checks']['no_directory_entry_mutations'])
        self.assertEqual(result['status'], 'BLOCKED')

    def test_missing_parent_watch_cannot_claim_original_directory_intact(self):
        result = module._evaluate(
            b'public', b'public', b'', 9, True, False,
            directory_watch=None, directory_inventory_ok=True,
            directory_inventory_names=('sample',))
        self.assertFalse(result['observed_checks']['both_watches_identified'])
        self.assertFalse(result['observed_checks']['no_directory_entry_mutations'])
        self.assertEqual(result['status'], 'BLOCKED')

    def test_valid_dual_watch_empty_buffer_and_only_sample_still_quiet(self):
        result = module._evaluate(
            b'public', b'public', b'', 9, True, False,
            directory_watch=10, directory_inventory_ok=True,
            directory_inventory_names=('sample',))
        self.assertTrue(result['observed_checks']['no_directory_entry_mutations'])
        self.assertEqual(result['status'], 'LOCAL_DISPOSABLE_WITNESS_UNVERIFIED')
        self.assertFalse(result['can_authorize_dispatch'])


    def test_oversized_plain_inventory_cannot_claim_quiet_generated_directory(self):
        names = ('sample',) + tuple('public-extra-%d' % i for i in range(2000))
        result = module._evaluate(
            b'public', b'public', b'', 9, True, False,
            directory_watch=10, directory_inventory_ok=True,
            directory_inventory_names=names)
        self.assertFalse(result['observed_checks']['no_directory_entry_mutations'])
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertFalse(result['can_authorize_dispatch'])

    def test_expected_two_name_persistent_inventory_remains_supported(self):
        raw = ev(wd=10, mask=module.IN_CREATE,
                 data=named(b'unexpected-public-sibling'))
        result = module._evaluate(
            b'public', b'public', raw, 9, True, False,
            directory_watch=10, directory_inventory_ok=False,
            directory_inventory_names=('sample', 'unexpected-public-sibling'),
            sibling_snapshot_stable=True, sibling_negative=True)
        self.assertTrue(result['observed_checks']['sibling_creation_control_detected'])
        self.assertEqual(result['status'], 'BLOCKED')


    def test_collector_rejects_oversized_integer_fd_before_poll(self):
        fd = module.MAX_FILE_DESCRIPTOR + 1
        with patch.object(module.select, 'poll') as factory:
            with self.assertRaisesRegex(OSError, 'nonstdio integer fd'):
                module._read_pending(fd)
            factory.assert_not_called()

    def test_snapshot_rejects_oversized_integer_fd_before_fstat(self):
        fd = module.MAX_FILE_DESCRIPTOR + 1
        with patch.object(module.os, 'open', return_value=fd):
            with patch.object(module.os, 'close') as close:
                with patch.object(module.os, 'fstat') as fstat:
                    with self.assertRaisesRegex(OSError, 'valid integer fd'):
                        module._snapshot_regular(Path('/tmp/public-fake-only'))
                    close.assert_not_called()
                    fstat.assert_not_called()

    def test_inotify_init_rejects_impossible_unsigned_width_before_any_watches(self):
        class Callable:
            def __init__(self, value): self.value = value; self.calls = 0
            def __call__(self, *_args): self.calls += 1; return self.value
        init = Callable(module.MAX_FILE_DESCRIPTOR + 1)
        add = Callable(9)
        class FakeLib:
            inotify_init1 = init
            inotify_add_watch = add
        with patch.object(module.ctypes, 'CDLL', return_value=FakeLib()):
            with patch.object(module.os, 'close') as close:
                with self.assertRaisesRegex(OSError, 'oversized descriptor'):
                    module._start_watch(Path('/tmp/public-fake-only'))
                close.assert_not_called()
        self.assertEqual(add.calls, 0)


    def test_live_inventory_read_accepts_generated_one_and_two_name_cases(self):
        with tempfile.TemporaryDirectory() as folder:
            parent = Path(folder)
            (parent / 'sample').write_bytes(b'public')
            self.assertEqual(module._bounded_inventory_names(parent),
                             ('sample',))
            (parent / module.PERSISTENT_SIBLING_NAME).write_bytes(b'extra')
            self.assertEqual(module._bounded_inventory_names(parent),
                             tuple(sorted(('sample', module.PERSISTENT_SIBLING_NAME))))

    def test_live_inventory_stops_after_third_entry_and_blocks_quiet_claim(self):
        class Entry:
            def __init__(self, name):
                self.name = name
        class Scandir:
            def __init__(self):
                self.reads = 0
            def __enter__(self):
                return self
            def __exit__(self, *_args):
                return False
            def __iter__(self):
                return self
            def __next__(self):
                self.reads += 1
                if self.reads > 3:
                    raise AssertionError('scanned beyond sufficient rejection witness')
                return Entry(('sample', 'public-a', 'public-b')[self.reads - 1])
        scan = Scandir()
        with patch.object(module.os, 'scandir', return_value=scan) as scandir:
            names = module._bounded_inventory_names(Path('/tmp/public-fake-only'))
            scandir.assert_called_once()
        self.assertEqual(scan.reads, 3)
        self.assertEqual(len(names), 3)
        result = module._evaluate(
            b'public', b'public', b'', 9, True, False,
            directory_watch=10, directory_inventory_ok=False,
            directory_inventory_names=names)
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertFalse(result['observed_checks']['no_directory_entry_mutations'])
        self.assertFalse(result['can_authorize_dispatch'])

    def test_live_inventory_rejects_nonplain_entry_name_before_sort(self):
        class HostileName:
            def __lt__(self, _other):
                raise AssertionError('must not sort malformed names')
        class Entry:
            name = HostileName()
        class Scandir:
            def __enter__(self):
                return iter((Entry(),))
            def __exit__(self, *_args):
                return False
        with patch.object(module.os, 'scandir', return_value=Scandir()):
            with self.assertRaisesRegex(OSError, 'malformed entry name'):
                module._bounded_inventory_names(Path('/tmp/public-fake-only'))


    def test_snapshot_rejects_bad_first_fstat_field_types_before_read(self):
        class FakeStat:
            def __init__(self, **changes):
                self.st_mode = module.stat.S_IFREG | 0o600
                self.st_dev = 1
                self.st_ino = 2
                self.st_nlink = 1
                self.st_size = 1
                self.st_mtime_ns = 100
                self.st_ctime_ns = 200
                self.st_uid = 0
                self.st_gid = 0
                for key, value in changes.items():
                    setattr(self, key, value)
        invalid = (('st_mode', True), ('st_dev', 1.0),
                   ('st_ino', None), ('st_size', '1'),
                   ('st_mtime_ns', object()), ('st_ctime_ns', False))
        for field, value in invalid:
            with self.subTest(field=field):
                with patch.object(module.os, 'open', return_value=17):
                    with patch.object(module.os, 'fstat',
                                      return_value=FakeStat(**{field: value})):
                        with patch.object(module.os, 'read') as read:
                            with patch.object(module.os, 'close') as close:
                                with self.assertRaisesRegex(OSError, 'noninteger metadata'):
                                    module._snapshot_regular(Path('/tmp/public-fake-only'))
                                read.assert_not_called()
                                close.assert_called_once_with(17)

    def test_snapshot_rejects_comparator_forged_fstat_inode_before_read(self):
        class AlwaysEqual:
            def __eq__(self, _other):
                return True
        class FakeStat:
            st_mode = module.stat.S_IFREG | 0o600
            st_dev = 1
            st_ino = AlwaysEqual()
            st_nlink = 1
            st_size = 1
            st_mtime_ns = 100
            st_ctime_ns = 200
            st_uid = 0
            st_gid = 0
        with patch.object(module.os, 'open', return_value=17):
            with patch.object(module.os, 'fstat', return_value=FakeStat()):
                with patch.object(module.os, 'read') as read:
                    with patch.object(module.os, 'close') as close:
                        with self.assertRaisesRegex(OSError, 'noninteger metadata'):
                            module._snapshot_regular(Path('/tmp/public-fake-only'))
                        read.assert_not_called()
                        close.assert_called_once_with(17)

    def test_snapshot_rejects_bad_final_fstat_metadata_and_closes_fd(self):
        class FakeStat:
            def __init__(self, ctime):
                self.st_mode = module.stat.S_IFREG | 0o600
                self.st_dev = 1
                self.st_ino = 2
                self.st_nlink = 1
                self.st_size = 1
                self.st_mtime_ns = 100
                self.st_ctime_ns = ctime
                self.st_uid = 0
                self.st_gid = 0
        with patch.object(module.os, 'open', return_value=17):
            with patch.object(module.os, 'fstat',
                              side_effect=(FakeStat(200), FakeStat(object()))) as fstat:
                with patch.object(module.os, 'read', return_value=b'x') as read:
                    with patch.object(module.os, 'close') as close:
                        with self.assertRaisesRegex(OSError, 'noninteger metadata'):
                            module._snapshot_regular(Path('/tmp/public-fake-only'))
                        self.assertEqual(fstat.call_count, 2)
                        read.assert_called_once_with(17, 2)
                        close.assert_called_once_with(17)


    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux watch test')
    def test_run_demo_refuses_patched_stdio_fd_without_close_or_snapshot(self):
        for fd in (0, 1, 2):
            with self.subTest(fd=fd):
                with patch.object(module, '_start_watch', return_value=(fd, 9, 10)):
                    with patch.object(module, '_snapshot_regular') as snapshot:
                        with patch.object(module, '_read_pending') as drain:
                            # TemporaryDirectory cleanup legitimately closes
                            # internal scan FDs. Preserve those real closes and
                            # prohibit only unsafe closure of the injected stdio.
                            real_close = os.close
                            with patch.object(module.os, 'close', wraps=real_close) as close:
                                result = module.run_demo()
                self.assertEqual(result['status'], 'BLOCKED')
                self.assertFalse(result['can_authorize_dispatch'])
                snapshot.assert_not_called()
                drain.assert_not_called()
                self.assertNotIn((fd,), [call.args for call in close.call_args_list])

    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux watch test')
    def test_run_demo_rejects_patched_aliased_watch_ids_and_closes_fd(self):
        rd, wr = os.pipe()
        try:
            with patch.object(module, '_start_watch', return_value=(rd, 9, 9)):
                with patch.object(module, '_snapshot_regular') as snapshot:
                    with patch.object(module, '_read_pending') as drain:
                        result = module.run_demo()
            self.assertEqual(result['status'], 'BLOCKED')
            snapshot.assert_not_called()
            drain.assert_not_called()
            with self.assertRaises(OSError):
                os.fstat(rd)
        finally:
            os.close(wr)

    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux watch test')
    def test_run_demo_refuses_non_tuple_registration_before_snapshot(self):
        with patch.object(module, '_start_watch', return_value=[17, 9, 10]):
            with patch.object(module, '_snapshot_regular') as snapshot:
                with patch.object(module, '_read_pending') as drain:
                    result = module.run_demo()
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertFalse(result['independent_os_proof_verified'])
        snapshot.assert_not_called()
        drain.assert_not_called()


    def test_direct_snapshot_result_rejects_malformed_helper_return(self):
        class Comparable:
            def __eq__(self, _other):
                return True
        malformed = (
            [((1, 2), b'public')],
            (1, 2),
            ((True, 2), b'public'),
            ((Comparable(), 2), b'public'),
            ((1, -2), b'public'),
            ((1, 2), bytearray(b'public')),
            ((1, 2), b'x' * 4097),
        )
        for value in malformed:
            with self.subTest(value=type(value).__name__):
                with self.assertRaises(OSError):
                    module._checked_snapshot_result(value)
        self.assertEqual(module._checked_snapshot_result(((0, 2), b'public')),
                         ((0, 2), b'public'))

    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux watch test')
    def test_run_demo_rejects_patched_hostile_first_snapshot_before_drain(self):
        rd, wr = os.pipe()
        class ForgedInode:
            def __eq__(self, _other):
                return True
        try:
            with patch.object(module, '_start_watch', return_value=(rd, 9, 10)):
                with patch.object(module, '_snapshot_regular',
                                  return_value=((ForgedInode(), 7), module.BEFORE)) as snapshot:
                    with patch.object(module, '_read_pending') as drain:
                        result = module.run_demo()
            self.assertEqual(result['status'], 'BLOCKED')
            self.assertFalse(result['can_authorize_dispatch'])
            snapshot.assert_called_once()
            drain.assert_not_called()
            with self.assertRaises(OSError):
                os.fstat(rd)
        finally:
            os.close(wr)

    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux watch test')
    def test_run_demo_rejects_injected_oversized_final_snapshot_before_drain(self):
        rd, wr = os.pipe()
        synthetic_contents = iter((module.BEFORE, b'x' * 4097))
        try:
            with patch.object(module, '_start_watch', return_value=(rd, 9, 10)):
                with patch.object(module, '_snapshot_regular', side_effect=lambda path: native_created_sample_snapshot(path, next(synthetic_contents))) as snapshot:
                    with patch.object(module, '_read_pending') as drain:
                        result = module.run_demo()
            self.assertEqual(result['status'], 'BLOCKED')
            self.assertEqual(snapshot.call_count, 2)
            self.assertFalse(result['independent_os_proof_verified'])
            drain.assert_not_called()
            with self.assertRaises(OSError):
                os.fstat(rd)
        finally:
            os.close(wr)


    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux watch test')
    def test_run_demo_rejects_nonstr_watch_descriptor_and_closes_valid_fd(self):
        rd, wr = os.pipe()
        class NeverCompare:
            def __eq__(self, _other):
                raise AssertionError('invalid watch identity must not compare')
        try:
            with patch.object(module, '_start_watch',
                              return_value=(rd, 9, NeverCompare())):
                with patch.object(module, '_snapshot_regular') as snapshot:
                    with patch.object(module, '_read_pending') as drain:
                        result = module.run_demo()
            self.assertEqual(result['status'], 'BLOCKED')
            self.assertFalse(result['can_authorize_dispatch'])
            snapshot.assert_not_called()
            drain.assert_not_called()
            with self.assertRaises(OSError):
                os.fstat(rd)
        finally:
            os.close(wr)


    def test_poll_register_nonvoid_return_never_checks_readiness(self):
        for response in (False, True, 0, 17, 'registered'):
            with self.subTest(response=repr(response)):
                class Nonvoid:
                    def register(self, *_args):
                        return response
                    def poll(self, _timeout):
                        raise AssertionError('no poll after malformed registration')
                with patch.object(module.select, 'poll', return_value=Nonvoid()):
                    with patch.object(module.os, 'read') as read:
                        with self.assertRaisesRegex(OSError, 'registration returned malformed'):
                            module._read_pending(17)
                        read.assert_not_called()

    def test_poll_register_forged_none_comparator_is_rejected(self):
        class LooksNone:
            def __eq__(self, _other):
                return True
        class Forged:
            def register(self, *_args):
                return LooksNone()
            def poll(self, _timeout):
                raise AssertionError('must not poll unvalidated registration')
        with patch.object(module.select, 'poll', return_value=Forged()):
            with patch.object(module.os, 'read') as read:
                with self.assertRaisesRegex(OSError, 'registration returned malformed'):
                    module._read_pending(17)
                read.assert_not_called()


    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux watch test')
    def test_generated_runner_rejects_wrong_baseline_fixture_before_mutation(self):
        rd, wr = os.pipe()
        try:
            with patch.object(module, '_start_watch', return_value=(rd, 9, 10)):
                # Keep the native O_EXCL inode so this exercise reaches the
                # *content* baseline mismatch, not DEC-830's earlier identity check.
                with patch.object(module, '_snapshot_regular',
                                  side_effect=lambda path: native_created_sample_snapshot(
                                      path, b'UNEXPECTED INITIAL')) as snapshot:
                    with patch.object(module, '_read_pending') as drain:
                        result = module.run_demo()
            self.assertEqual(result['status'], 'BLOCKED')
            self.assertFalse(result['can_authorize_dispatch'])
            snapshot.assert_called_once()
            drain.assert_not_called()
            with self.assertRaises(OSError):
                os.fstat(rd)
        finally:
            os.close(wr)

    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux watch test')
    def test_generated_runner_rejects_wrong_final_fixture_before_inventory(self):
        rd, wr = os.pipe()
        synthetic_contents = iter((module.BEFORE, b'UNEXPECTED FINAL'))
        try:
            with patch.object(module, '_start_watch', return_value=(rd, 9, 10)):
                with patch.object(module, '_snapshot_regular', side_effect=lambda path: native_created_sample_snapshot(path, next(synthetic_contents))) as snapshot:
                    with patch.object(module, '_bounded_inventory_names',
                                      return_value=()) as inventory:
                        with patch.object(module, '_read_pending') as drain:
                            result = module.run_demo()
            self.assertEqual(result['status'], 'BLOCKED')
            self.assertEqual(snapshot.call_count, 2)
            # One prewrite empty-directory census is expected; the final
            # inventory remains unreachable after a malformed final snapshot.
            inventory.assert_called_once()
            drain.assert_not_called()
            self.assertFalse(result['independent_os_proof_verified'])
            with self.assertRaises(OSError):
                os.fstat(rd)
        finally:
            os.close(wr)


    def test_first_inotify_watch_exception_closes_allocated_fd_once(self):
        class Callable:
            def __init__(self, result): self.result = result; self.calls = 0
            def __call__(self, *_args):
                self.calls += 1
                if isinstance(self.result, Exception):
                    raise self.result
                return self.result
        init = Callable(17)
        add = Callable(OSError(5, 'synthetic registration failure'))
        class FakeLib:
            inotify_init1 = init
            inotify_add_watch = add
        with patch.object(module.ctypes, 'CDLL', return_value=FakeLib()):
            with patch.object(module.os, 'close') as close:
                with self.assertRaises(OSError):
                    module._start_watch(Path('/tmp/public-fake-only'))
                close.assert_called_once_with(17)
        self.assertEqual(add.calls, 1)

    def test_directory_watch_exception_closes_allocated_fd_once(self):
        class Callable:
            def __init__(self, outputs): self.outputs = iter(outputs); self.calls = 0
            def __call__(self, *_args):
                self.calls += 1
                outcome = next(self.outputs)
                if isinstance(outcome, Exception):
                    raise outcome
                return outcome
        add = Callable([9, OSError(5, 'synthetic directory failure')])
        class FakeLib:
            inotify_init1 = Callable([17])
            inotify_add_watch = add
        with patch.object(module.ctypes, 'CDLL', return_value=FakeLib()):
            with patch.object(module.os, 'close') as close:
                with self.assertRaises(OSError):
                    module._start_watch(Path('/tmp/public-fake-only'))
                close.assert_called_once_with(17)
        self.assertEqual(add.calls, 2)

    def test_unexpected_watch_exception_is_handled_after_cleanup(self):
        class Callable:
            def __init__(self, outcome): self.outcome = outcome
            def __call__(self, *_args):
                if isinstance(self.outcome, Exception):
                    raise self.outcome
                return self.outcome
        class FakeLib:
            inotify_init1 = Callable(17)
            inotify_add_watch = Callable(RuntimeError('synthetic broken wrapper'))
        with patch.object(module.ctypes, 'CDLL', return_value=FakeLib()):
            with patch.object(module.os, 'close') as close:
                with self.assertRaisesRegex(OSError, 'registration raised unexpectedly'):
                    module._start_watch(Path('/tmp/public-fake-only'))
                close.assert_called_once_with(17)


    def test_snapshot_unexpected_open_exception_is_handled_before_fd_cleanup(self):
        with patch.object(module.os, 'open',
                          side_effect=RuntimeError('synthetic broken open')):
            with patch.object(module.os, 'close') as close:
                with self.assertRaisesRegex(OSError, 'snapshot open raised unexpectedly'):
                    module._snapshot_regular(Path('/tmp/public-fake-only'))
                close.assert_not_called()

    def test_snapshot_unexpected_fstat_exception_closes_valid_fd(self):
        with patch.object(module.os, 'open', return_value=17):
            with patch.object(module.os, 'fstat',
                              side_effect=RuntimeError('synthetic broken fstat')):
                with patch.object(module.os, 'read') as read:
                    with patch.object(module.os, 'close') as close:
                        with self.assertRaisesRegex(OSError, 'snapshot syscall raised unexpectedly'):
                            module._snapshot_regular(Path('/tmp/public-fake-only'))
                        read.assert_not_called()
                        close.assert_called_once_with(17)

    def test_snapshot_unexpected_read_exception_closes_valid_fd(self):
        class FakeStat:
            st_mode = module.stat.S_IFREG | 0o600
            st_dev = 1
            st_ino = 2
            st_nlink = 1
            st_size = 1
            st_mtime_ns = 100
            st_ctime_ns = 200
            st_uid = 0
            st_gid = 0
        with patch.object(module.os, 'open', return_value=17):
            with patch.object(module.os, 'fstat', return_value=FakeStat()):
                with patch.object(module.os, 'read',
                                  side_effect=RuntimeError('synthetic broken read')):
                    with patch.object(module.os, 'close') as close:
                        with self.assertRaisesRegex(OSError, 'snapshot syscall raised unexpectedly'):
                            module._snapshot_regular(Path('/tmp/public-fake-only'))
                        close.assert_called_once_with(17)


    def test_inventory_scandir_wrapper_exception_is_handled(self):
        with patch.object(module.os, 'scandir',
                          side_effect=RuntimeError('synthetic scandir failure')):
            with self.assertRaisesRegex(OSError, 'inventory scan raised unexpectedly'):
                module._bounded_inventory_names(Path('/tmp/public-fake-only'))

    def test_inventory_iterator_exception_after_first_entry_is_handled(self):
        class Entry:
            name = 'sample'
        class Scandir:
            def __init__(self):
                self.calls = 0
            def __enter__(self):
                return self
            def __exit__(self, *_args):
                return False
            def __iter__(self):
                return self
            def __next__(self):
                self.calls += 1
                if self.calls == 1:
                    return Entry()
                raise RuntimeError('synthetic broken directory iterator')
        scan = Scandir()
        with patch.object(module.os, 'scandir', return_value=scan):
            with self.assertRaisesRegex(OSError, 'inventory scan raised unexpectedly'):
                module._bounded_inventory_names(Path('/tmp/public-fake-only'))
        self.assertEqual(scan.calls, 2)


    def test_event_collector_poll_factory_exception_becomes_handled_oserror(self):
        with patch.object(module.select, 'poll',
                          side_effect=RuntimeError('synthetic broken poll factory')):
            with patch.object(module.os, 'read') as read:
                with self.assertRaisesRegex(OSError, 'collector wrapper raised unexpectedly'):
                    module._read_pending(17)
                read.assert_not_called()

    def test_event_collector_poll_readiness_exception_becomes_handled_oserror(self):
        class BrokenPoll:
            def register(self, *_args):
                return None
            def poll(self, _timeout):
                raise RuntimeError('synthetic broken poll response')
        with patch.object(module.select, 'poll', return_value=BrokenPoll()):
            with patch.object(module.os, 'read') as read:
                with self.assertRaisesRegex(OSError, 'collector wrapper raised unexpectedly'):
                    module._read_pending(17)
                read.assert_not_called()

    def test_event_collector_osread_exception_becomes_handled_oserror(self):
        class Ready:
            def register(self, *_args):
                return None
            def poll(self, _timeout):
                return [(17, module.select.POLLIN)]
        with patch.object(module.select, 'poll', return_value=Ready()):
            with patch.object(module.os, 'read',
                              side_effect=RuntimeError('synthetic broken read')) as read:
                with self.assertRaisesRegex(OSError, 'collector wrapper raised unexpectedly'):
                    module._read_pending(17)
                read.assert_called_once_with(17, 4096)


    def test_snapshot_metadata_refuses_impossible_unsigned_device_inode_ids(self):
        class FakeStat:
            def __init__(self, **changes):
                self.st_mode = module.stat.S_IFREG | 0o600
                self.st_dev = 1
                self.st_ino = 2
                self.st_nlink = 1
                self.st_size = 1
                self.st_mtime_ns = 100
                self.st_ctime_ns = 200
                self.st_uid = 0
                self.st_gid = 0
                for field, value in changes.items():
                    setattr(self, field, value)
        for field in ('st_dev', 'st_ino'):
            with self.subTest(field=field):
                with patch.object(module.os, 'open', return_value=17):
                    with patch.object(module.os, 'fstat',
                                      return_value=FakeStat(**{field: 1 << 64})):
                        with patch.object(module.os, 'read') as read:
                            with patch.object(module.os, 'close') as close:
                                with self.assertRaisesRegex(OSError, 'bounded regular inode'):
                                    module._snapshot_regular(Path('/tmp/public-fake-only'))
                                read.assert_not_called()
                                close.assert_called_once_with(17)

    def test_snapshot_helper_result_rejects_impossible_device_inode_width(self):
        for identity in ((1 << 64, 7), (3, 1 << 64)):
            with self.subTest(identity=identity):
                with self.assertRaisesRegex(OSError, 'invalid identity or bytes'):
                    module._checked_snapshot_result((identity, module.BEFORE))

    def test_snapshot_helper_result_preserves_maximum_uint64_identity_values(self):
        maximum = module.MAX_KERNEL_STAT_ID
        self.assertEqual(
            module._checked_snapshot_result(((maximum, maximum), module.BEFORE)),
            ((maximum, maximum), module.BEFORE))


    def test_inotify_library_loader_runtime_error_is_handled_without_close(self):
        with patch.object(module.ctypes, 'CDLL',
                          side_effect=RuntimeError('synthetic loader failure')):
            with patch.object(module.os, 'close') as close:
                with self.assertRaisesRegex(OSError, 'initialization raised unexpectedly'):
                    module._start_watch(Path('/tmp/public-fake-only'))
                close.assert_not_called()

    def test_inotify_init_runtime_error_is_handled_without_close(self):
        class Callable:
            def __init__(self, result): self.result = result
            def __call__(self, *_args):
                if isinstance(self.result, Exception):
                    raise self.result
                return self.result
        class FakeLib:
            inotify_init1 = Callable(RuntimeError('synthetic init wrapper failure'))
            inotify_add_watch = Callable(9)
        with patch.object(module.ctypes, 'CDLL', return_value=FakeLib()):
            with patch.object(module.os, 'close') as close:
                with self.assertRaisesRegex(OSError, 'initialization raised unexpectedly'):
                    module._start_watch(Path('/tmp/public-fake-only'))
                close.assert_not_called()

    def test_inotify_loader_native_oserror_is_preserved(self):
        with patch.object(module.ctypes, 'CDLL',
                          side_effect=OSError(12, 'synthetic native loader failure')):
            with patch.object(module.os, 'close') as close:
                with self.assertRaises(OSError) as outcome:
                    module._start_watch(Path('/tmp/public-fake-only'))
                self.assertEqual(outcome.exception.errno, 12)
                close.assert_not_called()


    def test_directory_move_without_rename_cookie_is_not_well_formed(self):
        for action in (module.IN_MOVED_FROM, module.IN_MOVED_TO):
            with self.subTest(action=action):
                raw = ev(wd=10, mask=action,
                         data=named(b'public-moved-child'), cookie=0)
                parsed = module._classify_stream(raw, 9, directory_watch=10)
                self.assertFalse(parsed['well_formed'])
                self.assertEqual(parsed['directory_changes'], 1)
                result = module._evaluate(
                    b'public', b'public', raw, 9, True, False,
                    directory_watch=10, directory_inventory_names=('sample',))
                self.assertEqual(result['status'], 'BLOCKED')
                self.assertFalse(result['observed_checks']['event_stream_complete'])

    def test_two_zero_cookie_moves_cannot_claim_complete_stream(self):
        name = named(b'public-child')
        raw = (ev(wd=10, mask=module.IN_MOVED_FROM, data=name, cookie=0)
               + ev(wd=10, mask=module.IN_MOVED_TO, data=name, cookie=0))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertFalse(parsed['well_formed'])
        self.assertEqual(parsed['directory_changes'], 2)

    def test_named_moves_with_nonzero_cookies_keep_existing_semantics(self):
        name = named(b'public-child')
        raw = (ev(wd=10, mask=module.IN_MOVED_FROM, data=name, cookie=31)
               + ev(wd=10, mask=module.IN_MOVED_TO, data=name, cookie=32))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['directory_changes'], 2)


    def test_snapshot_rejects_impossible_linux_mode_width_before_read(self):
        class FakeStat:
            def __init__(self, mode):
                self.st_mode = mode
                self.st_dev = 1
                self.st_ino = 2
                self.st_nlink = 1
                self.st_size = 1
                self.st_mtime_ns = 100
                self.st_ctime_ns = 200
                self.st_uid = 0
                self.st_gid = 0
        for mode in (-1, (1 << 32) | module.stat.S_IFREG | 0o600):
            with self.subTest(mode=mode):
                with patch.object(module.os, 'open', return_value=17):
                    with patch.object(module.os, 'fstat', return_value=FakeStat(mode)):
                        with patch.object(module.os, 'read') as read:
                            with patch.object(module.os, 'close') as close:
                                with self.assertRaisesRegex(OSError, 'bounded regular inode'):
                                    module._snapshot_regular(Path('/tmp/public-fake-only'))
                                read.assert_not_called()
                                close.assert_called_once_with(17)

    def test_snapshot_regular_mode_within_uint32_remains_valid(self):
        class FakeStat:
            st_mode = module.stat.S_IFREG | 0o600
            st_dev = 1
            st_ino = 2
            st_nlink = 1
            st_size = 1
            st_mtime_ns = 100
            st_ctime_ns = 200
            st_uid = 0
            st_gid = 0
        self.assertEqual(module._checked_snapshot_metadata(FakeStat()),
                         (module.stat.S_IFREG | 0o600, 1, 2, 1, 100, 200, 0, 0))


    def test_duplicate_move_from_cookie_direction_is_not_complete(self):
        raw = (ev(wd=10, mask=module.IN_MOVED_FROM,
                  data=named(b'one'), cookie=71)
               + ev(wd=10, mask=module.IN_MOVED_FROM,
                    data=named(b'two'), cookie=71))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertFalse(parsed['well_formed'])
        self.assertEqual(parsed['directory_changes'], 2)

    def test_duplicate_move_to_cookie_direction_is_not_complete(self):
        raw = (ev(wd=10, mask=module.IN_MOVED_TO,
                  data=named(b'one'), cookie=81)
               + ev(wd=10, mask=module.IN_MOVED_TO,
                    data=named(b'two'), cookie=81))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertFalse(parsed['well_formed'])
        self.assertEqual(parsed['directory_changes'], 2)

    def test_matching_move_cookie_directions_remain_complete(self):
        raw = (ev(wd=10, mask=module.IN_MOVED_FROM,
                  data=named(b'old-name'), cookie=99)
               + ev(wd=10, mask=module.IN_MOVED_TO,
                    data=named(b'new-name'), cookie=99))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['directory_changes'], 2)


    def test_zero_file_watch_cannot_claim_dual_watch_completeness(self):
        parsed = module._classify_stream(b'', 0, directory_watch=10)
        self.assertFalse(parsed['well_formed'])
        result = module._evaluate(b'public', b'public', b'', 0, True, False,
                                  directory_watch=10, directory_inventory_names=('sample',))
        self.assertFalse(result['observed_checks']['both_watches_identified'])
        self.assertFalse(result['observed_checks']['event_stream_complete'])
        self.assertEqual(result['status'], 'BLOCKED')

    def test_zero_directory_watch_cannot_claim_quiet_observation(self):
        parsed = module._classify_stream(b'', 9, directory_watch=0)
        self.assertFalse(parsed['well_formed'])
        result = module._evaluate(b'public', b'public', b'', 9, True, False,
                                  directory_watch=0, directory_inventory_names=('sample',))
        self.assertFalse(result['observed_checks']['both_watches_identified'])
        self.assertFalse(result['observed_checks']['no_directory_entry_mutations'])
        self.assertEqual(result['status'], 'BLOCKED')

    def test_watch_registration_refuses_zero_wd_and_closes_valid_fd(self):
        class CFunction:
            def __init__(self, values): self.values = iter(values); self.calls = 0
            def __call__(self, *_args):
                self.calls += 1
                return next(self.values)
        for watch_ids, count in (((0, 10), 1), ((9, 0), 2)):
            with self.subTest(watch_ids=watch_ids):
                add = CFunction(watch_ids)
                class FakeLib:
                    inotify_init1 = CFunction((17,))
                    inotify_add_watch = add
                with patch.object(module.ctypes, 'CDLL', return_value=FakeLib()):
                    with patch.object(module.os, 'close') as close:
                        with self.assertRaises(OSError):
                            module._start_watch(Path('/tmp/public-fake-only'))
                        close.assert_called_once_with(17)
                self.assertEqual(add.calls, count)

    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux watch test')
    def test_runner_rejects_patched_zero_wd_before_snapshot(self):
        for file_wd, dir_wd in ((0, 10), (9, 0)):
            with self.subTest(file_wd=file_wd, dir_wd=dir_wd):
                rd, wr = os.pipe()
                try:
                    with patch.object(module, '_start_watch', return_value=(rd, file_wd, dir_wd)):
                        with patch.object(module, '_snapshot_regular') as snapshot:
                            with patch.object(module, '_read_pending') as drain:
                                result = module.run_demo()
                    self.assertEqual(result['status'], 'BLOCKED')
                    snapshot.assert_not_called()
                    drain.assert_not_called()
                    with self.assertRaises(OSError):
                        os.fstat(rd)
                finally:
                    os.close(wr)


    def test_snapshot_rejects_mode_change_between_fstat_observations(self):
        class FakeStat:
            def __init__(self, mode):
                self.st_mode = module.stat.S_IFREG | mode
                self.st_dev = 1
                self.st_ino = 2
                self.st_nlink = 1
                self.st_size = 1
                self.st_mtime_ns = 100
                self.st_ctime_ns = 200
                self.st_uid = 0
                self.st_gid = 0
        with patch.object(module.os, 'open', return_value=17):
            with patch.object(module.os, 'fstat',
                              side_effect=(FakeStat(0o600), FakeStat(0o400))):
                with patch.object(module.os, 'read', return_value=b'x') as read:
                    with patch.object(module.os, 'close') as close:
                        with self.assertRaisesRegex(OSError, 'inode changed'):
                            module._snapshot_regular(Path('/tmp/public-fake-only'))
                        read.assert_called_once_with(17, 2)
                        close.assert_called_once_with(17)

    def test_snapshot_same_mode_still_returns_device_inode_and_bytes(self):
        class FakeStat:
            st_mode = module.stat.S_IFREG | 0o600
            st_dev = 1
            st_ino = 2
            st_nlink = 1
            st_size = 1
            st_mtime_ns = 100
            st_ctime_ns = 200
            st_uid = 0
            st_gid = 0
        with patch.object(module.os, 'open', return_value=17):
            with patch.object(module.os, 'fstat', return_value=FakeStat()):
                with patch.object(module.os, 'read', return_value=b'x') as read:
                    with patch.object(module.os, 'close') as close:
                        self.assertEqual(
                            module._snapshot_regular(Path('/tmp/public-fake-only')),
                            ((1, 2), b'x'))
                        read.assert_called_once_with(17, 2)
                        close.assert_called_once_with(17)


    def test_bounded_inventory_rejects_invalid_linux_encoded_names(self):
        class Entry:
            def __init__(self, name):
                self.name = name
        class Scan:
            def __init__(self, name):
                self.name = name
                self.calls = 0
            def __enter__(self):
                return self
            def __exit__(self, *_args):
                return False
            def __iter__(self):
                return self
            def __next__(self):
                self.calls += 1
                if self.calls == 1:
                    return Entry(self.name)
                raise StopIteration
        invalid = ('', '.', '..', 'child/name', 'bad\0name',
                   'x' * 256, 'é' * 128, '\ud800')
        for name in invalid:
            with self.subTest(name=repr(name)):
                scan = Scan(name)
                with patch.object(module.os, 'scandir', return_value=scan):
                    with self.assertRaisesRegex(OSError, 'malformed entry name'):
                        module._bounded_inventory_names(Path('/tmp/public-fake-only'))
                self.assertEqual(scan.calls, 2)

    def test_evaluator_rejects_impossible_encoded_inventory_names(self):
        invalid = ('', '.', '..', 'child/name', 'bad\0name',
                   'x' * 256, 'é' * 128, '\ud800')
        for name in invalid:
            with self.subTest(name=repr(name)):
                result = module._evaluate(
                    b'public', b'public', b'', 9, True, False,
                    directory_watch=10, directory_inventory_names=(name,))
                self.assertEqual(result['status'], 'BLOCKED')
                self.assertFalse(result['observed_checks']['no_directory_entry_mutations'])
                self.assertFalse(result['can_authorize_dispatch'])

    def test_inventory_accepts_bounded_linux_surrogateescaped_byte_name(self):
        name = os.fsdecode(b'public-\xff-entry')
        self.assertTrue(module._plausible_inventory_basename(name))
        self.assertTrue(module._plausible_inventory_basename('x' * 255))
        self.assertFalse(module._plausible_inventory_basename('x' * 256))
        self.assertFalse(module._plausible_inventory_basename('é' * 128))


    def test_runner_initial_public_file_write_runtime_error_blocks_without_watch(self):
        with patch.object(module.Path, 'open',
                          side_effect=RuntimeError('synthetic generated fixture writer')):
            with patch.object(module, '_start_watch') as register:
                outcome = module.run_demo()
        self.assertEqual(outcome['status'], 'BLOCKED')
        self.assertFalse(outcome['can_authorize_dispatch'])
        self.assertFalse(outcome['independent_os_proof_verified'])
        register.assert_not_called()

    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux watch test')
    def test_runner_replacement_wrapper_runtime_error_blocks_and_closes_watch(self):
        rd, wr = os.pipe()
        try:
            with patch.object(module, '_start_watch', return_value=(rd, 9, 10)):
                with patch.object(module, '_snapshot_regular',
                                  side_effect=lambda path: native_created_sample_snapshot(path)):
                    with patch.object(module.os, 'replace',
                                      side_effect=RuntimeError('synthetic replacement wrapper')):
                        with patch.object(module, '_read_pending') as drain:
                            result = module.run_demo(replace_watched_inode=True)
            self.assertEqual(result['status'], 'BLOCKED')
            self.assertFalse(result['can_authorize_dispatch'])
            drain.assert_not_called()
            with self.assertRaises(OSError):
                os.fstat(rd)
        finally:
            os.close(wr)

    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux watch test')
    def test_runner_revert_fsync_runtime_error_blocks_and_closes_watch(self):
        rd, wr = os.pipe()
        try:
            with patch.object(module, '_start_watch', return_value=(rd, 9, 10)):
                with patch.object(module, '_snapshot_regular',
                                  side_effect=lambda path: native_created_sample_snapshot(path)):
                    with patch.object(module.os, 'fsync',
                                      side_effect=RuntimeError('synthetic fsync wrapper')):
                        with patch.object(module, '_read_pending') as drain:
                            result = module.run_demo(negative=True)
            self.assertEqual(result['status'], 'BLOCKED')
            self.assertFalse(result['independent_os_proof_verified'])
            drain.assert_not_called()
            with self.assertRaises(OSError):
                os.fstat(rd)
        finally:
            os.close(wr)


    def test_snapshot_rejects_out_of_range_linux_stat_nanoseconds(self):
        class FakeStat:
            def __init__(self, **change):
                self.st_mode = module.stat.S_IFREG | 0o600
                self.st_dev = 1
                self.st_ino = 2
                self.st_nlink = 1
                self.st_size = 1
                self.st_mtime_ns = 100
                self.st_ctime_ns = 200
                self.st_uid = 0
                self.st_gid = 0
                for key, value in change.items():
                    setattr(self, key, value)
        for field in ('st_mtime_ns', 'st_ctime_ns'):
            for invalid in (module.MIN_KERNEL_TIMESTAMP_NS - 1,
                            module.MAX_KERNEL_TIMESTAMP_NS + 1, 1 << 128):
                with self.subTest(field=field, invalid=invalid):
                    with patch.object(module.os, 'open', return_value=17):
                        with patch.object(module.os, 'fstat',
                                          return_value=FakeStat(**{field: invalid})):
                            with patch.object(module.os, 'read') as read:
                                with patch.object(module.os, 'close') as close:
                                    with self.assertRaisesRegex(OSError, 'impossible nanosecond'):
                                        module._snapshot_regular(Path('/tmp/public-fake-only'))
                                    read.assert_not_called()
                                    close.assert_called_once_with(17)

    def test_stat_metadata_accepts_signed_linux_nanosecond_boundaries(self):
        class FakeStat:
            st_mode = module.stat.S_IFREG | 0o600
            st_dev = 1
            st_ino = 2
            st_nlink = 1
            st_size = 1
            st_mtime_ns = module.MIN_KERNEL_TIMESTAMP_NS
            st_ctime_ns = module.MAX_KERNEL_TIMESTAMP_NS
            st_uid = 0
            st_gid = 0
        self.assertEqual(
            module._checked_snapshot_metadata(FakeStat()),
            (FakeStat.st_mode, 1, 2, 1, module.MIN_KERNEL_TIMESTAMP_NS,
             module.MAX_KERNEL_TIMESTAMP_NS, 0, 0))

    def test_stat_metadata_accepts_negative_pre_epoch_timestamps(self):
        class FakeStat:
            st_mode = module.stat.S_IFREG | 0o600
            st_dev = 1
            st_ino = 2
            st_nlink = 1
            st_size = 1
            st_mtime_ns = -1_000_000_000
            st_ctime_ns = -1
            st_uid = 0
            st_gid = 0
        self.assertEqual(
            module._checked_snapshot_metadata(FakeStat()),
            (FakeStat.st_mode, 1, 2, 1, -1_000_000_000, -1, 0, 0))


    def test_inventory_rejects_overlong_name_before_encoding(self):
        with patch.object(module.os, 'fsencode',
                          side_effect=AssertionError('must not encode overlong name')) as encode:
            self.assertFalse(module._plausible_inventory_basename('x' * 256))
            self.assertFalse(module._plausible_inventory_basename('x' * 100000))
            encode.assert_not_called()

    def test_inventory_rejects_injected_nonbytes_encoder_results(self):
        class ForgedBytes(bytes):
            def __eq__(self, other):
                return True
        for response in (None, True, 'sample', bytearray(b'sample'),
                         ForgedBytes(b'sample')):
            with self.subTest(response=repr(response)):
                with patch.object(module.os, 'fsencode', return_value=response):
                    self.assertFalse(module._plausible_inventory_basename('sample'))

    def test_inventory_encoders_that_raise_fail_closed_in_evaluator(self):
        with patch.object(module.os, 'fsencode',
                          side_effect=RuntimeError('synthetic broken fsencode')):
            result = module._evaluate(
                b'public', b'public', b'', 9, True, False,
                directory_watch=10, directory_inventory_names=('sample',))
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertFalse(result['can_authorize_dispatch'])
        self.assertFalse(result['observed_checks']['no_directory_entry_mutations'])


    def test_disposable_cli_unknown_switch_emits_blocked_json_receipt(self):
        p = subprocess.run(
            [sys.executable, '-B', str(SCRIPT), '--source', '/protected'],
            capture_output=True, text=True, timeout=4)
        self.assertEqual(p.returncode, 2)
        result = json.loads(p.stdout)
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertFalse(result['can_authorize_dispatch'])
        self.assertFalse(result['independent_os_proof_verified'])
        self.assertIn('CLI arguments rejected', result['findings'][0])

    def test_disposable_cli_conflicting_negative_switches_emit_blocked_receipt(self):
        p = subprocess.run(
            [sys.executable, '-B', str(SCRIPT),
             '--execute-inode-replacement-negative',
             '--execute-sibling-creation-negative'],
            capture_output=True, text=True, timeout=4)
        self.assertEqual(p.returncode, 2)
        result = json.loads(p.stdout)
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertFalse(result['can_authorize_dispatch'])
        self.assertFalse(result['independent_os_proof_verified'])

    def test_disposable_cli_unknown_help_switch_emits_blocked_receipt(self):
        p = subprocess.run(
            [sys.executable, '-B', str(SCRIPT), '--help'],
            capture_output=True, text=True, timeout=4)
        self.assertEqual(p.returncode, 2)
        result = json.loads(p.stdout)
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertFalse(result['can_authorize_dispatch'])


    def test_reversed_rename_pair_same_cookie_is_not_a_complete_stream(self):
        raw = (ev(wd=10, mask=module.IN_MOVED_TO,
                  data=named(b'new-name'), cookie=321)
               + ev(wd=10, mask=module.IN_MOVED_FROM,
                    data=named(b'old-name'), cookie=321))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertFalse(parsed['well_formed'])
        self.assertEqual(parsed['directory_changes'], 2)
        outcome = module._evaluate(
            b'public', b'public', raw, 9, True, False,
            directory_watch=10, directory_inventory_names=('sample',))
        self.assertEqual(outcome['status'], 'BLOCKED')
        self.assertFalse(outcome['observed_checks']['event_stream_complete'])

    def test_opposite_direction_unpaired_rename_cookies_remain_well_formed(self):
        raw = (ev(wd=10, mask=module.IN_MOVED_TO,
                  data=named(b'new-name'), cookie=321)
               + ev(wd=10, mask=module.IN_MOVED_FROM,
                    data=named(b'old-name'), cookie=322))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['directory_changes'], 2)

    def test_interleaved_matching_rename_pair_retains_complete_stream(self):
        raw = (ev(wd=10, mask=module.IN_MOVED_FROM,
                  data=named(b'old-name'), cookie=321)
               + ev(wd=9, mask=module.IN_ATTRIB)
               + ev(wd=10, mask=module.IN_MOVED_TO,
                    data=named(b'new-name'), cookie=321))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['directory_changes'], 2)
        self.assertEqual(parsed['source_attribute_events'], 1)


    def test_paired_rename_cannot_change_file_into_directory(self):
        raw = (ev(wd=10, mask=module.IN_MOVED_FROM,
                  data=named(b'old-file'), cookie=49)
               + ev(wd=10, mask=module.IN_MOVED_TO | module.IN_ISDIR,
                    data=named(b'new-dir'), cookie=49))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertFalse(parsed['well_formed'])
        self.assertEqual(parsed['directory_changes'], 2)

    def test_paired_rename_cannot_change_directory_into_file(self):
        raw = (ev(wd=10, mask=module.IN_MOVED_FROM | module.IN_ISDIR,
                  data=named(b'old-dir'), cookie=50)
               + ev(wd=10, mask=module.IN_MOVED_TO,
                    data=named(b'new-file'), cookie=50))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertFalse(parsed['well_formed'])
        self.assertEqual(parsed['directory_changes'], 2)

    def test_paired_rename_matching_file_kind_remains_well_formed(self):
        raw = (ev(wd=10, mask=module.IN_MOVED_FROM,
                  data=named(b'old-file'), cookie=51)
               + ev(wd=10, mask=module.IN_MOVED_TO,
                    data=named(b'new-file'), cookie=51))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['directory_changes'], 2)

    def test_paired_rename_matching_directory_kind_remains_well_formed(self):
        raw = (ev(wd=10, mask=module.IN_MOVED_FROM | module.IN_ISDIR,
                  data=named(b'old-dir'), cookie=52)
               + ev(wd=10, mask=module.IN_MOVED_TO | module.IN_ISDIR,
                    data=named(b'new-dir'), cookie=52))
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['directory_changes'], 2)


    def test_rename_cookie_order_type_and_interleaving_matrix(self):
        for cookie in (0, 23, (1 << 32) - 1):
            for from_directory in (False, True):
                for to_directory in (False, True):
                    for reversed_pair in (False, True):
                        for interleaved in (False, True):
                            with self.subTest(cookie=cookie, from_dir=from_directory,
                                              to_dir=to_directory, reverse=reversed_pair,
                                              interleaved=interleaved):
                                from_mask = module.IN_MOVED_FROM
                                to_mask = module.IN_MOVED_TO
                                if from_directory:
                                    from_mask |= module.IN_ISDIR
                                if to_directory:
                                    to_mask |= module.IN_ISDIR
                                from_event = ev(wd=10, mask=from_mask,
                                                data=named(b'old-child'), cookie=cookie)
                                to_event = ev(wd=10, mask=to_mask,
                                              data=named(b'new-child'), cookie=cookie)
                                records = [to_event, from_event] if reversed_pair else [
                                    from_event, to_event]
                                if interleaved:
                                    records.insert(1, ev(wd=9, mask=module.IN_ATTRIB))
                                raw = b''.join(records)
                                parsed = module._classify_stream(
                                    raw, 9, directory_watch=10)
                                expected = (
                                    cookie != 0 and not reversed_pair
                                    and from_directory == to_directory)
                                self.assertIs(parsed['well_formed'], expected)
                                self.assertEqual(parsed['directory_changes'], 2)
                                result = module._evaluate(
                                    b'public', b'public', raw, 9, True, False,
                                    directory_watch=10,
                                    directory_inventory_names=('sample',))
                                self.assertEqual(result['status'], 'BLOCKED')
                                self.assertFalse(result['can_authorize_dispatch'])
                                self.assertFalse(result['independent_os_proof_verified'])

    def test_distinct_unpaired_rename_cookie_stream_stays_bounded_and_blocks(self):
        raw = b''.join(
            ev(wd=10, mask=module.IN_MOVED_FROM,
               data=named(('old-%03d' % i).encode('ascii')), cookie=i + 1)
            for i in range(128))
        self.assertLess(len(raw), 65536)
        parsed = module._classify_stream(raw, 9, directory_watch=10)
        self.assertTrue(parsed['well_formed'])
        self.assertEqual(parsed['directory_changes'], 128)
        result = module._evaluate(
            b'public', b'public', raw, 9, True, False,
            directory_watch=10, directory_inventory_names=('sample',))
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertFalse(result['can_authorize_dispatch'])

    def test_delayed_duplicate_rename_cookie_refuses_full_stream(self):
        first = ev(wd=10, mask=module.IN_MOVED_FROM,
                   data=named(b'first-child'), cookie=17)
        middle = b''.join(
            ev(wd=10, mask=module.IN_MOVED_FROM,
               data=named(('other-%03d' % i).encode('ascii')),
               cookie=i + 1000)
            for i in range(64))
        last = ev(wd=10, mask=module.IN_MOVED_FROM,
                  data=named(b'last-child'), cookie=17)
        parsed = module._classify_stream(first + middle + last, 9, directory_watch=10)
        self.assertFalse(parsed['well_formed'])
        self.assertEqual(parsed['directory_changes'], 66)


    def test_reserved_linux_stmode_bits_rejected_before_snapshot_read(self):
        class FakeStat:
            def __init__(self, mode):
                self.st_mode = mode
                self.st_dev = 1
                self.st_ino = 2
                self.st_nlink = 1
                self.st_size = 1
                self.st_mtime_ns = 100
                self.st_ctime_ns = 200
                self.st_uid = 0
                self.st_gid = 0
        for bit in ((1 << 16), (1 << 20), (1 << 31)):
            with self.subTest(bit=bit):
                with patch.object(module.os, 'open', return_value=17):
                    with patch.object(module.os, 'fstat',
                                      return_value=FakeStat(module.stat.S_IFREG | 0o600 | bit)):
                        with patch.object(module.os, 'read') as read:
                            with patch.object(module.os, 'close') as close:
                                with self.assertRaisesRegex(OSError, 'bounded regular inode'):
                                    module._snapshot_regular(Path('/tmp/public-fake-only'))
                                read.assert_not_called()
                                close.assert_called_once_with(17)

    def test_valid_special_permission_bits_remain_in_snapshot_metadata(self):
        class FakeStat:
            st_mode = module.stat.S_IFREG | 0o7777
            st_dev = 1
            st_ino = 2
            st_nlink = 1
            st_size = 1
            st_mtime_ns = 100
            st_ctime_ns = 200
            st_uid = 0
            st_gid = 0
        self.assertEqual(
            module._checked_snapshot_metadata(FakeStat()),
            (FakeStat.st_mode, 1, 2, 1, 100, 200, 0, 0))


    def test_snapshot_refuses_unlinked_or_multiply_linked_inode_before_read(self):
        class FakeStat:
            def __init__(self, nlink):
                self.st_mode = module.stat.S_IFREG | 0o600
                self.st_dev = 1
                self.st_ino = 2
                self.st_nlink = nlink
                self.st_size = 1
                self.st_mtime_ns = 100
                self.st_ctime_ns = 200
                self.st_uid = 0
                self.st_gid = 0
        for count in (0, 2, 3, 1 << 64, -1):
            with self.subTest(count=count):
                with patch.object(module.os, 'open', return_value=17):
                    with patch.object(module.os, 'fstat', return_value=FakeStat(count)):
                        with patch.object(module.os, 'read') as read:
                            with patch.object(module.os, 'close') as close:
                                with self.assertRaisesRegex(OSError, 'bounded regular inode'):
                                    module._snapshot_regular(Path('/tmp/public-fake-only'))
                                read.assert_not_called()
                                close.assert_called_once_with(17)

    def test_snapshot_refuses_forged_noninteger_hardlink_counts(self):
        class StrangeInt(int):
            def __eq__(self, other):
                return True
        class FakeStat:
            st_mode = module.stat.S_IFREG | 0o600
            st_dev = 1
            st_ino = 2
            st_nlink = 1
            st_size = 1
            st_mtime_ns = 100
            st_ctime_ns = 200
            st_uid = 0
            st_gid = 0
        for invalid in (True, 1.0, StrangeInt(1), '1', None):
            with self.subTest(count=repr(invalid)):
                FakeStat.st_nlink = invalid
                with self.assertRaisesRegex(OSError, 'noninteger metadata'):
                    module._checked_snapshot_metadata(FakeStat())

    def test_single_link_metadata_retains_existing_snapshot_tuple(self):
        class FakeStat:
            st_mode = module.stat.S_IFREG | 0o600
            st_dev = 1
            st_ino = 2
            st_nlink = 1
            st_size = 1
            st_mtime_ns = 100
            st_ctime_ns = 200
            st_uid = 0
            st_gid = 0
        self.assertEqual(
            module._checked_snapshot_metadata(FakeStat()),
            (FakeStat.st_mode, 1, 2, 1, 100, 200, 0, 0))


    @unittest.skipUnless(sys.platform == 'linux' and hasattr(os, 'link'),
                         'disposable Linux hard-link control')
    def test_live_generated_hardlink_alias_blocks_then_recovers_after_unlink(self):
        with tempfile.TemporaryDirectory(prefix='dec774-public-', dir='/tmp') as folder:
            path = Path(folder) / 'sample'
            alias = Path(folder) / 'second-public-link'
            path.write_bytes(module.BEFORE)
            initial = module._snapshot_regular(path)
            self.assertEqual(initial[1], module.BEFORE)
            os.link(path, alias)
            self.assertEqual(os.stat(path).st_nlink, 2)
            with self.assertRaisesRegex(OSError, 'bounded regular inode'):
                module._snapshot_regular(path)
            alias.unlink()
            self.assertEqual(os.stat(path).st_nlink, 1)
            self.assertEqual(module._snapshot_regular(path), initial)

    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux unlinked FD')
    def test_live_unlinked_generated_fd_metadata_is_not_accepted(self):
        with tempfile.TemporaryDirectory(prefix='dec774-public-', dir='/tmp') as folder:
            path = Path(folder) / 'sample'
            path.write_bytes(module.BEFORE)
            fd = os.open(path, os.O_RDONLY)
            try:
                path.unlink()
                self.assertEqual(os.fstat(fd).st_nlink, 0)
                with self.assertRaisesRegex(OSError, 'bounded regular inode'):
                    module._checked_snapshot_metadata(os.fstat(fd))
            finally:
                os.close(fd)


    def test_hardlink_alias_negative_mode_rejects_nonboolean_input_before_watch(self):
        for invalid in ('yes', 1, None, ()):
            with self.subTest(invalid=repr(invalid)):
                with patch.object(module, '_start_watch') as register:
                    result = module.run_demo(hardlink_negative=invalid)
                self.assertEqual(result['status'], 'BLOCKED')
                self.assertFalse(result['can_authorize_dispatch'])
                register.assert_not_called()

    def test_hardlink_alias_negative_conflicts_with_other_modes(self):
        for kwargs in ({'negative': True},
                       {'create_sibling': True},
                       {'replace_watched_inode': True},
                       {'transient_sibling': True}):
            with self.subTest(kwargs=kwargs):
                with patch.object(module, '_start_watch') as register:
                    result = module.run_demo(hardlink_negative=True, **kwargs)
                self.assertEqual(result['status'], 'BLOCKED')
                register.assert_not_called()

    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux hard-link mode')
    def test_hardlink_alias_negative_never_promotes_injected_snapshot(self):
        rd, wr = os.pipe()
        try:
            with patch.object(module, '_start_watch', return_value=(rd, 9, 10)):
                with patch.object(module, '_snapshot_regular',
                                  side_effect=lambda path: native_created_sample_snapshot(path)) as snapshot:
                    with patch.object(module, '_plausible_generated_hardlink_pair',
                                      return_value=True):
                        with patch.object(module, '_read_pending') as drain:
                            result = module.run_demo(hardlink_negative=True)
            self.assertEqual(result['status'], 'BLOCKED')
            self.assertIn('failed to refuse a hard-link alias',
                          ' '.join(result['findings']))
            self.assertFalse(result['can_authorize_dispatch'])
            self.assertFalse(result['independent_os_proof_verified'])
            self.assertEqual(snapshot.call_count, 2)
            drain.assert_not_called()
            with self.assertRaises(OSError):
                os.fstat(rd)
        finally:
            os.close(wr)

    def test_cli_explicit_hardlink_alias_negative_always_blocked(self):
        p = subprocess.run(
            [sys.executable, '-B', str(SCRIPT),
             '--execute-hardlink-alias-negative'],
            capture_output=True, text=True, timeout=6)
        self.assertEqual(p.returncode, 2)
        result = json.loads(p.stdout)
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertFalse(result['can_authorize_dispatch'])
        self.assertFalse(result['independent_os_proof_verified'])


    @unittest.skipUnless(sys.platform == 'linux' and hasattr(os, 'link'),
                         'disposable live Linux hard-link control')
    def test_live_hardlink_negative_reports_specific_control_refusal(self):
        result = module.run_demo(hardlink_negative=True)
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertIn(
            'deliberate generated hard-link alias negative control blocked',
            result['findings'])
        self.assertFalse(result['can_authorize_dispatch'])
        self.assertFalse(result['independent_os_proof_verified'])

    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux watch test')
    def test_hardlink_creation_wrapper_failure_blocks_and_closes_watcher(self):
        rd, wr = os.pipe()
        try:
            with patch.object(module, '_start_watch', return_value=(rd, 9, 10)):
                with patch.object(module, '_snapshot_regular',
                                  side_effect=lambda path: native_created_sample_snapshot(path)):
                    with patch.object(module.os, 'link',
                                      side_effect=RuntimeError('synthetic link syscall wrapper')):
                        with patch.object(module, '_read_pending') as drain:
                            result = module.run_demo(hardlink_negative=True)
            self.assertEqual(result['status'], 'BLOCKED')
            self.assertFalse(result['can_authorize_dispatch'])
            drain.assert_not_called()
            with self.assertRaises(OSError):
                os.fstat(rd)
        finally:
            os.close(wr)

    def test_cli_conflicting_hardlink_and_existing_mode_blocked_before_runner(self):
        p = subprocess.run(
            [sys.executable, '-B', str(SCRIPT),
             '--execute-hardlink-alias-negative',
             '--execute-reverted-write-negative'],
            capture_output=True, text=True, timeout=4)
        self.assertEqual(p.returncode, 2)
        result = json.loads(p.stdout)
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertIn('CLI arguments rejected', result['findings'][0])
        self.assertFalse(result['can_authorize_dispatch'])
        self.assertFalse(result['independent_os_proof_verified'])


    def test_snapshot_refuses_owner_or_group_change_during_read(self):
        class FakeStat:
            def __init__(self, uid, gid):
                self.st_mode = module.stat.S_IFREG | 0o600
                self.st_dev = 1
                self.st_ino = 2
                self.st_nlink = 1
                self.st_size = 1
                self.st_mtime_ns = 100
                self.st_ctime_ns = 200
                self.st_uid = uid
                self.st_gid = gid
        for old, new in ((FakeStat(10, 20), FakeStat(11, 20)),
                         (FakeStat(10, 20), FakeStat(10, 21))):
            with self.subTest(old=(old.st_uid, old.st_gid),
                              new=(new.st_uid, new.st_gid)):
                with patch.object(module.os, 'open', return_value=17):
                    with patch.object(module.os, 'fstat', side_effect=(old, new)):
                        with patch.object(module.os, 'read', return_value=b'x') as read:
                            with patch.object(module.os, 'close') as close:
                                with self.assertRaisesRegex(OSError, 'inode changed'):
                                    module._snapshot_regular(Path('/tmp/public-fake-only'))
                                read.assert_called_once_with(17, 2)
                                close.assert_called_once_with(17)

    def test_snapshot_rejects_invalid_linux_owner_group_ids(self):
        class ForgedInt(int):
            def __eq__(self, _other):
                return True
        class FakeStat:
            st_mode = module.stat.S_IFREG | 0o600
            st_dev = 1
            st_ino = 2
            st_nlink = 1
            st_size = 1
            st_mtime_ns = 100
            st_ctime_ns = 200
            st_uid = 0
            st_gid = 0
        for field in ('st_uid', 'st_gid'):
            for invalid in (-1, 1 << 32, True, 1.0, ForgedInt(0), '0'):
                with self.subTest(field=field, value=repr(invalid)):
                    FakeStat.st_uid = 0
                    FakeStat.st_gid = 0
                    setattr(FakeStat, field, invalid)
                    with self.assertRaises(OSError):
                        module._checked_snapshot_metadata(FakeStat())

    def test_snapshot_accepts_valid_uint32_owner_group_ids(self):
        class FakeStat:
            st_mode = module.stat.S_IFREG | 0o600
            st_dev = 1
            st_ino = 2
            st_nlink = 1
            st_size = 1
            st_mtime_ns = 100
            st_ctime_ns = 200
            st_uid = module.MAX_KERNEL_OWNER_ID
            st_gid = module.MAX_KERNEL_OWNER_ID
        self.assertEqual(
            module._checked_snapshot_metadata(FakeStat()),
            (FakeStat.st_mode, 1, 2, 1, 100, 200,
             module.MAX_KERNEL_OWNER_ID, module.MAX_KERNEL_OWNER_ID))


    def test_snapshot_all_checked_metadata_drift_fields_fail_closed(self):
        class FakeStat:
            def __init__(self, **changes):
                self.st_mode = module.stat.S_IFREG | 0o600
                self.st_dev = 1
                self.st_ino = 2
                self.st_nlink = 1
                self.st_size = 1
                self.st_mtime_ns = 100
                self.st_ctime_ns = 200
                self.st_uid = 10
                self.st_gid = 20
                for key, value in changes.items():
                    setattr(self, key, value)
        drift = {
            'st_mode': module.stat.S_IFREG | 0o400,
            'st_dev': 3,
            'st_ino': 4,
            'st_size': 2,
            'st_mtime_ns': 101,
            'st_ctime_ns': 201,
            'st_uid': 11,
            'st_gid': 21,
        }
        for field, value in drift.items():
            with self.subTest(field=field):
                with patch.object(module.os, 'open', return_value=17):
                    with patch.object(module.os, 'fstat',
                                      side_effect=(FakeStat(), FakeStat(**{field: value}))):
                        with patch.object(module.os, 'read', return_value=b'x') as read:
                            with patch.object(module.os, 'close') as close:
                                with self.assertRaisesRegex(OSError, 'inode changed'):
                                    module._snapshot_regular(Path('/tmp/public-fake-only'))
                                read.assert_called_once_with(17, 2)
                                close.assert_called_once_with(17)

    def test_snapshot_identical_eight_field_metadata_keeps_outward_identity(self):
        class FakeStat:
            st_mode = module.stat.S_IFREG | 0o600
            st_dev = 1
            st_ino = 2
            st_nlink = 1
            st_size = 1
            st_mtime_ns = 100
            st_ctime_ns = 200
            st_uid = 10
            st_gid = 20
        with patch.object(module.os, 'open', return_value=17):
            with patch.object(module.os, 'fstat', return_value=FakeStat()):
                with patch.object(module.os, 'read', return_value=b'x') as read:
                    with patch.object(module.os, 'close') as close:
                        self.assertEqual(
                            module._snapshot_regular(Path('/tmp/public-fake-only')),
                            ((1, 2), b'x'))
                        read.assert_called_once_with(17, 2)
                        close.assert_called_once_with(17)

    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux metadata')
    def test_live_generated_linux_snapshot_reports_actual_owner_group(self):
        with tempfile.TemporaryDirectory(prefix='dec778-public-', dir='/tmp') as folder:
            path = Path(folder) / 'sample'
            path.write_bytes(module.BEFORE)
            st = os.stat(path)
            checked = module._checked_snapshot_metadata(st)
            self.assertEqual(checked[-2:], (st.st_uid, st.st_gid))
            self.assertEqual(len(checked), 8)
            self.assertEqual(st.st_nlink, 1)
            self.assertEqual(module._snapshot_regular(path)[1], module.BEFORE)


    def test_generated_hardlink_pair_verifier_requires_matching_exact_ids(self):
        class FakeStat:
            def __init__(self, mode, dev, ino, nlink):
                self.st_mode = mode
                self.st_dev = dev
                self.st_ino = ino
                self.st_nlink = nlink
                self.st_uid = 10
                self.st_gid = 20
                self.st_size = len(module.BEFORE)
                self.st_mtime_ns = 100
                self.st_ctime_ns = 200
        normal = FakeStat(module.stat.S_IFREG | 0o600, 1, 2, 2)
        invalid = (
            FakeStat(module.stat.S_IFREG | 0o600, 1, 3, 2),
            FakeStat(module.stat.S_IFREG | 0o600, 4, 2, 2),
            FakeStat(module.stat.S_IFREG | 0o600, 1, 2, 1),
            FakeStat(module.stat.S_IFDIR | 0o700, 1, 2, 2),
            FakeStat((1 << 24) | module.stat.S_IFREG, 1, 2, 2),
            FakeStat(module.stat.S_IFREG | 0o600, 1, True, 2),
        )
        with patch.object(module.os, 'stat', side_effect=(normal, normal)):
            self.assertTrue(module._plausible_generated_hardlink_pair(
                Path('/tmp/public-one'), Path('/tmp/public-two')))
        for bad in invalid:
            with self.subTest(invalid=vars(bad)):
                with patch.object(module.os, 'stat',
                                  side_effect=(normal, bad)):
                    self.assertFalse(module._plausible_generated_hardlink_pair(
                        Path('/tmp/public-one'), Path('/tmp/public-two')))

    def test_generated_hardlink_pair_verifier_handles_missing_alias(self):
        with patch.object(module.os, 'stat',
                          side_effect=FileNotFoundError('synthetic missing alias')):
            self.assertFalse(module._plausible_generated_hardlink_pair(
                Path('/tmp/public-one'), Path('/tmp/public-two')))

    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux observer')
    def test_hardlink_mode_inert_link_wrapper_does_not_claim_guard_detection(self):
        rd, wr = os.pipe()
        try:
            with patch.object(module, '_start_watch', return_value=(rd, 9, 10)):
                with patch.object(module, '_snapshot_regular',
                                  side_effect=lambda path: native_created_sample_snapshot(path)) as snapshot:
                    with patch.object(module.os, 'link', return_value=None):
                        result = module.run_demo(hardlink_negative=True)
            self.assertEqual(result['status'], 'BLOCKED')
            self.assertIn('negative alias not verified', ' '.join(result['findings']))
            self.assertEqual(snapshot.call_count, 1)
            self.assertFalse(result['can_authorize_dispatch'])
            with self.assertRaises(OSError):
                os.fstat(rd)
        finally:
            os.close(wr)

    @unittest.skipUnless(sys.platform == 'linux' and hasattr(os, 'link'),
                         'disposable Linux hardlink pair')
    def test_live_generated_hardlink_pair_verifier_checks_kernel_alias(self):
        with tempfile.TemporaryDirectory(prefix='dec779-public-', dir='/tmp') as folder:
            path = Path(folder) / 'sample'
            alias = Path(folder) / 'second-public-link'
            path.write_bytes(module.BEFORE)
            self.assertFalse(module._plausible_generated_hardlink_pair(path, alias))
            os.link(path, alias)
            self.assertTrue(module._plausible_generated_hardlink_pair(path, alias))
            alias.unlink()
            self.assertFalse(module._plausible_generated_hardlink_pair(path, alias))


    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux watch')
    def test_hardlink_negative_rejects_nonvoid_link_wrapper_return(self):
        for invalid in (True, False, 0, 1, 'linked', object()):
            with self.subTest(link_status=repr(invalid)):
                rd, wr = os.pipe()
                try:
                    with patch.object(module, '_start_watch', return_value=(rd, 9, 10)):
                        with patch.object(module, '_snapshot_regular',
                                          side_effect=lambda path: native_created_sample_snapshot(path)) as snapshot:
                            with patch.object(module.os, 'link', return_value=invalid):
                                with patch.object(module, '_plausible_generated_hardlink_pair') as verify:
                                    outcome = module.run_demo(hardlink_negative=True)
                    self.assertEqual(outcome['status'], 'BLOCKED')
                    self.assertIn('malformed status', ' '.join(outcome['findings']))
                    self.assertFalse(outcome['can_authorize_dispatch'])
                    self.assertEqual(snapshot.call_count, 1)
                    verify.assert_not_called()
                    with self.assertRaises(OSError):
                        os.fstat(rd)
                finally:
                    os.close(wr)

    @unittest.skipUnless(sys.platform == 'linux' and hasattr(os, 'link'),
                         'disposable Linux link syscall')
    def test_native_link_syscall_returns_none_for_generated_alias(self):
        with tempfile.TemporaryDirectory(prefix='dec780-public-', dir='/tmp') as folder:
            path = Path(folder) / 'sample'
            alias = Path(folder) / 'public-hardlink-alias'
            path.write_bytes(module.BEFORE)
            self.assertIsNone(os.link(path, alias))
            self.assertTrue(module._plausible_generated_hardlink_pair(path, alias))


    def test_link_count_guard_raises_specific_oserror_subtype(self):
        class FakeStat:
            st_mode = module.stat.S_IFREG | 0o600
            st_dev = 1
            st_ino = 2
            st_nlink = 2
            st_size = 1
            st_mtime_ns = 100
            st_ctime_ns = 200
            st_uid = 1
            st_gid = 1
        with self.assertRaises(module._SnapshotHardlinkCountError):
            module._checked_snapshot_metadata(FakeStat())

    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux observer')
    def test_hardlink_control_does_not_credit_generic_snapshot_oserror(self):
        rd, wr = os.pipe()
        try:
            with patch.object(module, '_start_watch', return_value=(rd, 9, 10)):
                with patch.object(module, '_snapshot_regular',
                                  side_effect=native_created_sample_sequence(module.BEFORE,
                                               OSError('unrelated read failure'))):
                    with patch.object(module.os, 'link', return_value=None):
                        with patch.object(module, '_plausible_generated_hardlink_pair',
                                          return_value=True):
                            result = module.run_demo(hardlink_negative=True)
            self.assertEqual(result['status'], 'BLOCKED')
            self.assertIn('without link-count proof', ' '.join(result['findings']))
            self.assertNotIn('negative control blocked', ' '.join(result['findings']))
            self.assertFalse(result['can_authorize_dispatch'])
            with self.assertRaises(OSError):
                os.fstat(rd)
        finally:
            os.close(wr)

    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux observer')
    def test_hardlink_control_credits_only_specific_link_count_oserror(self):
        rd, wr = os.pipe()
        try:
            with patch.object(module, '_start_watch', return_value=(rd, 9, 10)):
                with patch.object(module, '_snapshot_regular',
                                  side_effect=native_created_sample_sequence(module.BEFORE,
                                               module._SnapshotHardlinkCountError('two links'))):
                    with patch.object(module.os, 'link', return_value=None):
                        with patch.object(module, '_plausible_generated_hardlink_pair',
                                          return_value=True):
                            result = module.run_demo(hardlink_negative=True)
            self.assertEqual(result['status'], 'BLOCKED')
            self.assertIn('negative control blocked', ' '.join(result['findings']))
            self.assertFalse(result['independent_os_proof_verified'])
            with self.assertRaises(OSError):
                os.fstat(rd)
        finally:
            os.close(wr)


    def test_generated_hardlink_alias_rejects_inconsistent_owner_or_size(self):
        class FakeStat:
            def __init__(self, **changes):
                self.st_mode = module.stat.S_IFREG | 0o600
                self.st_dev = 1
                self.st_ino = 2
                self.st_nlink = 2
                self.st_uid = 100
                self.st_gid = 200
                self.st_size = len(module.BEFORE)
                self.st_mtime_ns = 1000
                self.st_ctime_ns = 2000
                for key, value in changes.items():
                    setattr(self, key, value)
        baseline = FakeStat()
        for field, value in (
            ('st_uid', 101), ('st_gid', 201), ('st_size', len(module.BEFORE) + 1),
            ('st_mtime_ns', 1001), ('st_ctime_ns', 2001)):
            with self.subTest(field=field):
                with patch.object(module.os, 'stat',
                                  side_effect=(baseline, FakeStat(**{field: value}))):
                    self.assertFalse(module._plausible_generated_hardlink_pair(
                        Path('/tmp/public-a'), Path('/tmp/public-b')))
        with patch.object(module.os, 'stat', side_effect=(baseline, FakeStat())):
            self.assertTrue(module._plausible_generated_hardlink_pair(
                Path('/tmp/public-a'), Path('/tmp/public-b')))

    def test_generated_hardlink_alias_rejects_malformed_extended_metadata(self):
        class FakeStat:
            st_mode = module.stat.S_IFREG | 0o600
            st_dev = 1
            st_ino = 2
            st_nlink = 2
            st_uid = 10
            st_gid = 20
            st_size = len(module.BEFORE)
            st_mtime_ns = 100
            st_ctime_ns = 200
        original = {k: getattr(FakeStat, k) for k in
                    ('st_uid', 'st_gid', 'st_size', 'st_mtime_ns', 'st_ctime_ns')}
        for field, bad in (
            ('st_uid', -1), ('st_gid', 1 << 32), ('st_size', 4097),
            ('st_mtime_ns', module.MIN_KERNEL_TIMESTAMP_NS - 1),
            ('st_ctime_ns', module.MAX_KERNEL_TIMESTAMP_NS + 1),
            ('st_uid', True), ('st_size', 1.0)):
            with self.subTest(field=field, bad=repr(bad)):
                for name, value in original.items():
                    setattr(FakeStat, name, value)
                with patch.object(module.os, 'stat',
                                  side_effect=(FakeStat(), FakeStat())):
                    setattr(FakeStat, field, bad)
                    self.assertFalse(module._plausible_generated_hardlink_pair(
                        Path('/tmp/public-a'), Path('/tmp/public-b')))


    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux observer')
    def test_hardlink_guard_refusal_requires_persistent_alias_after_probe(self):
        rd, wr = os.pipe()
        try:
            with patch.object(module, '_start_watch', return_value=(rd, 9, 10)):
                with patch.object(module, '_snapshot_regular',
                                  side_effect=native_created_sample_sequence(module.BEFORE,
                                               module._SnapshotHardlinkCountError('two links'))):
                    with patch.object(module.os, 'link', return_value=None):
                        with patch.object(module, '_plausible_generated_hardlink_pair',
                                          side_effect=(True, False)) as verify:
                            outcome = module.run_demo(hardlink_negative=True)
            self.assertEqual(outcome['status'], 'BLOCKED')
            self.assertIn('changed during guard probe', ' '.join(outcome['findings']))
            self.assertNotIn('negative control blocked', ' '.join(outcome['findings']))
            self.assertEqual(verify.call_count, 2)
            self.assertFalse(outcome['can_authorize_dispatch'])
            with self.assertRaises(OSError):
                os.fstat(rd)
        finally:
            os.close(wr)

    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux observer')
    def test_hardlink_guard_refusal_rechecks_alias_before_local_credit(self):
        rd, wr = os.pipe()
        try:
            with patch.object(module, '_start_watch', return_value=(rd, 9, 10)):
                with patch.object(module, '_snapshot_regular',
                                  side_effect=native_created_sample_sequence(module.BEFORE,
                                               module._SnapshotHardlinkCountError('two links'))):
                    with patch.object(module.os, 'link', return_value=None):
                        with patch.object(module, '_plausible_generated_hardlink_pair',
                                          side_effect=(True, True)) as verify:
                            outcome = module.run_demo(hardlink_negative=True)
            self.assertEqual(outcome['status'], 'BLOCKED')
            self.assertIn('negative control blocked', ' '.join(outcome['findings']))
            self.assertEqual(verify.call_count, 2)
            self.assertFalse(outcome['independent_os_proof_verified'])
            with self.assertRaises(OSError):
                os.fstat(rd)
        finally:
            os.close(wr)


    def test_generated_link_alias_requires_exact_public_fixture_size(self):
        class FakeStat:
            def __init__(self, size):
                self.st_mode = module.stat.S_IFREG | 0o600
                self.st_dev = 1
                self.st_ino = 2
                self.st_nlink = 2
                self.st_uid = 10
                self.st_gid = 20
                self.st_size = size
                self.st_mtime_ns = 100
                self.st_ctime_ns = 200
        expected = len(module.BEFORE)
        for size in (0, expected - 1, expected + 1, 4096):
            with self.subTest(size=size):
                with patch.object(module.os, 'stat',
                                  side_effect=(FakeStat(size), FakeStat(size))):
                    self.assertFalse(module._plausible_generated_hardlink_pair(
                        Path('/tmp/public-a'), Path('/tmp/public-b')))
        with patch.object(module.os, 'stat',
                          side_effect=(FakeStat(expected), FakeStat(expected))):
            self.assertTrue(module._plausible_generated_hardlink_pair(
                Path('/tmp/public-a'), Path('/tmp/public-b')))

    @unittest.skipUnless(sys.platform == 'linux' and hasattr(os, 'link'),
                         'disposable generated Linux fixture')
    def test_live_hardlink_alias_has_exact_public_fixture_length(self):
        with tempfile.TemporaryDirectory(prefix='dec784-public-', dir='/tmp') as folder:
            source = Path(folder) / 'sample'
            alias = Path(folder) / 'public-hardlink-alias'
            source.write_bytes(module.BEFORE)
            self.assertIsNone(os.link(source, alias))
            self.assertEqual(os.stat(source).st_size, len(module.BEFORE))
            self.assertEqual(os.stat(alias).st_size, len(module.BEFORE))
            self.assertTrue(module._plausible_generated_hardlink_pair(source, alias))
            with alias.open('ab') as handle:
                handle.write(b'EXTRA')
            self.assertFalse(module._plausible_generated_hardlink_pair(source, alias))


    def test_generated_alias_must_match_baseline_snapshot_inode(self):
        class FakeStat:
            st_mode = module.stat.S_IFREG | 0o600
            st_dev = 11
            st_ino = 22
            st_nlink = 2
            st_uid = 10
            st_gid = 20
            st_size = len(module.BEFORE)
            st_mtime_ns = 100
            st_ctime_ns = 200
        for expected, valid in (((11, 22), True), ((11, 23), False),
                                ((12, 22), False), ((), False),
                                ((True, 22), False),
                                ((11, (1 << 64)), False)):
            with self.subTest(expected=expected):
                with patch.object(module.os, 'stat', return_value=FakeStat()):
                    self.assertIs(
                        module._plausible_generated_hardlink_pair(
                            Path('/tmp/public-one'), Path('/tmp/public-two'),
                            expected_inode=expected),
                        valid)

    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux observer')
    def test_hardlink_mode_rejects_alias_of_replaced_baseline_inode(self):
        rd, wr = os.pipe()
        try:
            with patch.object(module, '_start_watch', return_value=(rd, 9, 10)):
                # A baseline identity unrelated to the actual initial O_EXCL
                # writer must now fail BEFORE any hard-link alias probes.
                with patch.object(module, '_snapshot_regular',
                                  return_value=((0, 0), module.BEFORE)) as snapshot:
                    with patch.object(module.os, 'link') as link:
                        with patch.object(module, '_plausible_generated_hardlink_pair') as verify:
                            result = module.run_demo(hardlink_negative=True)
            self.assertEqual(result['status'], 'BLOCKED')
            self.assertIn('disposable inotify setup, read or cleanup failed',
                          result['findings'])
            self.assertEqual(snapshot.call_count, 1)
            link.assert_not_called()
            verify.assert_not_called()
            self.assertFalse(result['can_authorize_dispatch'])
            self.assertFalse(result['independent_os_proof_verified'])
            with self.assertRaises(OSError):
                os.fstat(rd)
        finally:
            os.close(wr)


    @unittest.skipUnless(sys.platform == 'linux' and hasattr(os, 'link'),
                         'disposable Linux hardlink alias')
    def test_live_replaced_public_path_cannot_match_original_alias_identity(self):
        with tempfile.TemporaryDirectory(prefix='dec786-public-', dir='/tmp') as folder:
            original = Path(folder) / 'sample'
            replacement = Path(folder) / 'replacement-public'
            alias = Path(folder) / 'public-hardlink-alias'
            original.write_bytes(module.BEFORE)
            first = os.stat(original)
            baseline = (first.st_dev, first.st_ino)
            replacement.write_bytes(module.BEFORE)
            self.assertNotEqual((os.stat(replacement).st_dev,
                                 os.stat(replacement).st_ino), baseline)
            os.replace(replacement, original)
            self.assertIsNone(os.link(original, alias))
            self.assertEqual(alias.read_bytes(), module.BEFORE)
            # A current pair can be mutually consistent but refer to a
            # different inode than the one watched at the baseline.
            self.assertTrue(module._plausible_generated_hardlink_pair(
                original, alias))
            self.assertFalse(module._plausible_generated_hardlink_pair(
                original, alias, expected_inode=baseline))

    @unittest.skipUnless(sys.platform == 'linux' and hasattr(os, 'link'),
                         'disposable Linux original inode')
    def test_live_original_public_inode_keeps_pinned_alias_identity(self):
        with tempfile.TemporaryDirectory(prefix='dec786-public-', dir='/tmp') as folder:
            original = Path(folder) / 'sample'
            alias = Path(folder) / 'public-hardlink-alias'
            original.write_bytes(module.BEFORE)
            first = os.stat(original)
            baseline = (first.st_dev, first.st_ino)
            self.assertIsNone(os.link(original, alias))
            self.assertTrue(module._plausible_generated_hardlink_pair(
                original, alias, expected_inode=baseline))
            alias.unlink()
            self.assertFalse(module._plausible_generated_hardlink_pair(
                original, alias, expected_inode=baseline))


    def test_hardlink_alias_single_field_drift_matrix_never_accepts(self):
        class FakeStat:
            def __init__(self, **changes):
                self.st_mode = module.stat.S_IFREG | 0o600
                self.st_dev = 11
                self.st_ino = 22
                self.st_nlink = 2
                self.st_uid = 10
                self.st_gid = 20
                self.st_size = len(module.BEFORE)
                self.st_mtime_ns = 100
                self.st_ctime_ns = 200
                for field, value in changes.items():
                    setattr(self, field, value)
        changes = {
            'st_mode': module.stat.S_IFREG | 0o400,
            'st_dev': 12,
            'st_ino': 23,
            'st_nlink': 1,
            'st_uid': 11,
            'st_gid': 21,
            'st_size': len(module.BEFORE) + 1,
            'st_mtime_ns': 101,
            'st_ctime_ns': 201,
        }
        for field, value in changes.items():
            for side in (0, 1):
                with self.subTest(field=field, side=side):
                    records = [FakeStat(), FakeStat()]
                    records[side] = FakeStat(**{field: value})
                    with patch.object(module.os, 'stat', side_effect=records) as observed:
                        self.assertFalse(module._plausible_generated_hardlink_pair(
                            Path('/tmp/public-a'), Path('/tmp/public-b'),
                            expected_inode=(11, 22)))
                        self.assertEqual(observed.call_count, 2)
        with patch.object(module.os, 'stat', side_effect=(FakeStat(), FakeStat())):
            self.assertTrue(module._plausible_generated_hardlink_pair(
                Path('/tmp/public-a'), Path('/tmp/public-b'),
                expected_inode=(11, 22)))

    def test_invalid_baseline_link_identity_never_reaches_path_stat(self):
        class FakeTuple(tuple):
            pass
        invalid = (True, (), (1,), (1, 2, 3), [1, 2],
                   (True, 2), (1, 1 << 64), FakeTuple((1, 2)),
                   (1.0, 2), ('1', 2))
        for value in invalid:
            with self.subTest(baseline=repr(value)):
                with patch.object(module.os, 'stat',
                                  side_effect=AssertionError('no stat allowed')) as observed:
                    self.assertFalse(module._plausible_generated_hardlink_pair(
                        Path('/tmp/public-a'), Path('/tmp/public-b'),
                        expected_inode=value))
                    observed.assert_not_called()


    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux watch')
    def test_hardlink_native_oserrors_block_before_alias_proof_and_close_fd(self):
        for native_error in (PermissionError(13, 'synthetic denied link'),
                             FileExistsError(17, 'synthetic existing link'),
                             OSError(31, 'synthetic too many links')):
            with self.subTest(errno=native_error.errno):
                rd, wr = os.pipe()
                try:
                    with patch.object(module, '_start_watch', return_value=(rd, 9, 10)):
                        with patch.object(module, '_snapshot_regular',
                                          side_effect=lambda path: native_created_sample_snapshot(path)) as snapshot:
                            with patch.object(module.os, 'link',
                                              side_effect=native_error):
                                with patch.object(module, '_plausible_generated_hardlink_pair') as verify:
                                    with patch.object(module, '_read_pending') as drain:
                                        outcome = module.run_demo(hardlink_negative=True)
                    self.assertEqual(outcome['status'], 'BLOCKED')
                    self.assertFalse(outcome['can_authorize_dispatch'])
                    self.assertFalse(outcome['independent_os_proof_verified'])
                    self.assertNotIn('negative control blocked',
                                     ' '.join(outcome['findings']))
                    self.assertEqual(snapshot.call_count, 1)
                    verify.assert_not_called()
                    drain.assert_not_called()
                    with self.assertRaises(OSError):
                        os.fstat(rd)
                finally:
                    os.close(wr)

    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux watch')
    def test_hardlink_alias_stat_failure_cannot_credit_detection_or_leak_fd(self):
        rd, wr = os.pipe()
        native_stat = os.stat

        def missing_only_generated_alias(path, *args, **kwargs):
            # os.path.isdir('/tmp') also invokes os.stat. An unscoped stat
            # mock would short-circuit the runner before alias verification.
            if Path(path).name == 'public-hardlink-alias':
                raise FileNotFoundError(2, 'synthetic missing alias')
            return native_stat(path, *args, **kwargs)

        try:
            with patch.object(module, '_start_watch', return_value=(rd, 9, 10)):
                with patch.object(module, '_snapshot_regular',
                                  side_effect=lambda path: native_created_sample_snapshot(path)) as snapshot:
                    with patch.object(module.os, 'link', return_value=None):
                        with patch.object(module.os, 'stat',
                                          side_effect=missing_only_generated_alias) as stat:
                            with patch.object(module, '_read_pending') as drain:
                                outcome = module.run_demo(hardlink_negative=True)
            self.assertTrue(any(
                call.args and Path(call.args[0]).name == 'public-hardlink-alias'
                for call in stat.call_args_list))
            self.assertEqual(outcome['status'], 'BLOCKED')
            self.assertIn('negative alias not verified', ' '.join(outcome['findings']))
            self.assertNotIn('negative control blocked', ' '.join(outcome['findings']))
            self.assertEqual(snapshot.call_count, 1)
            drain.assert_not_called()
            self.assertFalse(outcome['independent_os_proof_verified'])
            with self.assertRaises(OSError):
                os.fstat(rd)
        finally:
            os.close(wr)


    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux watch')
    def test_hardlink_scoped_missing_alias_stat_preserves_tmp_preflight(self):
        native_stat = os.stat
        probes = []

        def stat_only_missing_alias(path, *args, **kwargs):
            probes.append(Path(path).name)
            if Path(path).name == 'public-hardlink-alias':
                raise FileNotFoundError(2, 'synthetic alias missing')
            return native_stat(path, *args, **kwargs)

        rd, wr = os.pipe()
        try:
            with patch.object(module, '_start_watch', return_value=(rd, 9, 10)):
                with patch.object(module, '_snapshot_regular',
                                  side_effect=lambda path: native_created_sample_snapshot(path)) as snapshot:
                    with patch.object(module.os, 'link', return_value=None):
                        with patch.object(module.os, 'stat',
                                          side_effect=stat_only_missing_alias):
                            outcome = module.run_demo(hardlink_negative=True)
            self.assertIn('tmp', probes)
            self.assertIn('public-hardlink-alias', probes)
            self.assertEqual(outcome['status'], 'BLOCKED')
            self.assertIn('negative alias not verified', ' '.join(outcome['findings']))
            self.assertEqual(snapshot.call_count, 1)
            self.assertFalse(outcome['can_authorize_dispatch'])
            self.assertFalse(outcome['independent_os_proof_verified'])
            with self.assertRaises(OSError):
                os.fstat(rd)
        finally:
            os.close(wr)


    @unittest.skipUnless(sys.platform == 'linux' and hasattr(os, 'symlink'),
                         'disposable Linux generated symlink')
    def test_live_generated_symlink_is_not_hardlink_alias(self):
        with tempfile.TemporaryDirectory(prefix='dec790-public-', dir='/tmp') as folder:
            source = Path(folder) / 'sample'
            alias = Path(folder) / 'public-hardlink-alias'
            source.write_bytes(module.BEFORE)
            original_stat = os.stat(source)
            baseline = (original_stat.st_dev, original_stat.st_ino)
            alias.symlink_to(source)
            self.assertTrue(alias.is_symlink())
            self.assertFalse(module._plausible_generated_hardlink_pair(
                source, alias, expected_inode=baseline))
            alias.unlink()
            self.assertIsNone(os.link(source, alias))
            self.assertTrue(module._plausible_generated_hardlink_pair(
                source, alias, expected_inode=baseline))

    def test_hardlink_pair_stat_requests_nofollow_for_both_paths(self):
        class FakeStat:
            st_mode = module.stat.S_IFREG | 0o600
            st_dev = 1
            st_ino = 2
            st_nlink = 2
            st_uid = 10
            st_gid = 20
            st_size = len(module.BEFORE)
            st_mtime_ns = 100
            st_ctime_ns = 200
        source = Path('/tmp/public-a')
        alias = Path('/tmp/public-b')
        with patch.object(module.os, 'stat', return_value=FakeStat()) as stat_call:
            self.assertTrue(module._plausible_generated_hardlink_pair(
                source, alias, expected_inode=(1, 2)))
        self.assertEqual(stat_call.call_count, 2)
        self.assertEqual(stat_call.call_args_list[0].args, (source,))
        self.assertEqual(stat_call.call_args_list[1].args, (alias,))
        for call in stat_call.call_args_list:
            self.assertEqual(call.kwargs, {'follow_symlinks': False})


    def test_registers_both_generated_watches_without_following_symlinks(self):
        class Callable:
            def __init__(self, values):
                self.values = iter(values)
                self.calls = []
            def __call__(self, *args):
                self.calls.append(args)
                return next(self.values)
        init = Callable([17])
        add = Callable([9, 10])
        class FakeLib:
            inotify_init1 = init
            inotify_add_watch = add
        sample = Path('/tmp/disposable-public-only/sample')
        with patch.object(module.ctypes, 'CDLL', return_value=FakeLib()):
            self.assertEqual(module._start_watch(sample), (17, 9, 10))
        self.assertEqual(add.calls, [
            (17, os.fsencode(sample), module.MASK | module.IN_DONT_FOLLOW),
            (17, os.fsencode(sample.parent),
             module.DIRECTORY_MASK | module.IN_DONT_FOLLOW | module.IN_ONLYDIR),
        ])
        self.assertEqual(module.EVENT_ALLOWED & module.IN_DONT_FOLLOW, 0)
        self.assertEqual(module.EVENT_ALLOWED & module.IN_ONLYDIR, 0)

    def test_registration_option_bits_are_rejected_as_synthetic_event_flags(self):
        for flag in (module.IN_DONT_FOLLOW, module.IN_ONLYDIR):
            with self.subTest(flag=hex(flag)):
                raw = ev(wd=10, mask=module.IN_CREATE | flag,
                         data=named(b'public-child'))
                parsed = module._classify_stream(raw, 9, directory_watch=10)
                self.assertFalse(parsed['well_formed'])
                outcome = module._evaluate(
                    b'public', b'public', raw, 9, True, False,
                    directory_watch=10, directory_inventory_names=('sample',))
                self.assertEqual(outcome['status'], 'BLOCKED')
                self.assertFalse(outcome['can_authorize_dispatch'])


    def test_watch_path_encoder_rejects_forged_c_path_bytes(self):
        path = Path('/tmp/public-sample')
        class EvilBytes(bytes):
            pass
        for forged in (None, True, '', b'', b'/tmp/public-sample\x00suffix',
                       b'/tmp/other-sample', b'/etc/not-disposable',
                       bytearray(b'/tmp/public-sample'),
                       EvilBytes(b'/tmp/public-sample'), b'x' * 4096):
            with self.subTest(forged=repr(forged)):
                with patch.object(module.os, 'fsencode', return_value=forged):
                    with self.assertRaisesRegex(OSError, 'pathname'):
                        module._checked_watch_path_bytes(path)

    def test_watch_path_encoder_accepts_exact_surrogateescaped_bytes(self):
        name = os.fsdecode(b'public-\xff-entry')
        path = Path('/tmp') / name
        self.assertEqual(module._checked_watch_path_bytes(path),
                         os.fsencode(path))
        self.assertEqual(module._checked_watch_path_bytes(Path('/tmp/sample')),
                         b'/tmp/sample')

    def test_forged_watch_path_encoding_closes_owned_nonstdio_fd(self):
        class Callable:
            def __init__(self, result):
                self.result = result
                self.calls = 0
            def __call__(self, *_args):
                self.calls += 1
                return self.result
        init = Callable(17)
        add = Callable(9)
        class FakeLib:
            inotify_init1 = init
            inotify_add_watch = add
        with patch.object(module.ctypes, 'CDLL', return_value=FakeLib()):
            with patch.object(module.os, 'fsencode', return_value=b'/etc/forged-path'):
                with patch.object(module.os, 'close') as close:
                    with self.assertRaisesRegex(OSError, 'pathname'):
                        module._start_watch(Path('/tmp/public-sample'))
                    close.assert_called_once_with(17)
        self.assertEqual(add.calls, 0)
        self.assertEqual(init.calls, 1)


    @unittest.skipUnless(sys.platform == 'linux', 'live disposable Linux inotify')
    def test_live_generated_regular_file_and_directory_watches_still_register(self):
        with tempfile.TemporaryDirectory(prefix='dec793-public-', dir='/tmp') as folder:
            source = Path(folder) / 'sample'
            source.write_bytes(module.BEFORE)
            fd, file_wd, directory_wd = module._start_watch(source)
            try:
                self.assertGreaterEqual(fd, 3)
                self.assertGreater(file_wd, 0)
                self.assertGreater(directory_wd, 0)
                self.assertNotEqual(file_wd, directory_wd)
                identity, content = module._snapshot_regular(source)
                self.assertEqual(content, module.BEFORE)
                st = os.stat(source)
                self.assertEqual(identity, (st.st_dev, st.st_ino))
            finally:
                os.close(fd)

    @unittest.skipUnless(sys.platform == 'linux' and hasattr(os, 'symlink'),
                         'live disposable Linux inotify symlink')
    def test_live_symlink_watch_target_cannot_be_regular_snapshot(self):
        with tempfile.TemporaryDirectory(prefix='dec793-public-', dir='/tmp') as folder:
            source = Path(folder) / 'sample'
            alias = Path(folder) / 'public-symlink'
            source.write_bytes(module.BEFORE)
            alias.symlink_to(source)
            # With IN_DONT_FOLLOW, watch registration may watch the symlink
            # itself. O_NOFOLLOW must still refuse the alias as a sample.
            fd, file_wd, directory_wd = module._start_watch(alias)
            try:
                self.assertGreaterEqual(fd, 3)
                self.assertNotEqual(file_wd, directory_wd)
                with self.assertRaises(OSError):
                    module._snapshot_regular(alias)
            finally:
                os.close(fd)


    def test_watch_path_encoder_rejects_outside_tmp_or_traversal(self):
        rejected = ('relative/sample', '/etc/passwd', '/tmp2/sample',
                    '/tmp/../etc/passwd', '/tmp/private/../../etc',
                    '//tmp/public-sample', '/var/tmp/public-sample')
        for path in rejected:
            with self.subTest(path=path):
                with patch.object(module.os, 'fsencode',
                                  side_effect=AssertionError('must reject before encoding')) as encode:
                    with self.assertRaisesRegex(OSError, 'outside the /tmp scope'):
                        module._checked_watch_path_bytes(Path(path))
                    encode.assert_not_called()

    def test_watch_path_encoder_preserves_generated_tmp_root_and_children(self):
        for path in (Path('/tmp'), Path('/tmp/public-sample'),
                     Path('/tmp/dec677-disposable-public/sample')):
            with self.subTest(path=str(path)):
                self.assertEqual(module._checked_watch_path_bytes(path),
                                 os.fsencode(path))


    def test_watch_encoding_rejects_forged_fspath_and_encoder_agreement(self):
        path = Path('/tmp/actual-public-sample')
        # Materialize the Path's own textual representation BEFORE changing
        # the shared os.fspath wrapper. Python's lazy Path caches otherwise
        # let a patched wrapper influence this expected-value boundary.
        expected_path_text = str(path)
        self.assertEqual(expected_path_text, '/tmp/actual-public-sample')
        for forged in ('/tmp/another-public-sample', '/tmp',
                       '/etc/passwd', 'relative/public-sample'):
            with self.subTest(forged=forged):
                with patch.object(module.os, 'fspath', return_value=forged):
                    with patch.object(module.os, 'fsencode',
                                      side_effect=AssertionError('no encoding allowed')) as encode:
                        with self.assertRaisesRegex(OSError, 'fspath disagrees'):
                            module._checked_watch_path_bytes(path)
                        encode.assert_not_called()


    def test_watch_cold_path_refuses_forged_fspath_before_encoding(self):
        for forged in ('/tmp/unrelated-public', '/etc/passwd',
                       '/tmp/../public-substitute'):
            with self.subTest(forged=forged):
                # Do NOT warm str(path): the guard must work using the
                # actual source components despite a forged wrapper.
                path = Path('/tmp/dec677-disposable-public/sample')
                with patch.object(module.os, 'fspath', return_value=forged):
                    with patch.object(module.os, 'fsencode',
                                      side_effect=AssertionError('encoder must not run')) as encode:
                        with self.assertRaisesRegex(OSError, 'fspath disagrees'):
                            module._checked_watch_path_bytes(path)
                        encode.assert_not_called()

    def test_watch_encoding_plain_path_object_matches_native_fspath(self):
        path = Path('/tmp/dec677-disposable-public/sample')
        self.assertEqual(os.fspath(path), str(path))
        self.assertEqual(module._checked_watch_path_bytes(path), os.fsencode(path))


    def test_watch_encoder_refuses_custom_path_subclass_before_fspath(self):
        class ForgedPath(type(Path())):
            def __fspath__(self):
                raise AssertionError('injected path method must not run')
        path = ForgedPath('/tmp/public-sample')
        with patch.object(module.os, 'fsencode',
                          side_effect=AssertionError('injected encoder must not run')) as encode:
            with self.assertRaisesRegex(OSError, 'plain Path object'):
                module._checked_watch_path_bytes(path)
            encode.assert_not_called()

    def test_watch_encoder_refuses_string_bytes_and_keeps_plain_path(self):
        for wrong in ('/tmp/public-sample', b'/tmp/public-sample', None, True):
            with self.subTest(value=repr(wrong)):
                with patch.object(module.os, 'fsencode',
                                  side_effect=AssertionError('no encoding')) as encode:
                    with self.assertRaisesRegex(OSError, 'plain Path object'):
                        module._checked_watch_path_bytes(wrong)
                    encode.assert_not_called()
        self.assertEqual(module._checked_watch_path_bytes(Path('/tmp/public-sample')),
                         b'/tmp/public-sample')


    @unittest.skipUnless(sys.platform == 'linux', 'Linux disposable preflight')
    def test_runner_tmp_probe_exceptions_return_blocked_before_watch(self):
        for probe in ('isdir', 'islink'):
            with self.subTest(probe=probe):
                with patch.object(module.os.path, probe,
                                  side_effect=RuntimeError('synthetic tmp probe')):
                    with patch.object(module, '_start_watch') as register:
                        result = module.run_demo()
                self.assertEqual(result['status'], 'BLOCKED')
                self.assertIn('monitor unavailable', ' '.join(result['findings']))
                self.assertFalse(result['can_authorize_dispatch'])
                self.assertFalse(result['independent_os_proof_verified'])
                register.assert_not_called()

    @unittest.skipUnless(sys.platform == 'linux', 'Linux disposable preflight')
    def test_runner_tmp_probe_forged_truthiness_never_starts_watch(self):
        for probe, returned in (('isdir', 1), ('isdir', 'yes'),
                                ('islink', None), ('islink', 0),
                                ('islink', ''), ('islink', False)):
            if probe == 'islink' and returned is False:
                continue
            with self.subTest(probe=probe, returned=repr(returned)):
                with patch.object(module.os.path, 'isdir',
                                  return_value=returned if probe == 'isdir' else True):
                    with patch.object(module.os.path, 'islink',
                                      return_value=returned if probe == 'islink' else False):
                        with patch.object(module, '_start_watch') as register:
                            result = module.run_demo()
                self.assertEqual(result['status'], 'BLOCKED')
                self.assertFalse(result['can_authorize_dispatch'])
                register.assert_not_called()


    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux observer')
    def test_hardlink_initial_alias_helper_requires_exact_true(self):
        class TruthBomb:
            def __bool__(self):
                raise AssertionError('must never evaluate injected truthiness')
        for injected in (1, 'yes', object(), TruthBomb(), False, None):
            with self.subTest(injected=type(injected).__name__):
                rd, wr = os.pipe()
                try:
                    with patch.object(module, '_start_watch', return_value=(rd, 9, 10)):
                        with patch.object(module, '_snapshot_regular',
                                          side_effect=lambda path: native_created_sample_snapshot(path)) as snap:
                            with patch.object(module.os, 'link', return_value=None):
                                with patch.object(module, '_plausible_generated_hardlink_pair',
                                                  return_value=injected) as verify:
                                    with patch.object(module, '_read_pending') as drain:
                                        result = module.run_demo(hardlink_negative=True)
                    self.assertEqual(result['status'], 'BLOCKED')
                    self.assertIn('negative alias not verified', ' '.join(result['findings']))
                    self.assertFalse(result['can_authorize_dispatch'])
                    self.assertFalse(result['independent_os_proof_verified'])
                    self.assertEqual(snap.call_count, 1)
                    verify.assert_called_once()
                    drain.assert_not_called()
                    with self.assertRaises(OSError):
                        os.fstat(rd)
                finally:
                    os.close(wr)

    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux observer')
    def test_hardlink_postrefusal_alias_helper_requires_exact_true(self):
        class TruthBomb:
            def __bool__(self):
                raise AssertionError('must never evaluate injected truthiness')
        for injected in (1, 'yes', object(), TruthBomb(), False, None):
            with self.subTest(injected=type(injected).__name__):
                rd, wr = os.pipe()
                try:
                    with patch.object(module, '_start_watch', return_value=(rd, 9, 10)):
                        with patch.object(module, '_snapshot_regular',
                                          side_effect=native_created_sample_sequence(module.BEFORE,
                                                       module._SnapshotHardlinkCountError('two links'))) as snap:
                            with patch.object(module.os, 'link', return_value=None):
                                with patch.object(module, '_plausible_generated_hardlink_pair',
                                                  side_effect=(True, injected)) as verify:
                                    with patch.object(module, '_read_pending') as drain:
                                        result = module.run_demo(hardlink_negative=True)
                    self.assertEqual(result['status'], 'BLOCKED')
                    self.assertIn('changed during guard probe', ' '.join(result['findings']))
                    self.assertNotIn('negative control blocked', ' '.join(result['findings']))
                    self.assertFalse(result['can_authorize_dispatch'])
                    self.assertEqual(snap.call_count, 2)
                    self.assertEqual(verify.call_count, 2)
                    drain.assert_not_called()
                    with self.assertRaises(OSError):
                        os.fstat(rd)
                finally:
                    os.close(wr)


    def test_runner_rejects_forged_linux_platform_without_tmp_probes(self):
        class EqualLinux:
            def __eq__(self, other):
                return other == 'linux'

            def __ne__(self, other):
                return other != 'linux'

        class LinuxSubclass(str):
            pass

        for injected in (EqualLinux(), LinuxSubclass('linux')):
            with self.subTest(kind=type(injected).__name__):
                with patch.object(module.sys, 'platform', injected):
                    with patch.object(module.os.path, 'isdir') as isdir:
                        with patch.object(module.os.path, 'islink') as islink:
                            with patch.object(module, '_start_watch') as register:
                                result = module.run_demo()
                self.assertEqual(result['status'], 'BLOCKED')
                self.assertIn('monitor unavailable', ' '.join(result['findings']))
                self.assertFalse(result['can_authorize_dispatch'])
                self.assertFalse(result['independent_os_proof_verified'])
                isdir.assert_not_called()
                islink.assert_not_called()
                register.assert_not_called()

    def test_runner_rejects_nonstr_and_nonlinux_platform_without_tmp_io(self):
        for injected in ('darwin', 'win32', None, 3, True):
            with self.subTest(platform=repr(injected)):
                with patch.object(module.sys, 'platform', injected):
                    with patch.object(module.os.path, 'isdir') as isdir:
                        with patch.object(module, '_start_watch') as register:
                            result = module.run_demo()
                self.assertEqual(result['status'], 'BLOCKED')
                self.assertFalse(result['can_authorize_dispatch'])
                self.assertFalse(result['independent_os_proof_verified'])
                isdir.assert_not_called()
                register.assert_not_called()


    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux /tmp')
    def test_runner_refuses_substituted_generated_tmp_folder_before_write(self):
        class TempdirSubclass(str):
            pass

        candidate = '/tmp/dec677-disposable-public123'
        bad_values = (
            '/var/tmp/dec677-disposable-public123',
            '/tmp/unrelated-public-folder',
            '/tmp/dec677-disposable-',
            '/tmp/../tmp/dec677-disposable-public123',
            '/tmp//dec677-disposable-public123',
            TempdirSubclass(candidate),
            b'/tmp/dec677-disposable-public123',
            None,
        )
        for injected in bad_values:
            with self.subTest(folder=repr(injected)):
                with patch.object(module.tempfile, 'TemporaryDirectory') as tempdir:
                    tempdir.return_value.__enter__.return_value = injected
                    with patch.object(module.Path, 'open') as write:
                        with patch.object(module, '_start_watch') as register:
                            result = module.run_demo()
                self.assertEqual(result['status'], 'BLOCKED')
                self.assertFalse(result['can_authorize_dispatch'])
                self.assertFalse(result['independent_os_proof_verified'])
                write.assert_not_called()
                register.assert_not_called()
                tempdir.assert_called_once_with(
                    prefix=module.DISPOSABLE_PREFIX, dir='/tmp')

    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux /tmp')
    def test_genuine_generated_tmp_folder_passes_lexical_prewrite_check(self):
        with tempfile.TemporaryDirectory(prefix=module.DISPOSABLE_PREFIX,
                                         dir='/tmp') as folder:
            checked = module._checked_generated_folder(folder)
            self.assertEqual(checked, Path(folder))
            self.assertEqual(checked.parent, Path('/tmp'))
            self.assertTrue(checked.name.startswith(module.DISPOSABLE_PREFIX))


    def test_inventory_encoder_substitution_blocks_direct_quiet_evidence(self):
        for substituted in (b'other', b'sample-extra', b'.', b'..', b'', b'a/b'):
            with self.subTest(substituted=substituted):
                with patch.object(module.os, 'fsencode', return_value=substituted):
                    self.assertFalse(module._plausible_inventory_basename('sample'))
                    result = module._evaluate(
                        b'public', b'public', b'', 9, True, False,
                        directory_watch=10, directory_inventory_names=('sample',))
                self.assertEqual(result['status'], 'BLOCKED')
                self.assertFalse(
                    result['observed_checks']['no_directory_entry_mutations'])
                self.assertFalse(result['can_authorize_dispatch'])
                self.assertFalse(result['independent_os_proof_verified'])

    def test_inventory_exact_native_and_surrogateescaped_names_still_validate(self):
        for name in ('sample', 'a' * 255, os.fsdecode(b'public-' + bytes([255]) + b'-entry')):
            with self.subTest(name=repr(name)):
                self.assertTrue(module._plausible_inventory_basename(name))
        with patch.object(module.os, 'fsencode', return_value=b'a' * 255):
            self.assertFalse(module._plausible_inventory_basename('sample'))

    def test_bounded_inventory_scanner_rejects_substituted_encoder_bytes(self):
        class Entry:
            name = 'sample'
        class Scan:
            def __enter__(self):
                return self
            def __exit__(self, *_args):
                return False
            def __iter__(self):
                return iter((Entry(),))
        for wrong in (b'other', b'sample-substitution', b'x' * 255):
            with self.subTest(encoded=wrong):
                with patch.object(module.os, 'scandir', return_value=Scan()):
                    with patch.object(module.os, 'fsencode', return_value=wrong):
                        with self.assertRaisesRegex(OSError, 'malformed entry name'):
                            module._bounded_inventory_names(Path('/tmp/public-fake-only'))

    @unittest.skipUnless(sys.platform == 'linux', 'generated Linux /tmp inventory')
    def test_live_generated_inventory_surrogateescape_matches_real_bytes(self):
        with tempfile.TemporaryDirectory(prefix='dec805-public-', dir='/tmp') as folder:
            name = os.fsdecode(b'public-' + bytes([255]) + b'-entry')
            sample = Path(folder) / name
            sample.write_bytes(b'PUBLIC')
            self.assertEqual(os.fsencode(name), b'public-' + bytes([255]) + b'-entry')
            self.assertEqual(module._bounded_inventory_names(Path(folder)), (name,))


    @unittest.skipUnless(sys.platform == 'linux' and hasattr(os, 'symlink'),
                         'disposable Linux no-follow directory test')
    def test_generated_folder_refuses_symlink_path_even_with_valid_prefix(self):
        with tempfile.TemporaryDirectory(prefix=module.DISPOSABLE_PREFIX,
                                         dir='/tmp') as real_folder:
            alias = Path(real_folder + '-alias')
            alias.symlink_to(real_folder, target_is_directory=True)
            try:
                with self.assertRaisesRegex(OSError, 'not a real directory'):
                    module._checked_generated_folder(str(alias))
                self.assertEqual(module._checked_generated_folder(real_folder),
                                 Path(real_folder))
            finally:
                alias.unlink()

    def test_generated_folder_rejects_forged_lstat_mode_results(self):
        class FakeStat:
            def __init__(self, mode):
                self.st_mode = mode
        class ForgedInt(int):
            def __eq__(self, _other):
                return True
        path = '/tmp/' + module.DISPOSABLE_PREFIX + 'public-fixture'
        for mode in (module.stat.S_IFLNK | 0o777, module.stat.S_IFREG | 0o600,
                     True, ForgedInt(module.stat.S_IFDIR | 0o700),
                     (1 << 20) | module.stat.S_IFDIR):
            with self.subTest(mode=repr(mode)):
                with patch.object(module.os, 'lstat',
                                  return_value=FakeStat(mode)):
                    with self.assertRaisesRegex(OSError, 'not a real directory'):
                        module._checked_generated_folder(path)
        with patch.object(module.os, 'lstat',
                          side_effect=RuntimeError('synthetic lstat wrapper')):
            with self.assertRaisesRegex(OSError, 'could not be lstat checked'):
                module._checked_generated_folder(path)

    @unittest.skipUnless(sys.platform == 'linux' and hasattr(os, 'symlink'),
                         'disposable Linux prewrite symlink test')
    def test_runner_rejects_symlinked_generated_tempdir_before_sample_write(self):
        with tempfile.TemporaryDirectory(prefix=module.DISPOSABLE_PREFIX,
                                         dir='/tmp') as real_folder:
            alias = Path(real_folder + '-alias')
            alias.symlink_to(real_folder, target_is_directory=True)
            try:
                with patch.object(module.tempfile, 'TemporaryDirectory') as tempdir:
                    tempdir.return_value.__enter__.return_value = str(alias)
                    with patch.object(module.Path, 'open') as writer:
                        with patch.object(module, '_start_watch') as watch:
                            result = module.run_demo()
                self.assertEqual(result['status'], 'BLOCKED')
                self.assertFalse(result['can_authorize_dispatch'])
                writer.assert_not_called()
                watch.assert_not_called()
            finally:
                alias.unlink()


    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux directory permissions')
    def test_generated_folder_rejects_nonprivate_mode_then_accepts_0700(self):
        with tempfile.TemporaryDirectory(prefix=module.DISPOSABLE_PREFIX,
                                         dir='/tmp') as folder:
            self.assertEqual(module._checked_generated_folder(folder), Path(folder))
            for unsafe in (0o755, 0o770, 0o777, 0o1700):
                with self.subTest(mode=oct(unsafe)):
                    os.chmod(folder, unsafe)
                    try:
                        with self.assertRaisesRegex(OSError, 'not private'):
                            module._checked_generated_folder(folder)
                    finally:
                        os.chmod(folder, 0o700)
            self.assertEqual(module._checked_generated_folder(folder), Path(folder))

    @unittest.skipUnless(sys.platform == 'linux', 'Linux effective UID identity')
    def test_generated_folder_rejects_foreign_or_forged_owner_ids(self):
        class FakeStat:
            st_mode = module.stat.S_IFDIR | 0o700
            st_dev = 1
            st_ino = 2
            st_gid = 0
            st_nlink = 2
            def __init__(self, uid):
                self.st_uid = uid
        class ForgedInt(int):
            def __eq__(self, _other):
                return True
        path = '/tmp/' + module.DISPOSABLE_PREFIX + 'public-test'
        euid = os.geteuid()
        invalid = ((euid + 1) % (1 << 32), True, -1, 1 << 32,
                   str(euid), ForgedInt(euid))
        for owner in invalid:
            with self.subTest(owner=repr(owner)):
                with patch.object(module.os, 'lstat', return_value=FakeStat(owner)):
                    with self.assertRaisesRegex(OSError, 'not private'):
                        module._checked_generated_folder(path)
        with patch.object(module.os, 'lstat', return_value=FakeStat(euid)):
            self.assertEqual(module._checked_generated_folder(path), Path(path))

    @unittest.skipUnless(sys.platform == 'linux', 'Linux effective UID identity')
    def test_generated_folder_refuses_malformed_effective_owner_probe(self):
        class FakeStat:
            st_mode = module.stat.S_IFDIR | 0o700
            st_uid = 0
        path = '/tmp/' + module.DISPOSABLE_PREFIX + 'public-test'
        for forged in (True, 1.0, '0', -1, 1 << 32):
            with self.subTest(value=repr(forged)):
                with patch.object(module.os, 'lstat', return_value=FakeStat()):
                    with patch.object(module.os, 'geteuid', return_value=forged):
                        with self.assertRaisesRegex(OSError, 'not private'):
                            module._checked_generated_folder(path)
        with patch.object(module.os, 'lstat', return_value=FakeStat()):
            with patch.object(module.os, 'geteuid',
                              side_effect=RuntimeError('synthetic owner API')):
                with self.assertRaisesRegex(OSError, 'owner probe failed'):
                    module._checked_generated_folder(path)


    def test_inventory_nonutf8_byte_roundtrip_rejects_encoder_substitution(self):
        raw_name = b'public-' + bytes([255]) + b'-entry'
        decoded = os.fsdecode(raw_name)
        self.assertEqual(os.fsencode(decoded), raw_name)
        self.assertTrue(module._plausible_inventory_basename(decoded))
        self.assertFalse(module._plausible_inventory_basename(''))
        with patch.object(module.os, 'fsencode', return_value=b'public-other-entry'):
            self.assertFalse(module._plausible_inventory_basename(decoded))


    @unittest.skipUnless(sys.platform == 'linux', 'native generated /tmp permissions')
    def test_runner_blocks_shared_tempdir_before_writing_or_watching(self):
        with tempfile.TemporaryDirectory(prefix=module.DISPOSABLE_PREFIX,
                                         dir='/tmp') as folder:
            for mode in (0o755, 0o777):
                with self.subTest(mode=oct(mode)):
                    os.chmod(folder, mode)
                    try:
                        with patch.object(module.tempfile, 'TemporaryDirectory') as tempdir:
                            tempdir.return_value.__enter__.return_value = folder
                            with patch.object(module.Path, 'open') as write:
                                with patch.object(module, '_start_watch') as start:
                                    receipt = module.run_demo()
                        self.assertEqual(receipt['status'], 'BLOCKED')
                        self.assertFalse(receipt['can_authorize_dispatch'])
                        self.assertFalse(receipt['independent_os_proof_verified'])
                        write.assert_not_called()
                        start.assert_not_called()
                    finally:
                        os.chmod(folder, 0o700)


    @unittest.skipUnless(sys.platform == 'linux', 'Linux generated folder metadata')
    def test_generated_folder_rejects_impossible_device_inode_identity(self):
        class FakeStat:
            def __init__(self, **changes):
                self.st_mode = module.stat.S_IFDIR | 0o700
                self.st_uid = os.geteuid()
                self.st_dev = 1
                self.st_ino = 2
                self.st_gid = 0
                self.st_nlink = 2
                for field, value in changes.items():
                    setattr(self, field, value)

        class ForgedInt(int):
            def __eq__(self, _other):
                return True

        folder = '/tmp/' + module.DISPOSABLE_PREFIX + 'public-test'
        invalid = (
            ('st_dev', -1), ('st_dev', True), ('st_dev', 1 << 64),
            ('st_dev', ForgedInt(1)), ('st_ino', 0), ('st_ino', -1),
            ('st_ino', True), ('st_ino', 1 << 64), ('st_ino', ForgedInt(2))
        )
        for field, value in invalid:
            with self.subTest(field=field, value=repr(value)):
                with patch.object(module.os, 'lstat',
                                  return_value=FakeStat(**{field: value})):
                    with self.assertRaisesRegex(OSError, 'identity malformed'):
                        module._checked_generated_folder(folder)
        with patch.object(module.os, 'lstat', return_value=FakeStat()):
            self.assertEqual(module._checked_generated_folder(folder), Path(folder))

    @unittest.skipUnless(sys.platform == 'linux', 'native Linux /tmp inode')
    def test_native_private_tempdir_has_bounded_device_inode_identity(self):
        with tempfile.TemporaryDirectory(prefix=module.DISPOSABLE_PREFIX,
                                         dir='/tmp') as folder:
            st = os.lstat(folder)
            self.assertGreater(st.st_ino, 0)
            self.assertTrue(module.stat.S_ISDIR(st.st_mode))
            self.assertEqual(module._checked_generated_folder(folder), Path(folder))


    @unittest.skipUnless(sys.platform == 'linux', 'Linux generated tempdir stat')
    def test_generated_folder_refuses_malformed_gid_and_nlink_metadata(self):
        class FakeStat:
            st_mode = module.stat.S_IFDIR | 0o700
            st_dev = 1
            st_ino = 2
            st_uid = os.geteuid()
            st_gid = 0
            st_nlink = 2

        class ForgedInt(int):
            def __eq__(self, _other):
                return True

        folder = '/tmp/' + module.DISPOSABLE_PREFIX + 'public-test'
        for field, value in (
            ('st_gid', -1), ('st_gid', True), ('st_gid', 1 << 32),
            ('st_gid', ForgedInt(0)), ('st_nlink', 0),
            ('st_nlink', -1), ('st_nlink', True),
            ('st_nlink', 1 << 64), ('st_nlink', ForgedInt(2))
        ):
            with self.subTest(field=field, value=repr(value)):
                record = FakeStat()
                setattr(record, field, value)
                with patch.object(module.os, 'lstat', return_value=record):
                    with self.assertRaisesRegex(OSError, 'remaining metadata malformed'):
                        module._checked_generated_folder(folder)
        with patch.object(module.os, 'lstat', return_value=FakeStat()):
            self.assertEqual(module._checked_generated_folder(folder), Path(folder))

    @unittest.skipUnless(sys.platform == 'linux', 'native Linux generated directory')
    def test_native_generated_folder_gid_nlink_are_bounded(self):
        with tempfile.TemporaryDirectory(prefix=module.DISPOSABLE_PREFIX,
                                         dir='/tmp') as folder:
            st = os.lstat(folder)
            self.assertIs(type(st.st_gid), int)
            self.assertIs(type(st.st_nlink), int)
            self.assertGreaterEqual(st.st_nlink, 1)
            self.assertEqual(module._checked_generated_folder(folder), Path(folder))


    @unittest.skipUnless(sys.platform == 'linux' and hasattr(os, 'symlink'),
                         'disposable Linux sample prewrite controls')
    def test_runner_rejects_preexisting_public_file_or_symlink_before_write(self):
        for symlink in (False, True):
            with self.subTest(symlink=symlink):
                with tempfile.TemporaryDirectory(prefix=module.DISPOSABLE_PREFIX,
                                                 dir='/tmp') as folder:
                    sample = Path(folder) / 'sample'
                    target = Path(folder) / 'public-target'
                    target.write_bytes(b'UNCHANGED-PUBLIC')
                    if symlink:
                        sample.symlink_to(target)
                    else:
                        sample.write_bytes(b'UNCHANGED-PUBLIC')
                    with patch.object(module.tempfile, 'TemporaryDirectory') as provider:
                        provider.return_value.__enter__.return_value = folder
                        with patch.object(module.Path, 'open') as writer:
                            with patch.object(module, '_start_watch') as watch:
                                # Deliberately spoof empty prewrite inventory
                                # so the specific sample lstat guard is tested.
                                with patch.object(module, '_bounded_inventory_names',
                                                  return_value=()):
                                    receipt = module.run_demo()
                    self.assertEqual(receipt['status'], 'BLOCKED')
                    self.assertFalse(receipt['can_authorize_dispatch'])
                    self.assertFalse(receipt['independent_os_proof_verified'])
                    writer.assert_not_called()
                    watch.assert_not_called()
                    self.assertEqual(sample.read_bytes(), b'UNCHANGED-PUBLIC')
                    self.assertEqual(target.read_bytes(), b'UNCHANGED-PUBLIC')

    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux sample prewrite')
    def test_runner_rejects_unexpected_sample_lstat_failure_before_write(self):
        native_lstat = os.lstat

        def fail_generated_sample(path, *args, **kwargs):
            if os.fspath(path).endswith('/sample'):
                raise RuntimeError('synthetic sample stat failure')
            return native_lstat(path, *args, **kwargs)

        with patch.object(module.os, 'lstat', side_effect=fail_generated_sample):
            with patch.object(module.Path, 'open') as write:
                with patch.object(module, '_start_watch') as watch:
                    receipt = module.run_demo()
        self.assertEqual(receipt['status'], 'BLOCKED')
        self.assertFalse(receipt['can_authorize_dispatch'])
        self.assertFalse(receipt['independent_os_proof_verified'])
        write.assert_not_called()
        watch.assert_not_called()


    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux exclusive file create')
    def test_initial_exclusive_create_rejects_impossible_write_counts(self):
        for value in (None, True, False, 0, 1, len(module.BEFORE) - 1,
                      len(module.BEFORE) + 1, 'complete'):
            with self.subTest(value=repr(value)):
                with patch.object(module.Path, 'open') as opener:
                    opener.return_value.__enter__.return_value.fileno.return_value = 19
                    opener.return_value.__enter__.return_value.write.return_value = value
                    with patch.object(module, '_start_watch') as watch:
                        receipt = module.run_demo()
                self.assertEqual(receipt['status'], 'BLOCKED')
                self.assertFalse(receipt['can_authorize_dispatch'])
                self.assertFalse(receipt['independent_os_proof_verified'])
                opener.assert_called_once_with('xb')
                watch.assert_not_called()

    @unittest.skipUnless(sys.platform == 'linux' and hasattr(os, 'symlink'),
                         'native Linux exclusive file creation')
    def test_native_exclusive_create_refuses_symlink_without_touching_target(self):
        with tempfile.TemporaryDirectory(prefix='dec814-public-', dir='/tmp') as folder:
            source = Path(folder) / 'sample'
            target = Path(folder) / 'existing-public'
            target.write_bytes(b'UNCHANGED-PUBLIC')
            source.symlink_to(target)
            with self.assertRaises(FileExistsError):
                with source.open('xb') as stream:
                    stream.write(module.BEFORE)
            self.assertTrue(source.is_symlink())
            self.assertEqual(target.read_bytes(), b'UNCHANGED-PUBLIC')


    @unittest.skipUnless(sys.platform == 'linux' and hasattr(os, 'symlink'),
                         'native Linux exclusive creation race control')
    def test_false_absence_prewrite_lstat_cannot_bypass_exclusive_create(self):
        for symlink in (False, True):
            with self.subTest(symlink=symlink):
                with tempfile.TemporaryDirectory(prefix=module.DISPOSABLE_PREFIX,
                                                 dir='/tmp') as folder:
                    sample = Path(folder) / 'sample'
                    target = Path(folder) / 'public-existing'
                    target.write_bytes(b'UNCHANGED-PUBLIC')
                    if symlink:
                        sample.symlink_to(target)
                    else:
                        sample.write_bytes(b'UNCHANGED-PUBLIC')

                    original_lstat = os.lstat

                    def synthetic_missing_sample(path, *args, **kwargs):
                        if os.fspath(path) == str(sample):
                            raise FileNotFoundError(2, 'synthetic false absence')
                        return original_lstat(path, *args, **kwargs)

                    with patch.object(module.os, 'lstat',
                                      side_effect=synthetic_missing_sample):
                        with patch.object(module.tempfile, 'TemporaryDirectory') as tempdir:
                            tempdir.return_value.__enter__.return_value = folder
                            with patch.object(module, '_start_watch') as watch:
                                # Simulate both false empty-inventory evidence
                                # and false sample absence: O_EXCL must still
                                # reject the existing public sample object.
                                with patch.object(module, '_bounded_inventory_names',
                                                  return_value=()):
                                    receipt = module.run_demo()
                    self.assertEqual(receipt['status'], 'BLOCKED')
                    self.assertFalse(receipt['can_authorize_dispatch'])
                    self.assertFalse(receipt['independent_os_proof_verified'])
                    watch.assert_not_called()
                    self.assertEqual(sample.read_bytes(), b'UNCHANGED-PUBLIC')
                    self.assertEqual(target.read_bytes(), b'UNCHANGED-PUBLIC')
                    self.assertIs(sample.is_symlink(), symlink)


    @unittest.skipUnless(sys.platform == 'linux' and hasattr(os, 'link'),
                         'native Linux sample namespace collisions')
    def test_false_sample_absence_cannot_overwrite_hardlink_or_directory(self):
        for kind in ('hardlink', 'directory'):
            with self.subTest(kind=kind):
                with tempfile.TemporaryDirectory(prefix=module.DISPOSABLE_PREFIX,
                                                 dir='/tmp') as folder:
                    sample = Path(folder) / 'sample'
                    target = Path(folder) / 'public-hardlink-source'
                    target.write_bytes(b'PUBLIC-UNCHANGED')
                    if kind == 'hardlink':
                        os.link(target, sample)
                        original_inode = os.stat(target).st_ino
                    else:
                        sample.mkdir()
                        child = sample / 'public-unchanged-child'
                        child.write_bytes(b'PUBLIC-UNCHANGED')
                    native_lstat = os.lstat

                    def lie_missing(path, *args, **kwargs):
                        if os.fspath(path) == str(sample):
                            raise FileNotFoundError(2, 'synthetic absent sample')
                        return native_lstat(path, *args, **kwargs)

                    with patch.object(module.os, 'lstat', side_effect=lie_missing):
                        with patch.object(module.tempfile, 'TemporaryDirectory') as context:
                            context.return_value.__enter__.return_value = folder
                            with patch.object(module, '_start_watch') as watch:
                                # Keep the O_EXCL boundary under test even
                                # if a synthetic prior inventory lies empty.
                                with patch.object(module, '_bounded_inventory_names',
                                                  return_value=()):
                                    receipt = module.run_demo()
                    self.assertEqual(receipt['status'], 'BLOCKED')
                    self.assertFalse(receipt['can_authorize_dispatch'])
                    self.assertFalse(receipt['independent_os_proof_verified'])
                    watch.assert_not_called()
                    self.assertEqual(target.read_bytes(), b'PUBLIC-UNCHANGED')
                    if kind == 'hardlink':
                        self.assertEqual(sample.read_bytes(), b'PUBLIC-UNCHANGED')
                        self.assertEqual(os.stat(sample).st_ino, original_inode)
                    else:
                        self.assertTrue(sample.is_dir())
                        self.assertEqual(child.read_bytes(), b'PUBLIC-UNCHANGED')


    @unittest.skipUnless(sys.platform == 'linux', 'disposable Linux file close boundary')
    def test_initial_exclusive_close_failure_never_starts_watch(self):
        class RealisticPublicFdStat:
            st_mode = module.stat.S_IFREG | 0o600
            st_dev = 12
            st_ino = 99
            st_nlink = 1

        native_fstat = os.fstat

        def scoped_writer_fstat(fd):
            if fd == 19:
                return RealisticPublicFdStat()
            return native_fstat(fd)

        with patch.object(module.Path, 'open') as opener:
            stream = opener.return_value.__enter__.return_value
            stream.fileno.return_value = 19
            stream.write.return_value = len(module.BEFORE)
            opener.return_value.__exit__.side_effect = OSError(
                28, 'synthetic public file close failure')
            with patch.object(module.os, 'fstat',
                              side_effect=scoped_writer_fstat) as fst:
                with patch.object(module, '_start_watch') as watch:
                    receipt = module.run_demo()
        self.assertEqual(receipt['status'], 'BLOCKED')
        self.assertFalse(receipt['can_authorize_dispatch'])
        self.assertFalse(receipt['independent_os_proof_verified'])
        stream.write.assert_called_once_with(module.BEFORE)
        self.assertEqual(sum(call.args == (19,) for call in fst.call_args_list), 1)
        opener.return_value.__exit__.assert_called_once_with(None, None, None)
        watch.assert_not_called()

    @unittest.skipUnless(sys.platform == 'linux', 'exclusive writer fstat exception')
    def test_initial_writer_fstat_failure_blocks_and_exits_before_watcher(self):
        native_fstat = os.fstat
        for failure in (OSError(9, 'synthetic unreadable writer inode'),
                        RuntimeError('synthetic fstat wrapper fault')):
            with self.subTest(failure=type(failure).__name__):
                def scoped_writer_failure(fd):
                    if fd == 19:
                        raise failure
                    return native_fstat(fd)

                with patch.object(module.Path, 'open') as opener:
                    stream = opener.return_value.__enter__.return_value
                    stream.fileno.return_value = 19
                    stream.write.return_value = len(module.BEFORE)
                    with patch.object(module.os, 'fstat',
                                      side_effect=scoped_writer_failure) as fst:
                        with patch.object(module, '_start_watch') as watcher:
                            receipt = module.run_demo()
                self.assertEqual(receipt['status'], 'BLOCKED')
                self.assertFalse(receipt['can_authorize_dispatch'])
                self.assertFalse(receipt['independent_os_proof_verified'])
                stream.write.assert_called_once_with(module.BEFORE)
                self.assertEqual(sum(call.args == (19,) for call in fst.call_args_list), 1)
                opener.return_value.__exit__.assert_called_once()
                watcher.assert_not_called()

    @unittest.skipUnless(sys.platform == 'linux', 'native Linux exclusive baseline')
    def test_native_exclusive_creation_produces_exact_readable_source(self):
        with tempfile.TemporaryDirectory(prefix='dec817-public-', dir='/tmp') as folder:
            sample = Path(folder) / 'sample'
            with sample.open('xb') as writer:
                nbytes = writer.write(module.BEFORE)
                self.assertIs(type(nbytes), int)
                self.assertEqual(nbytes, len(module.BEFORE))
            identity, content = module._snapshot_regular(sample)
            stat_record = os.stat(sample)
            self.assertEqual(identity, (stat_record.st_dev, stat_record.st_ino))
            self.assertEqual(content, module.BEFORE)
            with self.assertRaises(FileExistsError):
                sample.open('xb')


    @unittest.skipUnless(sys.platform == 'linux', 'initial generated Linux fd boundary')
    def test_initial_exclusive_open_refuses_stdio_and_forged_fd_before_write(self):
        class ForgedInt(int):
            def __eq__(self, _other):
                return True

        for invalid in (None, True, 0, 1, 2, -1, 1 << 31,
                        '3', 3.0, ForgedInt(19)):
            with self.subTest(fd=repr(invalid)):
                with patch.object(module.Path, 'open') as opener:
                    stream = opener.return_value.__enter__.return_value
                    stream.fileno.return_value = invalid
                    with patch.object(module, '_start_watch') as watch:
                        receipt = module.run_demo()
                self.assertEqual(receipt['status'], 'BLOCKED')
                self.assertFalse(receipt['can_authorize_dispatch'])
                self.assertFalse(receipt['independent_os_proof_verified'])
                stream.write.assert_not_called()
                watch.assert_not_called()

    @unittest.skipUnless(sys.platform == 'linux', 'native Linux nonstdio sample fd')
    def test_native_exclusive_generated_file_uses_nonstdio_fd(self):
        with tempfile.TemporaryDirectory(prefix='dec818-public-', dir='/tmp') as folder:
            sample = Path(folder) / 'sample'
            with sample.open('xb') as stream:
                fd = stream.fileno()
                self.assertIs(type(fd), int)
                self.assertGreaterEqual(fd, 3)
                self.assertLessEqual(fd, module.MAX_FILE_DESCRIPTOR)
                self.assertEqual(stream.write(module.BEFORE), len(module.BEFORE))
            self.assertEqual(sample.read_bytes(), module.BEFORE)


    @unittest.skipUnless(sys.platform == 'linux', 'initial public sample fd exceptions')
    def test_initial_exclusive_fd_getter_exceptions_cannot_write_or_watch(self):
        for failure in (OSError(9, 'synthetic bad fd'),
                        RuntimeError('synthetic fileno wrapper failure'),
                        ValueError('synthetic fileno misuse')):
            with self.subTest(error=type(failure).__name__):
                with patch.object(module.Path, 'open') as opener:
                    stream = opener.return_value.__enter__.return_value
                    stream.fileno.side_effect = failure
                    with patch.object(module, '_start_watch') as watch:
                        receipt = module.run_demo()
                self.assertEqual(receipt['status'], 'BLOCKED')
                self.assertFalse(receipt['can_authorize_dispatch'])
                self.assertFalse(receipt['independent_os_proof_verified'])
                stream.fileno.assert_called_once_with()
                stream.write.assert_not_called()
                watch.assert_not_called()

    @unittest.skipUnless(sys.platform == 'linux', 'initial public sample writer errors')
    def test_initial_exclusive_writer_exceptions_cannot_start_watch(self):
        for failure in (OSError(28, 'synthetic disk full'),
                        RuntimeError('synthetic writer wrapper failure')):
            with self.subTest(error=type(failure).__name__):
                with patch.object(module.Path, 'open') as opener:
                    stream = opener.return_value.__enter__.return_value
                    stream.fileno.return_value = 19
                    stream.write.side_effect = failure
                    with patch.object(module, '_start_watch') as watch:
                        receipt = module.run_demo()
                self.assertEqual(receipt['status'], 'BLOCKED')
                self.assertFalse(receipt['can_authorize_dispatch'])
                self.assertFalse(receipt['independent_os_proof_verified'])
                stream.write.assert_called_once_with(module.BEFORE)
                watch.assert_not_called()

    @unittest.skipUnless(sys.platform == 'linux', 'native disposable Linux file cleanup')
    def test_initial_native_sample_fd_closes_after_fileno_or_write_exception(self):
        native_open = Path.open
        for fault in ('fileno', 'write'):
            with self.subTest(fault=fault):
                opened = []

                class FaultyPublicWriter:
                    def __init__(self, file):
                        self.file = file
                        self.fd = file.fileno()

                    def __enter__(self):
                        return self

                    def __exit__(self, exc_type, exc_value, traceback):
                        return self.file.__exit__(exc_type, exc_value, traceback)

                    def fileno(self):
                        if fault == 'fileno':
                            raise RuntimeError('synthetic unreadable initial fd')
                        return self.file.fileno()

                    def write(self, data):
                        if fault == 'write':
                            raise OSError(28, 'synthetic initial write failure')
                        return self.file.write(data)

                def controlled_open(path, mode='r', *args, **kwargs):
                    file = native_open(path, mode, *args, **kwargs)
                    if mode == 'xb':
                        writer = FaultyPublicWriter(file)
                        opened.append(writer)
                        return writer
                    return file

                with patch.object(module.Path, 'open', autospec=True,
                                  side_effect=controlled_open):
                    with patch.object(module, '_start_watch') as watch:
                        outcome = module.run_demo()
                self.assertEqual(outcome['status'], 'BLOCKED')
                self.assertFalse(outcome['can_authorize_dispatch'])
                self.assertFalse(outcome['independent_os_proof_verified'])
                self.assertEqual(len(opened), 1)
                self.assertTrue(opened[0].file.closed)
                with self.assertRaises(OSError):
                    os.fstat(opened[0].fd)
                watch.assert_not_called()

    @unittest.skipUnless(sys.platform == 'linux', 'native disposable Linux close')
    def test_initial_native_sample_fd_closes_before_postclose_error_blocks(self):
        native_open = Path.open
        opened = []

        class PostcloseFailure:
            def __init__(self, file):
                self.file = file
                self.fd = file.fileno()

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                self.file.__exit__(exc_type, exc_value, traceback)
                raise OSError(5, 'synthetic postclose failure')

            def fileno(self):
                return self.file.fileno()

            def write(self, data):
                return self.file.write(data)

        def controlled_open(path, mode='r', *args, **kwargs):
            file = native_open(path, mode, *args, **kwargs)
            if mode == 'xb':
                writer = PostcloseFailure(file)
                opened.append(writer)
                return writer
            return file

        with patch.object(module.Path, 'open', autospec=True,
                          side_effect=controlled_open):
            with patch.object(module, '_start_watch') as watch:
                outcome = module.run_demo()
        self.assertEqual(outcome['status'], 'BLOCKED')
        self.assertFalse(outcome['can_authorize_dispatch'])
        self.assertFalse(outcome['independent_os_proof_verified'])
        self.assertEqual(len(opened), 1)
        self.assertTrue(opened[0].file.closed)
        with self.assertRaises(OSError):
            os.fstat(opened[0].fd)
        watch.assert_not_called()


    @unittest.skipUnless(sys.platform == 'linux', 'private disposable /tmp inventory')
    def test_prewrite_nonempty_generated_folder_blocks_without_sample_write(self):
        with tempfile.TemporaryDirectory(prefix=module.DISPOSABLE_PREFIX,
                                         dir='/tmp') as folder:
            occupied = Path(folder) / 'public-preexisting-sibling'
            occupied.write_bytes(b'UNCHANGED-PUBLIC')
            with patch.object(module.tempfile, 'TemporaryDirectory') as tempdir:
                tempdir.return_value.__enter__.return_value = folder
                with patch.object(module.Path, 'open') as writer:
                    with patch.object(module, '_start_watch') as watch:
                        receipt = module.run_demo()
            self.assertEqual(receipt['status'], 'BLOCKED')
            self.assertFalse(receipt['can_authorize_dispatch'])
            self.assertFalse(receipt['independent_os_proof_verified'])
            writer.assert_not_called()
            watch.assert_not_called()
            self.assertFalse((Path(folder) / 'sample').exists())
            self.assertEqual(occupied.read_bytes(), b'UNCHANGED-PUBLIC')

    @unittest.skipUnless(sys.platform == 'linux', 'private disposable /tmp inventory')
    def test_prewrite_inventory_rejects_injected_nonempty_or_malformed_results(self):
        class FakeTuple(tuple):
            pass

        for names in (('public-sibling',), ('sample',),
                      ['not-a-tuple'], None, True, FakeTuple(())):
            with self.subTest(names=repr(names)):
                with patch.object(module, '_bounded_inventory_names',
                                  return_value=names) as scan:
                    with patch.object(module.Path, 'open') as writer:
                        with patch.object(module, '_start_watch') as watch:
                            receipt = module.run_demo()
                self.assertEqual(receipt['status'], 'BLOCKED')
                self.assertFalse(receipt['can_authorize_dispatch'])
                self.assertFalse(receipt['independent_os_proof_verified'])
                scan.assert_called_once()
                writer.assert_not_called()
                watch.assert_not_called()

    @unittest.skipUnless(sys.platform == 'linux', 'native Linux public disposable control')
    def test_native_exclusive_sample_after_empty_prewrite_census_stays_local(self):
        # Real /tmp private directory, empty-directory census, O_EXCL writer,
        # baseline/final nofollow snapshots and bounded final inventory.
        # Only the inotify watcher and empty kernel queue are stubbed.
        read_fd, write_fd = os.pipe()
        try:
            with patch.object(module, '_start_watch', return_value=(read_fd, 9, 10)):
                with patch.object(module, '_read_pending', return_value=b'') as drain:
                    receipt = module.run_demo()
            self.assertEqual(receipt['status'], 'LOCAL_DISPOSABLE_WITNESS_UNVERIFIED')
            self.assertFalse(receipt['can_authorize_dispatch'])
            self.assertFalse(receipt['independent_os_proof_verified'])
            self.assertTrue(receipt['observed_checks']['final_digest_equal'])
            self.assertTrue(receipt['observed_checks']['watched_inode_matches_final_path'])
            drain.assert_called_once_with(read_fd)
            with self.assertRaises(OSError):
                os.fstat(read_fd)
        finally:
            os.close(write_fd)

    @unittest.skipUnless(sys.platform == 'linux', 'native empty generated directory control')
    def test_native_empty_generated_folder_writes_then_stops_before_watch(self):
        observed = []

        def halt_before_watch(path):
            observed.append((path, path.read_bytes()))
            raise OSError(5, 'synthetic stop before watch registration')

        with patch.object(module, '_start_watch', side_effect=halt_before_watch) as watch:
            receipt = module.run_demo()
        self.assertEqual(receipt['status'], 'BLOCKED')
        self.assertFalse(receipt['can_authorize_dispatch'])
        self.assertFalse(receipt['independent_os_proof_verified'])
        watch.assert_called_once()
        self.assertEqual(len(observed), 1)
        source, data = observed[0]
        self.assertEqual(type(source), type(Path()))
        self.assertEqual(source.name, 'sample')
        self.assertEqual(source.parent.parent, Path('/tmp'))
        self.assertTrue(source.parent.name.startswith(module.DISPOSABLE_PREFIX))
        self.assertEqual(data, module.BEFORE)
        self.assertFalse(source.parent.exists())

    @unittest.skipUnless(sys.platform == 'linux', 'prewrite bounded empty scanner errors')
    def test_prewrite_bounded_inventory_scanner_exceptions_block_before_writer(self):
        for failure in (OSError(5, 'synthetic scanner I/O failure'),
                        RuntimeError('synthetic scanner wrapper failure')):
            with self.subTest(error=type(failure).__name__):
                with patch.object(module, '_bounded_inventory_names',
                                  side_effect=failure) as scanner:
                    with patch.object(module.Path, 'open') as writer:
                        with patch.object(module, '_start_watch') as watcher:
                            receipt = module.run_demo()
                self.assertEqual(receipt['status'], 'BLOCKED')
                self.assertFalse(receipt['can_authorize_dispatch'])
                self.assertFalse(receipt['independent_os_proof_verified'])
                scanner.assert_called_once()
                writer.assert_not_called()
                watcher.assert_not_called()

    @unittest.skipUnless(sys.platform == 'linux' and hasattr(os, 'symlink'),
                         'native generated Linux prewatch symlink')
    def test_pre_watcher_native_symlink_swap_refuses_identical_public_bytes(self):
        read_fd, write_fd = os.pipe()
        observed = []
        try:
            def substitute_before_watch(path):
                original = path.read_bytes()
                target = path.parent / 'public-reference'
                target.write_bytes(original)
                path.unlink()
                path.symlink_to(target)
                observed.append((original, target.read_bytes(), path.is_symlink()))
                return read_fd, 9, 10

            with patch.object(module, '_start_watch',
                              side_effect=substitute_before_watch) as watch:
                with patch.object(module, '_read_pending') as drain:
                    receipt = module.run_demo()
            self.assertEqual(receipt['status'], 'BLOCKED')
            self.assertFalse(receipt['can_authorize_dispatch'])
            self.assertFalse(receipt['independent_os_proof_verified'])
            watch.assert_called_once()
            drain.assert_not_called()
            self.assertEqual(observed, [(module.BEFORE, module.BEFORE, True)])
            with self.assertRaises(OSError):
                os.fstat(read_fd)
        finally:
            os.close(write_fd)

    @unittest.skipUnless(sys.platform == 'linux' and hasattr(os, 'link'),
                         'native generated Linux prewatch hardlink')
    def test_pre_watcher_native_hardlink_alias_refuses_identical_public_inode(self):
        read_fd, write_fd = os.pipe()
        observed = []
        try:
            def link_before_watch(path):
                alias = path.parent / 'public-alias'
                os.link(path, alias)
                st = os.stat(path, follow_symlinks=False)
                observed.append((path.read_bytes(), alias.read_bytes(), st.st_nlink))
                return read_fd, 9, 10

            with patch.object(module, '_start_watch',
                              side_effect=link_before_watch) as watch:
                with patch.object(module, '_read_pending') as drain:
                    receipt = module.run_demo()
            self.assertEqual(receipt['status'], 'BLOCKED')
            self.assertFalse(receipt['can_authorize_dispatch'])
            self.assertFalse(receipt['independent_os_proof_verified'])
            watch.assert_called_once()
            drain.assert_not_called()
            self.assertEqual(observed, [(module.BEFORE, module.BEFORE, 2)])
            with self.assertRaises(OSError):
                os.fstat(read_fd)
        finally:
            os.close(write_fd)

    @unittest.skipUnless(sys.platform == 'linux', 'native generated Linux inode swap')
    def test_postcreate_prewatch_identical_regular_inode_swap_is_blocked(self):
        read_fd, write_fd = os.pipe()
        observed = []
        try:
            def substitute_identical_before_watch(path):
                original = os.stat(path, follow_symlinks=False)
                replacement = path.parent / 'public-replacement'
                replacement.write_bytes(module.BEFORE)
                changed = os.stat(replacement, follow_symlinks=False)
                self.assertNotEqual((original.st_dev, original.st_ino),
                                    (changed.st_dev, changed.st_ino))
                os.replace(replacement, path)
                observed.append((path.read_bytes(), original.st_ino,
                                 os.stat(path, follow_symlinks=False).st_ino))
                return read_fd, 9, 10

            with patch.object(module, '_start_watch',
                              side_effect=substitute_identical_before_watch) as watch:
                with patch.object(module, '_read_pending') as drain:
                    receipt = module.run_demo()
            self.assertEqual(receipt['status'], 'BLOCKED')
            self.assertFalse(receipt['can_authorize_dispatch'])
            self.assertFalse(receipt['independent_os_proof_verified'])
            watch.assert_called_once()
            drain.assert_not_called()
            self.assertEqual(len(observed), 1)
            self.assertEqual(observed[0][0], module.BEFORE)
            self.assertNotEqual(observed[0][1], observed[0][2])
            with self.assertRaises(OSError):
                os.fstat(read_fd)
        finally:
            os.close(write_fd)

    def test_initial_created_inode_identity_rejects_forged_stat_fields(self):
        class FakeStat:
            def __init__(self, **changes):
                self.st_mode = module.stat.S_IFREG | 0o600
                self.st_dev = 12
                self.st_ino = 99
                self.st_nlink = 1
                for field, value in changes.items():
                    setattr(self, field, value)

        self.assertEqual(module._checked_initial_sample_identity(FakeStat()),
                         (12, 99))
        malformed = (
            ('st_mode', True),
            ('st_mode', module.stat.S_IFLNK | 0o777),
            ('st_mode', 1 << 32),
            ('st_dev', -1),
            ('st_dev', 1 << 64),
            ('st_ino', 0),
            ('st_ino', 1 << 64),
            ('st_ino', False),
            ('st_nlink', 0),
            ('st_nlink', 2),
            ('st_nlink', 1.0),
        )
        for field, value in malformed:
            with self.subTest(field=field, value=repr(value)):
                with self.assertRaisesRegex(OSError, 'identity malformed'):
                    module._checked_initial_sample_identity(FakeStat(**{field: value}))
        with self.assertRaisesRegex(OSError, 'metadata unreadable'):
            module._checked_initial_sample_identity(object())

    def test_watch_path_raw_segments_avoid_lazy_os_fspath_normalization(self):
        # Real Path joining keeps constructor strings; os.fspath monkeypatch
        # must not also be allowed to forge the supposedly original target.
        for path in (Path('/tmp') / 'public-generated',
                     Path('/tmp/dec677-disposable-public') / 'sample'):
            with self.subTest(path=str(path)):
                self.assertEqual(module._checked_watch_path_bytes(path),
                                 os.fsencode(path))

        for forged in ('/tmp/public-substitute', '/etc/passwd'):
            with self.subTest(forged=forged):
                # Fresh, unmaterialized Path. Even the formerly vulnerable
                # Python 3.12 lazy parts computation cannot bless a forgery.
                cold = Path('/tmp/dec677-disposable-public') / 'sample'
                with patch.object(module.os, 'fspath', return_value=forged):
                    with patch.object(module.os, 'fsencode',
                                      side_effect=AssertionError('must not encode')) as encode:
                        with self.assertRaisesRegex(OSError, 'fspath disagrees'):
                            module._checked_watch_path_bytes(cold)
                        encode.assert_not_called()

    def test_watch_path_rejects_missing_or_malformed_original_raw_segments(self):
        for invalid in ([], [123], [True], [None], ['/tmp', ''],
                        ['relative', 'sample']):
            with self.subTest(parts=repr(invalid)):
                path = Path('/tmp/original-public-sample')
                path._raw_paths = invalid
                with patch.object(module.os, 'fsencode',
                                  side_effect=AssertionError('must not encode')) as encode:
                    with self.assertRaisesRegex(
                            OSError, 'raw segments|outside the /tmp scope'):
                        module._checked_watch_path_bytes(path)
                    encode.assert_not_called()

    @unittest.skipUnless(sys.platform == 'linux', 'native Linux baseline inode race')
    def test_native_same_bytes_swap_between_postwatch_lstat_and_snapshot_blocks(self):
        native_snapshot = module._snapshot_regular
        read_fd, write_fd = os.pipe()
        observed = []
        try:
            def replace_just_before_original_snapshot(path):
                before = os.stat(path, follow_symlinks=False)
                replacement = path.parent / 'public-late-replacement'
                replacement.write_bytes(module.BEFORE)
                replacement_stat = os.stat(replacement, follow_symlinks=False)
                self.assertNotEqual((before.st_dev, before.st_ino),
                                    (replacement_stat.st_dev, replacement_stat.st_ino))
                os.replace(replacement, path)
                snapshot = native_snapshot(path)
                observed.append((before.st_ino, snapshot[0][1], snapshot[1]))
                return snapshot

            with patch.object(module, '_start_watch', return_value=(read_fd, 9, 10)) as start:
                with patch.object(module, '_snapshot_regular',
                                  side_effect=replace_just_before_original_snapshot) as snapshots:
                    with patch.object(module, '_read_pending') as drain:
                        receipt = module.run_demo()
            self.assertEqual(receipt['status'], 'BLOCKED')
            self.assertFalse(receipt['can_authorize_dispatch'])
            self.assertFalse(receipt['independent_os_proof_verified'])
            self.assertEqual(len(observed), 1)
            self.assertNotEqual(observed[0][0], observed[0][1])
            self.assertEqual(observed[0][2], module.BEFORE)
            start.assert_called_once()
            snapshots.assert_called_once()
            drain.assert_not_called()
            with self.assertRaises(OSError):
                os.fstat(read_fd)
        finally:
            os.close(write_fd)

    def test_watch_fspath_mutation_cannot_rewrite_original_expected_path(self):
        # Preserve sibling #1040's regression on the native-baseline branch.
        # Under CPython the Path's original constructor segments are stored;
        # an injected wrapper must not rewrite the precomputed expectation.
        for forged in ('/tmp/unrelated-public', '/etc/passwd'):
            with self.subTest(forged=forged):
                path = Path('/tmp/dec677-disposable-public') / 'sample'
                original_parts = tuple(path._raw_paths)
                self.assertEqual(original_parts,
                                 ('/tmp/dec677-disposable-public', 'sample'))

                def mutate_and_forge(_path):
                    path._raw_paths[:] = [forged]
                    return forged

                with patch.object(module.os, 'fspath',
                                  side_effect=mutate_and_forge) as fspath:
                    with patch.object(module.os, 'fsencode',
                                      side_effect=AssertionError('encoder must not run')) as encode:
                        with self.assertRaisesRegex(OSError, 'raw segments changed during encoding'):
                            module._checked_watch_path_bytes(path)
                        encode.assert_not_called()
                    fspath.assert_called_once_with(path)
                self.assertEqual(path._raw_paths, [forged])

    def test_watch_path_mutation_with_honest_fspath_text_is_rejected(self):
        # The wrapper mutates the source Path but returns its old correct
        # spelling. Equality of returned bytes/text alone is insufficient.
        for forged in ('/tmp/other-public', '/etc/passwd'):
            with self.subTest(forged=forged, stage='fspath'):
                path = Path('/tmp/dec677-disposable-public') / 'sample'
                genuine = str(path)

                def mutate_fspath(_path):
                    path._raw_paths[:] = [forged]
                    return genuine

                with patch.object(module.os, 'fspath',
                                  side_effect=mutate_fspath) as fspath:
                    with patch.object(module.os, 'fsencode',
                                      side_effect=AssertionError('must not encode')) as encode:
                        with self.assertRaisesRegex(OSError, 'raw segments changed'):
                            module._checked_watch_path_bytes(path)
                        encode.assert_not_called()
                    fspath.assert_called_once_with(path)

            with self.subTest(forged=forged, stage='fsencode'):
                path = Path('/tmp/dec677-disposable-public') / 'sample'
                genuine = os.fsencode(path)

                def mutate_encoder(_path):
                    path._raw_paths[:] = [forged]
                    return genuine

                with patch.object(module.os, 'fsencode',
                                  side_effect=mutate_encoder) as encoder:
                    with self.assertRaisesRegex(OSError, 'raw segments changed'):
                        module._checked_watch_path_bytes(path)
                    encoder.assert_called_once_with(path)

    def test_generated_directory_inode_helper_refuses_malformed_metadata(self):
        class FakeStat:
            def __init__(self, **changes):
                self.st_mode = module.stat.S_IFDIR | 0o700
                self.st_dev = 12
                self.st_ino = 97
                self.st_uid = os.geteuid()
                self.st_gid = os.getegid()
                self.st_nlink = 2
                for key, value in changes.items():
                    setattr(self, key, value)

        self.assertEqual(
            module._checked_generated_directory_identity(FakeStat()), (12, 97))
        failures = (
            ('st_mode', True), ('st_mode', module.stat.S_IFREG | 0o600),
            ('st_mode', module.stat.S_IFDIR | 0o755),
            ('st_dev', False), ('st_dev', -1), ('st_dev', 1 << 64),
            ('st_ino', 0), ('st_ino', None),
            ('st_uid', (os.geteuid() + 1) % (1 << 32)),
            ('st_gid', -1), ('st_gid', True), ('st_nlink', 0),
            ('st_nlink', 1.0),
        )
        for field, value in failures:
            with self.subTest(field=field, value=repr(value)):
                with self.assertRaisesRegex(OSError, 'identity malformed'):
                    module._checked_generated_directory_identity(
                        FakeStat(**{field: value}))
        with self.assertRaisesRegex(OSError, 'identity unreadable'):
            module._checked_generated_directory_identity(object())

    @unittest.skipUnless(sys.platform == 'linux', 'generated native Linux parent inode')
    def test_private_parent_inode_switch_blocks_before_baseline_or_inventory(self):
        native_lstat = os.lstat
        native_snapshot = module._snapshot_regular

        for stage in ('after-watch', 'before-inventory'):
            with self.subTest(stage=stage):
                read_fd, write_fd = os.pipe()
                observed = {'folder': None, 'switch': False, 'changed': False}
                snap_calls = []

                class AlteredDirectoryStat:
                    def __init__(self, original):
                        self.original = original
                        self.st_ino = original.st_ino + 1

                    def __getattr__(self, field):
                        return getattr(self.original, field)

                def scoped_lstat(path, *args, **kwargs):
                    record = native_lstat(path, *args, **kwargs)
                    if (observed['switch'] and not observed['changed']
                            and observed['folder'] is not None
                            and os.fspath(path) == observed['folder']):
                        observed['changed'] = True
                        observed['switch'] = False
                        return AlteredDirectoryStat(record)
                    return record

                def register_watch(path):
                    observed['folder'] = os.fspath(path.parent)
                    if stage == 'after-watch':
                        observed['switch'] = True
                    return read_fd, 9, 10

                def real_snapshot_with_final_boundary(path):
                    result = native_snapshot(path)
                    snap_calls.append(result)
                    if stage == 'before-inventory' and len(snap_calls) == 2:
                        observed['switch'] = True
                    return result

                try:
                    with patch.object(module.os, 'lstat', side_effect=scoped_lstat):
                        with patch.object(module, '_start_watch',
                                          side_effect=register_watch) as watcher:
                            with patch.object(module, '_snapshot_regular',
                                              side_effect=real_snapshot_with_final_boundary) as snapshot:
                                with patch.object(module, '_read_pending') as drain:
                                    receipt = module.run_demo()
                    self.assertTrue(observed['changed'])
                    self.assertEqual(receipt['status'], 'BLOCKED')
                    self.assertFalse(receipt['can_authorize_dispatch'])
                    self.assertFalse(receipt['independent_os_proof_verified'])
                    watcher.assert_called_once()
                    self.assertEqual(snapshot.call_count,
                                     0 if stage == 'after-watch' else 2)
                    drain.assert_not_called()
                    with self.assertRaises(OSError):
                        os.fstat(read_fd)
                finally:
                    os.close(write_fd)

    @unittest.skipUnless(sys.platform == 'linux', 'generated Linux post-inventory identity')
    def test_post_inventory_parent_substitution_blocks_before_event_drain(self):
        native_lstat = os.lstat
        native_inventory = module._bounded_inventory_names
        for forgery in ('different-inode', 'bad-mode'):
            with self.subTest(forgery=forgery):
                read_fd, write_fd = os.pipe()
                state = {'folder': None, 'scans': 0, 'changed': False}

                class AlteredDirectoryStat:
                    def __init__(self, source):
                        self.source = source
                        if forgery == 'different-inode':
                            self.st_ino = source.st_ino + 1
                        else:
                            self.st_mode = module.stat.S_IFDIR | 0o755

                    def __getattr__(self, field):
                        return getattr(self.source, field)

                def register(path):
                    state['folder'] = os.fspath(path.parent)
                    return read_fd, 9, 10

                def scanned(folder):
                    names = native_inventory(folder)
                    state['scans'] += 1
                    return names

                def modified_lstat(path, *args, **kwargs):
                    real = native_lstat(path, *args, **kwargs)
                    if (state['scans'] == 2 and not state['changed']
                            and state['folder'] == os.fspath(path)):
                        state['changed'] = True
                        return AlteredDirectoryStat(real)
                    return real

                try:
                    with patch.object(module.os, 'lstat',
                                      side_effect=modified_lstat):
                        with patch.object(module, '_bounded_inventory_names',
                                          side_effect=scanned) as census:
                            with patch.object(module, '_start_watch',
                                              side_effect=register) as watch:
                                with patch.object(module, '_read_pending') as drain:
                                    receipt = module.run_demo()
                    self.assertEqual(state['scans'], 2)
                    self.assertTrue(state['changed'])
                    self.assertEqual(receipt['status'], 'BLOCKED')
                    self.assertFalse(receipt['can_authorize_dispatch'])
                    self.assertFalse(receipt['independent_os_proof_verified'])
                    census.assert_called()
                    watch.assert_called_once()
                    drain.assert_not_called()
                    with self.assertRaises(OSError):
                        os.fstat(read_fd)
                finally:
                    os.close(write_fd)

    @unittest.skipUnless(sys.platform == 'linux', 'generated Linux post-inventory lstat')
    def test_post_inventory_parent_stat_exception_blocks_without_drain(self):
        native_lstat = os.lstat
        native_inventory = module._bounded_inventory_names
        for error in (OSError(5, 'synthetic directory stat failure'),
                      RuntimeError('synthetic directory stat wrapper failure')):
            with self.subTest(error=type(error).__name__):
                read_fd, write_fd = os.pipe()
                state = {'folder': None, 'scans': 0, 'failed': False}

                def register(path):
                    state['folder'] = os.fspath(path.parent)
                    return read_fd, 9, 10

                def scanned(folder):
                    value = native_inventory(folder)
                    state['scans'] += 1
                    return value

                def modified_lstat(path, *args, **kwargs):
                    if (state['scans'] == 2 and not state['failed']
                            and os.fspath(path) == state['folder']):
                        state['failed'] = True
                        raise error
                    return native_lstat(path, *args, **kwargs)

                try:
                    with patch.object(module.os, 'lstat',
                                      side_effect=modified_lstat):
                        with patch.object(module, '_bounded_inventory_names',
                                          side_effect=scanned) as census:
                            with patch.object(module, '_start_watch',
                                              side_effect=register) as watch:
                                with patch.object(module, '_read_pending') as drain:
                                    receipt = module.run_demo()
                    self.assertEqual(state['scans'], 2)
                    self.assertTrue(state['failed'])
                    self.assertEqual(receipt['status'], 'BLOCKED')
                    self.assertFalse(receipt['can_authorize_dispatch'])
                    self.assertFalse(receipt['independent_os_proof_verified'])
                    self.assertEqual(census.call_count, 2)
                    watch.assert_called_once()
                    drain.assert_not_called()
                    with self.assertRaises(OSError):
                        os.fstat(read_fd)
                finally:
                    os.close(write_fd)


    @unittest.skipUnless(sys.platform == 'linux', 'generated Linux drain identity')
    def test_parent_change_during_event_drain_blocks_before_evaluation(self):
        native_lstat = os.lstat
        for tamper in ('inode', 'stat-error'):
            with self.subTest(tamper=tamper):
                read_fd, write_fd = os.pipe()
                state = {'folder': None, 'drained': False, 'altered': False}

                class AlteredDirectoryStat:
                    def __init__(self, original):
                        self.original = original
                        self.st_ino = original.st_ino + 1

                    def __getattr__(self, field):
                        return getattr(self.original, field)

                def register(path):
                    state['folder'] = os.fspath(path.parent)
                    return read_fd, 9, 10

                def drain(_fd):
                    state['drained'] = True
                    return b''

                def injected_lstat(path, *args, **kwargs):
                    if (state['drained'] and not state['altered']
                            and state['folder'] == os.fspath(path)):
                        state['altered'] = True
                        if tamper == 'stat-error':
                            raise OSError('synthetic postdrain parent stat error')
                        return AlteredDirectoryStat(
                            native_lstat(path, *args, **kwargs))
                    return native_lstat(path, *args, **kwargs)

                try:
                    with patch.object(module.os, 'lstat',
                                      side_effect=injected_lstat):
                        with patch.object(module, '_start_watch',
                                          side_effect=register) as watcher:
                            with patch.object(module, '_read_pending',
                                              side_effect=drain) as reader:
                                with patch.object(module, '_evaluate') as evaluate:
                                    receipt = module.run_demo()
                    self.assertTrue(state['drained'])
                    self.assertTrue(state['altered'])
                    self.assertEqual(receipt['status'], 'BLOCKED')
                    self.assertFalse(receipt['can_authorize_dispatch'])
                    self.assertFalse(receipt['independent_os_proof_verified'])
                    watcher.assert_called_once()
                    reader.assert_called_once_with(read_fd)
                    evaluate.assert_not_called()
                    with self.assertRaises(OSError):
                        os.fstat(read_fd)
                finally:
                    os.close(write_fd)


    @unittest.skipUnless(sys.platform == 'linux', 'generated Linux sample drain identity')
    def test_sample_substitution_during_event_drain_blocks_before_evaluation(self):
        native_lstat = os.lstat
        for tamper in ('inode', 'stat-error'):
            with self.subTest(tamper=tamper):
                read_fd, write_fd = os.pipe()
                state = {'sample': None, 'drained': False, 'altered': False}

                class AlteredSampleStat:
                    def __init__(self, original):
                        self.original = original
                        self.st_ino = original.st_ino + 1

                    def __getattr__(self, field):
                        return getattr(self.original, field)

                def register(path):
                    state['sample'] = os.fspath(path)
                    return read_fd, 9, 10

                def drain(_fd):
                    state['drained'] = True
                    return b''

                def injected_lstat(path, *args, **kwargs):
                    if (state['drained'] and not state['altered']
                            and state['sample'] == os.fspath(path)):
                        state['altered'] = True
                        if tamper == 'stat-error':
                            raise OSError('synthetic postdrain sample stat error')
                        return AlteredSampleStat(
                            native_lstat(path, *args, **kwargs))
                    return native_lstat(path, *args, **kwargs)

                try:
                    with patch.object(module.os, 'lstat',
                                      side_effect=injected_lstat):
                        with patch.object(module, '_start_watch',
                                          side_effect=register) as watcher:
                            with patch.object(module, '_read_pending',
                                              side_effect=drain) as reader:
                                with patch.object(module, '_evaluate') as evaluate:
                                    receipt = module.run_demo()
                    self.assertTrue(state['drained'])
                    self.assertTrue(state['altered'])
                    self.assertEqual(receipt['status'], 'BLOCKED')
                    self.assertFalse(receipt['can_authorize_dispatch'])
                    self.assertFalse(receipt['independent_os_proof_verified'])
                    watcher.assert_called_once()
                    reader.assert_called_once_with(read_fd)
                    evaluate.assert_not_called()
                    with self.assertRaises(OSError):
                        os.fstat(read_fd)
                finally:
                    os.close(write_fd)


    @unittest.skipUnless(sys.platform == 'linux', 'generated Linux sample drain size')
    def test_sample_size_change_during_event_drain_blocks_before_evaluation(self):
        for late_bytes in (b'', module.BEFORE + b'PUBLIC-APPEND'):
            with self.subTest(late_bytes=repr(late_bytes)):
                read_fd, write_fd = os.pipe()
                state = {'sample': None, 'drained': False,
                         'initial_inode': None, 'final_inode': None}

                def register(path):
                    state['sample'] = path
                    state['initial_inode'] = os.lstat(path).st_ino
                    return read_fd, 9, 10

                def drain(_fd):
                    state['sample'].write_bytes(late_bytes)
                    state['final_inode'] = os.lstat(state['sample']).st_ino
                    state['drained'] = True
                    return b''

                try:
                    with patch.object(module, '_start_watch',
                                      side_effect=register) as watcher:
                        with patch.object(module, '_read_pending',
                                          side_effect=drain) as reader:
                            with patch.object(module, '_evaluate') as evaluate:
                                receipt = module.run_demo()
                    self.assertTrue(state['drained'])
                    self.assertEqual(state['initial_inode'], state['final_inode'])
                    self.assertEqual(receipt['status'], 'BLOCKED')
                    self.assertFalse(receipt['can_authorize_dispatch'])
                    self.assertFalse(receipt['independent_os_proof_verified'])
                    watcher.assert_called_once()
                    reader.assert_called_once_with(read_fd)
                    evaluate.assert_not_called()
                    with self.assertRaises(OSError):
                        os.fstat(read_fd)
                finally:
                    os.close(write_fd)


    @unittest.skipUnless(sys.platform == 'linux', 'generated Linux postdrain size metadata')
    def test_postdrain_sample_size_metadata_must_be_plain_exact_integer(self):
        native_lstat = os.lstat
        expected = len(module.BEFORE)

        class EqualLength:
            def __eq__(self, other):
                raise AssertionError('must never consult forged equality')

        class IntSubclass(int):
            pass

        cases = (True, float(expected), str(expected),
                 IntSubclass(expected), EqualLength(),
                 RuntimeError('synthetic size metadata exception'))
        for forged in cases:
            with self.subTest(forged=type(forged).__name__):
                read_fd, write_fd = os.pipe()
                state = {'sample': None, 'drained': False, 'injected': False}

                class ForgedSizeRecord:
                    def __init__(self, original):
                        self.original = original

                    @property
                    def st_size(self):
                        if isinstance(forged, RuntimeError):
                            raise forged
                        return forged

                    def __getattr__(self, field):
                        return getattr(self.original, field)

                def register(path):
                    state['sample'] = os.fspath(path)
                    return read_fd, 9, 10

                def drain(_fd):
                    state['drained'] = True
                    return b''

                def scoped_lstat(path, *args, **kwargs):
                    record = native_lstat(path, *args, **kwargs)
                    if (state['drained'] and not state['injected']
                            and state['sample'] == os.fspath(path)):
                        state['injected'] = True
                        return ForgedSizeRecord(record)
                    return record

                try:
                    with patch.object(module.os, 'lstat',
                                      side_effect=scoped_lstat):
                        with patch.object(module, '_start_watch',
                                          side_effect=register) as watch:
                            with patch.object(module, '_read_pending',
                                              side_effect=drain) as reader:
                                with patch.object(module, '_evaluate') as evaluate:
                                    receipt = module.run_demo()
                    self.assertTrue(state['injected'])
                    self.assertEqual(receipt['status'], 'BLOCKED')
                    self.assertFalse(receipt['can_authorize_dispatch'])
                    self.assertFalse(receipt['independent_os_proof_verified'])
                    watch.assert_called_once()
                    reader.assert_called_once_with(read_fd)
                    evaluate.assert_not_called()
                    with self.assertRaises(OSError):
                        os.fstat(read_fd)
                finally:
                    os.close(write_fd)

    @unittest.skipUnless(sys.platform == 'linux', 'generated Linux postdrain size control')
    def test_postdrain_unmodified_sample_can_reach_nonauthorizing_evaluator(self):
        read_fd, write_fd = os.pipe()
        try:
            outcome = module._outcome(['synthetic downstream evaluation'])
            with patch.object(module, '_start_watch',
                              return_value=(read_fd, 9, 10)) as watch:
                with patch.object(module, '_read_pending',
                                  return_value=b'') as drain:
                    with patch.object(module, '_evaluate',
                                      return_value=outcome) as evaluate:
                        receipt = module.run_demo()
            self.assertEqual(receipt, outcome)
            self.assertEqual(receipt['status'], 'BLOCKED')
            self.assertFalse(receipt['can_authorize_dispatch'])
            self.assertFalse(receipt['independent_os_proof_verified'])
            watch.assert_called_once()
            drain.assert_called_once_with(read_fd)
            evaluate.assert_called_once()
            with self.assertRaises(OSError):
                os.fstat(read_fd)
        finally:
            os.close(write_fd)


    @unittest.skipUnless(sys.platform == 'linux', 'generated Linux late same-length write')
    def test_same_length_write_during_event_drain_refuses_stale_snapshot(self):
        read_fd, write_fd = os.pipe()
        state = {'sample': None, 'initial_inode': None,
                 'late_inode': None, 'late_size': None, 'drained': False}

        def register(path):
            state['sample'] = path
            record = os.lstat(path)
            state['initial_inode'] = record.st_ino
            return read_fd, 9, 10

        def drain(_fd):
            path = state['sample']
            path.write_bytes(module.BEFORE[::-1])
            record = os.lstat(path)
            state['late_inode'] = record.st_ino
            state['late_size'] = record.st_size
            state['drained'] = True
            return b''

        try:
            with patch.object(module, '_start_watch',
                              side_effect=register) as watcher:
                with patch.object(module, '_read_pending',
                                  side_effect=drain) as reader:
                    with patch.object(module, '_evaluate') as evaluate:
                        receipt = module.run_demo()
            self.assertTrue(state['drained'])
            self.assertEqual(state['initial_inode'], state['late_inode'])
            self.assertEqual(state['late_size'], len(module.BEFORE))
            self.assertEqual(receipt['status'], 'BLOCKED')
            self.assertFalse(receipt['can_authorize_dispatch'])
            self.assertFalse(receipt['independent_os_proof_verified'])
            watcher.assert_called_once()
            reader.assert_called_once_with(read_fd)
            evaluate.assert_not_called()
            with self.assertRaises(OSError):
                os.fstat(read_fd)
        finally:
            os.close(write_fd)


    @unittest.skipUnless(sys.platform == 'linux', 'generated Linux postdrain snapshot')
    def test_postdrain_sample_snapshot_mismatch_blocks_without_evaluation(self):
        native_snapshot = module._snapshot_regular
        for forged in ('inode', 'bytes', 'malformed'):
            with self.subTest(forged=forged):
                read_fd, write_fd = os.pipe()
                state = {'drained': False, 'postdrain': 0}

                def register(_path):
                    return read_fd, 9, 10

                def drain(_fd):
                    state['drained'] = True
                    return b''

                def snapshot(path):
                    original = native_snapshot(path)
                    if not state['drained']:
                        return original
                    state['postdrain'] += 1
                    if forged == 'inode':
                        return ((original[0][0], original[0][1] + 1),
                                original[1])
                    if forged == 'bytes':
                        return (original[0], module.BEFORE[::-1])
                    return (original[0], 'not bytes')

                try:
                    with patch.object(module, '_start_watch',
                                      side_effect=register) as watcher:
                        with patch.object(module, '_snapshot_regular',
                                          side_effect=snapshot) as snapshots:
                            with patch.object(module, '_read_pending',
                                              side_effect=drain) as reader:
                                with patch.object(module, '_evaluate') as evaluate:
                                    receipt = module.run_demo()
                    self.assertEqual(state['postdrain'], 1)
                    self.assertEqual(snapshots.call_count, 3)
                    self.assertEqual(receipt['status'], 'BLOCKED')
                    self.assertFalse(receipt['can_authorize_dispatch'])
                    self.assertFalse(receipt['independent_os_proof_verified'])
                    watcher.assert_called_once()
                    reader.assert_called_once_with(read_fd)
                    evaluate.assert_not_called()
                    with self.assertRaises(OSError):
                        os.fstat(read_fd)
                finally:
                    os.close(write_fd)

    @unittest.skipUnless(sys.platform == 'linux', 'generated inode replacement control')
    def test_deliberate_replacement_still_reaches_nonauthorizing_evaluator(self):
        read_fd, write_fd = os.pipe()
        outcome = module._outcome(['generated replacement remains blocked'])
        try:
            with patch.object(module, '_start_watch',
                              return_value=(read_fd, 9, 10)) as watcher:
                with patch.object(module, '_read_pending',
                                  return_value=b'') as reader:
                    with patch.object(module, '_evaluate',
                                      return_value=outcome) as evaluate:
                        receipt = module.run_demo(replace_watched_inode=True)
            self.assertEqual(receipt, outcome)
            self.assertEqual(receipt['status'], 'BLOCKED')
            self.assertFalse(receipt['can_authorize_dispatch'])
            self.assertFalse(receipt['independent_os_proof_verified'])
            watcher.assert_called_once()
            reader.assert_called_once_with(read_fd)
            evaluate.assert_called_once()
            self.assertTrue(evaluate.call_args.kwargs['replacement_negative'])
            with self.assertRaises(OSError):
                os.fstat(read_fd)
        finally:
            os.close(write_fd)


    @unittest.skipUnless(sys.platform == 'linux', 'generated Linux final sample snapshot')
    def test_parent_replacement_during_final_sample_snapshot_blocks_evaluation(self):
        native_lstat = os.lstat
        native_snapshot = module._snapshot_regular
        for tamper in ('inode', 'stat-error'):
            with self.subTest(tamper=tamper):
                read_fd, write_fd = os.pipe()
                state = {'folder': None, 'snapshot_count': 0,
                         'switch': False, 'injected': False}

                class AlteredParentStat:
                    def __init__(self, original):
                        self.original = original
                        self.st_ino = original.st_ino + 1

                    def __getattr__(self, field):
                        return getattr(self.original, field)

                def register(path):
                    state['folder'] = os.fspath(path.parent)
                    return read_fd, 9, 10

                def snapshot(path):
                    result = native_snapshot(path)
                    state['snapshot_count'] += 1
                    if state['snapshot_count'] == 3:
                        state['switch'] = True
                    return result

                def injected_lstat(path, *args, **kwargs):
                    if (state['switch'] and not state['injected']
                            and state['folder'] == os.fspath(path)):
                        state['injected'] = True
                        if tamper == 'stat-error':
                            raise OSError('synthetic final parent stat error')
                        return AlteredParentStat(
                            native_lstat(path, *args, **kwargs))
                    return native_lstat(path, *args, **kwargs)

                try:
                    with patch.object(module.os, 'lstat',
                                      side_effect=injected_lstat):
                        with patch.object(module, '_start_watch',
                                          side_effect=register) as watcher:
                            with patch.object(module, '_snapshot_regular',
                                              side_effect=snapshot) as snapshots:
                                with patch.object(module, '_read_pending',
                                                  return_value=b'') as reader:
                                    with patch.object(module, '_evaluate') as evaluate:
                                        receipt = module.run_demo()
                    self.assertTrue(state['injected'])
                    self.assertEqual(state['snapshot_count'], 3)
                    self.assertEqual(snapshots.call_count, 3)
                    self.assertEqual(receipt['status'], 'BLOCKED')
                    self.assertFalse(receipt['can_authorize_dispatch'])
                    self.assertFalse(receipt['independent_os_proof_verified'])
                    watcher.assert_called_once()
                    reader.assert_called_once_with(read_fd)
                    evaluate.assert_not_called()
                    with self.assertRaises(OSError):
                        os.fstat(read_fd)
                finally:
                    os.close(write_fd)


    @unittest.skipUnless(sys.platform == 'linux', 'generated Linux final private-parent metadata')
    def test_final_parent_metadata_mutation_blocks_after_sample_resnapshot(self):
        native_lstat = os.lstat
        native_snapshot = module._snapshot_regular
        cases = (
            ('public-mode', 'st_mode', module.stat.S_IFDIR | 0o755),
            ('foreign-owner', 'st_uid', (os.geteuid() + 1) % (1 << 32)),
            ('impossible-links', 'st_nlink', 0),
        )
        for case, field, value in cases:
            with self.subTest(case=case):
                read_fd, write_fd = os.pipe()
                state = {'folder': None, 'snapshots': 0, 'injected': False}

                class AlteredDirectoryStat:
                    def __init__(self, original):
                        self.original = original
                        setattr(self, field, value)

                    def __getattr__(self, attr):
                        return getattr(self.original, attr)

                def register(path):
                    state['folder'] = os.fspath(path.parent)
                    return read_fd, 9, 10

                def snapshot(path):
                    result = native_snapshot(path)
                    state['snapshots'] += 1
                    return result

                def scoped_lstat(path, *args, **kwargs):
                    record = native_lstat(path, *args, **kwargs)
                    if (state['snapshots'] == 3 and not state['injected']
                            and state['folder'] == os.fspath(path)):
                        state['injected'] = True
                        return AlteredDirectoryStat(record)
                    return record

                try:
                    with patch.object(module.os, 'lstat',
                                      side_effect=scoped_lstat):
                        with patch.object(module, '_start_watch',
                                          side_effect=register) as watcher:
                            with patch.object(module, '_snapshot_regular',
                                              side_effect=snapshot):
                                with patch.object(module, '_read_pending',
                                                  return_value=b'') as reader:
                                    with patch.object(module, '_evaluate') as evaluate:
                                        result = module.run_demo()
                    self.assertTrue(state['injected'])
                    self.assertEqual(state['snapshots'], 3)
                    self.assertEqual(result['status'], 'BLOCKED')
                    self.assertFalse(result['can_authorize_dispatch'])
                    self.assertFalse(result['independent_os_proof_verified'])
                    watcher.assert_called_once()
                    reader.assert_called_once_with(read_fd)
                    evaluate.assert_not_called()
                    with self.assertRaises(OSError):
                        os.fstat(read_fd)
                finally:
                    os.close(write_fd)


    @unittest.skipUnless(sys.platform == 'linux', 'generated Linux receipt boundary')
    def test_injected_evaluator_cannot_promote_disposable_receipt_to_authorization(self):
        valid = module._outcome(['synthetic expected blocked result'])
        promoted = dict(valid, can_authorize_dispatch=True)
        verified = dict(valid, independent_os_proof_verified=True)
        wrong_status = dict(valid, status='AUTHORIZED')
        bad_checks = dict(valid, observed_checks={'quiet': 1})
        mismatch = dict(valid, status='LOCAL_DISPOSABLE_WITNESS_UNVERIFIED')
        cases = (('dispatch', promoted), ('os-proof', verified),
                 ('status', wrong_status), ('checks', bad_checks),
                 ('status-findings-mismatch', mismatch),
                 ('missing-fields', {'status': 'BLOCKED'}),
                 ('nondict', True))
        for case, forged in cases:
            with self.subTest(case=case):
                read_fd, write_fd = os.pipe()
                try:
                    with patch.object(module, '_start_watch',
                                      return_value=(read_fd, 9, 10)) as watcher:
                        with patch.object(module, '_read_pending',
                                          return_value=b'') as reader:
                            with patch.object(module, '_evaluate',
                                              return_value=forged) as evaluate:
                                result = module.run_demo()
                    self.assertEqual(result['status'], 'BLOCKED')
                    self.assertFalse(result['can_authorize_dispatch'])
                    self.assertFalse(result['independent_os_proof_verified'])
                    self.assertIn('invalid nonauthorizing receipt',
                                  ' '.join(result['findings']))
                    watcher.assert_called_once()
                    reader.assert_called_once_with(read_fd)
                    evaluate.assert_called_once()
                    with self.assertRaises(OSError):
                        os.fstat(read_fd)
                finally:
                    os.close(write_fd)


    def test_cli_rejects_injected_runner_authorization_receipts(self):
        valid = module._outcome(['generated blocked receipt'])
        invalid = (
            ('dispatch-promoted', dict(valid, can_authorize_dispatch=True)),
            ('proof-promoted', dict(valid, independent_os_proof_verified=True)),
            ('fabricated-authorized', dict(valid, status='AUTHORIZED')),
            ('missing-fields', {'status': 'BLOCKED'}),
            ('invalid-check', dict(valid, observed_checks={'quiet': 1})),
            ('nondict', None),
        )
        for case, forged in invalid:
            with self.subTest(case=case):
                stdout = io.StringIO()
                with patch.object(module, 'run_demo',
                                  return_value=forged) as runner:
                    with contextlib.redirect_stdout(stdout):
                        exit_code = module.main(['--execute-disposable-control'])
                self.assertEqual(exit_code, 2)
                receipt = json.loads(stdout.getvalue())
                self.assertEqual(receipt['status'], 'BLOCKED')
                self.assertIs(receipt['can_authorize_dispatch'], False)
                self.assertIs(receipt['independent_os_proof_verified'], False)
                self.assertIn('invalid nonauthorizing receipt',
                              ' '.join(receipt['findings']))
                runner.assert_called_once()

    def test_cli_preserves_both_nonauthorizing_receipt_exit_codes(self):
        for findings, expected_status, expected_code in (
                ([], 'LOCAL_DISPOSABLE_WITNESS_UNVERIFIED', 3),
                (['synthetic blocked'], 'BLOCKED', 2)):
            with self.subTest(expected_status=expected_status):
                native_receipt = module._outcome(findings, {'synthetic': True})
                stdout = io.StringIO()
                with patch.object(module, 'run_demo',
                                  return_value=native_receipt) as runner:
                    with contextlib.redirect_stdout(stdout):
                        code = module.main(['--execute-disposable-control'])
                self.assertEqual(code, expected_code)
                self.assertEqual(json.loads(stdout.getvalue()), native_receipt)
                runner.assert_called_once()


    def test_receipt_validator_rejects_nonplain_top_level_field_keys(self):
        class StringAlias(str):
            pass

        class MatchingObject:
            def __hash__(self):
                return hash('status')

            def __eq__(self, other):
                return other == 'status'

        for case, fake_key in (
                ('str-subclass', StringAlias('status')),
                ('equality-object', MatchingObject())):
            with self.subTest(case=case):
                valid = module._outcome(['generated blocked receipt'])
                forged = dict(valid)
                status = forged.pop('status')
                forged[fake_key] = status
                blocked = module._checked_disposable_observer_result(forged)
                self.assertIsNot(blocked, forged)
                self.assertEqual(blocked['status'], 'BLOCKED')
                self.assertFalse(blocked['can_authorize_dispatch'])
                self.assertFalse(blocked['independent_os_proof_verified'])
                self.assertIn('invalid nonauthorizing receipt',
                              ' '.join(blocked['findings']))

    def test_cli_rejects_equal_hash_nonstring_field_before_serialization(self):
        class MatchingObject:
            def __hash__(self):
                return hash('status')

            def __eq__(self, other):
                return other == 'status'

        valid = module._outcome(['synthetic blocked receipt'])
        forged = dict(valid)
        status = forged.pop('status')
        forged[MatchingObject()] = status
        stdout = io.StringIO()
        with patch.object(module, 'run_demo', return_value=forged) as runner:
            with contextlib.redirect_stdout(stdout):
                exit_code = module.main(['--execute-disposable-control'])
        self.assertEqual(exit_code, 2)
        receipt = json.loads(stdout.getvalue())
        self.assertEqual(receipt['status'], 'BLOCKED')
        self.assertIs(receipt['can_authorize_dispatch'], False)
        self.assertIs(receipt['independent_os_proof_verified'], False)
        self.assertIn('invalid nonauthorizing receipt',
                      ' '.join(receipt['findings']))
        runner.assert_called_once()


    def test_cli_runner_exception_emits_blocked_receipt_not_traceback(self):
        errors = (OSError(5, 'synthetic observer IO failure'),
                  RuntimeError('synthetic runner wrapper failure'),
                  TypeError('synthetic runner argument wrapper failure'),
                  ValueError('synthetic observer result failure'))
        for error in errors:
            with self.subTest(exception_type=type(error).__name__):
                stdout = io.StringIO()
                with patch.object(module, 'run_demo',
                                  side_effect=error) as runner:
                    with contextlib.redirect_stdout(stdout):
                        exit_code = module.main(['--execute-disposable-control'])
                self.assertEqual(exit_code, 2)
                receipt = json.loads(stdout.getvalue())
                self.assertEqual(receipt['status'], 'BLOCKED')
                self.assertIs(receipt['can_authorize_dispatch'], False)
                self.assertIs(receipt['independent_os_proof_verified'], False)
                self.assertIn('CLI runner raised unexpectedly',
                              ' '.join(receipt['findings']))
                runner.assert_called_once()


    def test_receipt_validator_refuses_unbounded_synthetic_findings_and_checks(self):
        baseline = module._outcome(['synthetic blocked'], {'quiet': False})
        for case, forged in (
                ('many-findings', dict(
                    baseline, findings=['finding-' + str(i)
                                        for i in range(module.MAX_RECEIPT_FINDINGS + 1)])),
                ('long-finding', dict(
                    baseline, findings=['x' * (module.MAX_RECEIPT_FINDING_CHARS + 1)])),
                ('empty-finding', dict(baseline, findings=[''])),
                ('many-checks', dict(
                    baseline, observed_checks={'key-' + str(i): True
                                               for i in range(module.MAX_RECEIPT_CHECKS + 1)})),
                ('long-key', dict(
                    baseline, observed_checks={
                        'x' * (module.MAX_RECEIPT_CHECK_KEY_CHARS + 1): True})),
                ('empty-key', dict(baseline, observed_checks={'': True}))):
            with self.subTest(case=case):
                blocked = module._checked_disposable_observer_result(forged)
                self.assertIsNot(blocked, forged)
                self.assertEqual(blocked['status'], 'BLOCKED')
                self.assertFalse(blocked['can_authorize_dispatch'])
                self.assertFalse(blocked['independent_os_proof_verified'])
                self.assertIn('invalid nonauthorizing receipt',
                              ' '.join(blocked['findings']))
        self.assertIs(module._checked_disposable_observer_result(baseline),
                      baseline)

    def test_cli_does_not_serialize_oversized_synthetic_runner_receipt(self):
        oversized = module._outcome(['x' * (module.MAX_RECEIPT_FINDING_CHARS + 1)])
        stdout = io.StringIO()
        with patch.object(module, 'run_demo', return_value=oversized) as runner:
            with contextlib.redirect_stdout(stdout):
                exit_code = module.main(['--execute-disposable-control'])
        self.assertEqual(exit_code, 2)
        output = stdout.getvalue()
        receipt = json.loads(output)
        self.assertLess(len(output), module.MAX_RECEIPT_FINDING_CHARS)
        self.assertEqual(receipt['status'], 'BLOCKED')
        self.assertFalse(receipt['can_authorize_dispatch'])
        self.assertFalse(receipt['independent_os_proof_verified'])
        self.assertIn('invalid nonauthorizing receipt',
                      ' '.join(receipt['findings']))
        runner.assert_called_once()

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
