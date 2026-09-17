# Manual Codex Desktop Validation Checklist

Use this checklist for behavior that fixture tests cannot prove. Run it only in a fresh,
disposable project outside the PromptSourceCode repository. Do not enable capture in the
PromptSourceCode development repository.

For the exact Milestone 6 developer procedure, including prepared inputs, copyable prompts,
UI actions, checkpoints, and the final validation command, use
[`MILESTONE_6_CODEX_DESKTOP_ACCEPTANCE.md`](MILESTONE_6_CODEX_DESKTOP_ACCEPTANCE.md).

Milestone 2 completed the standard-path checklist and Milestone 3 completed the optional
hook checklist in their tested Desktop environments. See
[`CODEX_DESKTOP_STANDARD_CAPTURE_VALIDATION.md`](CODEX_DESKTOP_STANDARD_CAPTURE_VALIDATION.md)
and [`CODEX_DESKTOP_HOOK_CAPTURE_VALIDATION.md`](CODEX_DESKTOP_HOOK_CAPTURE_VALIDATION.md)
for that evidence. Milestone 4 repeats the release-critical cases from the final bundle;
its factual results belong in
[`CODEX_DESKTOP_V1_RELEASE_READINESS.md`](CODEX_DESKTOP_V1_RELEASE_READINESS.md). Keep this
file reusable and unchecked for future regression runs.

## Setup

- [ ] Resolve and preserve any earlier disposable projects before creating a clearly
  named fresh local Git project; do not reset or silently reuse prior evidence.
- [ ] Record the source commit, release-asset manifest, Desktop, macOS, Python, and Git
  versions used by the run without publishing full session or turn identifiers.
- [ ] Create a disposable local Git repository and open it as a project in Codex Desktop.
- [ ] Append
  [`templates/AGENTS.prompt-source-loader.md`](../templates/AGENTS.prompt-source-loader.md)
  to the disposable project's root `AGENTS.md`, and install
  [`templates/prompt-source-instructions-v1.md`](../templates/prompt-source-instructions-v1.md)
  at `.prompt-source/instructions-v1.md`, plus
  [`hooks/prompt_source_core.py`](../hooks/prompt_source_core.py) at
  `.prompt-source/validate.py`.
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
  statement differ from the attached original. Keep the required pasted-image `Fidelity`
  field on one physical Markdown line. Do not require its bytes or digest to equal the
  pre-clipboard file.
- [ ] In one interaction and therefore one entry, exercise two differing artifacts whose
  names sanitize to the same asset name. Confirm the second payload receives `-002`
  before the extension and neither file is overwritten.
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
  in one file, every newly created entry is at physical EOF, asset references are flat,
  and no per-prompt directories exist.
- [ ] Run `git status` and a normal source-code staging exercise. Confirm generated
  `PROMPT_SOURCE.md` and `prompt_source_assets/` remain unstaged unless explicitly
  requested, while ordinary project files can be staged normally.
- [ ] Save the Desktop version and factual results with the Milestone 2 evidence; do not
  claim support for other environments based on this run.

## Standard-capture lifecycle

- [ ] Starting from the enabled final loader, dedicated file, and validator, complete an
  ordinary standard capture and record the history byte count and SHA-256.
- [ ] Change only the control line to `- Capture: disabled`, then submit a new Desktop
  interaction in the same task. Confirm the helper reports disabled and the history and
  assets remain byte-for-byte unchanged.
- [ ] Change only the control line back to `- Capture: enabled`, submit another
  interaction, and confirm capture resumes at physical EOF after the greatest structural
  entry number without rewriting older entries.
- [ ] Open a separate nested-project task sharing that history; confirm its first
  submission is `Initial prompt` even though the root history already contains entries.
- [ ] Confirm removing the loader, dedicated file, and validator is documented as stopping
  future standard capture without silently deleting existing history. Do not delete
  validation evidence merely to exercise that documented behavior.

## Optional hook-assisted validation

Run this section in another fresh disposable local Git project. Preserve earlier projects
and evidence. Use the final standard installation from the first Desktop prompt, and keep
the hook source and example definition inert until the listed explicit installation and
trust steps. Codex CLI is allowed only for `/hooks` review and trust; every capture case
uses Codex Desktop.

- [ ] Before installing hooks, complete one standard-capture interaction and confirm it is
  `Instruction-mediated`.
- [ ] Install the two reviewed Python files and exact project hook definitions. Before
  trust or activation, confirm another Desktop interaction still uses standard capture.
- [ ] In Codex CLI `/hooks`, separately review, enable, and trust the exact
  `UserPromptSubmit` and `Interrupt` definitions. Do not bypass trust.
- [ ] Fully restart Desktop, reopen the project, and start a new Desktop task.
- [ ] Submit an initial prompt with a known final-newline state. Independently inspect the
  stored UTF-8 bytes and confirm the hook's session ID, turn ID, byte count, digest, and
  final-newline field came from the event without publishing raw identifiers.
- [ ] Send an ordinary follow-up after completion. Confirm it has a different turn ID and
  is a separate claimed entry.
- [ ] During one active turn, send at least two steering messages. Confirm both remain
  separate and ordered and share the initiating turn ID.
- [ ] Submit the same text twice deliberately. Confirm two hook entries are created and
  claimed one-to-one rather than content-deduplicated.
- [ ] For every successful hook case, confirm agent enrichment claims the hook-created
  entry and does not append a duplicate.
- [ ] Send a correction. Confirm it points backward with `Supersedes` and leaves the
  earlier instruction unchanged.
- [ ] Complete a prompt that changes no task-work file and confirm `Changed files: None.`
- [ ] Attach a file or paste an image. Confirm user text, Desktop runtime context, and
  artifact metadata remain distinct; do not claim that the prompt hook captured binary
  data unless the actual event proves it.
- [ ] Start a long-running Desktop turn and press Stop. Confirm a trusted `Interrupt`
  event applies `Interrupted` with `Hook-confirmed Interrupt event.` only to unfinished
  entries having the matching session and turn IDs.
- [ ] Exercise an unmatched or ambiguous interrupt deterministically and confirm no
  history bytes change.
- [ ] Cause one hook invocation to be unavailable or fail without bypassing trust. Confirm
  the standard instruction-mediated path records the interaction successfully.
- [ ] Confirm successful hook capture followed by agent observation leaves exactly one
  entry for that interaction.
- [ ] Run the automated simultaneous-process test and confirm unique ordered entries and
  valid Markdown.
- [ ] Run failure injection before atomic replacement and confirm the last complete
  history remains byte-for-byte unchanged with no temporary file left behind.
- [ ] Inspect final topology: one root history, one flat optional assets directory, unique
  increasing structural numbers, and no persistent lock, log, status, input, result,
  runtime-context, or event-log file.
- [ ] Stage and commit ordinary disposable project work. Confirm generated history and
  assets remain unstaged, uncommitted, unpushed, unpublished, and unuploaded.
- [ ] Disable or remove both hooks, restart Desktop, and confirm the next interaction uses
  standard instruction-mediated capture successfully.

## Final 0.1.0 checks

- [ ] Validate the final history with the release hook core and deterministic format
  checks. Confirm unique increasing structural headings, canonical dynamic fences,
  newline reconstruction, required results, and schema marker 1.
- [ ] Confirm the final project contains no persistent lock, temporary, event-log, status,
  input, result, runtime-context, diagnostic, or bytecode-cache output.
- [ ] Confirm copied standard and hook assets match the release manifest before any
  deliberate failure injection; record non-sensitive sizes and SHA-256 values.
- [ ] Confirm generated provenance and optional hook installation files remain unstaged,
  uncommitted, unpushed, unpublished, and unuploaded, while an ordinary project file can
  be staged, committed, and pushed through the project's normal Git workflow.

For a new optional-hook implementation run, record case-by-case factual evidence without
rewriting the historical
[`CODEX_DESKTOP_HOOK_CAPTURE_VALIDATION.md`](CODEX_DESKTOP_HOOK_CAPTURE_VALIDATION.md).
For a 0.1.0 release run, record the final-bundle cases in
[`CODEX_DESKTOP_V1_RELEASE_READINESS.md`](CODEX_DESKTOP_V1_RELEASE_READINESS.md). Do not
mark the corresponding milestone complete unless every required Desktop-only case was
actually performed.
