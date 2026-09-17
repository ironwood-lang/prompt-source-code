#!/usr/bin/env python3
"""Install and validate PromptSourceCode's project-local instruction layout."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import os
from pathlib import Path
import re
import tempfile


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_INSTRUCTIONS = Path(".prompt-source/instructions-v1.md")
CANONICAL_VALIDATOR = Path(".prompt-source/validate.py")
VALIDATE_HISTORY_COMMAND = (
    'cd "$(git rev-parse --show-toplevel)" && '
    "/usr/bin/python3 .prompt-source/validate.py --validate-history"
)
LOADER_TEMPLATE = REPOSITORY_ROOT / "templates/AGENTS.prompt-source-loader.md"
INSTRUCTIONS_TEMPLATE = REPOSITORY_ROOT / "templates/prompt-source-instructions-v1.md"
VALIDATOR_SOURCE = REPOSITORY_ROOT / "hooks/prompt_source_core.py"

LOADER_BEGIN = "<!-- prompt-source-loader-begin -->"
LOADER_END = "<!-- prompt-source-loader-end -->"
INSTRUCTIONS_BEGIN = "<!-- prompt-source-instructions: 1 -->"
INSTRUCTIONS_END = "<!-- prompt-source-instructions-end -->"

MAX_LOADER_WORDS = 300
MAX_LOADER_BYTES = 2_048
MAX_INSTRUCTIONS_WORDS = 900
MAX_INSTRUCTIONS_BYTES = 6_144
MAX_COMBINED_WORDS = 1_200
MAX_COMBINED_BYTES = 8_192


class InstructionContractError(ValueError):
    """The installation is unsafe to read or modify automatically."""


@dataclass(frozen=True)
class Measurement:
    words: int
    bytes: int


def measure(text: str) -> Measurement:
    return Measurement(len(re.findall(r"\S+", text)), len(text.encode("utf-8")))


def decode_utf8(payload: bytes, label: str) -> str:
    try:
        return payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InstructionContractError(f"{label} is not readable UTF-8: {exc}") from exc


def extract_loader(text: str) -> str:
    if text.count(LOADER_BEGIN) != 1 or text.count(LOADER_END) != 1:
        raise InstructionContractError(
            "root AGENTS.md must contain exactly one complete loader marker pair"
        )
    start = text.index(LOADER_BEGIN)
    end = text.index(LOADER_END)
    if end < start:
        raise InstructionContractError("loader markers are out of order")
    return text[start : end + len(LOADER_END)]


def validate_loader(text: str) -> Measurement:
    block = extract_loader(text)
    if block != text.strip("\n"):
        raise InstructionContractError("loader template contains text outside its markers")
    if f"`{CANONICAL_INSTRUCTIONS.as_posix()}`" not in block:
        raise InstructionContractError("loader does not name the canonical instruction path")
    capture_controls = block.count("- Capture: enabled") + block.count("- Capture: disabled")
    if capture_controls != 1:
        raise InstructionContractError("loader must contain exactly one capture control")
    result = measure(block)
    if result.words > MAX_LOADER_WORDS or result.bytes > MAX_LOADER_BYTES:
        raise InstructionContractError("loader exceeds its word or byte budget")
    return result


def validate_instructions(text: str) -> Measurement:
    lines = text.splitlines()
    if not lines or lines[0] != INSTRUCTIONS_BEGIN:
        raise InstructionContractError("dedicated instructions are missing version marker 1")
    if lines[-1:] != [INSTRUCTIONS_END]:
        raise InstructionContractError("dedicated instructions are truncated")
    if text.count(INSTRUCTIONS_BEGIN) != 1 or text.count(INSTRUCTIONS_END) != 1:
        raise InstructionContractError("dedicated instruction markers conflict")
    if f"`{VALIDATE_HISTORY_COMMAND}`" not in text:
        raise InstructionContractError("dedicated instructions lack the Git-root validator command")
    result = measure(text)
    if result.words > MAX_INSTRUCTIONS_WORDS or result.bytes > MAX_INSTRUCTIONS_BYTES:
        raise InstructionContractError("dedicated instructions exceed their word or byte budget")
    return result


def validate_pair(loader: str, instructions: str) -> tuple[Measurement, Measurement]:
    loader_size = validate_loader(loader)
    instruction_size = validate_instructions(instructions)
    if (
        loader_size.words + instruction_size.words > MAX_COMBINED_WORDS
        or loader_size.bytes + instruction_size.bytes > MAX_COMBINED_BYTES
    ):
        raise InstructionContractError("combined always-read instructions exceed their budget")
    return loader_size, instruction_size


def append_loader(existing: bytes, loader: bytes) -> bytes:
    existing_text = decode_utf8(existing, "existing root AGENTS.md")
    loader_text = decode_utf8(loader, "loader template")
    validate_loader(loader_text)
    if LOADER_BEGIN in existing_text or LOADER_END in existing_text:
        raise InstructionContractError("existing root AGENTS.md already has a loader marker")
    if not existing:
        return loader if loader.endswith(b"\n") else loader + b"\n"
    separator = b"" if existing.endswith(b"\n\n") else (b"\n" if existing.endswith(b"\n") else b"\n\n")
    return existing + separator + loader.lstrip(b"\n")


def replace_loader(existing: bytes, loader: bytes) -> bytes:
    existing_text = decode_utf8(existing, "existing root AGENTS.md")
    loader_text = decode_utf8(loader, "loader template")
    validate_loader(loader_text)
    current = extract_loader(existing_text)
    return existing.replace(current.encode("utf-8"), loader_text.strip("\n").encode("utf-8"), 1)


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def install(project: Path, *, update: bool = False) -> None:
    project = project.resolve(strict=True)
    if not project.is_dir():
        raise InstructionContractError("project path is not a directory")
    loader = LOADER_TEMPLATE.read_bytes()
    instructions = INSTRUCTIONS_TEMPLATE.read_bytes()
    validator = VALIDATOR_SOURCE.read_bytes()
    validate_pair(
        decode_utf8(loader, "loader template"),
        decode_utf8(instructions, "dedicated instruction template"),
    )

    agents_path = project / "AGENTS.md"
    existing_agents = agents_path.read_bytes() if agents_path.exists() else b""
    has_marker = LOADER_BEGIN.encode() in existing_agents or LOADER_END.encode() in existing_agents
    if has_marker:
        if update:
            new_agents = replace_loader(existing_agents, loader)
        else:
            current = extract_loader(decode_utf8(existing_agents, "existing root AGENTS.md"))
            if current != decode_utf8(loader, "loader template").strip("\n"):
                raise InstructionContractError("a different loader is already installed")
            new_agents = existing_agents
    else:
        new_agents = append_loader(existing_agents, loader)

    destination = project / CANONICAL_INSTRUCTIONS
    if destination.exists() and not update and destination.read_bytes() != instructions:
        raise InstructionContractError("canonical instruction file already exists with different bytes")
    validator_destination = project / CANONICAL_VALIDATOR
    if (
        validator_destination.exists()
        and not update
        and validator_destination.read_bytes() != validator
    ):
        raise InstructionContractError("canonical validator already exists with different bytes")
    _atomic_write(destination, instructions)
    _atomic_write(validator_destination, validator)
    _atomic_write(agents_path, new_agents)


def check(project: Path) -> tuple[Measurement, Measurement]:
    project = project.resolve(strict=True)
    try:
        agents_payload = (project / "AGENTS.md").read_bytes()
    except OSError as exc:
        raise InstructionContractError(f"root AGENTS.md is missing or unreadable: {exc}") from exc
    try:
        instructions_payload = (project / CANONICAL_INSTRUCTIONS).read_bytes()
    except OSError as exc:
        raise InstructionContractError(
            f"dedicated instructions are missing or unreadable: {exc}"
        ) from exc
    try:
        validator_payload = (project / CANONICAL_VALIDATOR).read_bytes()
    except OSError as exc:
        raise InstructionContractError(
            f"standard validator is missing or unreadable: {exc}"
        ) from exc
    if validator_payload != VALIDATOR_SOURCE.read_bytes():
        raise InstructionContractError("standard validator is stale or conflicting")
    if instructions_payload != INSTRUCTIONS_TEMPLATE.read_bytes():
        raise InstructionContractError("dedicated instructions are stale or conflicting")
    agents = decode_utf8(agents_payload, "root AGENTS.md")
    instructions = decode_utf8(instructions_payload, "dedicated instructions")
    return validate_pair(extract_loader(agents), instructions)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("install", "update", "check"))
    parser.add_argument("project", type=Path)
    arguments = parser.parse_args()
    if arguments.mode in {"install", "update"}:
        install(arguments.project, update=arguments.mode == "update")
    loader, instructions = check(arguments.project)
    print(
        f"loader: {loader.words} words, {loader.bytes} bytes; "
        f"instructions: {instructions.words} words, {instructions.bytes} bytes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
