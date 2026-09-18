#!/usr/bin/env python3
"""Standard-library schema validator and optional-hook core for PromptSourceCode."""

from __future__ import annotations

import argparse
import base64
import binascii
from contextlib import contextmanager
from dataclasses import dataclass
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from typing import Any, Callable, Iterator


SCHEMA_MARKER = "<!-- prompt-source-schema: 1 -->"
HISTORY_NAME = "PROMPT_SOURCE.md"
HEADER = """<!-- prompt-source-schema: 1 -->

# Prompt Source

This file records the chronological user interactions that shaped this project. User
input is preserved at the Codex Desktop delivery boundary described by PromptSourceCode
format version 1.

Generated history and assets are local provenance. Do not stage, commit, push, publish,
or upload them unless the user explicitly requests it.
"""
INTERRUPT_REASON = "Hook-confirmed Interrupt event."
PASTED_IMAGE_FIDELITY = (
    "Byte-for-byte copy of the clipboard image materialized by Codex Desktop; "
    "binary identity with any pre-clipboard source is not claimed."
)
UNCERTAIN_DEDUPLICATION_NOTE = (
    "Identity with a hook-created observation could not be established safely; "
    "both observations were preserved."
)
REQUIRED_ENTRY_FIELDS = ("Interaction", "Status", "Capture method")
OPTIONAL_ENTRY_FIELDS = (
    "Observed at",
    "Session ID",
    "Turn ID",
    "Model",
    "Agent observation",
    "Deduplication note",
    "Continues",
    "Supersedes",
    "Status reason",
)
DESKTOP_ARTIFACT_KINDS = {"Attached file", "Attached image", "Pasted image"}
RUNTIME_CONTEXT_HEADING = "### Codex Desktop runtime context"
DESKTOP_ARTIFACT_CONTEXT = (
    "The agent observed a Codex Desktop attachment or pasted image accompanying this "
    "request. Artifact details are recorded separately; Desktop source-path notices "
    "and image markers are not user-authored input."
)
ARTIFACT_KINDS = {
    "Attached file",
    "Attached image",
    "Pasted image",
    "Repository file snapshot",
    "Requested artifact",
}
OPTIONAL_PRESERVED_ARTIFACT_FIELDS = (
    "Repository source",
    "Source byte count",
    "Source SHA-256",
    "Reuse note",
    "Pre-clipboard comparison",
)
# Frozen instruction pair for the standard path. Optional hook event handlers do
# not consult this control: their enablement and trust remain separate.
STANDARD_LOADER_SHA256 = "d64f51155fd5cba44370f9afd0300737f253b5db6244844dd8314af4fb6fd1ce"
STANDARD_INSTRUCTIONS_SHA256 = "6ce534674aa8bc5e3c4b3966e2a28791721210d648fc68a54e077b3084bf2a01"


class PromptSourceError(Exception):
    """Base class for safe, user-facing hook failures."""


class InvalidEvent(PromptSourceError):
    """The hook input is missing or contains an invalid reliable field."""


class HistoryConflict(PromptSourceError):
    """The existing history is incompatible, malformed, or changed concurrently."""


class NoReliableMatch(PromptSourceError):
    """No entry can be changed without guessing event identity."""


@dataclass(frozen=True)
class Entry:
    number: int
    start: int
    end: int
    text: str
    fields: dict[str, str]
    prompt: str
    final_newline: str

    @property
    def displayed_number(self) -> str:
        return f"{self.number:06d}"

    @property
    def utf8_sha256(self) -> str:
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()


def _required_string(payload: dict[str, Any], name: str, *, allow_empty: bool = False) -> str:
    value = payload.get(name)
    if not isinstance(value, str) or (not allow_empty and value == ""):
        qualifier = "a string" if allow_empty else "a non-empty string"
        raise InvalidEvent(f"{name!r} must be {qualifier}")
    return value


def _utf8_bytes(value: str, name: str) -> bytes:
    try:
        return value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise InvalidEvent(f"{name!r} is not valid UTF-8 text: {exc}") from exc


def read_event(stream: Any = None) -> dict[str, Any]:
    """Read exactly one UTF-8 JSON object from a binary stream."""
    source = sys.stdin.buffer if stream is None else stream
    raw = source.read()
    if not raw:
        raise InvalidEvent("hook stdin was empty")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InvalidEvent(f"hook stdin was not UTF-8: {exc}") from exc
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise InvalidEvent(f"hook stdin was not one complete JSON value: {exc}") from exc
    if not isinstance(payload, dict):
        raise InvalidEvent("hook input must be a JSON object")
    return payload


def _validated_root(root: Path, payload: dict[str, Any] | None = None) -> Path:
    try:
        resolved = root.resolve(strict=True)
    except OSError as exc:
        raise InvalidEvent(f"project root is unavailable: {exc}") from exc
    if not resolved.is_dir():
        raise InvalidEvent("project root is not a directory")
    if payload is not None:
        event_cwd = Path(_required_string(payload, "cwd"))
        try:
            event_root = event_cwd.resolve(strict=True)
        except OSError as exc:
            raise InvalidEvent(f"hook cwd is unavailable: {exc}") from exc
        if event_root != resolved:
            raise InvalidEvent(
                f"hook cwd {str(event_root)!r} does not match process cwd {str(resolved)!r}"
            )
    return resolved


def _validate_desktop_user_transcript(
    root: Path,
    payload: dict[str, Any],
    session_id: str,
) -> None:
    """Fail closed unless the event belongs to a persisted user-created Desktop task."""
    raw_path = _required_string(payload, "transcript_path")
    try:
        transcript_path = Path(raw_path).resolve(strict=True)
    except OSError as exc:
        raise InvalidEvent(f"hook transcript is unavailable: {exc}") from exc
    if not transcript_path.is_file():
        raise InvalidEvent("hook transcript path is not a file")
    try:
        with transcript_path.open("r", encoding="utf-8", newline="") as transcript:
            first_line = transcript.readline(1_048_577)
    except (OSError, UnicodeDecodeError) as exc:
        raise InvalidEvent(f"cannot read hook transcript metadata: {exc}") from exc
    if not first_line or len(first_line) > 1_048_576 or not first_line.endswith("\n"):
        raise InvalidEvent("hook transcript metadata is missing, oversized, or truncated")
    try:
        record = json.loads(first_line)
    except json.JSONDecodeError as exc:
        raise InvalidEvent(f"hook transcript metadata is not valid JSON: {exc}") from exc
    if not isinstance(record, dict) or record.get("type") != "session_meta":
        raise InvalidEvent("hook transcript does not begin with session_meta")
    metadata = record.get("payload")
    if not isinstance(metadata, dict):
        raise InvalidEvent("hook transcript session_meta payload is invalid")
    transcript_ids = [
        metadata[name] for name in ("session_id", "id") if name in metadata
    ]
    if not transcript_ids or any(
        not isinstance(value, str) or value != session_id for value in transcript_ids
    ):
        raise InvalidEvent("hook transcript session ID does not match the event")
    metadata_cwd = metadata.get("cwd")
    if not isinstance(metadata_cwd, str):
        raise InvalidEvent("hook transcript lacks a reliable project cwd")
    try:
        if Path(metadata_cwd).resolve(strict=True) != root:
            raise InvalidEvent("hook transcript cwd does not match the event project")
    except OSError as exc:
        raise InvalidEvent(f"hook transcript cwd is unavailable: {exc}") from exc
    if metadata.get("originator") != "Codex Desktop":
        raise InvalidEvent("hook event did not originate from Codex Desktop")
    if metadata.get("thread_source") != "user":
        raise InvalidEvent("hook event is not from a user-created Desktop task")


@contextmanager
def project_lock(root: Path) -> Iterator[None]:
    """Serialize writers by locking the existing project directory itself."""
    descriptor = os.open(root, os.O_RDONLY)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def _atomic_write(
    path: Path,
    text: str,
    *,
    before_replace: Callable[[Path], None] | None = None,
) -> None:
    """Durably replace a UTF-8 file without exposing a partial destination."""
    encoded = text.encode("utf-8")
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=path.parent,
            prefix=f".{path.name}.tmp-",
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(encoded)
            temporary.flush()
            os.fsync(temporary.fileno())
        if before_replace is not None:
            before_replace(temporary_path)
        os.replace(temporary_path, path)
        temporary_path = None
        directory_descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass


def _outside_fence_lines(text: str) -> tuple[list[tuple[int, str]], bool]:
    outside: list[tuple[int, str]] = []
    offset = 0
    fence_character: str | None = None
    fence_length = 0
    opening = re.compile(r"^(`{3,}|~{3,})[^\r\n]*\r?\n?$")
    for line in text.splitlines(keepends=True):
        stripped = line.rstrip("\r\n")
        if fence_character is None:
            outside.append((offset, line))
            match = opening.fullmatch(line)
            if match:
                fence_character = match.group(1)[0]
                fence_length = len(match.group(1))
        elif re.fullmatch(
            re.escape(fence_character) + "{" + str(fence_length) + ",}[ \t]*",
            stripped,
        ):
            fence_character = None
            fence_length = 0
        offset += len(line)
    return outside, fence_character is None


def _metadata(block: str) -> dict[str, str]:
    outside, balanced = _outside_fence_lines(block)
    if not balanced:
        raise HistoryConflict("entry contains an unclosed fenced payload")
    user_offsets = [
        offset for offset, line in outside if line.rstrip("\r\n") == "### User input"
    ]
    if len(user_offsets) != 1:
        raise HistoryConflict("each entry must contain exactly one structural User input section")
    prefix = block[: user_offsets[0]]
    pairs = re.findall(r"^- ([A-Za-z ]+): (.*)$", prefix, re.MULTILINE)
    fields: dict[str, str] = {}
    for key, value in pairs:
        if key in fields:
            raise HistoryConflict(f"entry contains duplicate metadata field {key!r}")
        fields[key] = value
    keys = list(fields)
    if tuple(keys[: len(REQUIRED_ENTRY_FIELDS)]) != REQUIRED_ENTRY_FIELDS:
        raise HistoryConflict("entry required metadata is missing or out of order")
    allowed = set(REQUIRED_ENTRY_FIELDS) | set(OPTIONAL_ENTRY_FIELDS)
    unknown = [key for key in keys if key not in allowed]
    if unknown:
        raise HistoryConflict(f"entry contains unrecognized metadata field {unknown[0]!r}")
    optional_ranks = [
        OPTIONAL_ENTRY_FIELDS.index(key)
        for key in keys[len(REQUIRED_ENTRY_FIELDS) :]
    ]
    if optional_ranks != sorted(optional_ranks):
        raise HistoryConflict("entry optional metadata fields are out of order")
    return fields


def _decode_payload(
    block: str,
    heading: str = "### User input",
    *,
    require_integrity: bool = False,
) -> tuple[str, str]:
    outside, balanced = _outside_fence_lines(block)
    if not balanced:
        raise HistoryConflict("entry contains an unclosed fenced payload")
    heading_offsets = [
        offset for offset, line in outside if line.rstrip("\r\n") == heading
    ]
    if len(heading_offsets) != 1:
        raise HistoryConflict(f"entry must contain exactly one {heading!r} heading")
    lines = block[heading_offsets[0] :].splitlines(keepends=True)
    heading_index = 0
    final_newline: str | None = None
    stored_bytes: int | None = None
    stored_sha256: str | None = None
    opening_index: int | None = None
    fence: str | None = None
    for index in range(heading_index + 1, len(lines)):
        line = lines[index]
        if line.startswith("- Final newline: "):
            final_newline = line.removeprefix("- Final newline: ").rstrip("\r\n")
        elif line.startswith("- Stored UTF-8 bytes: "):
            value = line.removeprefix("- Stored UTF-8 bytes: ").rstrip("\r\n")
            if not value.isdecimal():
                raise HistoryConflict("Stored UTF-8 bytes is not decimal")
            stored_bytes = int(value)
        elif line.startswith("- Stored SHA-256: "):
            stored_sha256 = line.removeprefix("- Stored SHA-256: ").rstrip("\r\n")
        match = re.fullmatch(r"(`{3,}|~{3,})text\r?\n", line)
        if match:
            opening_index = index
            fence = match.group(1)
            break
        if line.rstrip("\r\n").startswith("### "):
            break
    allowed_endings = {"LF": "\n", "CRLF": "\r\n", "CR": "\r", "None": ""}
    if final_newline not in {*allowed_endings, "Unknown"}:
        raise HistoryConflict("User input has an invalid or missing Final newline value")
    if opening_index is None or fence is None:
        raise HistoryConflict("User input has no canonical fenced payload")
    closing_index: int | None = None
    for index in range(opening_index + 1, len(lines)):
        if lines[index].rstrip("\r\n") == fence:
            closing_index = index
            break
    if closing_index is None:
        raise HistoryConflict("User input payload is truncated")
    if require_integrity and (stored_bytes is None or stored_sha256 is None):
        raise HistoryConflict("Hook-assisted input lacks required byte count or SHA-256")
    physical_body = "".join(lines[opening_index + 1 : closing_index])
    if not physical_body.endswith("\n"):
        raise HistoryConflict("User input lacks its structural LF")
    body = physical_body[:-1]
    prompt = body if final_newline == "Unknown" else body + allowed_endings[final_newline]

    longest = {}
    for character in ("`", "~"):
        runs = re.findall(re.escape(character) + r"+", body)
        longest[character] = max((len(run) for run in runs), default=0)
    expected_character = "`" if longest["`"] <= longest["~"] else "~"
    expected_length = max(3, longest[expected_character] + 1)
    if fence != expected_character * expected_length:
        raise HistoryConflict("User input does not use the canonical dynamic fence")

    prompt_bytes = prompt.encode("utf-8")
    if stored_bytes is not None and stored_bytes != len(prompt_bytes):
        raise HistoryConflict("Stored UTF-8 byte count does not match the payload")
    if stored_sha256 is not None:
        if not re.fullmatch(r"[0-9a-f]{64}", stored_sha256):
            raise HistoryConflict("Stored SHA-256 is not canonical lowercase hexadecimal")
        if stored_sha256 != hashlib.sha256(prompt_bytes).hexdigest():
            raise HistoryConflict("Stored SHA-256 does not match the payload")
    return prompt, final_newline


def _validate_artifacts(block: str) -> list[dict[str, str]]:
    """Validate the closed schema-1 artifact record structure, when present."""
    outside, balanced = _outside_fence_lines(block)
    if not balanced:
        raise HistoryConflict("entry contains an unclosed fenced payload")
    sections = [
        offset
        for offset, line in outside
        if line.rstrip("\r\n") == "### Artifacts"
    ]
    if not sections:
        return []
    if len(sections) != 1:
        raise HistoryConflict("entry contains duplicate Artifacts sections")
    section_start = sections[0]
    section_end = len(block)
    for offset, line in outside:
        stripped = line.rstrip("\r\n")
        if offset > section_start and stripped.startswith("### "):
            section_end = offset
            break
    headings: list[tuple[int, int, int]] = []
    for offset, line in outside:
        if not (section_start < offset < section_end):
            continue
        match = re.fullmatch(r"#### Artifact (\d+)\r?\n?", line)
        if match:
            headings.append((offset, offset + len(line), int(match.group(1))))
    if not headings:
        raise HistoryConflict("Artifacts section has no numbered artifact records")
    numbers = [number for _, _, number in headings]
    if numbers != list(range(1, len(numbers) + 1)):
        raise HistoryConflict("artifact record numbers are not consecutive from 1")

    records = []
    for index, (_, content_start, number) in enumerate(headings):
        content_end = headings[index + 1][0] if index + 1 < len(headings) else section_end
        fields: list[tuple[str, str]] = []
        for offset, line in outside:
            if not (content_start <= offset < content_end):
                continue
            stripped = line.rstrip("\r\n")
            if not stripped:
                continue
            match = re.fullmatch(r"- ([A-Za-z][A-Za-z0-9 ()-]*): (.*)", stripped)
            if match is None:
                raise HistoryConflict(
                    f"Artifact {number} contains noncanonical record content"
                )
            fields.append((match.group(1), match.group(2)))
        keys = [key for key, _ in fields]
        if len(keys) != len(set(keys)):
            raise HistoryConflict(f"Artifact {number} contains a duplicate field")
        values = dict(fields)
        records.append(values)
        if not keys or keys[0] != "Kind" or values["Kind"] not in ARTIFACT_KINDS:
            raise HistoryConflict(f"Artifact {number} has an invalid or missing Kind")
        original_index = 1 if len(keys) > 1 and keys[1] == "Original name (JSON)" else None
        variant_start = 2 if original_index is not None else 1
        if original_index is not None:
            try:
                original_name = json.loads(values["Original name (JSON)"])
            except json.JSONDecodeError as exc:
                raise HistoryConflict(
                    f"Artifact {number} Original name (JSON) is invalid"
                ) from exc
            if not isinstance(original_name, str):
                raise HistoryConflict(
                    f"Artifact {number} Original name (JSON) is not a string"
                )

        remaining = keys[variant_start:]
        if remaining and remaining[0] == "Preservation":
            if remaining != ["Preservation", "Unavailable reason"]:
                raise HistoryConflict(
                    f"Artifact {number} unavailable fields are missing or out of order"
                )
            if values["Preservation"] != "Unavailable" or not values["Unavailable reason"]:
                raise HistoryConflict(
                    f"Artifact {number} has an invalid unavailable-artifact record"
                )
            continue

        required = ["Preserved copy", "Byte count", "SHA-256", "Fidelity"]
        if remaining[: len(required)] != required:
            raise HistoryConflict(
                f"Artifact {number} preserved fields are missing or out of order"
            )
        optional = remaining[len(required) :]
        try:
            ranks = [OPTIONAL_PRESERVED_ARTIFACT_FIELDS.index(key) for key in optional]
        except ValueError as exc:
            raise HistoryConflict(
                f"Artifact {number} contains an unrecognized optional field"
            ) from exc
        if ranks != sorted(ranks):
            raise HistoryConflict(f"Artifact {number} optional fields are out of order")
        link = re.fullmatch(
            r"\[([^\]]+)\]\(<(prompt_source_assets/([^/>]+))>\)",
            values["Preserved copy"],
        )
        if link is None or link.group(1) != link.group(3):
            raise HistoryConflict(f"Artifact {number} Preserved copy link is invalid")
        if not _canonical_asset_name(link.group(3)):
            raise HistoryConflict(f"Artifact {number} filename lacks a canonical padded entry prefix")
        if not values["Byte count"].isdecimal():
            raise HistoryConflict(f"Artifact {number} Byte count is not decimal")
        if re.fullmatch(r"[0-9a-f]{64}", values["SHA-256"]) is None:
            raise HistoryConflict(f"Artifact {number} SHA-256 is invalid")
        if not values["Fidelity"]:
            raise HistoryConflict(f"Artifact {number} Fidelity is empty")
        if values["Kind"] == "Pasted image" and values["Fidelity"] != PASTED_IMAGE_FIDELITY:
            raise HistoryConflict(
                f"Artifact {number} pasted-image Fidelity is not canonical"
            )
    return records


def _canonical_asset_name(name: str) -> bool:
    match = re.fullmatch(r"prompt-(\d{6,})-[A-Za-z0-9][A-Za-z0-9._-]*", name)
    return bool(match and int(match.group(1)) > 0 and match.group(1) == f"{int(match.group(1)):06d}")


def desktop_runtime_context(block: str) -> tuple[str, str] | None:
    """Decode real context, never a heading quoted inside input or result fences."""
    outside, _ = _outside_fence_lines(block)
    sections = [line.rstrip("\r\n") for _, line in outside if line.startswith("### ")]
    if RUNTIME_CONTEXT_HEADING not in sections:
        return None
    if sections[:2] != ["### User input", RUNTIME_CONTEXT_HEADING]:
        raise HistoryConflict("Desktop runtime context must follow User input before artifacts/results")
    return _decode_payload(block, RUNTIME_CONTEXT_HEADING)


def _with_desktop_artifact_context(block: str) -> str:
    """Add one factual, path-free summary before artifacts, retaining existing context."""
    if desktop_runtime_context(block) is not None:
        return block
    outside, _ = _outside_fence_lines(block)
    offset = next((offset - 1 for offset, line in outside
                   if line.rstrip("\r\n") == "### Artifacts"), len(block))
    fence = _dynamic_fence(DESKTOP_ARTIFACT_CONTEXT)
    section = (
        f"\n{RUNTIME_CONTEXT_HEADING}\n\n- Final newline: None\n"
        "- Boundary note: Path-free summary of the agent-reported Desktop context; "
        "not a verbatim envelope or independent verification.\n\n"
        f"{fence}text\n{DESKTOP_ARTIFACT_CONTEXT}\n{fence}\n"
    )
    return block[:offset] + section + block[offset:]


def _require_desktop_artifact_context(block: str) -> None:
    """Guard new completions, without imposing a new requirement on old histories."""
    if any(record["Kind"] in DESKTOP_ARTIFACT_KINDS for record in _validate_artifacts(block)):
        context = desktop_runtime_context(block)
        if context is None or not context[0].strip():
            raise HistoryConflict("Desktop attachments/pastes require separated runtime context before completion")


def validate_history(text: str) -> list[Entry]:
    if not text.startswith(SCHEMA_MARKER + "\n"):
        raise HistoryConflict("existing history does not have the version 1 schema marker")
    if not text.endswith("\n"):
        raise HistoryConflict("existing history is truncated or lacks its final LF")
    outside, balanced = _outside_fence_lines(text)
    if not balanced:
        raise HistoryConflict("existing history contains an unclosed fenced payload")
    headings: list[tuple[int, int]] = []
    for offset, line in outside:
        match = re.fullmatch(r"## Entry (\d{6,})\r?\n?", line)
        if match:
            number = int(match.group(1))
            if match.group(1) != f"{number:06d}":
                raise HistoryConflict("structural entry heading is not canonically padded")
            headings.append((offset, number))
    prefix = text[: headings[0][0]] if headings else text
    expected_prefix = HEADER + ("\n" if headings else "")
    if prefix != expected_prefix:
        raise HistoryConflict("history header or content before the first entry is not canonical")
    numbers = [number for _, number in headings]
    if any(number < 1 for number in numbers):
        raise HistoryConflict("structural entry numbers must be positive")
    if any(current <= previous for previous, current in zip(numbers, numbers[1:])):
        raise HistoryConflict("structural entry headings are not in strictly increasing order")

    entries: list[Entry] = []
    for index, (start, number) in enumerate(headings):
        if index + 1 < len(headings):
            next_start = headings[index + 1][0]
            if text[next_start - 2 : next_start] != "\n\n":
                raise HistoryConflict("structural entries must be separated by one blank line")
            # The final LF before the next heading is the inter-entry separator,
            # not part of this entry. Keeping it outside the entry makes an
            # entry's optimistic-concurrency digest stable when later entries
            # are appended.
            end = next_start - 1
        else:
            end = len(text)
        block = text[start:end]
        fields = _metadata(block)
        for name in REQUIRED_ENTRY_FIELDS:
            if name not in fields:
                raise HistoryConflict(f"Entry {number:06d} lacks required field {name!r}")
        if fields["Interaction"] not in {
            "Initial prompt",
            "Follow-up",
            "Steering",
            "Correction",
        }:
            raise HistoryConflict(f"Entry {number:06d} has an invalid Interaction")
        if fields["Status"] not in {"In progress", "Completed", "Incomplete", "Interrupted"}:
            raise HistoryConflict(f"Entry {number:06d} has an invalid Status")
        if fields["Capture method"] not in {"Instruction-mediated", "Hook-assisted"}:
            raise HistoryConflict(f"Entry {number:06d} has an invalid Capture method")
        if fields.get("Agent observation") not in {None, "Pending", "Claimed"}:
            raise HistoryConflict(f"Entry {number:06d} has an invalid Agent observation")
        if fields.get("Agent observation") is not None and fields["Capture method"] != "Hook-assisted":
            raise HistoryConflict("Agent observation is valid only on Hook-assisted entries")
        if fields.get("Deduplication note") not in {
            None,
            UNCERTAIN_DEDUPLICATION_NOTE,
        }:
            raise HistoryConflict("Deduplication note is not the canonical safe-preservation note")
        for name in ("Continues", "Supersedes"):
            if name not in fields:
                continue
            match = re.fullmatch(r"Entry (\d{6,})", fields[name])
            if match is None:
                raise HistoryConflict(f"Entry {number:06d} has an invalid {name} reference")
            target = int(match.group(1))
            if match.group(1) != f"{target:06d}" or target >= number or target not in numbers:
                raise HistoryConflict(f"Entry {number:06d} has a non-backward {name} reference")
        if fields["Capture method"] == "Hook-assisted":
            if fields.get("Agent observation") is None:
                raise HistoryConflict(
                    f"Entry {number:06d} lacks required hook Agent observation"
                )
            for name in ("Session ID", "Turn ID"):
                try:
                    value = json.loads(fields[name])
                except (KeyError, json.JSONDecodeError) as exc:
                    raise HistoryConflict(
                        f"Entry {number:06d} has an invalid or missing {name}"
                    ) from exc
                if not isinstance(value, str) or value == "":
                    raise HistoryConflict(f"Entry {number:06d} has a non-string {name}")
        if fields["Status"] == "Interrupted":
            if fields["Capture method"] != "Hook-assisted":
                raise HistoryConflict("Interrupted entries must be Hook-assisted")
            if fields.get("Status reason") != INTERRUPT_REASON:
                raise HistoryConflict("Interrupted entry lacks the canonical hook reason")
        entry_outside, _ = _outside_fence_lines(block)
        result_count = sum(
            line.rstrip("\r\n") == "### Result" for _, line in entry_outside
        )
        if fields["Status"] == "Completed" and result_count != 1:
            raise HistoryConflict("Completed entries must contain exactly one Result section")
        if fields["Status"] == "In progress" and result_count != 0:
            raise HistoryConflict("In progress entries cannot contain a Result section")
        if fields["Status"] in {"Incomplete", "Interrupted"} and result_count > 1:
            raise HistoryConflict("terminal unfinished entries may contain at most one Result section")
        _validate_artifacts(block)
        prompt, final_newline = _decode_payload(
            block,
            require_integrity=fields["Capture method"] == "Hook-assisted",
        )
        entries.append(Entry(number, start, end, block, fields, prompt, final_newline))
    return entries


def _read_history(path: Path) -> tuple[str, list[Entry]]:
    if not path.exists():
        return HEADER, []
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise HistoryConflict(f"cannot read history as UTF-8: {exc}") from exc
    return text, validate_history(text)


def _json_field(value: str) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _split_final_newline(prompt: str) -> tuple[str, str]:
    if prompt.endswith("\r\n"):
        return prompt[:-2], "CRLF"
    if prompt.endswith("\n"):
        return prompt[:-1], "LF"
    if prompt.endswith("\r"):
        return prompt[:-1], "CR"
    return prompt, "None"


def _dynamic_fence(body: str) -> str:
    longest = {}
    for character in ("`", "~"):
        runs = re.findall(re.escape(character) + r"+", body)
        longest[character] = max((len(run) for run in runs), default=0)
    character = "`" if longest["`"] <= longest["~"] else "~"
    return character * max(3, longest[character] + 1)


def render_entry(
    number: int,
    *,
    interaction: str,
    session_id: str,
    turn_id: str,
    prompt: str,
    model: str | None,
    continues: int | None,
) -> str:
    body, final_newline = _split_final_newline(prompt)
    prompt_bytes = _utf8_bytes(prompt, "prompt")
    fence = _dynamic_fence(body)
    metadata = [
        f"## Entry {number:06d}",
        "",
        f"- Interaction: {interaction}",
        "- Status: In progress",
        "- Capture method: Hook-assisted",
        f"- Session ID: {_json_field(session_id)}",
        f"- Turn ID: {_json_field(turn_id)}",
    ]
    if model is not None:
        metadata.append(f"- Model: {_json_field(model)}")
    metadata.append("- Agent observation: Pending")
    if continues is not None:
        metadata.append(f"- Continues: Entry {continues:06d}")
    metadata.extend(
        [
            "",
            "### User input",
            "",
            f"- Final newline: {final_newline}",
            f"- Stored UTF-8 bytes: {len(prompt_bytes)}",
            f"- Stored SHA-256: {hashlib.sha256(prompt_bytes).hexdigest()}",
            "",
            f"{fence}text",
            body,
            fence,
            "",
        ]
    )
    return "\n".join(metadata)


def _entry_identity(entry: Entry) -> tuple[str, str]:
    return (
        json.loads(entry.fields["Session ID"]),
        json.loads(entry.fields["Turn ID"]),
    )


def capture_prompt(root: Path, payload: dict[str, Any]) -> dict[str, Any] | None:
    event_name = _required_string(payload, "hook_event_name")
    if event_name != "UserPromptSubmit":
        raise InvalidEvent(f"expected UserPromptSubmit, received {event_name!r}")
    session_id = _required_string(payload, "session_id")
    turn_id = _required_string(payload, "turn_id")
    prompt = _required_string(payload, "prompt", allow_empty=True)
    _utf8_bytes(prompt, "prompt")
    model_value = payload.get("model")
    if model_value is not None and (not isinstance(model_value, str) or model_value == ""):
        raise InvalidEvent("'model' must be a non-empty string when present")
    if payload.get("agent_id") is not None or payload.get("agent_type") is not None:
        return None
    root = _validated_root(root, payload)
    _validate_desktop_user_transcript(root, payload, session_id)
    history_path = root / HISTORY_NAME
    with project_lock(root):
        history, entries = _read_history(history_path)
        session_entries = [
            entry
            for entry in entries
            if entry.fields["Capture method"] == "Hook-assisted"
            and _entry_identity(entry)[0] == session_id
        ]
        same_turn = [entry for entry in session_entries if _entry_identity(entry)[1] == turn_id]
        if not session_entries:
            interaction = "Initial prompt"
            continues = None
        elif same_turn:
            interaction = "Steering"
            continues = same_turn[-1].number
        else:
            interaction = "Follow-up"
            continues = session_entries[-1].number
        number = max((entry.number for entry in entries), default=0) + 1
        block = render_entry(
            number,
            interaction=interaction,
            session_id=session_id,
            turn_id=turn_id,
            prompt=prompt,
            model=model_value,
            continues=continues,
        )
        updated = history + "\n" + block
        updated_entries = validate_history(updated)
        if updated_entries[-1].number != number:
            raise HistoryConflict("new hook entry is not the final structural entry")
        _atomic_write(history_path, updated)

    claim = {
        "entry_number": number,
        "session_id": session_id,
        "turn_id": turn_id,
        "prompt_utf8_base64": base64.b64encode(_utf8_bytes(prompt, "prompt")).decode("ascii"),
    }
    compact_claim = json.dumps(claim, ensure_ascii=False, separators=(",", ":"))
    context = (
        "PromptSourceCode hook matching context (synthetic; not user-authored):\n"
        f"{compact_claim}\n"
        "Before task work, claim the earliest Pending Hook-assisted entry matching all "
        "four values exactly. Enrich that entry; do not append a duplicate."
    )
    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }


def _decode_prompt_base64(payload: dict[str, Any]) -> str:
    encoded = _required_string(payload, "prompt_utf8_base64", allow_empty=True)
    try:
        raw = base64.b64decode(encoded, validate=True)
        return raw.decode("utf-8")
    except (ValueError, binascii.Error, UnicodeDecodeError) as exc:
        raise InvalidEvent(f"prompt_utf8_base64 is invalid: {exc}") from exc


def claim_entry(root: Path, claim: dict[str, Any]) -> Entry:
    root = _validated_root(root)
    session_id = _required_string(claim, "session_id")
    turn_id = _required_string(claim, "turn_id")
    prompt = _decode_prompt_base64(claim)
    requested_number = claim.get("entry_number")
    if not isinstance(requested_number, int) or requested_number < 1:
        raise InvalidEvent("entry_number must be a positive integer")
    history_path = root / HISTORY_NAME
    with project_lock(root):
        history, entries = _read_history(history_path)
        matches = [
            entry
            for entry in entries
            if entry.fields["Capture method"] == "Hook-assisted"
            and entry.fields["Status"] == "In progress"
            and entry.fields.get("Agent observation") == "Pending"
            and _entry_identity(entry) == (session_id, turn_id)
            and entry.prompt.encode("utf-8") == _utf8_bytes(prompt, "prompt_utf8_base64")
        ]
        if not matches:
            raise NoReliableMatch("no Pending hook entry matches session, turn, and exact prompt bytes")
        entry = matches[0]
        if entry.number != requested_number:
            raise NoReliableMatch(
                "the requested entry is not the earliest unmatched observation-order match"
            )
        claimed_block = entry.text.replace(
            "- Agent observation: Pending\n",
            "- Agent observation: Claimed\n",
            1,
        )
        updated = history[: entry.start] + claimed_block + history[entry.end :]
        claimed_entries = validate_history(updated)
        _atomic_write(history_path, updated)
        return next(item for item in claimed_entries if item.number == entry.number)


def interrupt_turn(root: Path, payload: dict[str, Any]) -> list[int]:
    event_name = _required_string(payload, "hook_event_name")
    if event_name != "Interrupt":
        raise InvalidEvent(f"expected Interrupt, received {event_name!r}")
    session_id = _required_string(payload, "session_id")
    turn_id = _required_string(payload, "turn_id")
    root = _validated_root(root, payload)
    _validate_desktop_user_transcript(root, payload, session_id)
    history_path = root / HISTORY_NAME
    with project_lock(root):
        history, entries = _read_history(history_path)
        matches = [
            entry
            for entry in entries
            if entry.fields["Capture method"] == "Hook-assisted"
            and entry.fields["Status"] == "In progress"
            and _entry_identity(entry) == (session_id, turn_id)
        ]
        if not matches:
            raise NoReliableMatch(
                "Interrupt matched no unfinished Hook-assisted entry with the supplied identifiers"
            )
        updated = history
        for entry in reversed(matches):
            interrupted = entry.text.replace(
                "- Status: In progress\n",
                "- Status: Interrupted\n",
                1,
            )
            metadata_end = interrupted.index("\n\n### User input\n")
            metadata = re.sub(
                r"^- Status reason: .*(?:\n|$)",
                "",
                interrupted[:metadata_end],
                flags=re.MULTILINE,
            ).rstrip("\n")
            interrupted = (
                metadata
                + f"\n- Status reason: {INTERRUPT_REASON}"
                + interrupted[metadata_end:]
            )
            updated = updated[: entry.start] + interrupted + updated[entry.end :]
        validate_history(updated)
        _atomic_write(history_path, updated)
        return [entry.number for entry in matches]


def replace_entry(root: Path, request: dict[str, Any]) -> Entry:
    """Atomically apply arbitrary agent enrichment with optimistic concurrency."""
    root = _validated_root(root)
    session_id = _required_string(request, "session_id")
    turn_id = _required_string(request, "turn_id")
    prompt = _decode_prompt_base64(request)
    expected_digest = _required_string(request, "expected_entry_sha256")
    if not re.fullmatch(r"[0-9a-f]{64}", expected_digest):
        raise InvalidEvent("expected_entry_sha256 must be lowercase SHA-256 hexadecimal")
    number = request.get("entry_number")
    if not isinstance(number, int) or number < 1:
        raise InvalidEvent("entry_number must be a positive integer")
    replacement_encoded = _required_string(request, "replacement_entry_base64", allow_empty=True)
    try:
        replacement = base64.b64decode(replacement_encoded, validate=True).decode("utf-8")
    except (ValueError, binascii.Error, UnicodeDecodeError) as exc:
        raise InvalidEvent(f"replacement_entry_base64 is invalid: {exc}") from exc
    history_path = root / HISTORY_NAME
    with project_lock(root):
        history, entries = _read_history(history_path)
        current = next((entry for entry in entries if entry.number == number), None)
        if current is None:
            raise NoReliableMatch(f"Entry {number:06d} does not exist")
        if current.utf8_sha256 != expected_digest:
            raise HistoryConflict("entry changed before agent enrichment; re-read instead of overwriting")
        if current.fields["Capture method"] != "Hook-assisted":
            raise HistoryConflict("agent replacement cannot relabel an instruction-created entry")
        if current.fields.get("Agent observation") != "Claimed":
            raise HistoryConflict("agent replacement requires a claimed hook observation")
        if _entry_identity(current) != (session_id, turn_id):
            raise NoReliableMatch("replacement identifiers do not match the current entry")
        if current.prompt.encode("utf-8") != _utf8_bytes(prompt, "prompt_utf8_base64"):
            raise NoReliableMatch("replacement prompt bytes do not match the current entry")
        updated = history[: current.start] + replacement + history[current.end :]
        updated_entries = validate_history(updated)
        if [entry.number for entry in updated_entries] != [entry.number for entry in entries]:
            raise HistoryConflict("replacement must be exactly the same structural entry")
        candidate = next(entry for entry in updated_entries if entry.number == number)
        if candidate.fields["Capture method"] != current.fields["Capture method"]:
            raise HistoryConflict("Capture method is immutable")
        if _entry_identity(candidate) != _entry_identity(current):
            raise HistoryConflict("hook-provided identifiers are immutable")
        if candidate.prompt.encode("utf-8") != current.prompt.encode("utf-8"):
            raise HistoryConflict("captured user input is immutable")
        if candidate.final_newline != current.final_newline:
            raise HistoryConflict("captured final-newline state is immutable")
        if current.fields.get("Model") != candidate.fields.get("Model"):
            raise HistoryConflict("hook-provided Model is immutable")
        previous_artifacts = _validate_artifacts(current.text)
        if _validate_artifacts(candidate.text)[:len(previous_artifacts)] != previous_artifacts:
            raise HistoryConflict("captured artifact facts are immutable")
        context = desktop_runtime_context(current.text)
        if context is not None and desktop_runtime_context(candidate.text) != context:
            raise HistoryConflict("captured runtime context is immutable")
        if current.fields.get("Agent observation") == "Claimed" and candidate.fields.get(
            "Agent observation"
        ) != "Claimed":
            raise HistoryConflict("a claimed hook observation cannot become Pending")
        old_status = current.fields["Status"]
        new_status = candidate.fields["Status"]
        if old_status != "In progress" and new_status != old_status:
            raise HistoryConflict(f"terminal status {old_status!r} cannot be replaced")
        if new_status == "Interrupted" and old_status != "Interrupted":
            raise HistoryConflict("only the Interrupt hook may create Interrupted status")
        if old_status == "In progress" and new_status == "Completed":
            _require_desktop_artifact_context(candidate.text)
        _atomic_write(history_path, updated)
        return next(entry for entry in updated_entries if entry.number == number)


def _write_json(value: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")


def validate_history_file(root: Path) -> list[Entry]:
    root = _validated_root(root)
    path = root / HISTORY_NAME
    if not path.is_file():
        raise HistoryConflict(f"{HISTORY_NAME} is missing")
    try:
        text = path.read_bytes().decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise HistoryConflict(f"cannot read history as UTF-8: {exc}") from exc
    entries = validate_history(text)
    assets = root / "prompt_source_assets"
    for entry in entries:
        for record in _validate_artifacts(entry.text):
            if "Preserved copy" not in record:
                continue
            relative = record["Preserved copy"].split("(<", 1)[1][:-2]
            path = root / relative
            if assets.is_symlink() or path.is_symlink() or not path.is_file():
                raise HistoryConflict(f"preserved copy is missing or not a regular local file: {relative}")
            payload = path.read_bytes()
            if len(payload) != int(record["Byte count"]) or hashlib.sha256(payload).hexdigest() != record["SHA-256"]:
                raise HistoryConflict(f"preserved copy differs from recorded bytes: {relative}")
    return entries


def standard_capture_state(root: Path) -> bool:
    """Read the live control, then verify the enabled installation without writes."""
    root = _validated_root(root)
    try:
        agents = (root / "AGENTS.md").read_bytes().decode("utf-8")
        begin = "<!-- prompt-source-loader-begin -->"
        end = "<!-- prompt-source-loader-end -->"
        if agents.count(begin) != 1 or agents.count(end) != 1:
            raise HistoryConflict("standard loader markers are missing or conflicting")
        start, stop = agents.index(begin), agents.index(end)
        if stop < start:
            raise HistoryConflict("standard loader markers are reversed")
        loader = agents[start : stop + len(end)]
        controls = re.findall(r"^- Capture: (enabled|disabled)$", loader, re.MULTILINE)
        if len(controls) != 1:
            raise HistoryConflict("standard loader must have one enabled/disabled control")
        canonical = loader.replace("- Capture: disabled", "- Capture: enabled")
        if hashlib.sha256(canonical.encode("utf-8")).hexdigest() != STANDARD_LOADER_SHA256:
            raise HistoryConflict("standard loader is stale, conflicting, or truncated")
        if controls[0] == "disabled":
            return False  # Do not even read the dedicated file while disabled.
        instructions = (root / ".prompt-source/instructions-v1.md").read_bytes()
        if hashlib.sha256(instructions).hexdigest() != STANDARD_INSTRUCTIONS_SHA256:
            raise HistoryConflict("dedicated instructions are stale, conflicting, or truncated")
    except (OSError, UnicodeDecodeError) as exc:
        raise HistoryConflict(f"standard installation is missing or unreadable: {exc}") from exc
    return True


def begin_standard(root: Path, request: dict[str, Any]) -> Entry | None:
    """Render and append one model-observed input; never infer a task from file length."""
    root = _validated_root(root)
    with project_lock(root):
        if not standard_capture_state(root):
            return None
        prompt = _required_string(request, "prompt", allow_empty=True)
        _utf8_bytes(prompt, "prompt")
        first = request.get("first_in_task")
        if not isinstance(first, bool):
            raise InvalidEvent("first_in_task must be a boolean from the current conversation")
        interaction = "Initial prompt" if first else request.get("interaction", "Follow-up")
        if interaction not in {"Initial prompt", "Follow-up", "Steering", "Correction"}:
            raise InvalidEvent("invalid standard interaction")
        if not first and interaction == "Initial prompt":
            raise InvalidEvent("Initial prompt requires first_in_task true")
        history, entries = _read_history(root / HISTORY_NAME)
        session = os.environ.get("CODEX_THREAD_ID")
        if session:
            same_task = [
                entry for entry in entries
                if entry.fields.get("Session ID") == _json_field(session)
                and entry.fields.get("Agent observation") != "Pending"
            ]
            if first and same_task:
                raise HistoryConflict("this runtime task already has captured submissions")
            if not first and not same_task and request.get("uncaptured_predecessor") is not True:
                raise HistoryConflict(
                    "no earlier capture belongs to this runtime task; use first_in_task true "
                    "for its first submission, or uncaptured_predecessor true only when an "
                    "earlier submission in this task was not captured"
                )
        number = max((entry.number for entry in entries), default=0) + 1
        metadata = [
            f"## Entry {number:06d}", "",
            f"- Interaction: {interaction}", "- Status: In progress",
            "- Capture method: Instruction-mediated",
        ]
        if session:
            metadata.append(f"- Session ID: {_json_field(session)}")
        if request.get("deduplication_uncertain") is True:
            metadata.append(f"- Deduplication note: {UNCERTAIN_DEDUPLICATION_NOTE}")
        for key, field in (("continues", "Continues"), ("supersedes", "Supersedes")):
            target = request.get(key)
            if target is None:
                continue
            if first or isinstance(target, bool) or not isinstance(target, int):
                raise InvalidEvent(f"{key} requires a backward entry number on a continuation")
            previous = next((entry for entry in entries if entry.number == target), None)
            if previous is None or target >= number:
                raise HistoryConflict(f"{key} does not identify an earlier entry")
            if key == "supersedes" and interaction != "Correction":
                raise InvalidEvent("only a correction may supersede an entry")
            if (key == "continues" and session
                    and previous.fields.get("Session ID") not in {None, _json_field(session)}):
                raise HistoryConflict("continuation points to another Desktop task")
            metadata.append(f"- {field}: Entry {target:06d}")
        recover = request.get("recover", [])
        if not isinstance(recover, list) or any(
            isinstance(n, bool) or not isinstance(n, int) for n in recover
        ):
            raise InvalidEvent("recover must be a list of known unfinished earlier-turn entry numbers")
        if len(set(recover)) != len(recover):
            raise InvalidEvent("recover contains duplicate entry numbers")
        for target in recover:
            previous = next((entry for entry in entries if entry.number == target), None)
            if (previous is None
                    or previous.fields["Capture method"] != "Instruction-mediated"
                    or previous.fields["Status"] != "In progress"):
                raise HistoryConflict("recover must identify unfinished standard entries")
            if session and previous.fields.get("Session ID") not in {None, _json_field(session)}:
                raise HistoryConflict("cannot recover another runtime task's unfinished work")
        for previous in reversed(entries):
            if previous.number not in recover:
                continue
            metadata_end = previous.text.index("\n\n### User input\n")
            prefix = previous.text[:metadata_end].replace("- Status: In progress", "- Status: Incomplete", 1)
            prefix = re.sub(r"\n- Status reason: [^\n]*", "", prefix)
            recovered = (
                prefix + "\n- Status reason: Completion reason unavailable; "
                "no reliable Interrupt event was observed." + previous.text[metadata_end:]
            )
            history = history[:previous.start] + recovered + history[previous.end:]
        fence = _dynamic_fence(prompt)
        block = "\n".join(metadata) + (
            f"\n\n### User input\n\n- Final newline: Unknown\n\n{fence}text\n"
            f"{prompt}\n{fence}\n"
        )
        updated = history + "\n" + block
        result = validate_history(updated)[-1]
        _atomic_write(root / HISTORY_NAME, updated)
        return result


def _unfinished_owned_entry(entries: list[Entry], request: dict[str, Any]) -> Entry:
    number = request.get("entry_number")
    if isinstance(number, bool) or not isinstance(number, int) or number < 1:
        raise InvalidEvent("entry_number must be a positive integer")
    entry = next((item for item in entries if item.number == number), None)
    if entry is None:
        raise NoReliableMatch("no entry matches entry_number")
    if entry.fields["Status"] != "In progress":
        raise HistoryConflict("entry is already terminal")
    session = entry.fields.get("Session ID")
    if session is not None and session != _json_field(os.environ.get("CODEX_THREAD_ID", "")):
        raise NoReliableMatch("entry belongs to a different runtime task")
    if entry.fields["Capture method"] == "Hook-assisted":
        if entry.fields.get("Agent observation") != "Claimed":
            raise NoReliableMatch("artifact enrichment requires a claimed hook entry")
        if request.get("expected_entry_sha256") != entry.utf8_sha256:
            raise HistoryConflict("hook entry changed; re-read its digest before enrichment")
    return entry


def _asset_basename(number: int, name: str, unnamed_paste: int | None = None) -> tuple[str, str]:
    """Implement schema-1 naming once, including its displayed entry number."""
    name = Path(name).name
    suffix = re.search(r"\.([A-Za-z0-9]{1,16})$", name)
    extension = "." + suffix.group(1).lower() if suffix else ""
    stem = name[:suffix.start()] if suffix else name
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", stem)
    stem = re.sub(r"-+", "-", stem).lstrip(".").strip("._-")[:80] or "artifact"
    if unnamed_paste is not None:
        stem = f"image-{unnamed_paste:03d}"
    return f"prompt-{number:06d}-{stem}", extension


def _publish_asset(path: Path, payload: bytes) -> None:
    """Publish complete bytes without overwriting even a racing external file."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".capture-", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)  # Atomic, and fails if the destination already exists.
        descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def preserve_artifact(root: Path, request: dict[str, Any]) -> Entry | None:
    """Copy one observed source and append canonical metadata before finalization."""
    root = _validated_root(root)
    with project_lock(root):
        if not standard_capture_state(root):
            return None
        history, entries = _read_history(root / HISTORY_NAME)
        entry = _unfinished_owned_entry(entries, request)
        records = _validate_artifacts(entry.text)
        if records:
            outside, _ = _outside_fence_lines(entry.text)
            if [line.rstrip("\r\n") for _, line in outside if line.startswith("### ")][-1] != "### Artifacts":
                raise HistoryConflict("existing Artifacts must be the final unfinished section")
        kind = request.get("kind")
        if kind is not None and (not isinstance(kind, str) or kind not in DESKTOP_ARTIFACT_KINDS):
            raise InvalidEvent("omit kind for filesystem sources; only observed Desktop attachment/paste kinds are accepted")
        block = _with_desktop_artifact_context(entry.text) if kind in DESKTOP_ARTIFACT_KINDS else entry.text
        source_value = request.get("source")
        source = None
        if source_value is not None:
            source = root / _required_string(request, "source")
        original = request.get("original_name", source.name if source is not None else None)
        if original is not None and (not isinstance(original, str) or not original):
            raise InvalidEvent("original_name must be a non-empty string or null")
        if original is not None:
            original = Path(original).name
            _utf8_bytes(original, "original_name")
        relative = None
        payload = None
        reason = None
        if source is None:
            reason = request.get("unavailable_reason", "Unknown")
            if not isinstance(reason, str) or not reason or any(c in reason for c in "\r\n"):
                raise InvalidEvent("unavailable_reason must be one non-empty factual line")
        else:
            try:
                source = source.resolve()
                try:
                    relative = source.relative_to(root)
                except ValueError:
                    pass
                if not source.is_file():
                    reason = "Source is missing or is not a regular file."
                else:
                    payload = source.read_bytes()
            except (OSError, RuntimeError) as exc:
                reason = f"Source data unavailable ({type(exc).__name__})."
        kind = kind or ("Repository file snapshot" if relative is not None else "Requested artifact")
        fields = [f"- Kind: {kind}"]
        if original is not None:
            fields.append(f"- Original name (JSON): {_json_field(original)}")
        if payload is None:
            fields += ["- Preservation: Unavailable", f"- Unavailable reason: {reason}"]
        else:
            assets = root / "prompt_source_assets"
            if assets.is_symlink() or (assets.exists() and not assets.is_dir()):
                raise HistoryConflict("assets must be a real project-local directory")
            assets.mkdir(exist_ok=True)
            unnamed = None
            if kind == "Pasted image" and original is None:
                unnamed = 1 + sum(r["Kind"] == "Pasted image" and "Original name (JSON)" not in r for r in records)
            stem, extension = _asset_basename(entry.number, original or source.name, unnamed)
            destination = assets / (stem + extension)
            if source.parent == assets and _canonical_asset_name(source.name):
                destination = source
            reused = False
            collision = 1
            while True:
                if destination.is_symlink() or destination.exists():
                    if not destination.is_symlink() and destination.is_file() and destination.read_bytes() == payload:
                        reused = True
                        break
                else:
                    try:
                        _publish_asset(destination, payload)
                        break
                    except FileExistsError:
                        continue
                collision += 1
                destination = assets / f"{stem}-{collision:03d}{extension}"
            copied = destination.read_bytes()
            if copied != payload or source.read_bytes() != payload:
                raise HistoryConflict("source or preserved copy changed during preservation; no artifact record written")
            digest = hashlib.sha256(copied).hexdigest()
            fidelity = {
                "Attached file": "Byte-for-byte copy of the attached original exposed by Codex Desktop.",
                "Attached image": "Byte-for-byte copy of the attached original exposed by Codex Desktop.",
                "Pasted image": PASTED_IMAGE_FIDELITY,
                "Repository file snapshot": "Byte-for-byte point-in-time copy of the repository source.",
                "Requested artifact": "Byte-for-byte copy of the requested source.",
            }[kind]
            name = destination.name
            fields += [f"- Preserved copy: [{name}](<prompt_source_assets/{name}>)",
                       f"- Byte count: {len(copied)}", f"- SHA-256: {digest}", f"- Fidelity: {fidelity}"]
            if relative is not None:
                # Encode destinations/labels without importing a networking library.
                link = "".join(chr(b) if chr(b) in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~/" else f"%{b:02X}"
                               for b in relative.as_posix().encode("utf-8"))
                fields.append(f"- Repository source: [{link}](<{link}>)")
            fields += [f"- Source byte count: {len(payload)}", f"- Source SHA-256: {digest}"]
            if reused:
                fields.append("- Reuse note: Existing flat asset verified byte-for-byte and reused.")
        addition = ("\n### Artifacts\n" if not records else "")
        addition += f"\n#### Artifact {len(records) + 1}\n\n" + "\n".join(fields) + "\n"
        updated = history[:entry.start] + block + addition + history[entry.end:]
        candidates = validate_history(updated)
        _atomic_write(root / HISTORY_NAME, updated)
        return next(item for item in candidates if item.number == entry.number)


def finish_standard(root: Path, request: dict[str, Any]) -> Entry | None:
    """Complete only the named unfinished standard entry, retaining its input bytes."""
    root = _validated_root(root)
    with project_lock(root):
        if not standard_capture_state(root):
            return None
        number = request.get("entry_number")
        if isinstance(number, bool) or not isinstance(number, int) or number < 1:
            raise InvalidEvent("entry_number must be a positive integer")
        result = _required_string(request, "result")
        outside, _ = _outside_fence_lines(result)
        if any(re.match(r"^(?:## Entry |### (?:User input|Codex Desktop runtime context|Artifacts|Result)(?:\s|$)|#### Artifact )", line)
               for _, line in outside):
            raise InvalidEvent("result cannot contain capture sections; use --preserve-artifact for artifacts")
        history, entries = _read_history(root / HISTORY_NAME)
        entry = next((item for item in entries if item.number == number), None)
        if entry is None or entry.fields["Capture method"] != "Instruction-mediated":
            raise NoReliableMatch("no standard entry matches entry_number")
        if entry.fields["Status"] != "In progress":
            raise HistoryConflict("standard entry is already terminal")
        session = entry.fields.get("Session ID")
        if session is not None and session != _json_field(os.environ.get("CODEX_THREAD_ID", "")):
            raise NoReliableMatch("entry belongs to a different runtime task")
        _require_desktop_artifact_context(entry.text)
        block = entry.text.replace("- Status: In progress\n", "- Status: Completed\n", 1)
        block += "\n### Result\n\n" + result + ("" if result.endswith("\n") else "\n")
        updated = history[: entry.start] + block + history[entry.end :]
        candidates = validate_history(updated)
        if [item.number for item in candidates] != [item.number for item in entries]:
            raise HistoryConflict("result must not add structural entries")
        _atomic_write(root / HISTORY_NAME, updated)
        return next(item for item in candidates if item.number == number)


def run_hook(root: Path, payload: dict[str, Any]) -> int:
    event_name = payload.get("hook_event_name")
    if event_name == "UserPromptSubmit":
        output = capture_prompt(root, payload)
        if output is None:
            sys.stderr.write("PromptSourceCode: ignored a non-root-agent UserPromptSubmit event\n")
        else:
            _write_json(output)
        return 0
    if event_name == "Interrupt":
        interrupt_turn(root, payload)
        _write_json({})
        return 0
    raise InvalidEvent(f"unsupported hook_event_name {event_name!r}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--claim", action="store_true", help="claim one hook entry from stdin JSON")
    mode.add_argument(
        "--replace-entry",
        action="store_true",
        help="atomically replace one hook entry from stdin JSON",
    )
    mode.add_argument(
        "--validate-history",
        action="store_true",
        help="validate the project history without changing it",
    )
    mode.add_argument("--capture-state", action="store_true", help="read the current standard capture control")
    mode.add_argument("--begin-standard", action="store_true", help="append a standard entry from stdin JSON")
    mode.add_argument("--finish-standard", action="store_true", help="complete a standard entry from stdin JSON")
    mode.add_argument("--preserve-artifact", action="store_true", help="preserve one source for an unfinished entry from stdin JSON")
    arguments = parser.parse_args(argv)
    standard_mode = arguments.capture_state or arguments.begin_standard or arguments.finish_standard or arguments.preserve_artifact
    error_label = "capture" if standard_mode else "hook"
    try:
        root = Path.cwd()
        installed = Path(__file__).resolve()
        if ((standard_mode or arguments.validate_history)
                and installed.name == "validate.py" and installed.parent.name == ".prompt-source"):
            root = installed.parent.parent
        if arguments.capture_state:
            _write_json({"capture": "enabled" if standard_capture_state(root) else "disabled"})
            return 0
        if arguments.validate_history:
            entries = validate_history_file(root)
            sys.stdout.write(f"PromptSourceCode: history valid ({len(entries)} entries)\n")
            return 0
        payload = read_event()
        if arguments.begin_standard or arguments.finish_standard or arguments.preserve_artifact:
            operation = preserve_artifact if arguments.preserve_artifact else (begin_standard if arguments.begin_standard else finish_standard)
            entry = operation(root, payload)
            if entry is None:
                _write_json({"capture": "disabled"})
            else:
                _write_json({
                    "capture": "enabled", "entry_number": entry.number,
                    "interaction": entry.fields["Interaction"], "entry_sha256": entry.utf8_sha256,
                })
            return 0
        if arguments.claim:
            entry = claim_entry(root, payload)
            _write_json({"entry_number": entry.number, "entry_sha256": entry.utf8_sha256})
            return 0
        if arguments.replace_entry:
            entry = replace_entry(root, payload)
            _write_json({"entry_number": entry.number, "entry_sha256": entry.utf8_sha256})
            return 0
        return run_hook(root, payload)
    except PromptSourceError as exc:
        sys.stderr.write(f"PromptSourceCode {error_label} error: {exc}\n")
        return 1
    except OSError as exc:
        sys.stderr.write(f"PromptSourceCode {error_label} I/O error: {exc}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
