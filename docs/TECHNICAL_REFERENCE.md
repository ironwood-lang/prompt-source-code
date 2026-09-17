# PromptSourceCode Technical Reference

This document contains the architecture, format boundaries, lifecycle behavior,
validation status, and contributor information deliberately omitted from the end-user
front page. The current implementation uses storage schema 1.

## Architecture

PromptSourceCode targets Codex Desktop and provides two capture layers:

1. **Standard capture:** a small marked loader in the root `AGENTS.md` reads the complete
   operational contract from `.prompt-source/instructions-v1.md` before capture or task
   work. A project-local `.prompt-source/validate.py` rereads capture state, creates entries,
   finalizes results, and checks schema-1 history. This required default works without global Codex configuration, hooks,
   skills, plugins, background services, or network access.
2. **Hook-assisted capture:** an explicitly enabled optional enhancement using
   `UserPromptSubmit` and `Interrupt`. Hooks improve prompt fidelity, identify mid-turn
   steering through turn metadata, and record button-only interruptions.

A skill is not part of the capture path because skill selection is conditional. Hooks do
not replace the loader and dedicated instructions; they enhance them.

## Canonical project output

All chronological text and provenance history lives in one file at the project root:

```text
PROMPT_SOURCE.md
```

Preserved artifacts live in one flat directory:

```text
prompt_source_assets/
```

PromptSourceCode does not create per-prompt directories or separate input, status,
result, runtime-context, event-log, or persistent lock files.

## Capture boundary

For text, PromptSourceCode preserves the exact representation delivered by Codex Desktop
to the agent. It does not claim to preserve raw keystrokes or editor state from before
Desktop serializes a submission.

Attached files can be preserved byte-for-byte when Desktop exposes their source paths.
Pasted images can be preserved byte-for-byte from the temporary files materialized by
Desktop, but those files may be encoded differently from the images that existed before
they entered the clipboard.

The complete frozen schema is defined in
[`PROMPT_SOURCE_FORMAT.md`](PROMPT_SOURCE_FORMAT.md).

## Release status and evidence

Milestones 0 through 4 established feasibility, the format and instruction contract,
standard capture, optional hooks, and the frozen release candidate. Milestone 5 prepared
the end-user onboarding surface and public 0.1.0 release.

Standard capture was validated from the first prompt in a clean disposable local Git
project with no hook, skill, plugin, background service, or network dependency. Its run
covered follow-ups, in-turn steering, corrections, no-change work, artifacts, real
Stop-button recovery, lifecycle controls, final structure, and practical Git behavior.

The optional hook enhancement was validated in a fresh disposable project using Codex
Desktop 26.911.61220 (9647) on macOS 26.6.2. That run covered explicit trust and restart,
exact event-text capture, ordinary follow-ups, same-turn steering, repeated identical
prompts, agent enrichment without duplication, correction, artifact enrichment, a real
trusted interruption, guarded hook failure with standard fallback, concurrent and
failure-injected writes, Git isolation, and standard capture after both hooks were
disabled.

The final clean-project acceptance run rechecked initial capture, follow-ups, in-turn
steering, corrections, no-change work, artifacts, lifecycle controls, exact hook capture,
one-to-one matching, a trusted interruption, guarded failure, disabled-hook fallback,
final structure, and Git isolation. Deterministic tests cover concurrency, interruption
races, atomic failure, malformed histories, repeated prompts, dynamic fences, and newline
states.

Evidence is preserved in:

- [`MILESTONE_6_VALIDATION_20260917.md`](MILESTONE_6_VALIDATION_20260917.md)
- [`CODEX_DESKTOP_STANDARD_CAPTURE_VALIDATION.md`](CODEX_DESKTOP_STANDARD_CAPTURE_VALIDATION.md)
- [`CODEX_DESKTOP_HOOK_CAPTURE_VALIDATION.md`](CODEX_DESKTOP_HOOK_CAPTURE_VALIDATION.md)
- [`CODEX_DESKTOP_V1_RELEASE_READINESS.md`](CODEX_DESKTOP_V1_RELEASE_READINESS.md)
- [`CODEX_DESKTOP_CAPTURE_EXPERIMENT.md`](CODEX_DESKTOP_CAPTURE_EXPERIMENT.md)
- [`ROADMAP.md`](ROADMAP.md)

## Standard capture lifecycle

Install [`../templates/AGENTS.prompt-source-loader.md`](../templates/AGENTS.prompt-source-loader.md)
as the bounded root loader and
[`../templates/prompt-source-instructions-v1.md`](../templates/prompt-source-instructions-v1.md)
at `.prompt-source/instructions-v1.md`. The root [`../AGENTS.md`](../AGENTS.md) here is
contributor guidance and must not be copied into an end-user project.

The installer also copies the shared standard-library schema module from
[`../hooks/prompt_source_core.py`](../hooks/prompt_source_core.py) to
`.prompt-source/validate.py`. The standard contract uses `--capture-state`,
`--begin-standard`, `--finish-standard`, and the read-only `--validate-history` mode. The
installed file is not configured as a hook, does not activate hooks, and performs no
network or Git operation.
When invoked as the installed `.prompt-source/validate.py`, its standard commands locate
the root from that file's location, so an absolute invocation from a nested cwd is safe.

The state check verifies the exact marked loader, rereads its current enabled/disabled
control, and verifies the dedicated instruction bytes only when enabled. Entry creation
and completion repeat that check under the existing directory lock. Disabled or invalid
installations therefore cannot write through these commands. The helper initializes the
header, chooses canonical fences, allocates numbers, and atomically writes text; the
agent still supplies the delivered prompt and factual results.

`first_in_task` describes the current conversation, not whether the shared history exists.
When the runtime exposes `CODEX_THREAD_ID`, the helper copies it into the existing schema-1
`Session ID` field and rejects contradictory task associations. It does not create an ID,
query global configuration, or read a transcript during capture. If earlier submissions
in the same task were not captured, the agent must explicitly supply
`uncaptured_predecessor: true`; an empty task history alone cannot establish that this is
the first user submission. Without the runtime identifier, classification uses the
agent-supplied conversation context. These facts do not make model-mediated text capture
deterministic.

Artifact/context enrichment remains agent work. The helper's serialized text writes do
not make arbitrary direct edits or artifact copies transactional. The standard path still
requires model compliance with the instructions.

The canonical project path and instruction marker are versioned independently of storage
schema. The loader is 300 words/2,048 bytes maximum, the dedicated contract is 900
words/6,144 bytes maximum, and their combined always-read footprint is 1,200 words/8,192
bytes maximum. [`../scripts/instruction_contract.py`](../scripts/instruction_contract.py)
enforces these ceilings, appends without replacing existing root guidance, installs the
matching validator, and leaves nested instructions untouched.

The loader contains the enabled/disabled control and exact begin/end markers. Updating
replaces only that block, the dedicated file, and the validator without rewriting history.
It resolves the canonical instruction path from `git rev-parse --show-toplevel`, including
when Codex Desktop opens a nested directory as a separate project.
Missing, unreadable, stale, conflicting, or truncated instructions—or a missing or
noncanonical validator—fail closed for capture while ordinary work continues under other
applicable project instructions. Disabling or removing the standard installation leaves
existing provenance untouched.

The full operational procedure is in [`INSTALLATION.md`](INSTALLATION.md).

## Optional hook-assisted capture

The optional enhancement consists of two inert Python source files and one example hook
definition under [`../hooks/`](../hooks/). It uses only `UserPromptSubmit` and `Interrupt`.
Copying the files does not activate them. The project owner must separately review,
enable, and trust both definitions through Codex CLI `/hooks`, then fully restart Desktop.

`UserPromptSubmit` atomically creates a canonical Hook-assisted entry before agent work.
The agent claims the earliest exact session, turn, and byte match and enriches it instead
of adding a duplicate. The handler validates that the hook transcript belongs to a
user-created Codex Desktop task, excluding subagents and internal feature prompts.
Repeated identical submissions remain distinct.

`Interrupt` changes unfinished hook-assisted interactions in the exact matching session
and turn to the canonical Interrupted state while preserving completed entries and
captured input.

Hook and agent-helper writes share project-directory serialization, full structural
validation, optimistic entry digests, and same-directory atomic replacement. They leave
no persistent lock or diagnostic log and perform no network or Git operations. A guarded
handler failure returns control to Desktop so the standard instruction-mediated path can
remain available.

Trust is bound to each exact hook definition. Any definition change requires another
review, trust decision, and Desktop restart. Never bypass hook trust. Installation,
updating, disabling, removal, and troubleshooting are documented in
[`OPTIONAL_HOOKS.md`](OPTIONAL_HOOKS.md).

## Generated history and Git

PromptSourceCode does not stage, commit, push, publish, or upload generated
`PROMPT_SOURCE.md` or `prompt_source_assets/` unless the user explicitly requests it.

This restriction applies only to generated provenance. It does not change the tracked
project's normal Git workflow for source code, tests, documentation, or other files. It is
an agent-behavior restriction, not an automatic `.gitignore` rule; generated history
normally remains visible as unstaged working-tree data for inspection.

## Compatibility and upgrades

The product release and storage schema are separate version axes: PromptSourceCode 0.1.0
implements schema 1. Existing valid schema-1 histories and artifacts are preserved during
updates. Unknown, malformed, incompatible, or future schemas are not silently repaired or
migrated. See [`COMPATIBILITY.md`](COMPATIBILITY.md) for the tested environment and upgrade
policy.

## Contributor validation

Acceptance compares captured text with exported Desktop `userMessage` records. Clipboard
fixtures establish what to submit, but cannot establish what Desktop delivered. The
validator matches case labels before comparing content, preserving separate observations
for deliberately repeated H03 prompts. A missing or extra entry cannot shift later cases.
Exports live outside the captured project and are used only by the developer's validator;
they are never a standard-capture runtime dependency. See the
[acceptance runbook](MILESTONE_6_CODEX_DESKTOP_ACCEPTANCE.md) for historical replay.
The [2026-09-17 recovery audit](MILESTONE_6_RECOVERY_20260917.md) records the preserved
Desktop failures, corrected validator findings, and deterministic repair results.

Run the deterministic contract checks with:

```text
python3 -m unittest discover -s tests -v
```

The copyable standard and hook files are frozen by byte count and SHA-256 in
[`../tests/fixtures/distribution-manifest.json`](../tests/fixtures/distribution-manifest.json).
Development must follow the root [`../AGENTS.md`](../AGENTS.md), keep documentation and
tests aligned, and never enable live capture in this repository.
