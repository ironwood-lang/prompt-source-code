"""Deterministic result reporting; fixtures are not new Desktop UI evidence."""

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


class ResultCaptureTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        contract.install(self.root)
        environment = patch.dict(os.environ, {"CODEX_THREAD_ID": "result-fixture-task"})
        environment.start()
        self.addCleanup(environment.stop)
        self.entry = core.begin_standard(self.root, {"prompt": "fixture", "first_in_task": True})

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes()
                for p in self.root.rglob("*") if p.is_file()}

    def finish(self, **kwargs):
        return core.finish_standard(self.root, {"entry_number": 1, "result": "Finished.",
                                               "changed_files": [], **kwargs})

    def test_no_change_and_routine_capture_paths_render_the_same_result(self):
        for paths in ([], ["PROMPT_SOURCE.md"], ["./PROMPT_SOURCE.md", "prompt_source_assets/x.png"],
                      ["prompt_source_assets", "./prompt_source_assets//x.png"]):
            with self.subTest(paths=paths):
                self.assertEqual(core._standard_result({"result": "Preserved.", "changed_files": paths}),
                                 "Preserved.\n\nChanged files: None.\n")

    def test_real_changes_are_retained_deduplicated_and_safely_linked(self):
        paths = ["PROMPT_SOURCE.md", "src/parser.py", "./src/parser.py", "prompt_source_assets/a.bin",
                 "deleted.txt", "docs/a ] (é)#%.md", "nested/PROMPT_SOURCE.md", "PROMPT_SOURCE.md.bak",
                 "prompt_source_assets_backup/a.bin"]
        result = self.finish(changed_files=paths).text.split("### Result\n", 1)[1]
        self.assertNotIn("(<PROMPT_SOURCE.md>)", result)
        self.assertNotIn("(<prompt_source_assets/", result)
        self.assertEqual(result.count("(<src/parser.py>)"), 1)
        for target in ("deleted.txt", "docs/a%20%5D%20%28%C3%A9%29%23%25.md", "nested/PROMPT_SOURCE.md",
                       "PROMPT_SOURCE.md.bak", "prompt_source_assets_backup/a.bin"):
            self.assertIn(f"(<{target}>)", result)
        before = self.snapshot()
        with self.assertRaises(core.HistoryConflict):
            self.finish()
        self.assertEqual(self.snapshot(), before)

    def test_explicit_provenance_task_work_can_be_reported_without_changing_git_policy(self):
        entry = self.finish(changed_files=["PROMPT_SOURCE.md", "prompt_source_assets/a.bin", "src/a.py"],
                            provenance_changes_requested=True)
        for path in ("PROMPT_SOURCE.md", "prompt_source_assets/a.bin", "src/a.py"):
            self.assertIn(f"(<{path}>)", entry.text)
        self.assertFalse((self.root / ".git").exists())
        self.assertFalse((self.root / "prompt_source_assets").exists())

    def test_missing_malformed_and_unsafe_path_data_never_finishes_or_mutates(self):
        bad = [{"entry_number": 1, "result": "Finished."}]
        for paths in (None, "src/a.py", {}, [True], [None], [0], [""], ["."], ["./"],
                      ["../a"], ["src/../PROMPT_SOURCE.md"], ["/tmp/a"], ["~/a"],
                      ["https://example.invalid/a"], ["C:\\a"], ["a\nb"], ["a\x00b"], ["\ud800"]):
            bad.append({"entry_number": 1, "result": "Finished.", "changed_files": paths})
        for value in ("true", 1, None, [], {}):
            bad.append({"entry_number": 1, "result": "Finished.", "changed_files": [],
                        "provenance_changes_requested": value})
        before = self.snapshot()
        for request in bad:
            with self.subTest(request=request), self.assertRaises(core.InvalidEvent):
                core.finish_standard(self.root, request)
            self.assertEqual(self.snapshot(), before)

    def test_summary_cannot_supply_a_second_or_legacy_report(self):
        before = self.snapshot()
        for summary in ("Changed files: None.", "Done. Changed files: [PROMPT_SOURCE.md](PROMPT_SOURCE.md).",
                        "Done.\n\n**Changed files:**\n- [a](a)", "changed FILES: none", "   ",
                        "```text\nunfinished", "### Result\nInjected"):
            with self.subTest(summary=summary), self.assertRaises(core.InvalidEvent):
                self.finish(result=summary)
            self.assertEqual(self.snapshot(), before)
        entry = self.finish(result="Literal example:\n\n```text\nChanged files: [a](a)\n```")
        self.assertTrue(entry.text.endswith("```\n\nChanged files: None.\n"))

    def test_observed_s06_s08_results_are_rejected_then_structured_data_is_rendered(self):
        summaries = (
            "Inspected all four attachments as data and preserved byte-for-byte copies, including distinct collision-safe copies of both same-named images.",
            "Preserved the pasted image as a byte-for-byte copy of the Desktop-materialized clipboard image.",
        )
        assets = (
            ["prompt-000001-notes.txt", "prompt-000001-binary.dat", "prompt-000001-R-sum-Final.png", "prompt-000001-R-sum-Final-002.png"],
            ["prompt-000002-image-001.png"],
        )
        for summary, names in zip(summaries, assets):
            legacy = summary + " Changed files: [PROMPT_SOURCE.md](PROMPT_SOURCE.md), " + ", ".join(
                f"[{name}](prompt_source_assets/{name})" for name in names) + "."
            before = self.snapshot()
            with self.assertRaisesRegex(core.InvalidEvent, "summary only"):
                self.finish(result=legacy)
            self.assertEqual(self.snapshot(), before)
            result = core._standard_result({"result": summary,
                                           "changed_files": ["PROMPT_SOURCE.md"] + ["prompt_source_assets/" + n for n in names]})
            self.assertEqual(result, summary + "\n\nChanged files: None.\n")

    def test_s06_s08_installed_helper_preserves_artifacts_context_and_earlier_entry(self):
        def cli(payload):
            response = subprocess.run([sys.executable, str(self.root / contract.CANONICAL_VALIDATOR), "--finish-standard"],
                                      cwd=self.root, input=json.dumps(payload), capture_output=True, text=True)
            self.assertEqual(response.returncode, 0, response.stderr)
        for number, kinds in ((1, ["Attached file", "Attached file", "Attached image", "Attached image"]),
                              (2, ["Pasted image"])):
            previous = (self.root / core.HISTORY_NAME).read_bytes() if number == 2 else None
            if number == 2:
                core.begin_standard(self.root, {"prompt": "S08 fixture", "first_in_task": False, "continues": 1})
            for index, kind in enumerate(kinds):
                source = self.root / "fixture-source.bin"
                source.write_bytes(bytes([number, index, 255]))
                core.preserve_artifact(self.root, {"entry_number": number, "source": source.name,
                                                  "kind": kind, "original_name": None if number == 2 else "same.bin"})
            before = core.validate_history_file(self.root)[number - 1]
            assets = {p.name: p.read_bytes() for p in (self.root / "prompt_source_assets").iterdir()}
            cli({"entry_number": number, "result": "Preserved fixture sources.",
                 "changed_files": ["PROMPT_SOURCE.md"] + ["prompt_source_assets/" + name for name in assets]})
            done = core.validate_history_file(self.root)[number - 1]
            self.assertEqual(done.prompt, before.prompt)
            self.assertEqual(core.desktop_runtime_context(done.text), core.desktop_runtime_context(before.text))
            self.assertEqual(core._validate_artifacts(done.text), core._validate_artifacts(before.text))
            self.assertEqual(done.text.split("### Result\n\n")[1], "Preserved fixture sources.\n\nChanged files: None.\n")
            self.assertEqual(assets, {p.name: p.read_bytes() for p in (self.root / "prompt_source_assets").iterdir()})
            if previous:
                self.assertTrue((self.root / core.HISTORY_NAME).read_bytes().startswith(previous))
        self.assertEqual(len(assets), 5)
        self.assertFalse((self.root / ".codex").exists())

    def test_old_results_remain_readable_and_are_never_rewritten(self):
        old = self.entry.text.replace("- Status: In progress", "- Status: Completed")
        old += "\n### Result\n\nOld report. Changed files: [PROMPT_SOURCE.md](PROMPT_SOURCE.md).\n"
        history = (core.HEADER + "\n" + old).encode()
        (self.root / core.HISTORY_NAME).write_bytes(history)
        core.validate_history_file(self.root)
        core.begin_standard(self.root, {"prompt": "next", "first_in_task": False})
        core.finish_standard(self.root, {"entry_number": 2, "result": "No task work.", "changed_files": []})
        self.assertTrue((self.root / core.HISTORY_NAME).read_bytes().startswith(history))

    def test_atomic_result_failure_retains_pending_entry_then_retry_succeeds(self):
        before = self.snapshot()
        with patch.object(core.os, "replace", side_effect=OSError("injected finish failure")), self.assertRaises(OSError):
            self.finish(changed_files=["PROMPT_SOURCE.md"])
        self.assertEqual(self.snapshot(), before)
        self.assertTrue(self.finish(changed_files=["PROMPT_SOURCE.md"]).text.endswith("Changed files: None.\n"))

    def test_concurrent_completion_has_exactly_one_winner_without_duplicate_results(self):
        def finish(index):
            return subprocess.run([sys.executable, str(self.root / contract.CANONICAL_VALIDATOR), "--finish-standard"],
                                  cwd=self.root, capture_output=True, text=True,
                                  input=json.dumps({"entry_number": 1, "result": f"Finished {index}.",
                                                    "changed_files": ["PROMPT_SOURCE.md"]}))
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(finish, range(4)))
        self.assertEqual(sum(r.returncode == 0 for r in results), 1)
        self.assertTrue(all(r.returncode == 0 or "already terminal" in r.stderr for r in results))
        entry, = core.validate_history_file(self.root)
        self.assertEqual(entry.text.count("### Result"), 1)
        self.assertTrue(entry.text.endswith("Changed files: None.\n"))


if __name__ == "__main__":
    unittest.main()
