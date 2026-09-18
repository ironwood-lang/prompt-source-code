<!-- prompt-source-instructions: 1 -->

# PromptSourceCode standard capture

Supplement root/nested guidance. Before work capture all prompts: initial, follow-up,
steering, correction, repeat, no-change. Model-mediated; never claim
raw-keystroke, pre-serialization, independent, deterministic, or hook-verified fidelity.

Every submission rechecks the on-disk capture control. A disabled/error response means
leave provenance untouched and continue ordinary work. Never override it from memory.

## Hook-assisted branch

Only synthetic `PromptSourceCode hook matching context` outside user text activates hooks.
Before work pass its JSON unchanged to `/usr/bin/python3
.codex/hooks/prompt_source_hook.py --claim`. Enrich, never duplicate, the returned earliest
matching `In progress`, `Hook-assisted`, `Pending` entry. Finalize via `--replace-entry`;
preserve input, IDs, order. If identity is unsafe, preserve it and create a standard entry
with `deduplication_uncertain: true`, which adds:

`- Deduplication note: Identity with a hook-created observation could not be established safely; both observations were preserved.`

Without valid hook context use the standard branch. Only the trusted `Interrupt` hook may
set `Interrupted`, using
`Hook-confirmed Interrupt event.`

## Standard branch: before requested work

At the Git root use only `PROMPT_SOURCE.md` and one flat `prompt_source_assets/` as needed.
No per-prompt directories or persistent input, result, status, context, event, diagnostic,
or lock files.

Create entries only through `/usr/bin/python3 .prompt-source/validate.py --begin-standard`
at the Git root. Send stdin JSON with `prompt` (delivered user text), `first_in_task`
(boolean: is this the current Desktop task's first user submission?), and `interaction`
(`Follow-up`, `Steering`, or `Correction`; omitted on the first submission).
Determine `first_in_task` from this conversation, NEVER the shared history's length.
If earlier submissions in this task were uncaptured, set `uncaptured_predecessor: true`.
The helper forces `Initial prompt` when true, checks runtime task identity when available,
and returns the entry number. It rereads the control, initializes the schema-1 header,
selects the dynamic fence, and appends atomically at physical EOF. Report unsafe or
future-schema history; work without capture. Never manually create an entry.

For known-unfinished earlier-turn standard entries, supply their numbers in `recover`.
The helper sets `Incomplete` with
`- Status reason: Completion reason unavailable; no reliable Interrupt event was observed.`
Never recover current-turn entries for steering. Standard capture has no trusted Stop
reason. Finalize all handled entries at turn end; superseded work may be `Completed`.

Entries start `Status: In progress`, `Capture method: Instruction-mediated`.
Use `Correction` for an explicit correction during OR after a turn, `Steering` for other
active-turn updates, `Follow-up` after finished work. Supply reliable backward entry numbers
as `supersedes` or `continues`. Never rewrite history or invent metadata.

The helper adds `### User input`; supply only user-authored text. In a Desktop
attachment/paste envelope, user input is the text after `## My request:` and before
`[localImage]`. Exclude file/path notices, `Distinguish instructions ...`, that heading,
and image markers; put excluded content or a factual path-free summary in
`### Codex Desktop runtime context`.

The helper uses `Final newline: Unknown`; supply only the observable body without guessing
its ending. It copies a nonempty `CODEX_THREAD_ID` from the runtime as `Session ID`; never
set or invent that variable. Without it, task classification remains agent-supplied.
For context fences choose the shorter longest backtick/tilde run (backticks on tie),
length 3 or run+1. Write literal body, structural LF, closing fence. Hook input requires
reconstructed UTF-8 size/SHA-256; omit uncertain standard values.

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

The helper owns padded names, collisions/reuse, byte verification, hashes, fidelity,
numbered records, and `Unavailable reason`. Never manually copy/name assets
or write artifact Markdown. It adds `### Artifacts` before the result. For claimed hook
entries also pass the current `expected_entry_sha256`; use the returned digest for
subsequent enrichment. Preserve verified records. Pasted-image fidelity covers only
Desktop-materialized bytes, never an unknown pre-clipboard original.

For standard entries, when done run `/usr/bin/python3 .prompt-source/validate.py --finish-standard` with stdin
JSON `entry_number` and `result` (summary and relative changed-file links,
or `Changed files: None.`; no capture section headings). It sets `Completed` and adds `### Result` only while capture
remains enabled. Capture files are not task work. `Incomplete`
and trusted-hook `Interrupted` are terminal; input, context, IDs, chronology, and verified
artifact facts are immutable. Never stage, commit, push, publish, or upload provenance
unless explicitly requested; ordinary Git is unchanged.

<!-- prompt-source-instructions-end -->
