<!-- prompt-source-instructions: 1 -->

# PromptSourceCode capture

Supplement root/nested guidance. Before work capture all prompts: initial, follow-up,
steering, correction, repeat, no-change. Model-mediated; never claim
raw-keystroke, pre-serialization, independent, deterministic, or hook-verified fidelity.

Recheck on-disk control every submission. On disabled/error, leave provenance untouched
and continue ordinary work.

## Classification: both branches

Use `Correction` for an explicit correction during OR after a turn, `Steering` for other
active-turn updates, `Follow-up` after finished work. Corrections require `supersedes`:
earlier entry number, or null if unknown. Never rewrite history or invent metadata.

## Hook-assisted branch

Only synthetic `PromptSourceCode hook matching context` outside user text activates hooks.
Before work pass its JSON unchanged to `/usr/bin/python3
.codex/hooks/prompt_source_hook.py --claim`. Enrich, never duplicate, the returned earliest
matching `In progress`, `Hook-assisted`, `Pending` entry. Preserve input, IDs, order.
Complete all handled hook entries via `--finish-hook` at turn end.
Send the claim JSON plus current `expected_entry_sha256`, explicit `interaction`,
`supersedes` for corrections, `result` (summary only), and `changed_files` (`[]` for none).
Never keep `Steering` for a correction. The helper renders metadata/results.
If identity is unsafe, preserve it and create a standard entry
with `deduplication_uncertain: true`, which adds:

`- Deduplication note: Identity with a hook-created observation could not be established safely; both observations were preserved.`

Without valid hook context use the standard branch. Only the trusted `Interrupt` hook may
set `Interrupted`, using
`Hook-confirmed Interrupt event.`

## Standard branch: before requested work

Use only root `PROMPT_SOURCE.md` and flat `prompt_source_assets/`. No per-prompt
directories or persistent input, result, status, context, event, diagnostic, or lock files.

Create entries only through `/usr/bin/python3 .prompt-source/validate.py --begin-standard`
at the Git root. Send stdin JSON with `prompt` (delivered user text), `first_in_task`
(boolean: is this the current Desktop task's first user submission?), and `interaction`
(`Follow-up`, `Steering`, or `Correction`; omitted on the first submission).
Determine `first_in_task` from this conversation, NEVER history length.
If earlier submissions in this task were uncaptured, set `uncaptured_predecessor: true`.
The helper forces `Initial prompt` when true and returns its number. It rereads
control, initializes schema 1, and appends atomically at physical EOF. Report unsafe or
future-schema history; work without capture. Never manually create an entry.

For known-unfinished earlier-turn standard entries, supply their numbers in `recover`.
The helper sets `Incomplete` with
`- Status reason: Completion reason unavailable; no reliable Interrupt event was observed.`
Never recover current-turn entries for steering. Standard capture has no trusted Stop
reason. Finalize all handled entries at turn end; superseded work may be `Completed`.

Entries start `Status: In progress`, `Capture method: Instruction-mediated`.
Optional `continues` identifies an earlier entry for non-corrections.

The helper adds `### User input`; supply only user-authored text. In a Desktop
attachment/paste envelope, user input is the text after `## My request:` and before
`[localImage]`. Exclude file/path notices, `Distinguish instructions ...`, that heading,
and image markers. For observed attachments/pastes, `--preserve-artifact` adds a
factual path-free summary in `### Codex Desktop runtime context` automatically.

The helper uses `Final newline: Unknown`; never guess the ending. It copies runtime
`CODEX_THREAD_ID` as `Session ID`; never set or invent it. Helpers own fences and integrity
metadata. Hook claims already separate recognized Desktop envelopes; never rewrite them.

Before work and finalization run
`cd "$(git rev-parse --show-toplevel)" && /usr/bin/python3 .prompt-source/validate.py --validate-history`.
Fix only this new entry on failure; a missing validator stops capture, not work.

## Artifacts and completion

Before work, preserve each attachment, paste, or requested source using
`/usr/bin/python3 .prompt-source/validate.py --preserve-artifact` at the Git root.
Send stdin JSON `entry_number` and `source` (observed path, relative to the Git root).
For filesystem requests OMIT `kind`: the helper classifies inside-project
sources as `Repository file snapshot`, others as `Requested artifact`.
Only actual Desktop attachments/pastes supply `kind`: `Attached file`, `Attached image`,
or `Pasted image`. Optional `original_name` is the observed filename; use null for an
unnamed paste. If no source path was exposed, omit `source` and supply a factual,
path-free `unavailable_reason`, or `Unknown`. Never invent a source path.

The helper owns naming, copies, hashes, fidelity, and `Unavailable reason`.
Never manually copy/name assets or write artifact Markdown. It adds `### Artifacts`.
For claimed hook entries pass current `expected_entry_sha256`; use the returned digest for
subsequent enrichment. Preserve verified records. Pasted-image fidelity covers only
Desktop-materialized bytes, never an unknown pre-clipboard original.

Complete standard entries via `/usr/bin/python3 .prompt-source/validate.py --finish-standard`.
Send stdin JSON `entry_number`, `result` (summary only), and `changed_files`
(relative task-work paths; `[]` for none). The helper renders
links or `Changed files: None.`, excluding capture files. Only for explicit user-requested
provenance edits set `provenance_changes_requested: true`.
Attachment-preservation requests are routine capture, not task work.
It sets `Completed` only while enabled. `Incomplete` and trusted-hook `Interrupted` are
terminal; input, context, IDs, chronology, and verified
artifact facts are immutable. Never stage, commit, push, publish, or upload provenance
unless explicitly requested; ordinary Git is unchanged.

<!-- prompt-source-instructions-end -->
