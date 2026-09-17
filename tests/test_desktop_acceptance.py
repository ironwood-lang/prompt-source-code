import json
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
