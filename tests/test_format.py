import base64
import hashlib
import json
from pathlib import Path
import re
import unittest
import zlib


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "expected-history.md"
ARTIFACTS = ROOT / "tests" / "fixtures" / "artifacts.json"
SPEC = ROOT / "docs" / "PROMPT_SOURCE_FORMAT.md"
TEMPLATE = ROOT / "templates" / "AGENTS.prompt-source-standard.md"
README = ROOT / "README.md"
MANUAL = ROOT / "docs" / "MANUAL_CODEX_DESKTOP_VALIDATION.md"
ROADMAP = ROOT / "docs" / "ROADMAP.md"
OPTIONAL_HOOKS = ROOT / "docs" / "OPTIONAL_HOOKS.md"
INSTALLATION = ROOT / "docs" / "INSTALLATION.md"
COMPATIBILITY = ROOT / "docs" / "COMPATIBILITY.md"
READINESS = ROOT / "docs" / "CODEX_DESKTOP_V1_RELEASE_READINESS.md"
RELEASE_MANIFEST = ROOT / "tests" / "fixtures" / "release-manifest.json"

SCHEMA_MARKER = "<!-- prompt-source-schema: 1 -->"
HEADER = """<!-- prompt-source-schema: 1 -->

# Prompt Source

This file records the chronological user interactions that shaped this project. User
input is preserved at the Codex Desktop delivery boundary described by PromptSourceCode
format version 1.

Generated history and assets are local provenance. Do not stage, commit, push, publish,
or upload them unless the user explicitly requests it.
"""


def outside_fence_lines(text):
    """Yield (offset, line) for Markdown lines that are not fenced payload content."""
    offset = 0
    fence_character = None
    fence_length = 0
    opening = re.compile(r"^(`{3,}|~{3,})[^\r\n]*\r?\n?$")

    for line in text.splitlines(keepends=True):
        stripped = line.rstrip("\r\n")
        if fence_character is None:
            yield offset, line
            match = opening.match(line)
            if match:
                fence_character = match.group(1)[0]
                fence_length = len(match.group(1))
        else:
            if re.fullmatch(
                re.escape(fence_character) + "{" + str(fence_length) + ",}[ \t]*",
                stripped,
            ):
                fence_character = None
                fence_length = 0
        offset += len(line)


def entry_blocks(text):
    headings = []
    for offset, line in outside_fence_lines(text):
        match = re.fullmatch(r"## Entry (\d{6,})\r?\n?", line)
        if match:
            headings.append((offset, int(match.group(1))))

    blocks = []
    for index, (start, number) in enumerate(headings):
        end = headings[index + 1][0] if index + 1 < len(headings) else len(text)
        blocks.append((number, text[start:end]))
    return blocks


def metadata(block):
    before_input = block.split("\n### User input\n", 1)[0]
    fields = {}
    for key, value in re.findall(r"^- ([A-Za-z ]+): (.+)$", before_input, re.MULTILINE):
        fields[key] = value
    return fields


def structural_headings(block):
    return [
        line.rstrip("\r\n")
        for _, line in outside_fence_lines(block)
        if re.match(r"^#{2,4} ", line)
    ]


def fenced_payload(block, heading="### User input"):
    """Return (marker, body, reconstructed, fence) for a canonical payload section."""
    lines = block.splitlines(keepends=True)
    heading_index = next(i for i, line in enumerate(lines) if line.rstrip("\r\n") == heading)

    marker = None
    opening_index = None
    opening_match = None
    for index in range(heading_index + 1, len(lines)):
        line = lines[index]
        if line.startswith("- Final newline: "):
            marker = line.removeprefix("- Final newline: ").rstrip("\r\n")
        match = re.fullmatch(r"(`{3,}|~{3,})text\r?\n", line)
        if match:
            opening_index = index
            opening_match = match
            break

    if marker is None or opening_index is None or opening_match is None:
        raise AssertionError(f"Malformed payload after {heading}")

    fence = opening_match.group(1)
    closing_index = None
    for index in range(opening_index + 1, len(lines)):
        if re.fullmatch(re.escape(fence) + r"\r?\n?", lines[index]):
            closing_index = index
            break
    if closing_index is None:
        raise AssertionError(f"Unclosed payload after {heading}")

    physical_body = "".join(lines[opening_index + 1 : closing_index])
    if physical_body:
        if not physical_body.endswith("\n"):
            raise AssertionError("Payload lacks the structural LF before its closing fence")
        body = physical_body[:-1]
    else:
        body = ""

    endings = {"LF": "\n", "CRLF": "\r\n", "CR": "\r", "None": ""}
    reconstructed = None if marker == "Unknown" else body + endings[marker]
    return marker, body, reconstructed, fence


def png_scanline(payload):
    """Return IHDR and decompressed scanline bytes for the tiny PNG fixtures."""
    if not payload.startswith(b"\x89PNG\r\n\x1a\n"):
        raise AssertionError("Fixture is not a PNG")
    position = 8
    ihdr = None
    idat = bytearray()
    while position < len(payload):
        length = int.from_bytes(payload[position : position + 4], "big")
        kind = payload[position + 4 : position + 8]
        data = payload[position + 8 : position + 8 + length]
        position += 12 + length
        if kind == b"IHDR":
            ihdr = data
        elif kind == b"IDAT":
            idat.extend(data)
        elif kind == b"IEND":
            break
    return ihdr, zlib.decompress(bytes(idat))


def markdown_fences_balanced(text):
    fence_character = None
    fence_length = 0
    for line in text.splitlines():
        if fence_character is None:
            match = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
            if match:
                fence_character = match.group(1)[0]
                fence_length = len(match.group(1))
        elif re.fullmatch(
            r" {0,3}"
            + re.escape(fence_character)
            + "{"
            + str(fence_length)
            + r",}[ \t]*",
            line,
        ):
            fence_character = None
            fence_length = 0
    return fence_character is None


class FormatFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.history = FIXTURE.read_text(encoding="utf-8")
        cls.blocks = entry_blocks(cls.history)
        cls.by_number = dict(cls.blocks)

    def test_required_schema_marker_and_header(self):
        self.assertTrue(self.history.startswith(HEADER + "\n"))
        self.assertEqual(self.history.splitlines()[0], SCHEMA_MARKER)
        self.assertIn(SCHEMA_MARKER, SPEC.read_text(encoding="utf-8"))
        self.assertIn(SCHEMA_MARKER, TEMPLATE.read_text(encoding="utf-8"))

    def test_entries_are_unique_ordered_and_contiguous(self):
        numbers = [number for number, _ in self.blocks]
        self.assertEqual(numbers, list(range(1, 13)))
        self.assertEqual(len(numbers), len(set(numbers)))
        self.assertNotIn(999999, numbers, "A heading inside user input became structure")

    def test_fixture_covers_interaction_types_and_completed_results(self):
        interaction_values = [metadata(block)["Interaction"] for _, block in self.blocks]
        interactions = set(interaction_values)
        self.assertEqual(
            interactions,
            {"Initial prompt", "Follow-up", "Steering", "Correction"},
        )
        self.assertEqual(interaction_values.count("Steering"), 2)
        for _, block in self.blocks:
            if metadata(block)["Status"] == "Completed":
                self.assertIn("### Result", structural_headings(block))

    def test_every_entry_has_canonical_required_metadata_and_one_user_section(self):
        allowed_statuses = {"In progress", "Completed", "Incomplete", "Interrupted"}
        allowed_methods = {"Instruction-mediated", "Hook-assisted"}
        for number, block in self.blocks:
            fields = metadata(block)
            self.assertIn(fields["Status"], allowed_statuses)
            self.assertIn(fields["Capture method"], allowed_methods)
            self.assertEqual(
                structural_headings(block).count("### User input"),
                1,
                f"Entry {number:06d} must have exactly one structural user section",
            )

    def test_complex_payload_survives_as_literal_text(self):
        marker, body, reconstructed, fence = fenced_payload(self.by_number[1])
        self.assertEqual(marker, "None")
        self.assertEqual(len(fence), 10)
        self.assertEqual(fence[0], "`")
        self.assertTrue(body.startswith("  Pleese  keep   every space.   \n\tA tab"))
        self.assertIn("Unicode: café, Ελληνικά, 日本語, 👩🏽‍💻", body)
        self.assertIn("`" * 9 + "python", body)
        self.assertIn("~" * 11 + "text", body)
        self.assertIn("## Entry 999999", body)
        self.assertTrue(reconstructed.endswith("No final newline follows this sentence."))
        self.assertFalse(reconstructed.endswith("\n"))

    def test_every_user_payload_uses_the_minimal_safe_dynamic_fence(self):
        for number, block in self.blocks:
            _, body, _, fence = fenced_payload(block)
            longest = {}
            for character in ("`", "~"):
                runs = re.findall(re.escape(character) + r"+", body)
                longest[character] = max((len(run) for run in runs), default=0)
            expected_character = "`" if longest["`"] <= longest["~"] else "~"
            expected_length = max(3, longest[expected_character] + 1)
            self.assertEqual(
                (fence[0], len(fence)),
                (expected_character, expected_length),
                f"Entry {number:06d} has a non-canonical fence",
            )

    def test_correction_points_backward_without_removing_original(self):
        correction = metadata(self.by_number[5])
        self.assertEqual(correction["Interaction"], "Correction")
        self.assertEqual(correction["Supersedes"], "Entry 000003")
        self.assertIn("Use blue for the example badge.", self.by_number[3])
        self.assertIn("make the badge amber, not blue", self.by_number[5])

    def test_desktop_context_is_separate_from_user_authored_input(self):
        _, attached_user, _, _ = fenced_payload(self.by_number[6])
        _, attached_context, _, _ = fenced_payload(
            self.by_number[6], "### Codex Desktop runtime context"
        )
        self.assertNotIn("Attached file: notes.txt", attached_user)
        self.assertIn("Attached file: notes.txt", attached_context)

        _, pasted_user, _, _ = fenced_payload(self.by_number[8])
        _, pasted_context, _, _ = fenced_payload(
            self.by_number[8], "### Codex Desktop runtime context"
        )
        self.assertNotIn("<image>", pasted_user)
        self.assertIn("no literal <image> tag was user-authored", pasted_context)

    def test_incomplete_and_interrupted_are_distinct(self):
        incomplete = metadata(self.by_number[10])
        self.assertEqual(incomplete["Status"], "Incomplete")
        self.assertEqual(incomplete["Capture method"], "Instruction-mediated")
        self.assertEqual(
            incomplete["Status reason"],
            "Completion reason unavailable; no reliable Interrupt event was observed.",
        )

        interrupted = metadata(self.by_number[11])
        self.assertEqual(interrupted["Status"], "Interrupted")
        self.assertEqual(interrupted["Capture method"], "Hook-assisted")
        self.assertIn("Session ID", interrupted)
        self.assertIn("Turn ID", interrupted)
        self.assertEqual(interrupted["Agent observation"], "Claimed")
        self.assertEqual(interrupted["Status reason"], "Hook-confirmed Interrupt event.")

        for _, block in self.blocks:
            fields = metadata(block)
            if fields["Status"] == "Interrupted":
                self.assertEqual(fields["Capture method"], "Hook-assisted")

    def test_no_change_result_is_explicit(self):
        fields = metadata(self.by_number[9])
        self.assertEqual(fields["Status"], "Completed")
        self.assertIn("Changed files: None.", self.by_number[9])

    def test_asset_references_are_flat_and_repository_relative(self):
        references = re.findall(
            r"\]\(<(prompt_source_assets/[^>]+)>\)", self.history
        )
        self.assertEqual(len(references), 4)
        self.assertEqual(len(references), len(set(references)))
        for reference in references:
            remainder = reference.removeprefix("prompt_source_assets/")
            self.assertNotIn("/", remainder)
            self.assertRegex(remainder, r"^prompt-\d{6,}-[A-Za-z0-9._-]+$")

    def test_same_entry_collision_uses_suffix_without_overwrite(self):
        block = self.by_number[7]
        base_path = "prompt_source_assets/prompt-000007-Logo-Final.png"
        collision_path = "prompt_source_assets/prompt-000007-Logo-Final-002.png"
        self.assertIn(base_path, block)
        self.assertIn(collision_path, block)

        manifest = json.loads(ARTIFACTS.read_text(encoding="utf-8"))
        by_path = {
            artifact.get("captured_path"): artifact
            for artifact in manifest["artifacts"]
            if artifact.get("captured_path")
        }
        first = base64.b64decode(by_path[base_path]["payload_base64"], validate=True)
        second = base64.b64decode(
            by_path[collision_path]["payload_base64"], validate=True
        )
        self.assertNotEqual(first, second)
        self.assertNotEqual(by_path[base_path]["sha256"], by_path[collision_path]["sha256"])

    def test_pasted_image_fidelity_is_one_physical_field_line(self):
        fidelity = (
            "- Fidelity: Byte-for-byte copy of the clipboard image materialized by "
            "Codex Desktop; binary identity with any pre-clipboard source is not claimed."
        )
        for path in (FIXTURE, SPEC, TEMPLATE):
            lines = path.read_text(encoding="utf-8").splitlines()
            expected = fidelity if path == FIXTURE else fidelity.removeprefix("- Fidelity: ")
            self.assertIn(expected, lines, f"{path} must keep the fidelity value on one line")

        manual = " ".join(MANUAL.read_text(encoding="utf-8").split())
        self.assertIn("one physical Markdown line", manual)
        self.assertIn("In one interaction and therefore one entry", manual)

    def test_unavailable_artifact_has_no_invented_copy_metadata(self):
        block = self.by_number[12]
        self.assertIn("- Preservation: Unavailable", block)
        self.assertIn("- Unavailable reason:", block)
        artifact_section = block.split("### Artifacts\n", 1)[1].split("### Result\n", 1)[0]
        self.assertNotIn("- Preserved copy:", artifact_section)
        self.assertNotIn("- Byte count:", artifact_section)
        self.assertNotIn("- SHA-256:", artifact_section)

    def test_artifact_manifest_has_verified_bytes_and_hashes(self):
        manifest = json.loads(ARTIFACTS.read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema"], 1)
        self.assertEqual(
            {artifact["kind"] for artifact in manifest["artifacts"]},
            {"Attached file", "Attached image", "Pasted image"},
        )
        pasted = None
        for artifact in manifest["artifacts"]:
            path = artifact.get("captured_path")
            if path is None:
                self.assertEqual(artifact["preservation"], "Unavailable")
                self.assertNotIn("sha256", artifact)
                self.assertNotIn("byte_count", artifact)
                continue

            self.assertNotIn("/", path.removeprefix("prompt_source_assets/"))
            payload = base64.b64decode(artifact["payload_base64"], validate=True)
            self.assertEqual(len(payload), artifact["byte_count"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), artifact["sha256"])
            self.assertIn(path, self.history)
            self.assertIn(artifact["sha256"], self.history)
            if artifact["id"] == "pasted-image":
                pasted = artifact

        self.assertIsNotNone(pasted)
        materialized = base64.b64decode(pasted["payload_base64"], validate=True)
        original = base64.b64decode(
            pasted["pre_clipboard_payload_base64"], validate=True
        )
        self.assertNotEqual(materialized, original)
        self.assertNotEqual(
            hashlib.sha256(materialized).hexdigest(),
            hashlib.sha256(original).hexdigest(),
        )
        self.assertEqual(png_scanline(materialized), png_scanline(original))
        self.assertTrue(pasted["decoded_pixels_equal"])

    def test_repository_does_not_contain_live_capture_outputs(self):
        self.assertFalse((ROOT / "PROMPT_SOURCE.md").exists())
        self.assertFalse((ROOT / "prompt_source_assets").exists())
        self.assertEqual(list(ROOT.rglob("PROMPT_SOURCE.md")), [])
        self.assertEqual(
            [path for path in ROOT.rglob("prompt_source_assets") if path.is_dir()], []
        )

    def test_standard_template_contains_required_contract(self):
        template = TEMPLATE.read_text(encoding="utf-8")
        normalized_template = " ".join(template.split())
        required_phrases = [
            "before performing the requested project work",
            "Each interaction gets its own sequential entry",
            "Capture method: Instruction-mediated",
            "Status: In progress",
            "Completion reason unavailable; no reliable Interrupt event was observed.",
            "Hook-confirmed Interrupt event.",
            "prompt_source_assets/",
            "Do not stage, commit, push, publish, or upload",
            "raw keystrokes or editor state",
            "Never alter or delete earlier user input",
            "prompt-source-standard-begin",
            "prompt-source-standard-end",
            "Capture: enabled",
            "Capture: disabled",
            "the final `### Git restriction` remains active",
            "Append the new entry at the physical end",
            "strictly increasing physical order",
            "never insertion after a matching result",
            "move only that newly created block to physical EOF",
            "PromptSourceCode hook matching context",
            "--claim",
            "--replace-entry",
            "earliest `In progress`, `Hook-assisted`, `Pending` observation",
            "Deduplication note",
            "Never relabel an instruction-created entry as `Hook-assisted`",
            "absent, disabled, untrusted, unavailable, or failed",
            "unrecognized or out-of-order entry metadata",
            "unsupported/future schema marker",
            "Completed, incomplete, and interrupted states are terminal",
        ]
        for phrase in required_phrases:
            self.assertIn(" ".join(phrase.split()), normalized_template)

    def test_readme_documents_standard_capture_lifecycle(self):
        readme = " ".join(README.read_text(encoding="utf-8").split())
        required_phrases = [
            "Install in a new or existing project",
            "Update the instruction block",
            "Disable or re-enable future capture",
            "Remove instructions or generated history",
            "agent-behavior restriction, not an automatic `.gitignore` rule",
            "Never copy it into an end-user project",
            "Optional Hook-Assisted Capture",
            "separate `/hooks` review and trust",
            "Never bypass hook trust",
        ]
        for phrase in required_phrases:
            self.assertIn(" ".join(phrase.split()), readme)

    def test_hook_contract_and_lifecycle_documentation_are_aligned(self):
        spec = " ".join(SPEC.read_text(encoding="utf-8").split())
        hooks = " ".join(OPTIONAL_HOOKS.read_text(encoding="utf-8").split())
        manual = " ".join(MANUAL.read_text(encoding="utf-8").split())
        required_spec = [
            "Agent observation: Pending",
            "same session ID, turn ID, and exact prompt bytes",
            "one-to-one and order-preserving",
            "project-directory lock and same-directory atomic replacement",
            "Hook-confirmed Interrupt event.",
            "failed replacement before the atomic rename leaves the last complete history",
        ]
        required_hooks = [
            "Codex CLI only for the explicit review-and-trust operation",
            "Fully restart Codex Desktop",
            "changes its hash and invalidates the prior decision",
            "Never use `--dangerously-bypass-hook-trust`",
            "make no network requests and run no Git commands",
            "absent, unavailable, disabled, untrusted, or failed",
            "disable both reviewed definitions",
        ]
        required_manual = [
            "at least two steering messages",
            "Submit the same text twice deliberately",
            "press Stop",
            "failure injection before atomic replacement",
            "Disable or remove both hooks",
        ]
        for phrase in required_spec:
            self.assertIn(" ".join(phrase.split()), spec)
        for phrase in required_hooks:
            self.assertIn(" ".join(phrase.split()), hooks)
        for phrase in required_manual:
            self.assertIn(" ".join(phrase.split()), manual)

    def test_format_freeze_and_compatibility_policy_are_explicit(self):
        spec = " ".join(SPEC.read_text(encoding="utf-8").split())
        compatibility = " ".join(COMPATIBILITY.read_text(encoding="utf-8").split())
        required_spec = [
            "frozen, normative PromptSourceCode schema-1 contract",
            "The integer is the storage-format compatibility version",
            "Schema 1 is a closed contract",
            "permitted status transitions",
            "Ordering, concurrency, and crash-safety guarantees",
            "Invalid, truncated, incompatible, and future histories",
            "numbering gap by itself is valid",
            "Future PromptSourceCode compatibility",
        ]
        required_compatibility = [
            "Format compatibility",
            "Capture-environment support",
            "Codex Desktop 26.908.70816 (9275)",
            "Codex Desktop 26.911.61220 (9647)",
            "`/usr/bin/python3` 3.9.6",
            "does not claim capture-environment support",
            "Do not rewrite, renumber, normalize, or recreate existing schema-1 entries",
            "Modifying a command or handler property invalidates the prior decision",
            "Version 1 makes no promise that such a tool exists",
        ]
        for phrase in required_spec:
            self.assertIn(" ".join(phrase.split()), spec)
        for phrase in required_compatibility:
            self.assertIn(" ".join(phrase.split()), compatibility)

    def test_installation_guide_covers_the_complete_user_lifecycle(self):
        guide = " ".join(INSTALLATION.read_text(encoding="utf-8").split())
        required = [
            "Install standard capture in a new project",
            "Add standard capture to an existing `AGENTS.md`",
            "Verify the first capture",
            "Update the standard instruction block",
            "Disable and re-enable standard capture",
            "Remove the standard instructions",
            "Optionally install the inert hook files",
            "Review and trust each hook explicitly",
            "Update, disable, re-enable, or remove the hooks",
            "Diagnose hook failures without losing the fallback",
            "Understand Git behavior",
            "Upgrade an earlier installation",
            "The tested CLI did not display raw trust hashes",
            "modifying a command or handler property invalidates the prior decision",
            "Codex CLI only for hook review and trust",
            "Never bypass hook trust",
        ]
        for phrase in required:
            self.assertIn(" ".join(phrase.split()), guide)

    def test_copyable_release_assets_match_the_frozen_manifest(self):
        manifest = json.loads(RELEASE_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["prompt_source_schema"], 1)
        self.assertEqual(manifest["release"], "version 1")
        expected_paths = {
            "templates/AGENTS.prompt-source-standard.md",
            "hooks/hooks.json.example",
            "hooks/prompt_source_core.py",
            "hooks/prompt_source_hook.py",
        }
        self.assertEqual(set(manifest["files"]), expected_paths)
        for relative, expected in manifest["files"].items():
            payload = (ROOT / relative).read_bytes()
            self.assertEqual(len(payload), expected["byte_count"], relative)
            self.assertEqual(hashlib.sha256(payload).hexdigest(), expected["sha256"], relative)

    def test_release_readiness_report_exists_and_does_not_claim_publication(self):
        report = " ".join(READINESS.read_text(encoding="utf-8").split())
        for phrase in (
            "Version 1 Release Readiness",
            "Disposable project isolation",
            "Case-by-case outcomes",
            "Automated validation",
            "Final storage topology",
            "Defects found and resolutions",
            "Ready for an explicitly authorized tag",
            "No version tag, GitHub release, or package publication was created",
        ):
            self.assertIn(" ".join(phrase.split()), report)

    def test_markdown_fences_and_internal_links_are_valid(self):
        for path in ROOT.rglob("*.md"):
            self.assertTrue(
                markdown_fences_balanced(path.read_text(encoding="utf-8")),
                f"Unbalanced Markdown fence in {path}",
            )

        authored_docs = [*ROOT.glob("*.md"), *sorted((ROOT / "docs").glob("*.md"))]
        authored_docs.append(TEMPLATE)
        for path in authored_docs:
            text = path.read_text(encoding="utf-8")
            outside_text = "".join(line for _, line in outside_fence_lines(text))
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", outside_text):
                if target.startswith(("http://", "https://", "#")):
                    continue
                target = target.strip("<>").split("#", 1)[0]
                resolved = (path.parent / target).resolve()
                self.assertTrue(resolved.exists(), f"Broken local link in {path}: {target}")


if __name__ == "__main__":
    unittest.main()
