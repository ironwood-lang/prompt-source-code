# PromptSourceCode Development Instructions

## Purpose

PromptSourceCode preserves the human interaction history that shaped an AI-assisted
software project. Its guiding principle and slogan are:

> The prompt history is the new source code.

This file governs development of PromptSourceCode itself. Keep the installable end-user
instructions in their own documented template; do not make users copy this development
file into their projects.

## 0.1.0 Scope

- Target Codex Desktop first. Do not broaden 0.1.0 to Codex CLI, the Codex IDE
  extension, Claude Code, or other agents unless the user explicitly changes the scope.
- Use `AGENTS.md` instructions as the required, default capture mechanism.
- Treat hooks as an explicit, optional enhancement layered on top of the instructions.
- Do not use a skill as a prompt-capture mechanism. A future skill may assist installation
  or configuration, but capture must not depend on conditional skill selection.
- Do not require hooks, a plugin, a background service, or network access for standard
  capture.

## Product Invariants

- Store all chronological textual history in one root-level `PROMPT_SOURCE.md` file.
- Store preserved binary artifacts in one flat `prompt_source_assets/` directory and
  reference them from `PROMPT_SOURCE.md`.
- Do not create per-prompt directories or separate input, status, result, or runtime-context
  files.
- Record every distinct user interaction as a separate chronological entry. This includes
  initial prompts, ordinary follow-ups, mid-turn steering, corrections, and changes of
  direction.
- Preserve the exact text representation delivered by Codex Desktop to the agent. Do not
  claim to preserve raw keystrokes or editor state from before Desktop serialization.
- Distinguish user-authored text, Codex Desktop runtime context, and artifact metadata.
- Preserve attached files byte-for-byte when the source path is available.
- For pasted images, preserve the temporary image delivered by Codex Desktop byte-for-byte
  without claiming it is binary-identical to an unknown pre-paste source file.
- Standard capture is model-mediated and must be described honestly. Do not call model
  read-back or self-comparison independent verification.
- Create an entry as `In progress` before doing the requested work. Mark it `Completed`
  only after the work finishes. If execution ends unexpectedly, retain an explicit
  incomplete state without inventing a reason.
- Never delete or rewrite an earlier interaction because it was corrected, contradicted,
  abandoned, or superseded later.
- By default, do not stage, commit, push, publish, or upload the generated
  `PROMPT_SOURCE.md` or `prompt_source_assets/`. Include those generated provenance
  artifacts in Git only when the user explicitly requests it.
- This generated-artifact restriction must not interfere with the tracked project's normal
  Git workflow. Source code, tests, documentation, and other project files may be staged,
  committed, and pushed normally according to the user's instructions.

## Optional Hook Enhancement

- Limit the first hook implementation to `UserPromptSubmit` and `Interrupt` unless evidence
  establishes that another event is necessary.
- Use hook-provided session and turn identifiers to associate steering and interruptions
  with the correct turn.
- Prevent duplicate entries when both the hook and the agent observe the same prompt.
- Keep the standard `AGENTS.md` behavior functional when hooks are absent, untrusted,
  disabled, or fail.
- Do not install or activate hooks silently. Document the current Codex CLI `/hooks` trust
  requirement and the need to restart Desktop after trust changes.
- Never recommend bypassing hook trust.
- Hooks must remain local, perform no network operations, and perform no Git operations.

## Repository Work

- Keep `README.md`, the format specification, templates, hook behavior, and tests aligned.
- Treat `docs/CODEX_DESKTOP_CAPTURE_EXPERIMENT.md` as evidence from the completed
  experiment. Do not rewrite its findings to fit an implementation preference.
- Do not create `PROMPT_SOURCE.md` or `prompt_source_assets/` in this repository. The
  PromptSourceCode repository develops the product but is not itself a capture target.
- Run end-to-end capture experiments in a separate disposable project outside this
  repository. Repository test fixtures may model expected files without enabling capture
  for PromptSourceCode's own development history.
- Prefer small, inspectable Markdown, Python, and JSON artifacts over a large framework.
- Add automated tests for deterministic code and maintain a short manual Codex Desktop test
  checklist for behavior that cannot be exercised outside the app.
- Do not claim support for an environment that has not been tested.

## Git Operations

This repository is intended to be published on GitHub. Do not interpret the product's
generated-artifact exclusion as a prohibition on publishing the PromptSourceCode project
or any project that uses it.

The PromptSourceCode repository's source, tests, and documentation follow the normal Git
workflow. Unless the user explicitly says not to commit or push, completed development
changes may be committed and pushed directly to the intended branch. Do not open a pull
request merely in order to merge the work; use a pull request only when the user
explicitly requests that workflow.

Keep GitHub release bodies empty so release pages show only the downloadable files. Put
release descriptions, instructions, and other explanatory text in `README.md` or `docs/`.

The product's default Git exclusion applies only to the generated `PROMPT_SOURCE.md` and
`prompt_source_assets/` in projects being captured.
