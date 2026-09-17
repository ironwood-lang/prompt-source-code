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
block before task work. Optional hook work was subsequently completed in Milestone 3;
the 0.1.0 release candidate was subsequently completed in Milestone 4. Public tagging and
publication were explicitly authorized and completed in Milestone 5.

## Milestone 3: Optional Hook Enhancement

**Status:** Complete

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

Completed on 2026-09-17 in a fresh disposable local Git project using Codex Desktop
26.911.61220 (9647) on macOS 26.6.2. The implementation uses only local standard-library
Python, `UserPromptSubmit`, and `Interrupt`. Explicit project-local installation, separate
Codex CLI `/hooks` review and trust, and a full Desktop restart were exercised. Codex CLI
was not used as the capture environment.

The live run covered exact event bytes and final-newline state, session/turn association,
ordinary follow-ups, two same-turn steering messages, repeated identical prompts,
one-to-one agent claims, correction, no-change work, separate artifact enrichment, a real
Stop with a trusted interruption, a conservative unmatched interrupt, guarded hook
failure with standard fallback, generated-history Git isolation, final storage topology,
and standard capture after both hooks were disabled. Deterministic tests additionally
covered simultaneous processes, prompt/interrupt/enrichment races, malformed and
structurally conflicting history, and failure before atomic replacement.

Validation exposed and resolved four material defects: an internal Desktop feature event
crossed the initial event boundary, a structural separator destabilized an earlier entry
digest, interruption metadata used noncanonical spacing, and an unguarded handler launch
failure blocked Desktop message delivery. Evidence and the resulting boundaries are
recorded in
[`CODEX_DESKTOP_HOOK_CAPTURE_VALIDATION.md`](CODEX_DESKTOP_HOOK_CAPTURE_VALIDATION.md).

## Milestone 4: 0.1.0 Release Candidate

**Status:** Complete

- Freeze the format with an explicit schema/version marker.
- Finish concise installation and troubleshooting documentation.
- Provide copyable standard instructions and optional hook assets.
- Add upgrade and compatibility notes.
- Run the complete clean-project acceptance checklist in Codex Desktop.
- Tag and publish only after an explicit user request.

Completed on 2026-09-17 using the frozen release bundle in a fresh disposable local Git
project. The run covered the complete standard lifecycle, inert optional assets, separate
hook review and trust, trusted exact capture, one-to-one matching, a real interruption,
guarded failure, disabled-hook fallback, final structural validation, and generated-file
Git isolation while ordinary project files retained normal commit and push behavior.

The format freeze, environment, case results, hashes, limitations, and release decision
are recorded in
[`CODEX_DESKTOP_V1_RELEASE_READINESS.md`](CODEX_DESKTOP_V1_RELEASE_READINESS.md). No tag,
GitHub release, package publication, or other release artifact was created as part of
this milestone; public release was deliberately deferred to Milestone 5.

## Milestone 5: 0.1.0 Public Launch

**Status:** Complete

- Replace the repository front page with a concise end-user explanation, installation
  path, example, and hands-on test checklist.
- Move architecture, capture boundaries, hook mechanics, contributor validation, and
  other implementation detail to a dedicated technical reference.
- Distinguish the `0.1.0` product release from storage schema 1 throughout release-facing
  documentation and fixtures.
- Re-run deterministic validation, verify download-facing links and documentation, and
  preserve the already accepted release assets byte-for-byte.
- Create and push the `v0.1.0` tag from synchronized `main` after explicit authorization.
- Publish the GitHub release so users can download the tagged source archives and test the
  documented installation path.

**Exit criterion:** A new user can understand the product from the front page, download
the public 0.1.0 release, install standard capture, run the example, and find the deeper
technical material without the README becoming an implementation specification.

Completed on 2026-09-17 after the owner explicitly authorized tagging and publication.
The GitHub release is the distribution artifact; no separate language-package publication
was invented for this documentation-and-local-assets project. User testing remains
welcome through the front-page checklist and issue tracker. Release notes are in
[`RELEASE_NOTES_0.1.0.md`](RELEASE_NOTES_0.1.0.md). The publication gate passed all 50
deterministic tests and 80 repeated concurrency/failure-injection invocations.

## 0.1.0 Non-goals

- Codex CLI as a supported capture environment.
- The Codex IDE extension.
- Claude Code or other coding agents.
- Cloud capture or synchronization.
- Automatic Git publication of generated `PROMPT_SOURCE.md` or
  `prompt_source_assets/`.
- A skill as a required capture mechanism.
