from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "phase8a_exp044_operator.py"


class Exp044NextActionScriptTests(unittest.TestCase):
    def test_next_mode_is_read_only_and_has_no_execute_argument(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('"next"', text)
        self.assertIn('"read_only": True', text)
        self.assertIn("PRESERVATION_DISPATCH_REQUIRED", text)
        self.assertIn("FEATURE_DISPATCH_REQUIRED", text)
        self.assertIn("OUTCOME_DISPATCH_REQUIRED", text)
        self.assertIn("OUTCOME_REPLACEMENT_DISPATCH_REQUIRED", text)
        self.assertIn("MODEL_PROTOCOL_SOURCE_OPEN", text)
        self.assertIn("MODEL_PROTOCOL_FROZEN", text)
        self.assertIn("MODEL_RUN_EXECUTION_CLOSED", text)
        self.assertIn("MODEL_RUN_FAILURE_REVIEWED", text)
        self.assertIn("validate_reviewed_failed_model_run", text)
        self.assertIn("build_model_workflow_source_gate", text)
        self.assertIn("build_model_run_source_gate", text)

        parser_start = text.index("def parser()")
        parser_end = text.index("def _print_report", parser_start)
        parser = text[parser_start:parser_end]
        next_start = parser.index('"next"')
        advance_start = parser.index('"advance"', next_start)
        next_parser = parser[next_start:advance_start]
        self.assertNotIn("--execute", next_parser)

    def test_gh_auth_check_is_silent_so_nested_next_remains_json(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        start = text.index("def _require_gh_auth()")
        end = text.index("def parser()", start)
        auth_block = text[start:end]
        self.assertIn('_run(("gh", "auth", "status"))', auth_block)
        self.assertNotIn("capture=False", auth_block)

    def test_advance_reuses_public_next_plan_and_requires_explicit_execute(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('"advance"', text)
        self.assertIn("_read_next_plan_via_public_cli()", text)
        self.assertIn("dispatch_command_for_next_report", text)
        self.assertIn("confirmed != plan", text)
        self.assertIn('"dispatch_submitted"] = True', text)

        parser_start = text.index("def parser()")
        parser_end = text.index("def _print_report", parser_start)
        parser = text[parser_start:parser_end]
        advance_start = parser.index('"advance"')
        preserve_start = parser.index('"preserve-phase2"', advance_start)
        advance_parser = parser[advance_start:preserve_start]
        self.assertIn("--execute", advance_parser)

    def test_next_mode_never_submits_a_dispatch(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        main_start = text.index("def main(")
        next_start = text.index('if args.command == "next"', main_start)
        preserve_start = text.index('if args.command == "preserve-phase2"', next_start)
        next_block = text[next_start:preserve_start]
        self.assertIn('if args.command == "next"', next_block)
        self.assertNotIn("_run(command, capture=False)", next_block)
        self.assertNotIn('"dispatch_submitted"', next_block)
        self.assertIn("select_only_manual_main_run", next_block)
        self.assertIn("build_execution_status", next_block)


if __name__ == "__main__":
    unittest.main()
