"""Executable artifact contracts, including the failed Desktop P02 reproduction."""

import base64
from concurrent.futures import ThreadPoolExecutor
import hashlib
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


class ArtifactCaptureTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.workspace = Path(temporary.name).resolve()
        self.root = self.workspace / "project"
        self.root.mkdir()
        contract.install(self.root)
        environment = patch.dict(os.environ, {"CODEX_THREAD_ID": "artifact-task"})
        environment.start()
        self.addCleanup(environment.stop)
        self.entry = core.begin_standard(self.root, {"prompt": "preserve sources", "first_in_task": True})

    def source(self, name="inputs/notes.txt", payload=b"source\x00\xff\r\n"):
        path = self.workspace / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        return path

    def preserve(self, source=None, **options):
        request = {"entry_number": self.entry.number, **options}
        if source is not None:
            request["source"] = str(source)
        return core.preserve_artifact(self.root, request)

    def history(self):
        return (self.root / core.HISTORY_NAME).read_bytes()

    def assets(self):
        return {p.name: p.read_bytes() for p in (self.root / "prompt_source_assets").glob("*") if p.is_file()}

    def records(self, entry=None):
        return core._validate_artifacts((entry or core.validate_history_file(self.root)[0]).text)

    def test_exact_preflight_four_sources_have_padded_names_and_requested_kind(self):
        core.finish_standard(self.root, {"entry_number": 1, "result": "Changed files: None."})
        original = self.history()
        self.entry = core.begin_standard(self.root, {"prompt": "P02", "first_in_task": False})
        fixtures = [("notes.txt", b"notes\n"), ("binary.dat", bytes(range(256)) * 4),
                    ("collision-a/Résumé Final ??.PNG", b"image A"),
                    ("collision-b/Résumé Final ??.PNG", b"image B")]
        for name, payload in fixtures:
            self.preserve(self.source("inputs/artifacts/" + name, payload))
        entry = core.finish_standard(self.root, {"entry_number": 2, "result": "Changed files: None."})
        records = self.records(entry)
        self.assertEqual([r["Kind"] for r in records], ["Requested artifact"] * 4)
        self.assertEqual(self.assets(), dict(zip(
            ("prompt-000002-notes.txt", "prompt-000002-binary.dat", "prompt-000002-R-sum-Final.png", "prompt-000002-R-sum-Final-002.png"),
            [payload for _, payload in fixtures])))
        self.assertTrue(self.history().startswith(original))
        self.assertNotIn(str(self.workspace), entry.text)
        self.assertLess(entry.text.index("### Artifacts"), entry.text.index("### Result"))
        for record, (_, payload) in zip(records, fixtures):
            self.assertEqual(record["SHA-256"], hashlib.sha256(payload).hexdigest())
            self.assertEqual(record["Byte count"], str(len(payload)))
        core.validate_history_file(self.root)

    def test_basename_rule_table(self):
        for name, expected in (
            ("../a/Résumé Final ??.PNG", ("prompt-000001-R-sum-Final", ".png")),
            ("...__---.TXT", ("prompt-000001-artifact", ".txt")),
            ("a---b.data!", ("prompt-000001-a-b.data", "")),
            ("x." + "A" * 17, ("prompt-000001-x." + "A" * 17, "")),
            ("a" * 100 + ".BIN", ("prompt-000001-" + "a" * 80, ".bin")),
        ):
            with self.subTest(name=name):
                self.assertEqual(core._asset_basename(1, name), expected)
        self.assertEqual(core._asset_basename(1000000, "name.png"), ("prompt-1000000-name", ".png"))

    def test_classification_uses_resolved_location_and_encodes_repository_links(self):
        local = self.source("project/fixtures/a ] (é).txt")
        external = self.source()
        alias = self.root / "outside.txt"
        alias.symlink_to(external)
        inside_alias = self.workspace / "inside.txt"
        inside_alias.symlink_to(local)
        for path in (local, external, alias, inside_alias):
            self.preserve(path)
        records = self.records()
        self.assertEqual([r["Kind"] for r in records], ["Repository file snapshot", "Requested artifact", "Requested artifact", "Repository file snapshot"])
        self.assertIn("fixtures/a%20%5D%20%28%C3%A9%29.txt", records[0]["Repository source"])
        self.assertNotIn("Repository source", records[2])
        for invalid in ("Repository file snapshot", "Requested artifact", "image", False):
            before = self.history()
            with self.assertRaises(core.InvalidEvent):
                self.preserve(external, kind=invalid)
            self.assertEqual(self.history(), before)

    def test_observed_ui_kinds_and_unnamed_paste_fidelity(self):
        source = self.source("inputs/materialized.PNG")
        for kind in ("Attached file", "Attached image", "Pasted image"):
            self.preserve(source, kind=kind)
        self.preserve(source, kind="Pasted image", original_name=None)
        self.preserve(source, kind="Pasted image", original_name=None)
        records = self.records()
        self.assertIn("prompt-000001-image-001.png", records[3]["Preserved copy"])
        self.assertIn("prompt-000001-image-002.png", records[4]["Preserved copy"])
        self.assertNotIn("Original name (JSON)", records[3])
        for record in records[2:]:
            self.assertEqual(record["Fidelity"], core.PASTED_IMAGE_FIDELITY)
        self.assertIn("- Fidelity: " + core.PASTED_IMAGE_FIDELITY, self.history().decode().splitlines())

    def test_same_bytes_reuse_and_differing_bytes_collision_never_overwrite(self):
        source = self.source()
        self.preserve(source)
        first = self.assets()
        self.preserve(source)
        self.assertEqual(self.assets(), first)
        self.assertIn("Reuse note", self.records()[1])
        source.write_bytes(b"changed")
        self.preserve(source)
        self.assertEqual(self.assets(), {**first, "prompt-000001-notes-002.txt": b"changed"})

    def test_direct_flat_asset_reused_across_entries_without_renaming_history(self):
        self.preserve(self.source())
        core.finish_standard(self.root, {"entry_number": 1, "result": "Changed files: None."})
        before, assets = self.history(), self.assets()
        self.entry = core.begin_standard(self.root, {"prompt": "reuse", "first_in_task": False})
        record = self.records(self.preserve(self.root / "prompt_source_assets/prompt-000001-notes.txt"))[0]
        self.assertIn("prompt-000001-notes.txt", record["Preserved copy"])
        self.assertIn("Reuse note", record)
        self.assertEqual(self.assets(), assets)
        self.assertTrue(self.history().startswith(before))

    def test_missing_unreadable_and_unexposed_sources_create_no_placeholder(self):
        self.preserve(self.workspace / "missing.txt")
        self.preserve(kind="Pasted image", unavailable_reason="No source path exposed.")
        source = self.source()
        read = Path.read_bytes
        def denied(path):
            if path == source:
                raise PermissionError("test private path must not be stored")
            return read(path)
        with patch.object(Path, "read_bytes", denied):
            self.preserve(source)
        records = self.records()
        self.assertEqual(len(records), 3)
        for record in records:
            self.assertEqual(record["Preservation"], "Unavailable")
            self.assertNotIn("Preserved copy", record)
            self.assertNotIn("Byte count", record)
            self.assertNotIn("SHA-256", record)
        self.assertIn("PermissionError", records[2]["Unavailable reason"])
        self.assertNotIn("test private path", self.history().decode())
        self.assertFalse((self.root / "prompt_source_assets").exists())

    def test_foreign_terminal_invalid_or_disabled_capture_cannot_copy(self):
        source = self.source()
        before = self.history()
        with patch.dict(os.environ, {"CODEX_THREAD_ID": "foreign-task"}), self.assertRaises(core.NoReliableMatch):
            self.preserve(source)
        with self.assertRaises(core.InvalidEvent):
            self.preserve(source, entry_number=True)
        agents = self.root / "AGENTS.md"
        enabled = agents.read_bytes()
        agents.write_bytes(enabled.replace(b"Capture: enabled", b"Capture: disabled"))
        self.assertIsNone(self.preserve(source))
        agents.write_bytes(enabled + b"<!-- prompt-source-loader-begin -->")
        with self.assertRaises(core.HistoryConflict):
            self.preserve(source)
        agents.write_bytes(enabled)
        self.assertEqual(self.history(), before)
        core.finish_standard(self.root, {"entry_number": 1, "result": "Changed files: None."})
        with self.assertRaises(core.HistoryConflict):
            self.preserve(source)
        self.assertFalse((self.root / "prompt_source_assets").exists())

    def test_symlink_storage_rejected_and_symlink_collision_not_overwritten(self):
        source = self.source()
        assets = self.root / "prompt_source_assets"
        assets.symlink_to(source.parent, target_is_directory=True)
        before = self.history()
        with self.assertRaises(core.HistoryConflict):
            self.preserve(source)
        self.assertEqual(self.history(), before)
        assets.unlink()
        assets.mkdir()
        collision = assets / "prompt-000001-notes.txt"
        collision.symlink_to(source)
        original = source.read_bytes()
        self.preserve(source)
        self.assertTrue(collision.is_symlink())
        self.assertEqual(source.read_bytes(), original)
        self.assertIn("prompt-000001-notes-002.txt", self.records()[0]["Preserved copy"])

    def test_copy_failure_leaves_history_and_no_partial_temporary_file(self):
        before = self.history()
        with patch.object(core.os, "link", side_effect=OSError("injected publication failure")):
            with self.assertRaises(OSError):
                self.preserve(self.source())
        self.assertEqual(self.history(), before)
        self.assertEqual(list((self.root / "prompt_source_assets").iterdir()), [])

    def test_history_failure_retains_complete_copy_and_retry_reuses_it(self):
        before = self.history()
        source = self.source()
        with patch.object(core.os, "replace", side_effect=OSError("injected history failure")):
            with self.assertRaises(OSError):
                self.preserve(source)
        self.assertEqual(self.history(), before)
        self.assertEqual(self.assets(), {"prompt-000001-notes.txt": source.read_bytes()})
        self.assertFalse(list(self.root.rglob(".*tmp-*")))
        self.preserve(source)
        self.assertIn("Reuse note", self.records()[0])

    def test_post_history_replace_failure_never_deletes_a_referenced_asset(self):
        atomic_write = core._atomic_write
        def failed_after_replace(path, text):
            atomic_write(path, text)
            raise OSError("injected post-replace directory fsync failure")
        with patch.object(core, "_atomic_write", failed_after_replace), self.assertRaises(OSError):
            self.preserve(self.source())
        self.assertEqual(len(self.records()), 1)
        core.validate_history_file(self.root)

    def test_changing_source_is_not_recorded_as_verified(self):
        source = self.source()
        before = self.history()
        read, count = Path.read_bytes, 0
        def changing(path):
            nonlocal count
            if path == source:
                count += 1
                if count > 1:
                    return b"changed during comparison"
            return read(path)
        with patch.object(Path, "read_bytes", changing), self.assertRaises(core.HistoryConflict):
            self.preserve(source)
        self.assertEqual(self.history(), before)

    def test_validator_rejects_bad_prefixes_and_missing_tampered_or_symlinked_copies(self):
        self.preserve(self.source())
        text = self.history().decode()
        for prefix in ("prompt-1-", "prompt-0000001-", "prompt-000000-", "other-"):
            with self.subTest(prefix=prefix), self.assertRaises(core.HistoryConflict):
                core.validate_history(text.replace("prompt-000001-", prefix))
        destination = self.root / "prompt_source_assets/prompt-000001-notes.txt"
        original = destination.read_bytes()
        destination.write_bytes(b"tampered")
        with self.assertRaisesRegex(core.HistoryConflict, "differs"):
            core.validate_history_file(self.root)
        destination.unlink()
        with self.assertRaisesRegex(core.HistoryConflict, "missing"):
            core.validate_history_file(self.root)
        destination.symlink_to(self.source(payload=original))
        with self.assertRaisesRegex(core.HistoryConflict, "regular local"):
            core.validate_history_file(self.root)

    def test_result_cannot_smuggle_artifacts_but_fenced_examples_are_literal(self):
        before = self.history()
        for result in ("Summary\n\n### Artifacts\n", "### User input\n", "### Codex Desktop runtime context\n", "## Entry 000002\n"):
            with self.assertRaises(core.InvalidEvent):
                core.finish_standard(self.root, {"entry_number": 1, "result": result})
            self.assertEqual(self.history(), before)
        core.finish_standard(self.root, {"entry_number": 1, "result": "Example:\n\n```text\n### Artifacts\n```\n\nChanged files: None."})

    def test_claimed_hook_enrichment_uses_digest_and_keeps_verified_facts_immutable(self):
        block = core.render_entry(1, interaction="Initial prompt", session_id="artifact-task", turn_id="turn",
                                  prompt="artifact", model=None, continues=None)
        (self.root / core.HISTORY_NAME).write_text(core.HEADER + "\n" + block)
        with self.assertRaises(core.NoReliableMatch):
            self.preserve(self.source())
        claim = {"entry_number": 1, "session_id": "artifact-task", "turn_id": "turn",
                 "prompt_utf8_base64": base64.b64encode(b"artifact").decode()}
        claimed = core.claim_entry(self.root, claim)
        with self.assertRaises(core.HistoryConflict):
            self.preserve(self.source(), expected_entry_sha256="0" * 64)
        updated = self.preserve(self.source(), expected_entry_sha256=claimed.utf8_sha256)
        replacement = updated.text.replace("- Kind: Requested artifact", "- Kind: Attached file")
        request = {**claim, "expected_entry_sha256": updated.utf8_sha256,
                   "replacement_entry_base64": base64.b64encode(replacement.encode()).decode()}
        with self.assertRaisesRegex(core.HistoryConflict, "artifact facts"):
            core.replace_entry(self.root, request)
        completed = updated.text.replace("Status: In progress", "Status: Completed") + "\n### Result\n\nChanged files: None.\n"
        request["replacement_entry_base64"] = base64.b64encode(completed.encode()).decode()
        core.replace_entry(self.root, request)
        core.validate_history_file(self.root)

    def test_concurrent_artifact_calls_share_flat_copies_and_number_records(self):
        sources = [self.source(f"inputs/{i}/notes.txt", bytes([i])) for i in range(2)]
        nested = self.root / "packages/demo"
        nested.mkdir(parents=True)
        def capture(index):
            source = "../" + str(sources[index % 2].relative_to(self.workspace))
            return subprocess.run([sys.executable, str(self.root / contract.CANONICAL_VALIDATOR), "--preserve-artifact"],
                                  cwd=nested, input=json.dumps({"entry_number": 1, "source": source}),
                                  capture_output=True, text=True)
        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(capture, range(8)))
        for result in results:
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(self.records()), 8)
        self.assertEqual(set(self.assets()), {"prompt-000001-notes.txt", "prompt-000001-notes-002.txt"})
        self.assertEqual(set(self.assets().values()), {b"\x00", b"\x01"})
        self.assertFalse((nested / core.HISTORY_NAME).exists())
        self.assertFalse((self.root / ".codex").exists())


if __name__ == "__main__":
    unittest.main()
