# PromptSourceCode Roadmap

## Why Use Milestones

PromptSourceCode is intentionally small, but its core promise is about fidelity and
provenance. The implementation does not need a large framework; it does need a precise
format, conservative instructions, deterministic optional hooks, and evidence that the two
capture paths do not corrupt or duplicate history.

## Milestone 0: Codex Desktop Feasibility

**Status:** Complete

- Validate agent-visible text fidelity.
- Validate normal follow-ups and mid-turn steering.
- Validate byte-preserving attached-file capture.
- Establish the fidelity boundary for pasted images.
- Test button-only interruption behavior without hooks.
- Test `UserPromptSubmit` and `Interrupt` in Desktop after explicit hook trust.
- Record the Desktop-only hook onboarding limitation.

Evidence is documented in
[`CODEX_DESKTOP_CAPTURE_EXPERIMENT.md`](CODEX_DESKTOP_CAPTURE_EXPERIMENT.md).

## Milestone 1: Format and Instruction Contract

**Status:** Complete

- Specify the canonical `PROMPT_SOURCE.md` structure.
- Define entry numbering, status transitions, capture-method labels, and result fields.
- Define a robust representation for arbitrary Markdown and nested code fences.
- Define artifact naming, collision handling, hashing, and relative references.
- Define how user text, Desktop runtime context, and artifact metadata remain distinct.
- Write the installable standard-capture `AGENTS.md` block.
- Add representative fixtures and a manual validation checklist.

**Exit criterion:** A fresh Codex Desktop project can use the documented instructions to
produce one readable, chronological `PROMPT_SOURCE.md` and one flat assets directory for
all tested interaction types.

Delivered in:

- [`PROMPT_SOURCE_FORMAT.md`](PROMPT_SOURCE_FORMAT.md)
- [`../templates/AGENTS.prompt-source-standard.md`](../templates/AGENTS.prompt-source-standard.md)
- [`../tests/fixtures/expected-history.md`](../tests/fixtures/expected-history.md)
- [`../tests/test_format.py`](../tests/test_format.py)
- [`MANUAL_CODEX_DESKTOP_VALIDATION.md`](MANUAL_CODEX_DESKTOP_VALIDATION.md)

The fixture contract and deterministic checks are complete. The first full run of the
final standard template in a clean disposable Desktop project is deliberately retained as
the Milestone 2 release-candidate validation, so this milestone does not claim that later
test has already occurred.

## Milestone 2: Standard Capture Release Candidate

**Status:** Complete

- Test the standard instructions in a clean disposable repository, separate from the
  PromptSourceCode repository, from its first prompt.
- Test follow-ups, multiple steering messages, corrections, and superseded instructions.
- Test attached text, binary files, attached images, and pasted images.
- Test unfinished-entry recovery after interruption or application exit.
- Verify that generated `PROMPT_SOURCE.md` and `prompt_source_assets/` are excluded from
  Git staging, commits, pushes, and uploads by default without affecting normal Git
  operations for other project files.
- Document installation, updating, disabling, and removal.

**Exit criterion:** Standard capture works without a skill, plugin, hook, background service,
or network access and its limitations are stated accurately.

Completed on 2026-09-16 in a fresh disposable local Git project using Codex Desktop
26.908.70816 (9275) on macOS 26.6.2. The run used the project-root standard template from
its first prompt and exercised all listed interaction, artifact, recovery, structure, and
Git cases. It used no PromptSourceCode hook, skill, plugin, background service, or network
dependency. Evidence, hashes, limitations, and independent byte-level checks are recorded
in
[`CODEX_DESKTOP_STANDARD_CAPTURE_VALIDATION.md`](CODEX_DESKTOP_STANDARD_CAPTURE_VALIDATION.md).

Release-candidate hardening added explicit installation/update boundaries, an enabled or
disabled capture control, removal guidance, a same-entry collision check, and a
single-physical-line pasted-image fidelity field. A post-run cross-task test also exposed
ambiguous insertion after repeated result text; the contract now requires EOF-only append,
physical-order verification, and bounded repair of only a newly misplaced unfinished
block before task work. The optional hook enhancement remains Milestone 3 work; version 1
release hardening and tagging remain Milestone 4 work.

## Milestone 3: Optional Hook Enhancement

**Status:** Not started

- Implement minimal `UserPromptSubmit` and `Interrupt` handlers.
- Keep hook installation inert until the user explicitly enables it.
- Document Codex CLI `/hooks` review and trust, plus the Desktop restart requirement.
- Associate initial prompts, steering, and interruption events through session and turn IDs.
- Prevent duplication between hook-captured prompts and agent-mediated processing.
- Protect `PROMPT_SOURCE.md` from partial writes and concurrent update corruption.
- Confirm that standard capture continues working when hooks are unavailable or fail.
- Add deterministic unit tests and repeat the Desktop integration test.

**Exit criterion:** An opted-in user gains deterministic agent-visible text capture and
explicit interruption records without changing the canonical storage format.

## Milestone 4: Version 1 Release

**Status:** Not started

- Freeze the format with an explicit schema/version marker.
- Finish concise installation and troubleshooting documentation.
- Provide copyable standard instructions and optional hook assets.
- Add upgrade and compatibility notes.
- Run the complete clean-project acceptance checklist in Codex Desktop.
- Tag and publish only after an explicit user request.

## Version 1 Non-goals

- Codex CLI as a supported capture environment.
- The Codex IDE extension.
- Claude Code or other coding agents.
- Cloud capture or synchronization.
- Automatic Git publication of generated `PROMPT_SOURCE.md` or
  `prompt_source_assets/`.
- A skill as a required capture mechanism.
