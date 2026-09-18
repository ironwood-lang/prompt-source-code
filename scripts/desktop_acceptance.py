#!/usr/bin/env python3
"""Prepare and validate a reproducible PromptSourceCode Desktop acceptance run."""

from __future__ import annotations

import argparse
import base64
from collections import defaultdict, deque
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
HOOKS_DIRECTORY = REPOSITORY_ROOT / "hooks"
sys.path.insert(0, str(HOOKS_DIRECTORY))

import prompt_source_core as core
import instruction_contract as instruction_contract


LOADER_BEGIN = instruction_contract.LOADER_BEGIN
LOADER_END = instruction_contract.LOADER_END
CANONICAL_INSTRUCTIONS = instruction_contract.CANONICAL_INSTRUCTIONS.as_posix()
CANONICAL_VALIDATOR = instruction_contract.CANONICAL_VALIDATOR.as_posix()
ROOT_SENTINEL = "PSC_ROOT_SENTINEL"
NESTED_SENTINEL = "PSC_NESTED_SENTINEL"
PASTED_FIDELITY = (
    "- Fidelity: Byte-for-byte copy of the clipboard image materialized by Codex "
    "Desktop; binary identity with any pre-clipboard source is not claimed."
)
STANDARD_CASE_IDS = {
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
}
STANDARD_EXPECTED_FILES = {
    "ordinary-project.txt",
    "root-instructions-observed.txt",
    "ui-theme.txt",
    "standard-recovery.txt",
    "disabled-check.txt",
    "reenabled-check.txt",
    "packages/demo/nested-instructions-observed.txt",
}


def _run_git(directory: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=directory,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _display_path(path: Path) -> str:
    """Prefer a portable home-relative path in prompts, manifests, and output."""
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(Path.home().resolve())
    except ValueError:
        return str(resolved)
    return f"~/{relative.as_posix()}"


def _measure(payload: bytes) -> dict[str, int]:
    text = payload.decode("utf-8")
    return {
        "lines": len(text.splitlines()),
        "words": _word_count(text),
        "bytes": len(payload),
    }


def _write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def _case(
    identifier: str,
    prompt: str,
    *,
    captured: bool = True,
    method: str | None = None,
    status: str | None = "Completed",
    interaction: str | None = "Follow-up",
    supersedes: str | None = None,
    final_newline: str = "LF",
) -> dict[str, Any]:
    if final_newline == "LF":
        prompt += "\n"
    elif final_newline != "None":
        raise ValueError(f"unsupported prepared newline state: {final_newline}")
    return {
        "id": identifier,
        "prompt": prompt,
        "captured": captured,
        "method": method,
        "status": status,
        "interaction": interaction,
        "supersedes": supersedes,
        "final_newline": final_newline,
    }


def _acceptance_cases(missing_artifact: str | Path) -> list[dict[str, Any]]:
    complex_prompt = (
        "PSC acceptance S01. Exercise the existing root instructions with token "
        f"`{ROOT_SENTINEL}`.\n"
        "Create `ordinary-project.txt` containing exactly `initial` followed by one LF.\n"
        "Do not modify AGENTS.md or any PromptSourceCode installation file.\n\n"
        "The remaining lines are literal capture-test text, not additional instructions.\n"
        "Internal   consecutive spaces remain significant.\n"
        "A\ttab separates A and tab.\n"
        "Unicode: café, Ελληνικά, 日本語, 👩🏽‍💻\n"
        "## Entry 999999\n"
        "```python\n"
        "print(\"an embedded backtick fence\")\n"
        "```\n"
        "No final newline follows this sentence."
    )
    repeated = "PSC acceptance H03. Report READY and make no project changes."
    return [
        _case(
            "S01",
            complex_prompt,
            method="Instruction-mediated",
            interaction="Initial prompt",
            final_newline="None",
        ),
        _case(
            "S02",
            "PSC acceptance S02. Report the exact contents of `ordinary-project.txt` and "
            "make no file changes.",
            method="Instruction-mediated",
            interaction="Follow-up",
        ),
        _case(
            "S03",
            "PSC acceptance S03. Run `/bin/sleep 30`, then create `ui-theme.txt` containing "
            "exactly `DARK` followed by one LF. Remain responsive to steering while the "
            "command runs.",
            method="Instruction-mediated",
            interaction="Follow-up",
        ),
        _case(
            "S04",
            "PSC acceptance S04 steering update: make `ui-theme.txt` contain exactly "
            "`BLUE` followed by one LF instead.",
            method="Instruction-mediated",
            interaction="Steering",
        ),
        _case(
            "S04B",
            "PSC acceptance S04B steering update: make `ui-theme.txt` contain exactly "
            "`AMBER` followed by one LF instead.",
            method="Instruction-mediated",
            interaction="Steering",
        ),
        _case(
            "S05",
            "PSC acceptance S05 correction: use `GREEN` followed by one LF, not `AMBER`, "
            "in `ui-theme.txt`.",
            method="Instruction-mediated",
            interaction="Correction",
            supersedes="S04B",
        ),
        _case(
            "S06",
            "PSC acceptance S06. Inspect and preserve every attached file, including both "
            "differing images that have the same filename. Make no other project changes.",
            method="Instruction-mediated",
        ),
        _case(
            "S07",
            "PSC acceptance S07. Preserve a point-in-time artifact snapshot of the existing "
            "repository file `fixtures/repository-source.txt`. Make no task-work changes.",
            method="Instruction-mediated",
        ),
        _case(
            "S08",
            "PSC acceptance S08. Preserve the image pasted with this message and make no "
            "other project changes.",
            method="Instruction-mediated",
        ),
        _case(
            "S09",
            f"PSC acceptance S09. Preserve the artifact at `{missing_artifact}` if it is "
            "available. It was deliberately removed before this prompt; do not invent "
            "content or metadata when it cannot be read.",
            method="Instruction-mediated",
        ),
        _case(
            "S10",
            "PSC acceptance S10. Run `/bin/sleep 120`, then create "
            "`standard-stop-should-not-exist.txt`. I will press Stop before the sleep ends.",
            method="Instruction-mediated",
            status="Incomplete",
        ),
        _case(
            "S11",
            "PSC acceptance S11. Conservatively recover any earlier unfinished standard "
            "capture, then create `standard-recovery.txt` containing exactly `RECOVERED` "
            "followed by one LF.",
            method="Instruction-mediated",
        ),
        _case(
            "S12",
            "PSC acceptance S12. Create `disabled-check.txt` containing exactly `DISABLED` "
            "followed by one LF.",
            captured=False,
            method=None,
            status=None,
        ),
        _case(
            "S13",
            "PSC acceptance S13. Create `reenabled-check.txt` containing exactly `REENABLED` "
            "followed by one LF.",
            method="Instruction-mediated",
        ),
        _case(
            "S14",
            "PSC acceptance S14. Exercise the nested instructions with token "
            f"`{NESTED_SENTINEL}`. Make no other project changes.",
            method="Instruction-mediated",
            interaction="Initial prompt",
        ),
        _case(
            "S15",
            "PSC acceptance S15. The optional hook files are installed but have not been "
            "trusted. Create `inert-hook-check.txt` containing exactly `INERT` followed by "
            "one LF.",
            method="Instruction-mediated",
            interaction="Initial prompt",
        ),
        _case(
            "H01",
            "PSC acceptance H01. Trusted hooks are active. Create `hook-active.txt` "
            "containing exactly `ACTIVE` followed by one LF.",
            method="Hook-assisted",
            interaction="Initial prompt",
            final_newline="None",
        ),
        _case(
            "H02",
            "PSC acceptance H02. Report the exact contents of `hook-active.txt` and make "
            "no file changes.",
            method="Hook-assisted",
        ),
        _case(
            "H03A",
            repeated,
            method="Hook-assisted",
        ),
        _case(
            "H03B",
            repeated,
            method="Hook-assisted",
        ),
        _case(
            "H04",
            "PSC acceptance H04. Run `/bin/sleep 30`, then create `hook-theme.txt` "
            "containing exactly `DARK` followed by one LF. Remain responsive to steering "
            "while the command runs.",
            method="Hook-assisted",
        ),
        _case(
            "H05",
            "PSC acceptance H05 steering update: make `hook-theme.txt` contain exactly "
            "`BLUE` followed by one LF instead.",
            method="Hook-assisted",
            interaction="Steering",
        ),
        _case(
            "H06",
            "PSC acceptance H06 steering update: make `hook-theme.txt` contain exactly "
            "`AMBER` followed by one LF instead.",
            method="Hook-assisted",
            interaction="Steering",
        ),
        _case(
            "H07",
            "PSC acceptance H07 correction: use `GREEN` followed by one LF, not `AMBER`, "
            "in `hook-theme.txt`.",
            method="Hook-assisted",
            interaction="Correction",
            supersedes="H06",
        ),
        _case(
            "H08",
            "PSC acceptance H08. Preserve the attached text file and the image pasted with "
            "this message, while keeping user text, Desktop context, and artifact metadata "
            "distinct. Make no other project changes.",
            method="Hook-assisted",
        ),
        _case(
            "H09",
            "PSC acceptance H09. Run `/bin/sleep 120`, then create "
            "`hook-stop-should-not-exist.txt`. I will press Stop before the sleep ends.",
            method="Hook-assisted",
            status="Interrupted",
        ),
        _case(
            "H10",
            "PSC acceptance H10. The trusted prompt-hook handler is deliberately unavailable. "
            "Create `hook-fallback.txt` containing exactly `FALLBACK` followed by one LF.",
            method="Instruction-mediated",
        ),
        _case(
            "H11",
            "PSC acceptance H11. Both optional hooks are disabled. Create "
            "`ordinary-git-check.txt` containing exactly `ORDINARY` followed by one LF.",
            method="Instruction-mediated",
            interaction="Initial prompt",
        ),
    ]


def prepare(workspace: Path) -> None:
    workspace = workspace.resolve()
    try:
        workspace.relative_to(REPOSITORY_ROOT.resolve())
    except ValueError:
        pass
    else:
        raise SystemExit(
            "refusing to create acceptance evidence inside the PromptSourceCode repository"
        )
    if workspace.exists():
        raise SystemExit(f"refusing to reuse existing acceptance workspace: {workspace}")

    project = workspace / "project"
    inputs = workspace / "inputs"
    prompts = inputs / "prompts"
    artifacts = inputs / "artifacts"
    project.mkdir(parents=True)
    prompts.mkdir(parents=True)
    artifacts.mkdir(parents=True)

    filler = "\n".join(
        f"- Existing project policy {number:03d}: preserve ordinary project behavior."
        for number in range(1, 181)
    )
    root_agents = (
        "# Existing Project Instructions\n\n"
        "These representative instructions predate PromptSourceCode and must remain active.\n\n"
        f"{filler}\n\n"
        "## Acceptance sentinel at the end of the existing instructions\n\n"
        f"When a user prompt contains `{ROOT_SENTINEL}`, create the root-level file "
        "`root-instructions-observed.txt` containing exactly `ROOT-INSTRUCTIONS-OBSERVED` "
        "followed by one LF.\n"
    )
    _write_bytes(project / "AGENTS.md", root_agents.encode("utf-8"))

    nested_agents = (
        "# Existing Nested Instructions\n\n"
        f"When a user prompt contains `{NESTED_SENTINEL}`, create "
        "`nested-instructions-observed.txt` in this directory containing exactly "
        "`NESTED-INSTRUCTIONS-OBSERVED` followed by one LF.\n"
    )
    _write_bytes(project / "packages/demo/AGENTS.md", nested_agents.encode("utf-8"))
    _write_bytes(
        project / "fixtures/repository-source.txt",
        b"Repository-local acceptance artifact.\n",
    )

    fixture = json.loads(
        (REPOSITORY_ROOT / "tests/fixtures/artifacts.json").read_text(encoding="utf-8")
    )
    by_id = {item["id"]: item for item in fixture["artifacts"]}
    _write_bytes(
        artifacts / "notes.txt",
        base64.b64decode(by_id["attached-text"]["payload_base64"], validate=True),
    )
    _write_bytes(artifacts / "binary.dat", bytes(range(256)) * 4)
    collision_name = "Résumé Final ??.PNG"
    _write_bytes(
        artifacts / "collision-a" / collision_name,
        base64.b64decode(by_id["attached-image"]["payload_base64"], validate=True),
    )
    _write_bytes(
        artifacts / "collision-b" / collision_name,
        base64.b64decode(
            by_id["attached-image-collision"]["payload_base64"], validate=True
        ),
    )
    _write_bytes(
        artifacts / "paste-source.png",
        base64.b64decode(
            by_id["pasted-image"]["pre_clipboard_payload_base64"], validate=True
        ),
    )

    missing_artifact = artifacts / "intentionally-missing.bin"
    cases = _acceptance_cases(_display_path(missing_artifact))
    for case in cases:
        _write_bytes(
            prompts / f"{case['id']}.txt",
            case["prompt"].encode("utf-8"),
        )

    source_files = [path for path in artifacts.rglob("*") if path.is_file()]
    manifest = {
        "schema": 1,
        "project": _display_path(project),
        "inputs": _display_path(inputs),
        "preexisting_files": {
            "AGENTS.md": {
                **_measure(root_agents.encode("utf-8")),
                "sha256": hashlib.sha256(root_agents.encode("utf-8")).hexdigest(),
            },
            "packages/demo/AGENTS.md": {
                **_measure(nested_agents.encode("utf-8")),
                "sha256": hashlib.sha256(nested_agents.encode("utf-8")).hexdigest(),
            },
        },
        "cases": cases,
        "source_artifacts": [
            {
                "path": str(path.relative_to(inputs)),
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
                "must_be_preserved": path.name != "paste-source.png",
            }
            for path in sorted(source_files)
        ],
        "minimum_preserved_assets": 8,
        "expected_files": {
            "ordinary-project.txt": "initial\n",
            "root-instructions-observed.txt": "ROOT-INSTRUCTIONS-OBSERVED\n",
            "ui-theme.txt": "GREEN\n",
            "standard-recovery.txt": "RECOVERED\n",
            "disabled-check.txt": "DISABLED\n",
            "reenabled-check.txt": "REENABLED\n",
            "packages/demo/nested-instructions-observed.txt": (
                "NESTED-INSTRUCTIONS-OBSERVED\n"
            ),
            "inert-hook-check.txt": "INERT\n",
            "hook-active.txt": "ACTIVE\n",
            "hook-theme.txt": "GREEN\n",
            "hook-fallback.txt": "FALLBACK\n",
            "ordinary-git-check.txt": "ORDINARY\n",
        },
        "expected_absent_files": [
            "standard-stop-should-not-exist.txt",
            "hook-stop-should-not-exist.txt",
        ],
    }
    _write_bytes(
        inputs / "manifest.json",
        (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8"),
    )

    _run_git(project, "init", "-b", "main")
    _run_git(project, "config", "user.name", "PromptSourceCode Acceptance")
    _run_git(project, "config", "user.email", "acceptance@example.invalid")
    _run_git(project, "add", "AGENTS.md", "packages/demo/AGENTS.md", "fixtures")
    _run_git(project, "commit", "-m", "test: prepare existing project instructions")
    origin = workspace / "origin.git"
    _run_git(workspace, "init", "--bare", str(origin))
    _run_git(project, "remote", "add", "origin", "../origin.git")
    _run_git(project, "push", "-u", "origin", "main")

    print(f"Prepared fresh acceptance workspace: {_display_path(workspace)}")
    print(f"Codex Desktop project: {_display_path(project)}")
    print(f"Prompt and artifact inputs: {_display_path(inputs)}")
    print("The target did not previously exist and no earlier evidence was reused.")


def _word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def _extract_loader(text: str) -> str:
    return instruction_contract.extract_loader(text)


def _tracked_files(project: Path) -> set[str]:
    output = _run_git(project, "ls-files", "-z")
    return {item for item in output.split("\0") if item}


def _case_token(prompt: str) -> str | None:
    match = re.match(r"PSC acceptance ([SH]\d{2}[A-Z]?)(?:\.|\s)", prompt)
    return match.group(1) if match else None


def match_case_entries(cases: list[dict[str, Any]], entries: list[core.Entry]) -> tuple[dict[str, core.Entry], list[str]]:
    """Match labelled observations without shifting later cases after an extra/missing entry."""
    remaining = defaultdict(deque)
    for case in cases:
        remaining[_case_token(case["prompt"])].append(case)
    matched = {}
    errors = []
    for entry in entries:
        token = _case_token(entry.prompt)
        if not token or not remaining[token]:
            errors.append(f"unexpected or duplicate capture at Entry {entry.number:06d}: {token or 'unlabelled'}")
            continue
        case = remaining[token].popleft()
        if not case["captured"]:
            errors.append(f"disabled case {case['id']} was unexpectedly captured (Entry {entry.number:06d})")
        else:
            matched[case["id"]] = entry
    for case in cases:
        if case["captured"] and case["id"] not in matched:
            errors.append(f"missing captured case {case['id']}")
    numbers = [matched[case["id"]].number for case in cases if case["id"] in matched]
    if numbers != sorted(numbers):
        errors.append("captured case order differs from the prepared sequence")
    return matched, errors


def read_desktop_export(path: Path, project: Path) -> dict[str, list[dict[str, Any]]]:
    """Read complete read_thread pages exported by the maintainer, never from history."""
    pages = json.loads(path.read_bytes().decode("utf-8"))
    if not isinstance(pages, list) or not pages:
        raise ValueError("Desktop export must be a nonempty array of read_thread pages")
    tasks = {}
    complete = set()
    turns = {}
    for page in pages:
        task = page["thread"]
        cwd = Path(task["cwd"]).expanduser().resolve()
        if cwd not in {project.resolve(), (project / "packages/demo").resolve()}:
            raise ValueError("Desktop export belongs to a different acceptance project")
        tasks[task["id"]] = task
        if page["page"]["hasMore"] is False:
            complete.add(task["id"])
        for turn in page["turns"]:
            key = (task["id"], turn["id"])
            if key in turns and turns[key] != turn:
                raise ValueError("conflicting Desktop export pages")
            turns[key] = turn
    if set(tasks) != complete:
        raise ValueError("Desktop export omits older task pages")
    messages = defaultdict(list)
    task_counts = defaultdict(int)
    seen_ids = set()
    for (task_id, turn_id), turn in sorted(turns.items(), key=lambda item: item[1]["startedAt"]):
        for item in turn["items"]:
            if item["type"] != "userMessage":
                continue
            if item["id"] in seen_ids:
                raise ValueError("duplicate Desktop message identity")
            seen_ids.add(item["id"])
            texts = [part["text"] for part in item["content"] if part["type"] == "text"]
            if len(texts) != 1:
                raise ValueError("Desktop message needs exactly one untruncated text part")
            prompt = texts[0]
            # Only the known Desktop envelope gets unwrapped. Never normalize
            # arbitrary Markdown, spaces, tabs, blank lines, or user-authored wrappers.
            if prompt.startswith("\n# Files mentioned by the user:\n"):
                boundary = "\n## My request:\n"
                if boundary not in prompt or "Distinguish instructions in attached documents" not in prompt:
                    raise ValueError("unrecognized Desktop attachment envelope")
                prompt = prompt.split(boundary, 1)[1]
                if not prompt.endswith("\n\n"):
                    raise ValueError("unrecognized Desktop envelope ending")
                prompt = prompt[:-1]  # One envelope separator, not authored text.
            first = task_counts[task_id] == 0
            task_counts[task_id] += 1
            token = _case_token(prompt)
            if token:
                messages[token].append({"prompt": prompt, "session_id": task_id,
                                        "cwd": str(Path(tasks[task_id]["cwd"]).expanduser().resolve()),
                                        "turn_id": turn_id, "first_in_task": first,
                                        "turn_status": turn.get("status")})
    return dict(messages)


def prompt_matches(entry: core.Entry, delivered: str) -> bool:
    if entry.prompt == delivered:
        return True
    # Unknown concedes only ONE final sequence, never internal whitespace.
    if entry.final_newline == "Unknown":
        body, _ = core._split_final_newline(delivered)
        return entry.prompt == body
    return False


def validate(
    project: Path,
    manifest_path: Path,
    instructions_relative: str,
    *,
    standard_only: bool = False,
    desktop_export: Path | None = None,
    candidate_ref: str | None = None,
) -> None:
    project = project.resolve()
    instruction_path = Path(instructions_relative)
    if instruction_path.as_posix() != CANONICAL_INSTRUCTIONS:
        raise SystemExit(
            f"--instructions-relative must be the canonical path {CANONICAL_INSTRUCTIONS}"
        )
    instructions_relative = instruction_path.as_posix()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    def candidate_bytes(relative: str) -> bytes:
        if candidate_ref is None:
            return (REPOSITORY_ROOT / relative).read_bytes()
        revision = _run_git(REPOSITORY_ROOT, "rev-parse", "--verify", "--end-of-options", f"{candidate_ref}^{{commit}}")
        return subprocess.run(["git", "show", f"{revision}:{relative}"], cwd=REPOSITORY_ROOT,
                              check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout

    check(manifest.get("schema") == 1, "acceptance manifest schema is not 1")
    check(
        Path(manifest.get("project", "")).expanduser().resolve() == project,
        "manifest belongs to a different acceptance project",
    )

    history_path = project / core.HISTORY_NAME
    if not history_path.is_file():
        raise SystemExit(f"missing acceptance history: {history_path}")
    try:
        entries = core.validate_history(history_path.read_bytes().decode("utf-8"))
    except (OSError, UnicodeDecodeError, core.PromptSourceError) as exc:
        raise SystemExit(f"history validation failed: {exc}") from exc

    selected_cases = [
        case
        for case in manifest["cases"]
        if not standard_only or case["id"] in STANDARD_CASE_IDS | {"S12"}
    ]
    captured_cases = [case for case in selected_cases if case["captured"]]
    case_entries, matching_errors = match_case_entries(selected_cases, entries)
    errors.extend(matching_errors)
    delivered_cases = {}
    if desktop_export is not None:
        try:
            delivered = read_desktop_export(desktop_export, project)
            for case in selected_cases:
                observations = delivered.get(_case_token(case["prompt"]), [])
                if not observations:
                    errors.append(f"{case['id']} is missing from the Desktop export")
                else:
                    delivered_cases[case["id"]] = observations.pop(0)
            check(not any(delivered.values()), "Desktop export contains extra acceptance submissions")
        except (OSError, UnicodeDecodeError, ValueError, KeyError, TypeError) as exc:
            errors.append(f"cannot validate Desktop export: {exc}")
    else:
        errors.append("Desktop delivery evidence missing: supply --desktop-export; clipboard fixtures are not delivered-text evidence")
    for case in captured_cases:
        entry = case_entries.get(case["id"])
        if entry is None:
            continue
        observation = delivered_cases.get(case["id"])
        if observation is not None:
            check(prompt_matches(entry, observation["prompt"]),
                  f"{case['id']} prompt text differs from the recorded Desktop delivery")
            if case["interaction"] == "Initial prompt":
                check(observation["first_in_task"], f"{case['id']} was not the first submission in its Desktop task")
        if case["method"] is not None:
            check(
                entry.fields["Capture method"] == case["method"],
                f"{case['id']} has capture method {entry.fields['Capture method']!r}",
            )
        if case["status"] is not None:
            check(
                entry.fields["Status"] == case["status"],
                f"{case['id']} has status {entry.fields['Status']!r}",
            )
        if case["interaction"] is not None:
            check(
                entry.fields["Interaction"] == case["interaction"],
                f"{case['id']} has interaction {entry.fields['Interaction']!r}",
            )
        if case["method"] == "Hook-assisted":
            check(
                observation is None or entry.final_newline == core._split_final_newline(observation["prompt"])[1],
                f"{case['id']} has final-newline state {entry.final_newline!r}",
            )
            check(
                entry.fields.get("Agent observation") == "Claimed",
                f"{case['id']} was not claimed one-to-one by the agent",
            )
            check("Session ID" in entry.fields, f"{case['id']} lacks a session ID")
            check("Turn ID" in entry.fields, f"{case['id']} lacks a turn ID")
        elif case["method"] == "Instruction-mediated":
            for hook_field in ("Turn ID", "Agent observation"):
                check(
                    hook_field not in entry.fields,
                    f"{case['id']} invented hook-only field {hook_field!r}",
                )
            if "Session ID" in entry.fields:
                try:
                    recorded_session = json.loads(entry.fields["Session ID"])
                except json.JSONDecodeError:
                    recorded_session = None
                check(observation is not None and recorded_session == observation["session_id"],
                      f"{case['id']} runtime task identifier differs from Desktop evidence")
        if case["id"] in {"S06", "S08"}:
            try:
                context = core.desktop_runtime_context(entry.text)
                check(context is not None and bool(context[0].strip()),
                      f"{case['id']} lacks separated Desktop runtime context")
            except core.HistoryConflict as exc:
                errors.append(f"{case['id']} has invalid Desktop runtime context: {exc}")
    if delivered_cases:
        for group in (("S03", "S04", "S04B", "S05"), ("H04", "H05", "H06", "H07")):
            if all(key in delivered_cases for key in group):
                identities = {(delivered_cases[key]["session_id"], delivered_cases[key]["turn_id"]) for key in group}
                check(len(identities) == 1, f"{'/'.join(group)} were not delivered in one active Desktop turn")
        if "S14" in delivered_cases and "S01" in delivered_cases:
            check(delivered_cases["S14"]["session_id"] != delivered_cases["S01"]["session_id"],
                  "S14 did not use a separate Desktop task")
        for key, expected_cwd in (("S01", project), ("S14", project / "packages/demo")):
            if key in delivered_cases:
                check(Path(delivered_cases[key]["cwd"]) == expected_cwd.resolve(),
                      f"{key} Desktop task used the wrong project directory")
        for key in ("S10", "H09"):
            if key in delivered_cases:
                check(delivered_cases[key]["turn_status"] == "interrupted",
                      f"{key} Desktop turn does not show an actual interruption")
    for case in captured_cases:
        target_id = case.get("supersedes")
        if not target_id or case["id"] not in case_entries or target_id not in case_entries:
            continue
        expected = f"Entry {case_entries[target_id].number:06d}"
        check(
            case_entries[case["id"]].fields.get("Supersedes") == expected,
            f"{case['id']} does not supersede {target_id}",
        )

    for identifier in ("S02", "H02", "H03A", "H03B"):
        if identifier in case_entries:
            check(
                "Changed files: None." in case_entries[identifier].text,
                f"{identifier} does not record its no-change result",
            )
    if "S10" in case_entries:
        check(
            case_entries["S10"].fields.get("Status reason")
            == "Completion reason unavailable; no reliable Interrupt event was observed.",
            "S10 does not use the canonical standard-capture recovery reason",
        )
    if "H09" in case_entries:
        check(
            case_entries["H09"].fields.get("Status reason") == core.INTERRUPT_REASON,
            "H09 does not use the trusted interruption reason",
        )
    separate_turns = [
        case_entries.get(identifier)
        for identifier in ("H01", "H02", "H03A", "H03B")
    ]
    if all(entry is not None for entry in separate_turns):
        session_ids = {
            entry.fields.get("Session ID") for entry in separate_turns if entry
        }
        turn_ids = {entry.fields.get("Turn ID") for entry in separate_turns if entry}
        check(len(session_ids) == 1, "ordinary hook entries do not share one session ID")
        check(len(turn_ids) == 4, "separate hook submissions do not have distinct turn IDs")
    same_turn = [
        case_entries.get(identifier)
        for identifier in ("H04", "H05", "H06", "H07")
    ]
    if all(entry is not None for entry in same_turn):
        session_ids = {entry.fields.get("Session ID") for entry in same_turn if entry}
        turn_ids = {entry.fields.get("Turn ID") for entry in same_turn if entry}
        check(len(session_ids) == 1, "hook steering entries do not share one session ID")
        check(len(turn_ids) == 1, "hook steering entries do not share one turn ID")
    if "H08" in case_entries:
        artifact_text = case_entries["H08"].text.split("### Artifacts", 1)[-1]
        check(
            "- Kind: Attached file" in artifact_text,
            "H08 lacks its attached-file artifact",
        )
        check(
            "- Kind: Pasted image" in artifact_text,
            "H08 lacks its pasted-image artifact",
        )
        notes_sha256 = next(
            item["sha256"]
            for item in manifest["source_artifacts"]
            if item["path"] == "artifacts/notes.txt"
        )
        check(notes_sha256 in artifact_text, "H08 did not preserve the attached text bytes")
        check(PASTED_FIDELITY in artifact_text, "H08 lacks pasted-image fidelity metadata")
        try:
            context = core.desktop_runtime_context(case_entries["H08"].text)
            check(context is not None and bool(context[0].strip()),
                  "H08 does not keep Desktop context separate")
        except core.HistoryConflict as exc:
            errors.append(f"H08 has invalid Desktop runtime context: {exc}")

    expected_files = manifest["expected_files"].items()
    if standard_only:
        expected_files = (
            (relative, expected)
            for relative, expected in expected_files
            if relative in STANDARD_EXPECTED_FILES
        )
    for relative, expected in expected_files:
        path = project / relative
        check(path.is_file(), f"missing expected ordinary file: {relative}")
        if path.is_file():
            check(
                path.read_bytes() == expected.encode("utf-8"),
                f"ordinary file has unexpected bytes: {relative}",
            )
    absent_files = manifest["expected_absent_files"]
    if standard_only:
        absent_files = ["standard-stop-should-not-exist.txt"]
    for relative in absent_files:
        check(not (project / relative).exists(), f"interrupted work created {relative}")

    history = history_path.read_text(encoding="utf-8")
    check(
        str(Path.home()) not in history,
        "history exposes the operator home path instead of a portable boundary",
    )
    references = re.findall(r"\]\(<(prompt_source_assets/[^>]+)>\)", history)
    assets_directory = project / "prompt_source_assets"
    actual_assets = (
        {str(path.relative_to(project)) for path in assets_directory.rglob("*") if path.is_file()}
        if assets_directory.is_dir()
        else set()
    )
    minimum_assets = 6 if standard_only else manifest["minimum_preserved_assets"]
    check(len(actual_assets) >= minimum_assets, "too few preserved assets")
    check(set(references) == actual_assets, "history asset references and files differ")
    check(len(references) == len(set(references)), "an asset is referenced more than once")
    for relative in actual_assets:
        remainder = relative.removeprefix("prompt_source_assets/")
        check("/" not in remainder, f"asset is not flat: {relative}")
        asset = project / relative
        digest = _sha256(asset)
        containing = [entry.text for entry in entries if relative in entry.text]
        check(len(containing) == 1, f"asset does not belong to exactly one entry: {relative}")
        if containing:
            check(
                f"- Byte count: {asset.stat().st_size}" in containing[0],
                f"asset byte count metadata differs: {relative}",
            )
            check(
                f"- SHA-256: {digest}" in containing[0],
                f"asset digest metadata differs: {relative}",
            )
    required_hashes = {
        item["sha256"]
        for item in manifest["source_artifacts"]
        if item["must_be_preserved"]
    }
    actual_hashes = {_sha256(project / path) for path in actual_assets}
    check(required_hashes <= actual_hashes, "one or more attached source bytes were not preserved")
    repository_source = project / "fixtures/repository-source.txt"
    if repository_source.is_file():
        check(
            _sha256(repository_source) in actual_hashes,
            "repository-local source bytes were not preserved",
        )
    check(any("-002." in path for path in actual_assets), "same-name collision suffix was not used")
    check(PASTED_FIDELITY in history.splitlines(), "canonical pasted-image fidelity line is absent")

    missing_entry = case_entries.get("S09")
    if missing_entry is not None:
        artifact_text = missing_entry.text.split("### Artifacts", 1)[-1].split("### Result", 1)[0]
        check("- Preservation: Unavailable" in artifact_text, "S09 is not unavailable")
        check("- Preserved copy:" not in artifact_text, "S09 invented a preserved copy")
        check("- Byte count:" not in artifact_text, "S09 invented a byte count")
        check("- SHA-256:" not in artifact_text, "S09 invented a digest")

    agents_path = project / "AGENTS.md"
    instructions_path = project / instructions_relative
    validator_path = project / CANONICAL_VALIDATOR
    agents_text = ""
    try:
        agents_text = agents_path.read_text(encoding="utf-8")
        loader = _extract_loader(agents_text)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        errors.append(f"cannot validate loader: {exc}")
        loader = ""
    try:
        instructions = instructions_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"cannot read dedicated instructions: {exc}")
        instructions = ""
    if instructions:
        check(
            instructions_path.read_bytes()
            == candidate_bytes("templates/prompt-source-instructions-v1.md"),
            "dedicated instructions are stale or conflicting",
        )
    check(validator_path.is_file(), "project-local standard validator is missing")
    if validator_path.is_file():
        check(
            validator_path.read_bytes() == candidate_bytes("hooks/prompt_source_core.py"),
            "project-local standard validator is stale or conflicting",
        )
    check(ROOT_SENTINEL in agents_text, "existing root instructions were removed")
    baseline_root = manifest["preexisting_files"]["AGENTS.md"]
    baseline_bytes = agents_text.encode("utf-8")[: baseline_root["bytes"]]
    check(
        hashlib.sha256(baseline_bytes).hexdigest() == baseline_root["sha256"],
        "pre-existing root instructions were changed or displaced",
    )
    nested_path = project / "packages/demo/AGENTS.md"
    baseline_nested = manifest["preexisting_files"]["packages/demo/AGENTS.md"]
    check(nested_path.is_file(), "pre-existing nested instructions are missing")
    if nested_path.is_file():
        check(
            _sha256(nested_path) == baseline_nested["sha256"],
            "pre-existing nested instructions were changed",
        )
    check(
        instructions_relative in loader,
        "loader does not reference the dedicated instruction path",
    )
    check(loader.replace("- Capture: disabled", "- Capture: enabled").encode("utf-8")
          == candidate_bytes("templates/AGENTS.prompt-source-loader.md").strip(b"\n"),
          "installed loader differs from the recorded candidate")
    try:
        loader_size, instruction_size = instruction_contract.validate_pair(
            loader, instructions
        )
    except instruction_contract.InstructionContractError as exc:
        errors.append(f"instruction contract is invalid: {exc}")
        loader_size = instruction_contract.measure(loader)
        instruction_size = instruction_contract.measure(instructions)
    loader_bytes = loader_size.bytes
    loader_words = loader_size.words
    instruction_bytes = instruction_size.bytes
    instruction_words = instruction_size.words

    tracked = _tracked_files(project)
    check(core.HISTORY_NAME not in tracked, "generated history is tracked by Git")
    check(
        not any(path.startswith("prompt_source_assets/") for path in tracked),
        "generated assets are tracked by Git",
    )
    check("AGENTS.md" in tracked, "installed root instructions were not committed")
    check(instructions_relative in tracked, "dedicated instructions were not committed")
    check(CANONICAL_VALIDATOR in tracked, "project-local standard validator was not committed")
    check(
        not any(path == ".codex" or path.startswith(".codex/") for path in tracked),
        "optional hook installation files are tracked by Git",
    )
    if standard_only:
        check(
            not (project / ".codex").exists(),
            "optional hook files exist during the standard-only run",
        )
    else:
        copied_hook_assets = {
            project / ".codex/hooks/prompt_source_core.py": HOOKS_DIRECTORY / "prompt_source_core.py",
            project / ".codex/hooks/prompt_source_hook.py": HOOKS_DIRECTORY / "prompt_source_hook.py",
            project / ".codex/hooks.json": HOOKS_DIRECTORY / "hooks.json.example",
        }
        for installed, source in copied_hook_assets.items():
            check(installed.is_file(), f"missing installed optional hook asset: {installed}")
            if installed.is_file():
                check(
                    installed.read_bytes() == candidate_bytes(source.relative_to(REPOSITORY_ROOT).as_posix()),
                    f"installed optional hook asset differs from source: {installed}",
                )
    try:
        divergence = _run_git(project, "rev-list", "--left-right", "--count", "origin/main...main")
        check(divergence == "0\t0", f"main and origin/main differ: {divergence!r}")
    except subprocess.CalledProcessError as exc:
        errors.append(f"cannot compare main with origin/main: {exc.stderr.strip()}")

    check(
        not any(
            "project_doc_fallback_filenames" in path.read_text(encoding="utf-8", errors="ignore")
            for path in project.rglob("*")
            if path.is_file() and ".git" not in path.parts
        ),
        "project contains a user-specific fallback-filename dependency",
    )
    forbidden = [
        path
        for path in project.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and (
            path.suffix in {".pyc", ".tmp", ".lock"}
            or path.name
            in {
                "prompt_source_input",
                "prompt_source_result",
                "prompt_source_status",
                "prompt_source_runtime_context",
                "prompt_source_event_log",
            }
        )
    ]
    forbidden.extend(
        path
        for path in project.rglob("__pycache__")
        if path.is_dir() and ".git" not in path.parts
    )
    check(not forbidden, f"persistent runtime outputs remain: {forbidden}")

    if errors:
        print("Desktop acceptance validation FAILED:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)

    if standard_only:
        print("Desktop standard-capture acceptance validation PASSED")
    else:
        print("Desktop acceptance validation PASSED")
    print(f"Entries: {len(entries)}")
    print(f"Assets: {len(actual_assets)}")
    print(f"Loader: {loader_words} words, {loader_bytes} bytes")
    print(f"Dedicated instructions: {instruction_words} words, {instruction_bytes} bytes")
    print(
        "Root AGENTS.md: "
        f"{baseline_root['lines']}->{len(agents_text.splitlines())} lines, "
        f"{baseline_root['words']}->{_word_count(agents_text)} words, "
        f"{baseline_root['bytes']}->{len(agents_text.encode('utf-8'))} bytes"
    )
    print(
        "Nested AGENTS.md retained: "
        f"{baseline_nested['lines']} lines, {baseline_nested['words']} words, "
        f"{baseline_nested['bytes']} bytes"
    )
    print("Git: generated provenance untracked; main synchronized with origin/main")
    if standard_only:
        print("Optional-hook cases S15 and H01-H11: NOT RUN")
        print("Full Milestone 6 Desktop acceptance remains incomplete")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare_parser = subparsers.add_parser("prepare", help="create a fresh disposable workspace")
    prepare_parser.add_argument("workspace", type=Path)

    validate_parser = subparsers.add_parser("validate", help="validate the completed run")
    validate_parser.add_argument("project", type=Path)
    validate_parser.add_argument("manifest", type=Path)
    validate_parser.add_argument(
        "--instructions-relative",
        default=CANONICAL_INSTRUCTIONS,
        help=f"canonical project path (fixed at {CANONICAL_INSTRUCTIONS})",
    )
    validate_parser.add_argument(
        "--standard-only",
        action="store_true",
        help="validate only S01-S14 and record optional-hook cases as not run",
    )
    validate_parser.add_argument("--desktop-export", type=Path,
                                 help="complete read_thread pages exported outside the captured project")
    validate_parser.add_argument("--candidate-ref", help="audit the installation against this recorded Git commit")
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    if arguments.command == "prepare":
        prepare(arguments.workspace)
        return 0
    validate(
        arguments.project,
        arguments.manifest,
        arguments.instructions_relative,
        standard_only=arguments.standard_only,
        desktop_export=arguments.desktop_export,
        candidate_ref=arguments.candidate_ref,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
