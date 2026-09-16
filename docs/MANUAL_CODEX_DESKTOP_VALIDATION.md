# Manual Codex Desktop Validation Checklist

Use this checklist for behavior that fixture tests cannot prove. Run it only in a fresh,
disposable project outside the PromptSourceCode repository. Do not enable capture in the
PromptSourceCode development repository.

Milestone 1 supplies this checklist; the complete clean-project run and release-candidate
evidence are Milestone 2 work.

## Setup

- [ ] Create a disposable local Git repository and open it as a project in Codex Desktop.
- [ ] Add the contents of
  [`templates/AGENTS.prompt-source-standard.md`](../templates/AGENTS.prompt-source-standard.md)
  to the disposable project's root `AGENTS.md`.
- [ ] Confirm that no PromptSourceCode hook, skill, plugin, background service, or network
  dependency is enabled for the standard-path run.
- [ ] Confirm that the first captured interaction creates one root `PROMPT_SOURCE.md` with
  schema marker `<!-- prompt-source-schema: 1 -->` before requested project work starts.

## Text and chronology

- [ ] Submit text containing misspellings, leading, trailing, and consecutive spaces,
  tabs, blank lines, Unicode, Markdown headings and links, long backtick and tilde fences,
  PromptSourceCode-like headings, and a known final-newline state.
- [ ] Inspect the dynamic fence and final-newline field. Confirm that the stored text is
  the representation delivered to the agent; do not describe this model-mediated check as
  independent verification or as preservation of pre-serialization editor state.
- [ ] Send a normal follow-up after completion and confirm it receives the next entry.
- [ ] During one active turn, send two steering messages. Confirm that each is recorded as
  a separate ordered entry before it is acted upon and that all handled entries are
  finalized when the turn finishes.
- [ ] Send a correction that supersedes an earlier instruction. Confirm that the
  correction points back with `Supersedes` and that the earlier user input is unchanged.
- [ ] Ask a question that changes no repository files. Confirm that it completes with
  `Changed files: None.`

## Artifacts

- [ ] Attach a text or binary file whose source is available. Confirm a direct child of
  `prompt_source_assets/` is created and compare source and copy with byte count, SHA-256,
  and a binary comparison tool.
- [ ] Attach an image file and perform the same byte-for-byte checks.
- [ ] Paste that image through the clipboard. Confirm that the Desktop-materialized
  temporary image is copied before it disappears and that its artifact kind and fidelity
  statement differ from the attached original. Do not require its bytes or digest to
  equal the pre-clipboard file.
- [ ] Exercise two artifacts that sanitize to the same asset name. Confirm the second
  differing payload receives `-002` before the extension and neither file is overwritten.
- [ ] Reference an artifact already inside the disposable repository. Confirm a
  point-in-time snapshot is still placed directly in `prompt_source_assets/`.
- [ ] Make an external artifact unavailable before preservation. Confirm the entry remains,
  `Preservation: Unavailable` is recorded, and no byte count, digest, link, or placeholder
  is invented.

## Unfinished work and Git behavior

- [ ] Start a turn and press Stop in Desktop while using standard capture only. Confirm
  that the prompt entry exists but the instructions do not claim to have observed the
  button-only interruption.
- [ ] On the next interaction, confirm the stale entry becomes `Incomplete` with the
  unknown-reason text. It must not become `Interrupted` without a trusted hook event.
- [ ] Inspect the final history: entry numbers are unique and ordered, textual history is
  in one file, asset references are flat, and no per-prompt directories exist.
- [ ] Run `git status` and a normal source-code staging exercise. Confirm generated
  `PROMPT_SOURCE.md` and `prompt_source_assets/` remain unstaged unless explicitly
  requested, while ordinary project files can be staged normally.
- [ ] Save the Desktop version and factual results with the Milestone 2 evidence; do not
  claim support for other environments based on this run.
