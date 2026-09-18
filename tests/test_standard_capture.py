"""Behavioral regressions for the installed standard path (no enabled hooks)."""

import hashlib
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "hooks"))
import instruction_contract as contract
import prompt_source_core as core


class StandardCaptureTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        contract.install(self.root)
        self.environment = patch.dict(os.environ, {"CODEX_THREAD_ID": "fixture-root-task"})
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def begin(self, prompt="literal `text`", first=True, **kwargs):
        return core.begin_standard(self.root, {"prompt": prompt, "first_in_task": first, **kwargs})

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes()
                for p in self.root.rglob("*") if p.is_file()}

    def disable(self):
        path = self.root / "AGENTS.md"
        path.write_bytes(path.read_bytes().replace(b"- Capture: enabled", b"- Capture: disabled"))

    def test_release_pair_is_the_pair_checked_at_runtime(self):
        self.assertEqual(hashlib.sha256(contract.LOADER_TEMPLATE.read_bytes().strip(b"\n")).hexdigest(), core.STANDARD_LOADER_SHA256)
        self.assertEqual(hashlib.sha256(contract.INSTRUCTIONS_TEMPLATE.read_bytes()).hexdigest(), core.STANDARD_INSTRUCTIONS_SHA256)
        self.assertTrue(core.standard_capture_state(self.root))

    def test_live_disable_blocks_creation_and_completion_then_reenable_appends(self):
        first = self.begin()
        self.disable()
        before = self.snapshot()
        self.assertFalse(core.standard_capture_state(self.root))
        self.assertIsNone(self.begin("must not be recorded", first=False))
        self.assertIsNone(core.finish_standard(self.root, {"entry_number": first.number, "result": "Finished.", "changed_files": []}))
        self.assertEqual(self.snapshot(), before)
        path = self.root / "AGENTS.md"
        path.write_bytes(path.read_bytes().replace(b"- Capture: disabled", b"- Capture: enabled"))
        second = self.begin("resumed", first=False)
        self.assertEqual(second.number, 2)
        self.assertEqual(second.fields["Interaction"], "Follow-up")
        self.assertEqual(core.validate_history_file(self.root)[0].text, first.text)

    def test_disabled_does_not_read_missing_or_unreadable_dedicated_file(self):
        self.disable()
        (self.root / contract.CANONICAL_INSTRUCTIONS).unlink()
        before = self.snapshot()
        self.assertFalse(core.standard_capture_state(self.root))
        self.assertIsNone(self.begin())
        self.assertEqual(self.snapshot(), before)

    def test_each_new_task_starts_initial_even_with_existing_history(self):
        first = self.begin()
        core.finish_standard(self.root, {"entry_number": first.number, "result": "Finished.", "changed_files": []})
        original = (self.root / core.HISTORY_NAME).read_bytes()
        with patch.dict(os.environ, {"CODEX_THREAD_ID": "fixture-nested-task"}):
            # Reproduce the bad classification; the runtime guard rejects it.
            with self.assertRaisesRegex(core.HistoryConflict, "no earlier capture belongs"):
                self.begin("nested", first=False, interaction="Follow-up")
            self.assertEqual((self.root / core.HISTORY_NAME).read_bytes(), original)
            nested = self.begin("nested", interaction="Follow-up")
            self.assertEqual(nested.fields["Interaction"], "Initial prompt")
            self.assertEqual(nested.number, 2)
            self.assertTrue((self.root / core.HISTORY_NAME).read_bytes().startswith(original))
            with self.assertRaises(core.HistoryConflict):
                self.begin("another message", first=True)

    def test_first_capture_after_an_uncaptured_submission_is_a_followup(self):
        entry = self.begin("capture resumed after an uncaptured first message", first=False,
                           uncaptured_predecessor=True)
        self.assertEqual(entry.fields["Interaction"], "Follow-up")

    def test_runtime_identifier_is_optional_and_never_fabricated(self):
        with patch.dict(os.environ, {}, clear=True):
            entry = self.begin()
        self.assertNotIn("Session ID", entry.fields)
        self.assertNotIn("Turn ID", entry.fields)
        self.assertNotIn("Agent observation", entry.fields)

    def test_uncertain_pending_hook_is_preserved_alongside_standard_observation(self):
        hook = core.render_entry(1, interaction="Initial prompt", session_id="fixture-root-task",
                                 turn_id="fixture-turn", prompt="same prompt", model=None, continues=None)
        original = (core.HEADER + "\n" + hook).encode("utf-8")
        (self.root / core.HISTORY_NAME).write_bytes(original)
        entry = self.begin("same prompt", deduplication_uncertain=True)
        self.assertEqual(entry.fields["Capture method"], "Instruction-mediated")
        self.assertEqual(entry.fields["Deduplication note"], core.UNCERTAIN_DEDUPLICATION_NOTE)
        self.assertTrue((self.root / core.HISTORY_NAME).read_bytes().startswith(original))

    def test_repeat_steering_correction_and_immutable_completion(self):
        first = self.begin("same prompt")
        second = self.begin("same prompt", first=False, interaction="Steering", continues=1)
        third = self.begin("Correction: replace that.", first=False,
                           interaction="Correction", supersedes=second.number)
        self.assertEqual([e.number for e in core.validate_history_file(self.root)], [1, 2, 3])
        self.assertEqual(third.fields["Supersedes"], "Entry 000002")
        done = core.finish_standard(self.root, {"entry_number": first.number,
                                               "result": "Superseded before work.", "changed_files": []})
        self.assertEqual(done.prompt, first.prompt)
        before = self.snapshot()
        with self.assertRaises(core.HistoryConflict):
            core.finish_standard(self.root, {"entry_number": first.number, "result": "rewrite"})
        self.assertEqual(self.snapshot(), before)

    def test_invalid_installations_fail_before_history_or_artifact_changes(self):
        self.begin()
        original = self.snapshot()
        mutations = [
            ("AGENTS.md", None),
            ("AGENTS.md", original["AGENTS.md"] + b"<!-- prompt-source-loader-begin -->"),
            ("AGENTS.md", original["AGENTS.md"].replace(b"Capture: enabled", b"Capture: maybe")),
            ("AGENTS.md", original["AGENTS.md"].replace(b"instructions-v1", b"instructions-v2")),
            (".prompt-source/instructions-v1.md", None),
            (".prompt-source/instructions-v1.md", b"\xff"),
            (".prompt-source/instructions-v1.md", original[".prompt-source/instructions-v1.md"][:-20]),
            (".prompt-source/instructions-v1.md", original[".prompt-source/instructions-v1.md"] + b"stale"),
        ]
        for relative, contents in mutations:
            with self.subTest(relative=relative, contents=contents):
                path = self.root / relative
                if contents is None:
                    path.unlink()
                else:
                    path.write_bytes(contents)
                before = self.snapshot()
                with self.assertRaises(core.HistoryConflict):
                    self.begin("next", first=False)
                self.assertEqual(self.snapshot(), before)
                path.write_bytes(original[relative])

    def test_permission_error_fails_closed_without_changing_provenance(self):
        self.begin()
        before = self.snapshot()
        original_read = Path.read_bytes
        def read(path):
            if path == self.root / contract.CANONICAL_INSTRUCTIONS:
                raise PermissionError("fixture permission denied")
            return original_read(path)
        with patch.object(Path, "read_bytes", read):
            with self.assertRaisesRegex(core.HistoryConflict, "unreadable"):
                self.begin("cannot read", first=False)
        self.assertEqual(self.snapshot(), before)

    def test_unknown_newline_and_complex_text_are_literal(self):
        for index, prompt in enumerate(("a", "a\n", "a\r\n", "a\r", "", "  x\t\n\n```python\nx\n```\n~~~\n## Entry 999999")):
            entry = self.begin(prompt, first=index == 0)
            self.assertEqual(entry.prompt, prompt)
            self.assertEqual(entry.final_newline, "Unknown")
            self.assertNotIn("Stored SHA-256", entry.text)

    def test_failed_atomic_begin_preserves_history_and_leaves_no_runtime_file(self):
        self.begin()
        before = self.snapshot()
        with patch.object(core.os, "replace", side_effect=OSError("injected")):
            with self.assertRaises(OSError):
                self.begin("failed append", first=False)
        self.assertEqual(self.snapshot(), before)

    def test_failed_or_foreign_completion_preserves_history(self):
        entry = self.begin()
        before = self.snapshot()
        request = {"entry_number": entry.number, "result": "Finished.", "changed_files": []}
        with patch.dict(os.environ, {"CODEX_THREAD_ID": "fixture-other-task"}):
            with self.assertRaises(core.NoReliableMatch):
                core.finish_standard(self.root, request)
        self.assertEqual(self.snapshot(), before)
        with patch.object(core.os, "replace", side_effect=OSError("injected")):
            with self.assertRaises(OSError):
                core.finish_standard(self.root, request)
        self.assertEqual(self.snapshot(), before)

    def test_concurrent_standard_tasks_append_distinct_initial_entries(self):
        def capture(index):
            environment = {**os.environ, "CODEX_THREAD_ID": f"fixture-task-{index}"}
            return subprocess.run(
                [sys.executable, str(self.root / contract.CANONICAL_VALIDATOR), "--begin-standard"],
                cwd=self.root, env=environment, text=True, capture_output=True,
                input=json.dumps({"prompt": f"submission-{index}", "first_in_task": True}),
            )
        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(capture, range(12)))
        for result in results:
            self.assertEqual(result.returncode, 0, result.stderr)
        entries = core.validate_history_file(self.root)
        self.assertEqual([entry.number for entry in entries], list(range(1, 13)))
        self.assertEqual({entry.prompt for entry in entries}, {f"submission-{i}" for i in range(12)})
        self.assertEqual({entry.fields["Interaction"] for entry in entries}, {"Initial prompt"})
        self.assertEqual(len({entry.fields["Session ID"] for entry in entries}), 12)
        self.assertEqual(set(self.snapshot()), {
            "AGENTS.md", contract.CANONICAL_INSTRUCTIONS.as_posix(),
            contract.CANONICAL_VALIDATOR.as_posix(), core.HISTORY_NAME,
        })

    def test_recovery_changes_only_named_earlier_work_and_keeps_unknown_reason(self):
        original = self.begin("interrupted before completion")
        following = self.begin("recover and continue", first=False, recover=[original.number])
        entries = core.validate_history_file(self.root)
        self.assertEqual(entries[0].prompt, original.prompt)
        self.assertEqual(entries[0].fields["Status"], "Incomplete")
        self.assertEqual(entries[0].fields["Status reason"], "Completion reason unavailable; no reliable Interrupt event was observed.")
        self.assertEqual(following.fields["Status"], "In progress")
        before = self.snapshot()
        with self.assertRaises(core.HistoryConflict):
            self.begin("retry", first=False, recover=[original.number])
        self.assertEqual(self.snapshot(), before)

    def test_installed_commands_run_without_hooks_from_nested_git_directory(self):
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.root, check=True)
        nested = self.root / "packages/demo"
        nested.mkdir(parents=True)
        command = 'cd "$(git rev-parse --show-toplevel)" && /usr/bin/python3 .prompt-source/validate.py '
        for mode, payload in (("--capture-state", None),
                              ("--begin-standard", {"prompt": "nested", "first_in_task": True}),
                              ("--finish-standard", {"entry_number": 1, "result": "Finished.", "changed_files": []}),
                              ("--validate-history", None)):
            result = subprocess.run(command + mode, shell=True, executable="/bin/sh", cwd=nested,
                                    input=json.dumps(payload) if payload else None,
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.root / ".codex").exists())
        self.assertFalse((nested / core.HISTORY_NAME).exists())
        self.assertEqual(len(core.validate_history_file(self.root)), 1)
        direct = subprocess.run(["/usr/bin/python3", str(self.root / contract.CANONICAL_VALIDATOR),
                                 "--begin-standard"], cwd=nested,
                                input=json.dumps({"prompt": "absolute helper from nested cwd", "first_in_task": False}),
                                text=True, capture_output=True)
        self.assertEqual(direct.returncode, 0, direct.stderr)
        self.assertEqual(json.loads(direct.stdout)["entry_number"], 2)
        self.assertFalse((nested / core.HISTORY_NAME).exists())


if __name__ == "__main__":
    unittest.main()
