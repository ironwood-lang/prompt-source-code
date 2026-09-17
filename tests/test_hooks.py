import base64
import io
import json
import multiprocessing
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / "hooks"
HOOK_EVENTS = ROOT / "tests" / "fixtures" / "hook-events.json"
sys.path.insert(0, str(HOOKS))

import prompt_source_core as core


def user_transcript(
    root,
    session,
    *,
    originator="Codex Desktop",
    thread_source="user",
    metadata_session=None,
    metadata_cwd=None,
    force=False,
):
    root = Path(root)
    directory = root / ".test-transcripts"
    directory.mkdir(exist_ok=True)
    path = directory / f"{session}.jsonl"
    record = {
        "timestamp": "fixture",
        "type": "session_meta",
        "payload": {
            "session_id": metadata_session or session,
            "id": metadata_session or session,
            "cwd": str(metadata_cwd or root),
            "originator": originator,
            "thread_source": thread_source,
        },
    }
    serialized = json.dumps(record, separators=(",", ":")) + "\n"
    if force:
        path.write_text(serialized, encoding="utf-8")
    else:
        try:
            with path.open("x", encoding="utf-8") as transcript:
                transcript.write(serialized)
        except FileExistsError:
            pass
    return path


def generated_outputs(root):
    return [path for path in Path(root).iterdir() if path.name != ".test-transcripts"]


def prompt_event(root, prompt, *, session="session-1", turn="turn-1", model="model-1"):
    return {
        "session_id": session,
        "turn_id": turn,
        "transcript_path": str(user_transcript(root, session)),
        "cwd": str(root),
        "hook_event_name": "UserPromptSubmit",
        "model": model,
        "permission_mode": "default",
        "prompt": prompt,
    }


def interrupt_event(root, *, session="session-1", turn="turn-1"):
    return {
        "session_id": session,
        "turn_id": turn,
        "transcript_path": str(user_transcript(root, session)),
        "cwd": str(root),
        "hook_event_name": "Interrupt",
        "model": "model-1",
        "permission_mode": "default",
    }


def claim(number, prompt, *, session="session-1", turn="turn-1"):
    return {
        "entry_number": number,
        "session_id": session,
        "turn_id": turn,
        "prompt_utf8_base64": base64.b64encode(prompt.encode("utf-8")).decode("ascii"),
    }


def replacement_request(entry, replacement, prompt, *, session="session-1", turn="turn-1"):
    return {
        **claim(entry.number, prompt, session=session, turn=turn),
        "expected_entry_sha256": entry.utf8_sha256,
        "replacement_entry_base64": base64.b64encode(replacement.encode("utf-8")).decode(
            "ascii"
        ),
    }


def capture_worker(root, index, start, queue):
    try:
        start.wait()
        core.capture_prompt(
            Path(root),
            prompt_event(
                root,
                "simultaneous payload\n",
                session="concurrent-session",
                turn=f"turn-{index}",
            ),
        )
        queue.put(None)
    except Exception as exc:  # pragma: no cover - returned to parent for assertion
        queue.put(f"{type(exc).__name__}: {exc}")


def interrupt_worker(root, start, queue):
    try:
        start.wait()
        core.interrupt_turn(Path(root), interrupt_event(root))
        queue.put("interrupt:ok")
    except Exception as exc:
        queue.put(f"interrupt:{type(exc).__name__}")


def replace_worker(root, request, start, queue):
    try:
        start.wait()
        core.replace_entry(Path(root), request)
        queue.put("replace:ok")
    except Exception as exc:
        queue.put(f"replace:{type(exc).__name__}")


def capture_steering_worker(root, start, queue):
    try:
        start.wait()
        core.capture_prompt(Path(root), prompt_event(root, "racing steering\n"))
        queue.put("capture:ok")
    except Exception as exc:
        queue.put(f"capture:{type(exc).__name__}")


class HookCaptureTests(unittest.TestCase):
    def test_representative_hook_event_fixture_parses_and_associates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = json.loads(HOOK_EVENTS.read_text(encoding="utf-8"))
            submitted = dict(fixture["user_prompt_submit"])
            interrupted = dict(fixture["interrupt"])
            submitted["cwd"] = str(root)
            interrupted["cwd"] = str(root)
            transcript = str(user_transcript(root, submitted["session_id"]))
            submitted["transcript_path"] = transcript
            interrupted["transcript_path"] = transcript
            core.capture_prompt(root, submitted)
            self.assertEqual(core.interrupt_turn(root, interrupted), [1])
            entry = core.validate_history(
                (root / core.HISTORY_NAME).read_text(encoding="utf-8")
            )[0]
            self.assertEqual(entry.prompt, submitted["prompt"])
            self.assertEqual(entry.final_newline, "CRLF")
            self.assertEqual(entry.fields["Status"], "Interrupted")

    def test_user_prompt_submit_preserves_exact_utf8_and_dynamic_fence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prompt = (
                "  leading and  repeated spaces\n"
                "Unicode café 👩🏽‍💻\n"
                "````nested````\n"
                "### User input\n"
                "## Entry 999999\r\n"
            )
            output = core.capture_prompt(root, prompt_event(root, prompt))
            self.assertIsNotNone(output)
            history = (root / core.HISTORY_NAME).read_text(encoding="utf-8")
            entries = core.validate_history(history)
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0].prompt.encode("utf-8"), prompt.encode("utf-8"))
            self.assertEqual(entries[0].final_newline, "CRLF")
            self.assertEqual(entries[0].fields["Session ID"], '"session-1"')
            self.assertEqual(entries[0].fields["Turn ID"], '"turn-1"')
            self.assertEqual(entries[0].fields["Agent observation"], "Pending")
            self.assertNotIn(999999, [entry.number for entry in entries])
            context = output["hookSpecificOutput"]["additionalContext"]
            self.assertIn('"entry_number":1', context)
            self.assertIn(claim(1, prompt)["prompt_utf8_base64"], context)
            self.assertEqual(generated_outputs(root), [root / core.HISTORY_NAME])

    def test_newline_states_and_empty_prompt(self):
        cases = [("a\n", "LF"), ("a\r\n", "CRLF"), ("a\r", "CR"), ("a", "None"), ("", "None")]
        for index, (prompt, marker) in enumerate(cases):
            with self.subTest(marker=marker, prompt=repr(prompt)):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    core.capture_prompt(root, prompt_event(root, prompt, turn=f"turn-{index}"))
                    entry = core.validate_history(
                        (root / core.HISTORY_NAME).read_text(encoding="utf-8")
                    )[0]
                    self.assertEqual(entry.prompt, prompt)
                    self.assertEqual(entry.final_newline, marker)

    def test_followup_and_steering_association_use_hook_turn_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            core.capture_prompt(root, prompt_event(root, "initial\n", turn="turn-a"))
            core.capture_prompt(root, prompt_event(root, "steer one\n", turn="turn-a"))
            core.capture_prompt(root, prompt_event(root, "steer two\n", turn="turn-a"))
            core.capture_prompt(root, prompt_event(root, "follow up\n", turn="turn-b"))
            entries = core.validate_history(
                (root / core.HISTORY_NAME).read_text(encoding="utf-8")
            )
            self.assertEqual(
                [entry.fields["Interaction"] for entry in entries],
                ["Initial prompt", "Steering", "Steering", "Follow-up"],
            )
            self.assertEqual(entries[1].fields["Continues"], "Entry 000001")
            self.assertEqual(entries[2].fields["Continues"], "Entry 000002")
            self.assertEqual(entries[3].fields["Continues"], "Entry 000003")
            self.assertEqual(
                [json.loads(entry.fields["Turn ID"]) for entry in entries],
                ["turn-a", "turn-a", "turn-a", "turn-b"],
            )

    def test_hook_append_uses_physical_eof_after_repeated_result_text(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = (ROOT / "tests" / "fixtures" / "expected-history.md").read_text(
                encoding="utf-8"
            )
            history = fixture
            path = root / core.HISTORY_NAME
            path.write_text(history, encoding="utf-8")
            previous = core.validate_history(history)
            core.capture_prompt(
                root,
                prompt_event(root, "append only at physical EOF\n", session="new-session"),
            )
            updated = path.read_text(encoding="utf-8")
            entries = core.validate_history(updated)
            self.assertEqual(entries[-1].number, previous[-1].number + 1)
            self.assertEqual(entries[-1].prompt, "append only at physical EOF\n")
            self.assertEqual(entries[-1].start, updated.rindex("## Entry "))
            self.assertEqual(updated[: len(history)], history)

    def test_repeated_identical_prompts_are_distinct_and_claimed_one_to_one(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prompt = "identical\n"
            core.capture_prompt(root, prompt_event(root, prompt))
            core.capture_prompt(root, prompt_event(root, prompt))
            before = core.validate_history(
                (root / core.HISTORY_NAME).read_text(encoding="utf-8")
            )
            self.assertEqual([entry.number for entry in before], [1, 2])
            with self.assertRaises(core.NoReliableMatch):
                core.claim_entry(root, claim(2, prompt))
            first = core.claim_entry(root, claim(1, prompt))
            second = core.claim_entry(root, claim(2, prompt))
            self.assertEqual(first.fields["Agent observation"], "Claimed")
            self.assertEqual(second.fields["Agent observation"], "Claimed")

    def test_claim_requires_exact_session_turn_and_prompt_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            core.capture_prompt(root, prompt_event(root, "same text\n"))
            mismatches = [
                claim(1, "same text"),
                claim(1, "same text\n", session="other"),
                claim(1, "same text\n", turn="other"),
            ]
            for value in mismatches:
                with self.assertRaises(core.NoReliableMatch):
                    core.claim_entry(root, value)
            entry = core.validate_history(
                (root / core.HISTORY_NAME).read_text(encoding="utf-8")
            )[0]
            self.assertEqual(entry.fields["Agent observation"], "Pending")

    def test_subagent_prompt_is_not_a_user_interaction(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = prompt_event(root, "internal delegation\n")
            payload.update({"agent_id": "child", "agent_type": "worker"})
            self.assertIsNone(core.capture_prompt(root, payload))
            self.assertFalse((root / core.HISTORY_NAME).exists())

    def test_interrupt_marks_every_unfinished_entry_in_one_turn_and_preserves_completed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prompts = ["initial\n", "steering one\n", "steering two\n"]
            for prompt in prompts:
                core.capture_prompt(root, prompt_event(root, prompt))
            claimed = core.claim_entry(root, claim(1, prompts[0]))
            completed = claimed.text.replace(
                "- Status: In progress\n", "- Status: Completed\n", 1
            )
            completed += "\n### Result\n\nCompleted before Stop.\n\nChanged files: None.\n"
            core.replace_entry(root, replacement_request(claimed, completed, prompts[0]))
            changed = core.interrupt_turn(root, interrupt_event(root))
            self.assertEqual(changed, [2, 3])
            entries = core.validate_history(
                (root / core.HISTORY_NAME).read_text(encoding="utf-8")
            )
            self.assertEqual(
                [entry.fields["Status"] for entry in entries],
                ["Completed", "Interrupted", "Interrupted"],
            )
            self.assertEqual(entries[1].fields["Status reason"], core.INTERRUPT_REASON)
            self.assertEqual(entries[2].fields["Status reason"], core.INTERRUPT_REASON)
            for entry in entries[1:]:
                self.assertIn(
                    f"- Status reason: {core.INTERRUPT_REASON}\n\n### User input",
                    entry.text,
                )
                self.assertNotIn("\n\n- Status reason:", entry.text)
            self.assertIn("initial", entries[0].prompt)
            self.assertIn("steering one", entries[1].prompt)

    def test_interrupt_replaces_a_preexisting_status_reason(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prompt = "waiting\n"
            core.capture_prompt(root, prompt_event(root, prompt))
            entry = core.claim_entry(root, claim(1, prompt))
            enriched = entry.text.replace(
                "- Agent observation: Claimed\n",
                "- Agent observation: Claimed\n- Status reason: Waiting on task work.\n",
                1,
            )
            core.replace_entry(root, replacement_request(entry, enriched, prompt))
            self.assertEqual(core.interrupt_turn(root, interrupt_event(root)), [1])
            final = core.validate_history(
                (root / core.HISTORY_NAME).read_text(encoding="utf-8")
            )[0]
            self.assertEqual(final.fields["Status reason"], core.INTERRUPT_REASON)
            self.assertNotIn("Waiting on task work.", final.text)
            self.assertIn(
                f"- Status reason: {core.INTERRUPT_REASON}\n\n### User input",
                final.text,
            )

    def test_unmatched_interrupt_is_conservative_and_byte_preserving(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            core.capture_prompt(root, prompt_event(root, "work\n"))
            path = root / core.HISTORY_NAME
            before = path.read_bytes()
            with self.assertRaises(core.NoReliableMatch):
                core.interrupt_turn(root, interrupt_event(root, turn="other"))
            self.assertEqual(path.read_bytes(), before)

    def test_agent_replacement_is_atomic_and_preserves_immutable_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prompt = "correct me\n"
            core.capture_prompt(root, prompt_event(root, prompt))
            entry = core.claim_entry(root, claim(1, prompt))
            replacement = entry.text.replace(
                "- Interaction: Initial prompt\n", "- Interaction: Correction\n", 1
            )
            replacement = replacement.replace(
                "- Status: In progress\n", "- Status: Completed\n", 1
            )
            replacement += "\n### Result\n\nCorrection handled.\n\nChanged files: None.\n"
            updated = core.replace_entry(root, replacement_request(entry, replacement, prompt))
            self.assertEqual(updated.fields["Interaction"], "Correction")
            self.assertEqual(updated.fields["Status"], "Completed")
            self.assertEqual(updated.prompt, prompt)
            bad = updated.text.replace(prompt.rstrip("\n"), "rewritten")
            with self.assertRaises(core.HistoryConflict):
                core.replace_entry(root, replacement_request(updated, bad, prompt))

    def test_agent_correction_association_points_backward_without_rewriting(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original_prompt = "Use ALPHA.\n"
            correction_prompt = "Correction: use BETA instead.\n"
            core.capture_prompt(root, prompt_event(root, original_prompt, turn="turn-a"))
            original = core.claim_entry(
                root,
                claim(1, original_prompt, turn="turn-a"),
            )
            original_completed = original.text.replace(
                "- Status: In progress\n", "- Status: Completed\n", 1
            )
            original_completed += (
                "\n### Result\n\nRecorded ALPHA pending later direction.\n\n"
                "Changed files: None.\n"
            )
            core.replace_entry(
                root,
                replacement_request(
                    original,
                    original_completed,
                    original_prompt,
                    turn="turn-a",
                ),
            )

            core.capture_prompt(root, prompt_event(root, correction_prompt, turn="turn-b"))
            correction = core.claim_entry(
                root,
                claim(2, correction_prompt, turn="turn-b"),
            )
            corrected = correction.text.replace(
                "- Interaction: Follow-up\n", "- Interaction: Correction\n", 1
            ).replace(
                "- Continues: Entry 000001\n",
                "- Supersedes: Entry 000001\n",
                1,
            )
            corrected = corrected.replace(
                "- Status: In progress\n", "- Status: Completed\n", 1
            )
            corrected += "\n### Result\n\nApplied BETA.\n\nChanged files: None.\n"
            core.replace_entry(
                root,
                replacement_request(
                    correction,
                    corrected,
                    correction_prompt,
                    turn="turn-b",
                ),
            )
            entries = core.validate_history(
                (root / core.HISTORY_NAME).read_text(encoding="utf-8")
            )
            self.assertEqual(entries[1].fields["Interaction"], "Correction")
            self.assertEqual(entries[1].fields["Supersedes"], "Entry 000001")
            self.assertEqual(entries[0].prompt, original_prompt)

    def test_later_steering_appends_do_not_change_earlier_entry_digest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base = "base prompt\n"
            core.capture_prompt(root, prompt_event(root, base))
            claimed = core.claim_entry(root, claim(1, base))
            original_digest = claimed.utf8_sha256

            core.capture_prompt(root, prompt_event(root, "steering one\n"))
            core.capture_prompt(root, prompt_event(root, "steering two\n"))

            entries = core.validate_history(
                (root / core.HISTORY_NAME).read_text(encoding="utf-8")
            )
            self.assertEqual(entries[0].utf8_sha256, original_digest)
            replacement = claimed.text.replace(
                "- Status: In progress\n", "- Status: Completed\n", 1
            )
            replacement += "\n### Result\n\nCompleted after steering.\n\nChanged files: None.\n"
            updated = core.replace_entry(
                root,
                replacement_request(claimed, replacement, base),
            )
            self.assertEqual(updated.fields["Status"], "Completed")
            final = core.validate_history(
                (root / core.HISTORY_NAME).read_text(encoding="utf-8")
            )
            self.assertEqual([entry.number for entry in final], [1, 2, 3])
            self.assertEqual(final[1].prompt, "steering one\n")
            self.assertEqual(final[2].prompt, "steering two\n")

    def test_simultaneous_prompt_processes_produce_unique_ordered_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            user_transcript(root, "concurrent-session")
            context = multiprocessing.get_context("fork")
            start = context.Event()
            queue = context.Queue()
            processes = [
                context.Process(target=capture_worker, args=(root, index, start, queue))
                for index in range(12)
            ]
            for process in processes:
                process.start()
            start.set()
            for process in processes:
                process.join(15)
                self.assertEqual(process.exitcode, 0)
            errors = [queue.get(timeout=2) for _ in processes]
            self.assertEqual(errors, [None] * len(processes))
            entries = core.validate_history(
                (root / core.HISTORY_NAME).read_text(encoding="utf-8")
            )
            self.assertEqual([entry.number for entry in entries], list(range(1, 13)))
            self.assertEqual(len({json.loads(entry.fields["Turn ID"]) for entry in entries}), 12)
            self.assertEqual(generated_outputs(root), [root / core.HISTORY_NAME])

    def test_interrupt_racing_agent_update_never_overwrites_terminal_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prompt = "race\n"
            core.capture_prompt(root, prompt_event(root, prompt))
            entry = core.claim_entry(root, claim(1, prompt))
            replacement = entry.text.replace(
                "- Status: In progress\n", "- Status: Completed\n", 1
            )
            replacement += "\n### Result\n\nCompleted.\n\nChanged files: None.\n"
            request = replacement_request(entry, replacement, prompt)
            context = multiprocessing.get_context("fork")
            start = context.Event()
            queue = context.Queue()
            processes = [
                context.Process(target=interrupt_worker, args=(root, start, queue)),
                context.Process(target=replace_worker, args=(root, request, start, queue)),
            ]
            for process in processes:
                process.start()
            start.set()
            for process in processes:
                process.join(15)
                self.assertEqual(process.exitcode, 0)
            outcomes = {queue.get(timeout=2), queue.get(timeout=2)}
            self.assertIn(
                outcomes,
                [
                    {"interrupt:ok", "replace:HistoryConflict"},
                    {"replace:ok", "interrupt:NoReliableMatch"},
                ],
            )
            final = core.validate_history(
                (root / core.HISTORY_NAME).read_text(encoding="utf-8")
            )[0]
            self.assertIn(final.fields["Status"], {"Completed", "Interrupted"})
            if final.fields["Status"] == "Interrupted":
                self.assertEqual(final.fields["Status reason"], core.INTERRUPT_REASON)

    def test_interrupt_racing_prompt_capture_is_serialized_without_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            core.capture_prompt(root, prompt_event(root, "base\n"))
            context = multiprocessing.get_context("fork")
            start = context.Event()
            queue = context.Queue()
            processes = [
                context.Process(target=interrupt_worker, args=(root, start, queue)),
                context.Process(target=capture_steering_worker, args=(root, start, queue)),
            ]
            for process in processes:
                process.start()
            start.set()
            for process in processes:
                process.join(15)
                self.assertEqual(process.exitcode, 0)
            self.assertEqual(
                {queue.get(timeout=2), queue.get(timeout=2)},
                {"interrupt:ok", "capture:ok"},
            )
            final = core.validate_history(
                (root / core.HISTORY_NAME).read_text(encoding="utf-8")
            )
            self.assertEqual([entry.number for entry in final], [1, 2])
            self.assertEqual(final[0].fields["Status"], "Interrupted")
            self.assertIn(
                [entry.fields["Status"] for entry in final],
                [
                    ["Interrupted", "Interrupted"],
                    ["Interrupted", "In progress"],
                ],
            )

    def test_atomic_failure_retains_last_complete_history_and_removes_tempfile(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            core.capture_prompt(root, prompt_event(root, "stable\n"))
            path = root / core.HISTORY_NAME
            before = path.read_bytes()

            def fail(_temporary):
                raise OSError("injected before replace")

            with self.assertRaises(OSError):
                core._atomic_write(path, before.decode("utf-8") + "bad", before_replace=fail)
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(generated_outputs(root), [path])

    def test_malformed_input_wrong_event_and_cwd_mismatch_do_not_create_history(self):
        with self.assertRaises(core.InvalidEvent):
            core.read_event(io.BytesIO(b'{"truncated":'))
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as other:
            root = Path(directory)
            wrong = prompt_event(root, "x")
            wrong["hook_event_name"] = "Stop"
            with self.assertRaises(core.InvalidEvent):
                core.capture_prompt(root, wrong)
            mismatched = prompt_event(root, "x")
            mismatched["cwd"] = other
            with self.assertRaises(core.InvalidEvent):
                core.capture_prompt(root, mismatched)
            invalid_unicode = prompt_event(root, "\ud800")
            with self.assertRaises(core.InvalidEvent):
                core.capture_prompt(root, invalid_unicode)
            self.assertFalse((root / core.HISTORY_NAME).exists())

    def test_background_or_unverifiable_prompt_fails_closed_to_standard_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            missing = prompt_event(root, "internal suggestion")
            missing["transcript_path"] = None
            with self.assertRaises(core.InvalidEvent):
                core.capture_prompt(root, missing)

            feature = prompt_event(root, "internal suggestion", session="feature-session")
            feature["transcript_path"] = str(
                user_transcript(
                    root,
                    "feature-session",
                    thread_source="ambient_suggestions",
                    force=True,
                )
            )
            with self.assertRaises(core.InvalidEvent):
                core.capture_prompt(root, feature)

            cli = prompt_event(root, "CLI input", session="cli-session")
            cli["transcript_path"] = str(
                user_transcript(
                    root,
                    "cli-session",
                    originator="Codex CLI",
                    force=True,
                )
            )
            with self.assertRaises(core.InvalidEvent):
                core.capture_prompt(root, cli)

            wrong_session = prompt_event(root, "wrong session", session="event-session")
            wrong_session["transcript_path"] = str(
                user_transcript(root, "transcript-session")
            )
            with self.assertRaises(core.InvalidEvent):
                core.capture_prompt(root, wrong_session)

            conflicting_ids = prompt_event(
                root,
                "conflicting transcript IDs",
                session="conflicting-session",
            )
            transcript = Path(conflicting_ids["transcript_path"])
            record = json.loads(transcript.read_text(encoding="utf-8"))
            record["payload"]["session_id"] = "different-session"
            transcript.write_text(
                json.dumps(record, separators=(",", ":")) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(core.InvalidEvent):
                core.capture_prompt(root, conflicting_ids)

            with tempfile.TemporaryDirectory() as other:
                wrong_project = prompt_event(root, "wrong project", session="cwd-session")
                wrong_project["transcript_path"] = str(
                    user_transcript(
                        root,
                        "cwd-session",
                        metadata_cwd=other,
                        force=True,
                    )
                )
                with self.assertRaises(core.InvalidEvent):
                    core.capture_prompt(root, wrong_project)
            self.assertFalse((root / core.HISTORY_NAME).exists())

    def test_non_v1_truncated_and_out_of_order_history_are_not_repaired(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / core.HISTORY_NAME
            bad_values = [
                "<!-- prompt-source-schema: 2 -->\n",
                core.HEADER + "\n## Entry 000001\n",
                core.HEADER
                + "\n"
                + core.render_entry(
                    0,
                    interaction="Initial prompt",
                    session_id="session-1",
                    turn_id="turn-1",
                    prompt="zero\n",
                    model=None,
                    continues=None,
                ),
            ]
            for value in bad_values:
                path.write_text(value, encoding="utf-8")
                before = path.read_bytes()
                with self.assertRaises(core.HistoryConflict):
                    core.capture_prompt(root, prompt_event(root, "x\n"))
                self.assertEqual(path.read_bytes(), before)

            path.unlink()
            core.capture_prompt(root, prompt_event(root, "one\n", turn="one"))
            core.capture_prompt(root, prompt_event(root, "two\n", turn="two"))
            text = path.read_text(encoding="utf-8")
            entries = core.validate_history(text)
            swapped = text[: entries[0].start] + entries[1].text + entries[0].text
            path.write_text(swapped, encoding="utf-8")
            before = path.read_bytes()
            with self.assertRaises(core.HistoryConflict):
                core.capture_prompt(root, prompt_event(root, "three\n", turn="three"))
            self.assertEqual(path.read_bytes(), before)

    def test_unknown_or_out_of_order_metadata_and_invalid_results_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / core.HISTORY_NAME
            core.capture_prompt(root, prompt_event(root, "metadata\n"))
            valid = path.read_text(encoding="utf-8")

            unknown = valid.replace(
                "- Agent observation: Pending\n",
                "- Future field: opaque\n- Agent observation: Pending\n",
                1,
            )
            path.write_text(unknown, encoding="utf-8")
            before = path.read_bytes()
            with self.assertRaises(core.HistoryConflict):
                core.capture_prompt(root, prompt_event(root, "next\n", turn="turn-2"))
            self.assertEqual(path.read_bytes(), before)

            out_of_order = valid.replace(
                '- Session ID: "session-1"\n- Turn ID: "turn-1"\n',
                '- Turn ID: "turn-1"\n- Session ID: "session-1"\n',
                1,
            )
            path.write_text(out_of_order, encoding="utf-8")
            before = path.read_bytes()
            with self.assertRaises(core.HistoryConflict):
                core.capture_prompt(root, prompt_event(root, "next\n", turn="turn-2"))
            self.assertEqual(path.read_bytes(), before)

            path.write_text(valid, encoding="utf-8")
            pending = core.validate_history(valid)[0]
            completed_without_result = pending.text.replace(
                "- Status: In progress\n", "- Status: Completed\n", 1
            )
            with self.assertRaises(core.HistoryConflict):
                core.replace_entry(
                    root,
                    replacement_request(pending, completed_without_result, "metadata\n"),
                )

            in_progress_with_result = (
                pending.text + "\n### Result\n\nPremature.\n\nChanged files: None.\n"
            )
            with self.assertRaises(core.HistoryConflict):
                core.replace_entry(
                    root,
                    replacement_request(pending, in_progress_with_result, "metadata\n"),
                )

            duplicate = (
                core.HEADER
                + "\n"
                + core.render_entry(
                    1,
                    interaction="Initial prompt",
                    session_id="session-1",
                    turn_id="turn-1",
                    prompt="one\n",
                    model=None,
                    continues=None,
                )
                + "\n"
                + core.render_entry(
                    1,
                    interaction="Follow-up",
                    session_id="session-1",
                    turn_id="turn-2",
                    prompt="duplicate\n",
                    model=None,
                    continues=1,
                )
            )
            path.write_text(duplicate, encoding="utf-8")
            before = path.read_bytes()
            with self.assertRaises(core.HistoryConflict):
                core.capture_prompt(root, prompt_event(root, "three\n", turn="three"))
            self.assertEqual(path.read_bytes(), before)

    def test_failed_hook_process_leaves_standard_fallback_available(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            process = subprocess.run(
                [sys.executable, str(HOOKS / "prompt_source_hook.py")],
                cwd=root,
                input=b'{"hook_event_name":"UserPromptSubmit"',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertNotEqual(process.returncode, 0)
            self.assertIn(b"PromptSourceCode hook error", process.stderr)
            self.assertFalse((root / core.HISTORY_NAME).exists())

            definition = json.loads(
                (HOOKS / "hooks.json.example").read_text(encoding="utf-8")
            )
            guarded_command = definition["hooks"]["UserPromptSubmit"][0]["hooks"][0][
                "command"
            ]
            unavailable = subprocess.run(
                guarded_command,
                cwd=root,
                input=json.dumps(prompt_event(root, "fallback\n")).encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                executable="/bin/sh",
                check=False,
            )
            self.assertEqual(unavailable.returncode, 0)
            self.assertEqual(unavailable.stdout, b"")
            self.assertIn(b"continuing with standard capture", unavailable.stderr)
            self.assertFalse((root / core.HISTORY_NAME).exists())

            success_root = root / "guard-success"
            installed_hooks = success_root / ".codex" / "hooks"
            installed_hooks.mkdir(parents=True)
            for name in ("prompt_source_core.py", "prompt_source_hook.py"):
                (installed_hooks / name).write_bytes((HOOKS / name).read_bytes())
            successful = subprocess.run(
                guarded_command,
                cwd=success_root,
                input=json.dumps(
                    prompt_event(success_root, "guarded success\n", session="guard-session")
                ).encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                executable="/bin/sh",
                check=False,
            )
            self.assertEqual(successful.returncode, 0)
            output = json.loads(successful.stdout)
            self.assertEqual(
                output["hookSpecificOutput"]["hookEventName"],
                "UserPromptSubmit",
            )
            captured = core.validate_history(
                (success_root / core.HISTORY_NAME).read_text(encoding="utf-8")
            )
            self.assertEqual(len(captured), 1)
            self.assertEqual(captured[0].prompt, "guarded success\n")

            fixture = (ROOT / "tests" / "fixtures" / "expected-history.md").read_text(
                encoding="utf-8"
            )
            (root / core.HISTORY_NAME).write_text(fixture, encoding="utf-8")
            self.assertGreater(len(core.validate_history(fixture)), 0)

    def test_agent_cannot_replace_an_unclaimed_hook_entry(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prompt = "must claim first\n"
            core.capture_prompt(root, prompt_event(root, prompt))
            entry = core.validate_history(
                (root / core.HISTORY_NAME).read_text(encoding="utf-8")
            )[0]
            with self.assertRaises(core.HistoryConflict):
                core.replace_entry(root, replacement_request(entry, entry.text, prompt))

    def test_hook_assets_are_inert_local_and_have_only_two_events(self):
        config = json.loads((HOOKS / "hooks.json.example").read_text(encoding="utf-8"))
        self.assertEqual(set(config["hooks"]), {"UserPromptSubmit", "Interrupt"})
        self.assertIn(".codex/hooks/prompt_source_hook.py", json.dumps(config))
        for event in ("UserPromptSubmit", "Interrupt"):
            command = config["hooks"][event][0]["hooks"][0]["command"]
            self.assertIn("/bin/sh -c", command)
            self.assertIn("continuing with standard capture", command)
        self.assertFalse((ROOT / ".codex" / "hooks.json").exists())
        source = "\n".join(
            path.read_text(encoding="utf-8") for path in sorted(HOOKS.glob("*.py"))
        )
        config_text = (HOOKS / "hooks.json.example").read_text(encoding="utf-8")
        for forbidden in (
            r"\bimport\s+(?:socket|subprocess|urllib|http|requests|httpx)\b",
            r"\bfrom\s+(?:socket|subprocess|urllib|http|requests|httpx)\b",
            r"\b(?:curl|wget)\b",
            r"\bgit\s+(?:add|commit|push|fetch|pull|status|rev-parse)\b",
        ):
            self.assertIsNone(re.search(forbidden, source, flags=re.IGNORECASE))
            self.assertIsNone(re.search(forbidden, config_text, flags=re.IGNORECASE))


if __name__ == "__main__":
    unittest.main()
