import base64
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import instruction_contract as contract


class InstructionContractTests(unittest.TestCase):
    def test_canonical_path_markers_and_size_budgets_are_frozen(self):
        loader = contract.LOADER_TEMPLATE.read_text(encoding="utf-8")
        instructions = contract.INSTRUCTIONS_TEMPLATE.read_text(encoding="utf-8")
        loader_size, instruction_size = contract.validate_pair(loader, instructions)

        self.assertEqual(
            contract.CANONICAL_INSTRUCTIONS.as_posix(),
            ".prompt-source/instructions-v1.md",
        )
        self.assertEqual(
            contract.CANONICAL_VALIDATOR.as_posix(),
            ".prompt-source/validate.py",
        )
        self.assertEqual(loader.count(contract.LOADER_BEGIN), 1)
        self.assertEqual(loader.count(contract.LOADER_END), 1)
        self.assertEqual(instructions.splitlines()[0], contract.INSTRUCTIONS_BEGIN)
        self.assertEqual(instructions.splitlines()[-1], contract.INSTRUCTIONS_END)
        self.assertIn(f"`{contract.VALIDATE_HISTORY_COMMAND}`", instructions)
        self.assertIn("git rev-parse --show-toplevel", loader)
        self.assertIn("never the current or nested directory", " ".join(loader.split()))
        normalized_instructions = " ".join(instructions.split())
        self.assertIn("Desktop attachment/paste envelope", normalized_instructions)
        self.assertIn(
            "user input is the text after `## My request:`",
            normalized_instructions,
        )
        self.assertLessEqual(loader_size.words, contract.MAX_LOADER_WORDS)
        self.assertLessEqual(loader_size.bytes, contract.MAX_LOADER_BYTES)
        self.assertLessEqual(instruction_size.words, contract.MAX_INSTRUCTIONS_WORDS)
        self.assertLessEqual(instruction_size.bytes, contract.MAX_INSTRUCTIONS_BYTES)
        self.assertLessEqual(
            loader_size.words + instruction_size.words,
            contract.MAX_COMBINED_WORDS,
        )
        self.assertLessEqual(
            loader_size.bytes + instruction_size.bytes,
            contract.MAX_COMBINED_BYTES,
        )
        self.assertFalse(
            (ROOT / "templates/AGENTS.prompt-source-standard.md").exists()
        )

    def test_install_preserves_existing_root_nested_history_and_assets(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            root_before = b"# Existing root\n\nKeep this byte sequence; no final newline"
            nested_before = b"# Nested\n\nNested guidance remains.\n"
            history_before = b"existing history bytes"
            asset_before = b"existing asset bytes\x00"
            (project / "AGENTS.md").write_bytes(root_before)
            nested = project / "packages/demo/AGENTS.md"
            nested.parent.mkdir(parents=True)
            nested.write_bytes(nested_before)
            (project / "PROMPT_SOURCE.md").write_bytes(history_before)
            assets = project / "prompt_source_assets"
            assets.mkdir()
            (assets / "kept.bin").write_bytes(asset_before)

            contract.install(project)
            installed_root = (project / "AGENTS.md").read_bytes()
            self.assertTrue(installed_root.startswith(root_before + b"\n\n"))
            self.assertEqual(installed_root[: len(root_before)], root_before)
            self.assertEqual(nested.read_bytes(), nested_before)
            self.assertEqual((project / "PROMPT_SOURCE.md").read_bytes(), history_before)
            self.assertEqual((assets / "kept.bin").read_bytes(), asset_before)
            self.assertEqual(
                (project / contract.CANONICAL_INSTRUCTIONS).read_bytes(),
                contract.INSTRUCTIONS_TEMPLATE.read_bytes(),
            )
            self.assertEqual(
                (project / contract.CANONICAL_VALIDATOR).read_bytes(),
                contract.VALIDATOR_SOURCE.read_bytes(),
            )
            contract.check(project)

            before_second_install = installed_root
            contract.install(project)
            self.assertEqual((project / "AGENTS.md").read_bytes(), before_second_install)

    def test_update_replaces_only_loader_dedicated_file_and_validator(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "AGENTS.md").write_text("root-before\n", encoding="utf-8")
            contract.install(project)
            agents_path = project / "AGENTS.md"
            agents = agents_path.read_text(encoding="utf-8") + "\nroot-after\n"
            agents = agents.replace("- Capture: enabled", "- Capture: disabled")
            agents_path.write_text(agents, encoding="utf-8")
            (project / contract.CANONICAL_INSTRUCTIONS).write_text(
                "stale dedicated bytes\n", encoding="utf-8"
            )
            (project / contract.CANONICAL_VALIDATOR).write_text(
                "stale validator bytes\n", encoding="utf-8"
            )

            contract.install(project, update=True)
            updated = agents_path.read_text(encoding="utf-8")
            self.assertTrue(updated.startswith("root-before\n"))
            self.assertTrue(updated.endswith("\nroot-after\n"))
            self.assertIn("- Capture: enabled", updated)
            self.assertNotIn("- Capture: disabled", updated)
            self.assertEqual(
                (project / contract.CANONICAL_INSTRUCTIONS).read_bytes(),
                contract.INSTRUCTIONS_TEMPLATE.read_bytes(),
            )
            self.assertEqual(
                (project / contract.CANONICAL_VALIDATOR).read_bytes(),
                contract.VALIDATOR_SOURCE.read_bytes(),
            )

    def test_disabled_loader_remains_a_valid_installation(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            contract.install(project)
            agents = project / "AGENTS.md"
            agents.write_text(
                agents.read_text(encoding="utf-8").replace(
                    "- Capture: enabled", "- Capture: disabled"
                ),
                encoding="utf-8",
            )
            contract.check(project)

    def test_validator_command_resolves_git_root_from_nested_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            subprocess.run(
                ["git", "init", "-q", "-b", "main"],
                cwd=project,
                check=True,
            )
            contract.install(project)
            (project / "PROMPT_SOURCE.md").write_bytes(
                (ROOT / "tests/fixtures/expected-history.md").read_bytes()
            )
            # File validation now checks the referenced bytes as well as the schema.
            fixtures = json.loads((ROOT / "tests/fixtures/artifacts.json").read_text())
            for artifact in fixtures["artifacts"]:
                if artifact["captured_path"] is not None:
                    destination = project / artifact["captured_path"]
                    destination.parent.mkdir(exist_ok=True)
                    destination.write_bytes(base64.b64decode(artifact["payload_base64"], validate=True))
            nested = project / "packages/demo"
            nested.mkdir(parents=True)

            result = subprocess.run(
                contract.VALIDATE_HISTORY_COMMAND,
                cwd=nested,
                shell=True,
                executable="/bin/sh",
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                result.stdout.strip(),
                "PromptSourceCode: history valid (12 entries)",
            )

    def test_dedicated_instruction_path_resolves_from_nested_git_project(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            subprocess.run(
                ["git", "init", "-q", "-b", "main"],
                cwd=project,
                check=True,
            )
            contract.install(project)
            nested = project / "packages/demo"
            nested.mkdir(parents=True)

            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=nested,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            resolved = Path(result.stdout.strip()) / contract.CANONICAL_INSTRUCTIONS

            self.assertEqual(
                resolved.resolve(),
                (project / contract.CANONICAL_INSTRUCTIONS).resolve(),
            )
            self.assertEqual(
                resolved.read_bytes(),
                contract.INSTRUCTIONS_TEMPLATE.read_bytes(),
            )

    def test_missing_unreadable_stale_conflicting_and_truncated_files_fail_closed(self):
        cases = {
            "missing": None,
            "unreadable": b"\xff\xfe",
            "wrong-version": (
                contract.INSTRUCTIONS_TEMPLATE.read_text(encoding="utf-8")
                .replace(contract.INSTRUCTIONS_BEGIN, "<!-- prompt-source-instructions: 2 -->", 1)
                .encode("utf-8")
            ),
            "stale": (
                contract.INSTRUCTIONS_TEMPLATE.read_text(encoding="utf-8")
                .replace("# PromptSourceCode standard capture", "# Stale standard capture", 1)
                .encode("utf-8")
            ),
            "conflicting": (
                contract.INSTRUCTIONS_TEMPLATE.read_text(encoding="utf-8")
                + contract.INSTRUCTIONS_BEGIN
                + "\n"
            ).encode("utf-8"),
            "truncated": contract.INSTRUCTIONS_TEMPLATE.read_text(encoding="utf-8")
            .replace(contract.INSTRUCTIONS_END + "\n", "", 1)
            .encode("utf-8"),
        }
        for label, replacement in cases.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as directory:
                project = Path(directory)
                contract.install(project)
                dedicated = project / contract.CANONICAL_INSTRUCTIONS
                if replacement is None:
                    dedicated.unlink()
                else:
                    dedicated.write_bytes(replacement)
                with self.assertRaises(contract.InstructionContractError):
                    contract.check(project)

    def test_missing_or_stale_standard_validator_fails_closed(self):
        replacements = {
            "missing": None,
            "unreadable": b"\xff\xfe",
            "stale": b"#!/usr/bin/env python3\n# stale\n",
        }
        for label, replacement in replacements.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as directory:
                project = Path(directory)
                contract.install(project)
                validator = project / contract.CANONICAL_VALIDATOR
                if replacement is None:
                    validator.unlink()
                else:
                    validator.write_bytes(replacement)
                with self.assertRaises(contract.InstructionContractError):
                    contract.check(project)

    def test_partial_or_duplicate_loader_is_never_appended_over(self):
        values = [
            f"root\n{contract.LOADER_BEGIN}\n",
            f"root\n{contract.LOADER_END}\n",
            (
                f"root\n{contract.LOADER_BEGIN}\n{contract.LOADER_BEGIN}\n"
                f"{contract.LOADER_END}\n"
            ),
        ]
        for value in values:
            with self.subTest(value=value), tempfile.TemporaryDirectory() as directory:
                project = Path(directory)
                agents = project / "AGENTS.md"
                agents.write_text(value, encoding="utf-8")
                before = agents.read_bytes()
                with self.assertRaises(contract.InstructionContractError):
                    contract.install(project)
                self.assertEqual(agents.read_bytes(), before)
                self.assertFalse((project / contract.CANONICAL_INSTRUCTIONS).exists())
                self.assertFalse((project / contract.CANONICAL_VALIDATOR).exists())

    def test_standard_layout_has_no_global_codex_configuration_dependency(self):
        text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (
                contract.LOADER_TEMPLATE,
                contract.INSTRUCTIONS_TEMPLATE,
                ROOT / "README.md",
                ROOT / "docs/INSTALLATION.md",
                ROOT / "docs/COMPATIBILITY.md",
            )
        )
        for forbidden in (
            "project_doc_fallback_filenames",
            "~/.codex/config.toml",
            "$CODEX_HOME",
            "global PromptSourceCode configuration",
        ):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
