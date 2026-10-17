"""DEC-1483: parse Git's actual subcommand, never scan argument words.

Source-only Linux GitHub Actions log parsing, not actual runner privilege
attestation, artifact integrity or annual execution authorization.
"""
from __future__ import annotations
import re
import shlex
import unittest

RUNNER = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z "
    r"\[command\]/usr/bin/git (.+)$")
WITH_VALUE = frozenset((
    "-c", "-C", "--git-dir", "--work-tree", "--namespace",
    "--super-prefix", "--config-env",
))
WITHOUT_VALUE = frozenset((
    "--no-pager", "--paginate", "-p", "-P",
    "--no-optional-locks", "--literal-pathspecs",
    "--glob-pathspecs", "--noglob-pathspecs", "--icase-pathspecs",
    "--no-replace-objects",
))
INLINE_VALUE = ("--git-dir=", "--work-tree=", "--namespace=",
                "--super-prefix=", "--config-env=")
NAME = re.compile(r"[a-z][a-z0-9-]*\Z")


def reviewed_runner_git_subcommand(raw_line):
    """Return command, None for irrelevant lines, '' for malformed Git line."""
    if type(raw_line) is not str:
        return None
    match = RUNNER.fullmatch(raw_line)
    if match is None:
        return None
    try:
        args = shlex.split(match.group(1), posix=True)
    except ValueError:
        return ""
    i = 0
    while i < len(args):
        token = args[i]
        if token in WITH_VALUE:
            if i + 1 >= len(args) or not args[i+1]:
                return ""
            i += 2
            continue
        if token in WITHOUT_VALUE:
            i += 1
            continue
        if (token.startswith(INLINE_VALUE) or
                token.startswith("-C") and len(token) > 2 or
                token.startswith("-c") and len(token) > 2 and "=" in token[2:]):
            i += 1
            continue
        if token.startswith("-"):
            return ""
        return token if NAME.fullmatch(token) is not None else ""
    return ""


class ReviewedGitRunnerSubcommandIsNotAnArgumentWord(unittest.TestCase):
    def setUp(self):
        self.prefix = "2026-10-17T11:49:01.4210120Z [command]/usr/bin/git "

    def parse(self, command):
        return reviewed_runner_git_subcommand(self.prefix + command)

    def test_observed_git_fetch_with_protocol_config(self):
        self.assertEqual(self.parse(
            "-c protocol.version=2 fetch --no-tags origin +abc:refs/remotes/pull/1698/merge"),
            "fetch")

    def test_observed_git_checkout_is_detected(self):
        self.assertEqual(self.parse(
            "checkout --progress --force refs/remotes/pull/1698/merge"),
            "checkout")

    def test_git_show_argument_clean_is_not_git_clean(self):
        self.assertEqual(self.parse("show clean"), "show")

    def test_git_log_argument_merge_is_not_git_merge(self):
        self.assertEqual(self.parse("log -1 --format=merge"), "log")

    def test_git_show_argument_named_reset_is_not_reset(self):
        self.assertEqual(self.parse("show reset"), "show")

    def test_git_submodule_foreach_quoted_git_clean_is_not_top_level_clean(self):
        self.assertEqual(self.parse(
            'submodule foreach --recursive sh -c "git clean -fd"'), "submodule")

    def test_git_restore_is_identified_as_mutating_command(self):
        self.assertEqual(self.parse("restore --worktree ."), "restore")

    def test_git_read_tree_is_identified_as_mutating_command(self):
        self.assertEqual(self.parse("read-tree HEAD"), "read-tree")

    def test_git_cherry_pick_is_identified_as_mutating_command(self):
        self.assertEqual(self.parse("cherry-pick aabbccd"), "cherry-pick")

    def test_git_worktree_is_identified_with_git_dir_global_option(self):
        self.assertEqual(self.parse(
            "--git-dir=/repo/.git worktree add /tmp/w HEAD"), "worktree")

    def test_git_checkout_is_identified_after_worktree_flag(self):
        self.assertEqual(self.parse(
            "-C /repo -c protocol.version=2 checkout other"), "checkout")

    def test_git_config_in_real_checkout_action_is_recognized(self):
        self.assertEqual(self.parse(
            "config --local --name-only --get-regexp core.sshCommand"),
            "config")

    def test_missing_global_option_value_fails_closed(self):
        self.assertEqual(self.parse("-c"), "")

    def test_unknown_global_option_fails_closed(self):
        self.assertEqual(self.parse("--unknown checkout other"), "")

    def test_unterminated_shell_quote_fails_closed(self):
        self.assertEqual(self.parse("show 'unclosed"), "")

    def test_unrelated_shell_echo_is_not_runner_git_command(self):
        self.assertIsNone(reviewed_runner_git_subcommand(
            "2026-10-17T11:49:01Z echo git checkout other"))

    def test_boolean_log_text_is_not_a_command(self):
        self.assertIsNone(reviewed_runner_git_subcommand(True))

    def test_parsing_source_commands_does_not_grant_annual_execution(self):
        self.assertEqual(self.parse("restore ."), "restore")
        self.assertNotEqual(self.parse("restore ."), "ANNUAL_DISPATCH_AUTHORIZED")
