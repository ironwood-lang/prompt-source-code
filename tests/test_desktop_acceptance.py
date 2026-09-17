import json
import contextlib
import io
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import desktop_acceptance as acceptance


RUNBOOK = ROOT / "docs/MILESTONE_6_CODEX_DESKTOP_ACCEPTANCE.md"
ROADMAP = ROOT / "docs/ROADMAP.md"


class DesktopAcceptanceToolTests(unittest.TestCase):
    def make_run(self, workspace, *, disabled_capture=False, nested_followup=False):
        """Synthetic end-to-end fixture; this is not evidence of a Desktop UI run."""
        acceptance.prepare(workspace)
        project = workspace / "project"
        manifest_path = workspace / "inputs/manifest.json"
        manifest = json.loads(manifest_path.read_text())
        acceptance.instruction_contract.install(project)
        acceptance._run_git(project, "add", "AGENTS.md", ".prompt-source")
        acceptance._run_git(project, "commit", "-m", "fixture installation")
        acceptance._run_git(project, "push", "origin", "main")
        selected = [c for c in manifest["cases"] if c["id"].startswith("S") and c["id"] != "S15"]
        root_turns, nested_turns = [], []
        history = acceptance.core.HEADER
        case_numbers = {}
        for index, case in enumerate(selected):
            prompt = case["prompt"]
            if case["id"] == "S01":
                prompt = prompt.replace("\n## Entry 999999", "\n\n## Entry 999999").replace("\n```\nNo final", "\n```\n\nNo final") + "\n"
            turn = {"id": f"turn-{index}", "startedAt": index,
                    "status": "interrupted" if case["id"] == "S10" else "completed", "items": [
                {"type": "userMessage", "id": f"message-{index}", "content": [{"type": "text", "text": prompt}]}]}
            if case["id"] in {"S04", "S04B", "S05"}:
                root_turns[-1]["items"].extend(turn["items"])
            else:
                (nested_turns if case["id"] == "S14" else root_turns).append(turn)
            if not case["captured"] and not disabled_capture:
                continue
            number = len(case_numbers) + 1
            case_numbers[case["id"]] = number
            interaction = case["interaction"]
            if nested_followup and case["id"] == "S14":
                interaction = "Follow-up"
            block = f"## Entry {number:06d}\n\n- Interaction: {interaction}\n- Status: {case['status'] or 'Completed'}\n- Capture method: Instruction-mediated\n"
            if case["supersedes"]:
                block += f"- Supersedes: Entry {case_numbers[case['supersedes']]:06d}\n"
            if case["id"] == "S10":
                block += "- Status reason: Completion reason unavailable; no reliable Interrupt event was observed.\n"
            body = acceptance.core._split_final_newline(prompt)[0]
            fence = acceptance.core._dynamic_fence(body)
            block += f"\n### User input\n\n- Final newline: Unknown\n\n{fence}text\n{body}\n{fence}\n"
            sources = []
            if case["id"] in {"S06", "S08"}:
                block += "\n### Codex Desktop runtime context\n\n- Final newline: None\n\n```text\nFixture attachment envelope.\n```\n"
            if case["id"] == "S06":
                sources = [(workspace / "inputs" / item["path"], "Attached file")
                           for item in manifest["source_artifacts"] if item["must_be_preserved"]]
            if case["id"] == "S07":
                sources = [(project / "fixtures/repository-source.txt", "Repository file snapshot")]
            if case["id"] == "S08":
                sources = [(workspace / "inputs/artifacts/paste-source.png", "Pasted image")]
            if sources:
                assets = project / "prompt_source_assets"
                assets.mkdir(exist_ok=True)
                block += "\n### Artifacts\n"
                for artifact_index, (source, kind) in enumerate(sources, 1):
                    name = f"prompt-{number:06d}-fixture-{artifact_index:03d}.bin"
                    destination = assets / name
                    destination.write_bytes(source.read_bytes())
                    fidelity = acceptance.core.PASTED_IMAGE_FIDELITY if kind == "Pasted image" else "Fixture source copied byte-for-byte."
                    block += (f"\n#### Artifact {artifact_index}\n\n- Kind: {kind}\n"
                              f"- Preserved copy: [{name}](<prompt_source_assets/{name}>)\n"
                              f"- Byte count: {destination.stat().st_size}\n- SHA-256: {acceptance._sha256(destination)}\n"
                              f"- Fidelity: {fidelity}\n")
            if case["id"] == "S09":
                block += "\n### Artifacts\n\n#### Artifact 1\n\n- Kind: Requested artifact\n- Preservation: Unavailable\n- Unavailable reason: Not present.\n"
            if case["status"] != "Incomplete":
                block += "\n### Result\n\nFixture result.\n\nChanged files: None.\n"
            history += "\n" + block
        (project / "PROMPT_SOURCE.md").write_text(history, encoding="utf-8")
        for relative, value in manifest["expected_files"].items():
            if relative in acceptance.STANDARD_EXPECTED_FILES:
                (project / relative).write_text(value, encoding="utf-8")
        pages = []
        for task, cwd, turns in (("root", project, root_turns), ("nested", project / "packages/demo", nested_turns)):
            pages.append({"thread": {"id": task, "cwd": str(cwd)},
                          "page": {"hasMore": False}, "turns": list(reversed(turns))})
        export = workspace / "desktop-export.json"
        export.write_text(json.dumps(pages), encoding="utf-8")
        return project, manifest_path, export

    def test_full_validator_uses_desktop_delivery_and_reports_only_real_case_errors(self):
        for disabled, nested_bad in ((False, False), (True, False), (True, True)):
            with self.subTest(disabled=disabled, nested_bad=nested_bad), tempfile.TemporaryDirectory() as temporary:
                with contextlib.redirect_stdout(io.StringIO()):
                    project, manifest, export = self.make_run(Path(temporary) / "run", disabled_capture=disabled, nested_followup=nested_bad)
                output, errors = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                    if disabled or nested_bad:
                        with self.assertRaises(SystemExit):
                            acceptance.validate(project, manifest, acceptance.CANONICAL_INSTRUCTIONS,
                                                standard_only=True, desktop_export=export)
                    else:
                        acceptance.validate(project, manifest, acceptance.CANONICAL_INSTRUCTIONS,
                                            standard_only=True, desktop_export=export)
                actual = errors.getvalue().splitlines()[1:]
                expected = []
                if disabled:
                    expected.append("- disabled case S12 was unexpectedly captured (Entry 000013)")
                if nested_bad:
                    expected.append("- S14 has interaction 'Follow-up'")
                self.assertEqual(actual, expected)
                if not expected:
                    self.assertIn("PASSED", output.getvalue())
                    self.assertIn("NOT RUN", output.getvalue())

    def test_case_alignment_handles_missing_duplicate_out_of_order_and_repeated_cases(self):
        cases = acceptance._acceptance_cases("/fixture/missing")
        def entry(number, prompt):
            return acceptance.core.Entry(number, 0, 0, "", {}, prompt, "Unknown")
        by_id = {c["id"]: c for c in cases}
        sequence = [by_id[key] for key in ("S12", "S13", "S14")]
        matched, errors = acceptance.match_case_entries(sequence, [entry(1, by_id["S14"]["prompt"])])
        self.assertEqual(list(matched), ["S14"])
        self.assertEqual(errors, ["missing captured case S13"])
        repeated = [by_id[key] for key in ("H03A", "H03B")]
        matched, errors = acceptance.match_case_entries(repeated, [entry(1, repeated[0]["prompt"]), entry(2, repeated[0]["prompt"])])
        self.assertEqual(list(matched), ["H03A", "H03B"])
        self.assertEqual(errors, [])
        matched, errors = acceptance.match_case_entries(sequence, [entry(1, by_id["S14"]["prompt"]), entry(2, by_id["S13"]["prompt"]), entry(3, by_id["S14"]["prompt"])])
        self.assertEqual(len(errors), 2)
        self.assertIn("duplicate", errors[0])
        self.assertIn("order", errors[1])

    def test_delivery_comparison_never_normalizes_internal_whitespace(self):
        prompt = "a  b\t\n\n## heading\n"
        entry = acceptance.core.Entry(1, 0, 0, "", {}, prompt[:-1], "Unknown")
        self.assertTrue(acceptance.prompt_matches(entry, prompt))
        self.assertFalse(acceptance.prompt_matches(entry, prompt.replace("\n\n", "\n")))
        self.assertFalse(acceptance.prompt_matches(entry, prompt.replace("a  b", "a b")))
        self.assertFalse(acceptance.prompt_matches(entry, prompt + "\n"))

    def test_export_is_required_and_an_actual_delivery_mismatch_is_not_waived(self):
        with tempfile.TemporaryDirectory() as temporary:
            with contextlib.redirect_stdout(io.StringIO()):
                project, manifest, export = self.make_run(Path(temporary) / "run")
            for supplied in (None, export):
                if supplied:
                    pages = json.loads(export.read_text())
                    pages[0]["turns"][-1]["items"][0]["content"][0]["text"] += "tampered"
                    export.write_text(json.dumps(pages))
                errors = io.StringIO()
                with contextlib.redirect_stderr(errors), self.assertRaises(SystemExit):
                    acceptance.validate(project, manifest, acceptance.CANONICAL_INSTRUCTIONS,
                                        standard_only=True, desktop_export=supplied)
                expected = "S01 prompt text differs from the recorded Desktop delivery" if supplied else "Desktop delivery evidence missing"
                self.assertIn(expected, errors.getvalue())

    def test_desktop_export_rejects_wrong_project_partial_pages_and_duplicate_messages(self):
        with tempfile.TemporaryDirectory() as temporary:
            with contextlib.redirect_stdout(io.StringIO()):
                project, _, export = self.make_run(Path(temporary) / "run")
            original = export.read_text()
            for mutation in ("project", "partial", "duplicate"):
                pages = json.loads(original)
                if mutation == "project":
                    pages[0]["thread"]["cwd"] = str(project.parent)
                elif mutation == "partial":
                    pages[0]["page"]["hasMore"] = True
                else:
                    pages[0]["turns"][0]["items"].append(pages[0]["turns"][0]["items"][0])
                export.write_text(json.dumps(pages))
                with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                    acceptance.read_desktop_export(export, project)

    def test_nested_case_requires_the_nested_project_not_just_a_new_task(self):
        with tempfile.TemporaryDirectory() as temporary:
            with contextlib.redirect_stdout(io.StringIO()):
                project, manifest, export = self.make_run(Path(temporary) / "run")
            pages = json.loads(export.read_text())
            pages[1]["thread"]["cwd"] = str(project)
            export.write_text(json.dumps(pages))
            errors = io.StringIO()
            with contextlib.redirect_stderr(errors), self.assertRaises(SystemExit):
                acceptance.validate(project, manifest, acceptance.CANONICAL_INSTRUCTIONS,
                                    standard_only=True, desktop_export=export)
            self.assertEqual(errors.getvalue().splitlines()[1:], [
                "- S14 Desktop task used the wrong project directory",
            ])

    def test_prepare_creates_fresh_project_prompts_and_artifacts(self):
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "acceptance"
            acceptance.prepare(workspace)

            project = workspace / "project"
            inputs = workspace / "inputs"
            manifest = json.loads(
                (inputs / "manifest.json").read_text(encoding="utf-8")
            )
            cases = {case["id"]: case for case in manifest["cases"]}

            self.assertEqual(len(cases), 28)
            self.assertFalse(cases["S01"]["prompt"].endswith("\n"))
            self.assertIn("`PSC_ROOT_SENTINEL`", cases["S01"]["prompt"])
            self.assertIn("Internal   consecutive spaces", cases["S01"]["prompt"])
            self.assertIn("```python", cases["S01"]["prompt"])
            self.assertNotIn("````", cases["S01"]["prompt"])
            self.assertNotIn("~~~~~~~~~~~", cases["S01"]["prompt"])
            self.assertIn("`PSC_NESTED_SENTINEL`", cases["S14"]["prompt"])
            self.assertFalse(cases["H01"]["prompt"].endswith("\n"))
            self.assertEqual(cases["H03A"]["prompt"], cases["H03B"]["prompt"])
            self.assertFalse(cases["S12"]["captured"])
            self.assertFalse(
                (inputs / "artifacts/intentionally-missing.bin").exists()
            )
            self.assertNotIn(str(Path.home()), json.dumps(manifest))
            self.assertNotIn(str(Path.home()), cases["S09"]["prompt"])
            self.assertGreater((project / "AGENTS.md").stat().st_size, 10_000)
            self.assertEqual(manifest["minimum_preserved_assets"], 8)
            self.assertGreater(
                manifest["preexisting_files"]["AGENTS.md"]["bytes"],
                10_000,
            )
            self.assertIn(
                acceptance.ROOT_SENTINEL,
                (project / "AGENTS.md").read_text(encoding="utf-8"),
            )
            self.assertIn(
                acceptance.NESTED_SENTINEL,
                (project / "packages/demo/AGENTS.md").read_text(encoding="utf-8"),
            )

            collision_a = inputs / "artifacts/collision-a/Résumé Final ??.PNG"
            collision_b = inputs / "artifacts/collision-b/Résumé Final ??.PNG"
            self.assertNotEqual(collision_a.read_bytes(), collision_b.read_bytes())
            self.assertEqual(
                acceptance._run_git(
                    project,
                    "rev-list",
                    "--left-right",
                    "--count",
                    "origin/main...main",
                ),
                "0\t0",
            )
            self.assertEqual(
                acceptance._run_git(project, "remote", "get-url", "origin"),
                "../origin.git",
            )

    def test_prepare_refuses_to_reuse_a_path(self):
        with tempfile.TemporaryDirectory() as temporary:
            existing = Path(temporary) / "existing"
            existing.mkdir()
            with self.assertRaises(SystemExit):
                acceptance.prepare(existing)

    def test_prepare_refuses_a_workspace_inside_the_development_repository(self):
        with self.assertRaises(SystemExit):
            acceptance.prepare(ROOT / "__psc_acceptance_test_forbidden__")

    def test_loader_extraction_and_size_counting(self):
        text = (
            "Existing instructions.\n"
            f"{acceptance.LOADER_BEGIN}\n"
            "Read the dedicated capture instructions.\n"
            f"{acceptance.LOADER_END}\n"
        )
        loader = acceptance._extract_loader(text)
        self.assertTrue(loader.startswith(acceptance.LOADER_BEGIN))
        self.assertTrue(loader.endswith(acceptance.LOADER_END))
        self.assertEqual(acceptance._word_count(loader), 11)

    def test_validator_requires_the_frozen_instruction_path(self):
        with self.assertRaises(SystemExit):
            acceptance.validate(
                Path("/tmp/project"),
                Path("/tmp/manifest.json"),
                "../outside.md",
            )
        self.assertEqual(
            acceptance.CANONICAL_INSTRUCTIONS,
            ".prompt-source/instructions-v1.md",
        )
        self.assertEqual(
            acceptance.CANONICAL_VALIDATOR,
            ".prompt-source/validate.py",
        )

    def test_standard_only_mode_has_the_frozen_case_and_file_scope(self):
        arguments = acceptance.build_parser().parse_args(
            [
                "validate",
                "/tmp/project",
                "/tmp/manifest.json",
                "--standard-only",
            ]
        )
        self.assertTrue(arguments.standard_only)
        self.assertEqual(
            acceptance.STANDARD_CASE_IDS,
            {
                "S01",
                "S02",
                "S03",
                "S04",
                "S04B",
                "S05",
                "S06",
                "S07",
                "S08",
                "S09",
                "S10",
                "S11",
                "S13",
                "S14",
            },
        )
        self.assertNotIn("S12", acceptance.STANDARD_CASE_IDS)
        self.assertNotIn("S15", acceptance.STANDARD_CASE_IDS)
        self.assertNotIn("H01", acceptance.STANDARD_CASE_IDS)
        self.assertIn("disabled-check.txt", acceptance.STANDARD_EXPECTED_FILES)

    def test_runbook_covers_every_prepared_case_and_validation_gate(self):
        runbook = RUNBOOK.read_text(encoding="utf-8")
        normalized = " ".join(runbook.split())
        cases = acceptance._acceptance_cases(Path("/prepared/intentionally-missing.bin"))
        for case in cases:
            if case["id"] == "S01":
                self.assertIn(
                    "Internal   consecutive spaces remain significant.",
                    runbook,
                )
                self.assertIn(
                    "No final newline follows this sentence.",
                    runbook,
                )
            elif case["id"] == "S09":
                self.assertIn("<prepared missing path>", runbook)
            else:
                self.assertIn(case["prompt"].rstrip("\n"), runbook, case["id"])

        for phrase in (
            "desktop_acceptance.py prepare",
            "desktop_acceptance.py validate",
            "--standard-only",
            "Optional-hook cases S15 and H01-H11",
            acceptance.LOADER_BEGIN,
            acceptance.LOADER_END,
            "PSC_INSTRUCTIONS_RELATIVE=.prompt-source/instructions-v1.md",
            "instruction_contract.py install",
            "instruction_contract.py check",
            "at most 300 words and 2,048 UTF-8 bytes",
            "at most 900 words and 6,144 UTF-8 bytes",
            "at most 1,200 words and 8,192 UTF-8 bytes",
            "test_unmatched_interrupt_is_conservative_and_byte_preserving",
            "This is 80 stress test invocations",
            "Do not mark Milestone 6 complete",
        ):
            self.assertIn(" ".join(phrase.split()), normalized)

    def test_roadmap_treats_independence_as_existing_and_drops_pre_1_0_upgrade_burden(self):
        roadmap = " ".join(ROADMAP.read_text(encoding="utf-8").split())
        self.assertIn(
            "Preserve the standard path's existing independence",
            roadmap,
        )
        self.assertIn(
            "pre-1.0 experiments and do not impose an upgrade-compatibility requirement",
            roadmap,
        )
        self.assertNotIn(
            "Preserve the full-inline 0.1.0 installation as a compatible capture path",
            roadmap,
        )


if __name__ == "__main__":
    unittest.main()
