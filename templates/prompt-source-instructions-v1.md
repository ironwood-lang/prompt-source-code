<!-- prompt-source-instructions: 1 -->

# PromptSourceCode standard capture

Supplement root/nested guidance. Before work capture each prompt, follow-up, steering,
correction, repeat, and no-change request. Capture is model-mediated; never claim
raw-keystroke, pre-serialization, independent, deterministic, or hook-verified fidelity.

## Hook-assisted branch

Only synthetic `PromptSourceCode hook matching context` outside user text activates hooks.
Before work pass its JSON unchanged to `/usr/bin/python3
.codex/hooks/prompt_source_hook.py --claim`. Enrich, never duplicate, the returned earliest
matching `In progress`, `Hook-assisted`, `Pending` entry. Finalize through `--replace-entry`;
preserve input, IDs, and order. If identity is unsafe, preserve it and add a standard entry
with:

`- Deduplication note: Identity with a hook-created observation could not be established safely; both observations were preserved.`

Without valid hook context use the standard branch. Only the trusted `Interrupt` hook may
set `Interrupted`, using
`Hook-confirmed Interrupt event.`

## Standard branch: before requested work

At the Git root use only `PROMPT_SOURCE.md` and one flat `prompt_source_assets/` as needed.
No per-prompt directories or persistent input, result, status, context, event, diagnostic,
or lock files.

If history is absent, create this exact UTF-8 header:

```text
<!-- prompt-source-schema: 1 -->

# Prompt Source

This file records the chronological user interactions that shaped this project. User
input is preserved at the Codex Desktop delivery boundary described by PromptSourceCode
format version 1.

Generated history and assets are local provenance. Do not stage, commit, push, publish,
or upload them unless the user explicitly requests it.
```

Otherwise require valid schema-1 UTF-8: canonical fences, ordered metadata, one user-input
section per entry, increasing headings, and valid lifecycle/results. Preserve and report
unsafe or future-schema history; work without capture.

Before appending, change only a known-unfinished earlier-turn standard `In progress` to
`Incomplete`; never change current-turn entries for steering. Standard capture has no
trusted Stop reason; always add
`- Status reason: Completion reason unavailable; no reliable Interrupt event was observed.`
At turn end finalize handled entries; superseded work may be `Completed`. Preserve terminal
entries and earlier input.

Append at physical EOF, one above the greatest structural number and padded to six or more
digits; never fill gaps. Re-read before writing; retry collisions. Start:

```text
## Entry 000001

- Interaction: Initial prompt
- Status: In progress
- Capture method: Instruction-mediated
```

`Initial prompt`: the current Desktop task's first submission even with history. `Follow-up`:
after a finished turn. `Steering` for every active-turn submission, even replacing values
or saying “instead”. `Correction`: only a later turn explicitly identifying a correction
or mistake. Only corrections use `Supersedes`; others add reliable backward `Continues`.
Never rewrite history. Optional metadata:
`Observed at`, `Session ID`, `Turn ID`, `Model`, `Agent observation`, `Deduplication note`,
`Continues`, `Supersedes`, `Status reason`. Never invent values.

Add one `### User input` containing only user-authored Desktop-delivered text. `Final
newline`: `LF`, `CRLF`, `CR`, `None`, or `Unknown`; standard uses `Unknown` unless reliably
exposed, never guessed `None`. If known, remove only that final sequence. Find longest
backtick/tilde runs; choose the shorter (backticks on tie), length 3 or run+1. Always
calculate: any backtick and no tilde requires `~~~text`, not ```text. Write literal body,
one structural LF, then the closing fence. Hook entries require reconstructed UTF-8
size/SHA-256; omit uncertain standard values. Put Desktop context in `### Codex Desktop
runtime context` under the same rules.

Re-read: the new entry must be final with increasing headings. Before work, move only this
exact unfinished block to EOF if misplaced; otherwise stop capture.

Before work and finalization run
`cd "$(git rev-parse --show-toplevel)" && /usr/bin/python3 .prompt-source/validate.py --validate-history`.
Fix only this new entry on failure; a missing validator stops capture, not work.

## Artifacts and completion

Copy accessible attachments, pasted images, and repository sources byte-for-byte as direct
children. Name from the basename: `prompt-<entry>-<stem><extension>`. Lowercase a final
1–16 ASCII-alphanumeric extension. In the stem replace other runs with `-`, collapse
hyphens, remove leading dots, trim punctuation, cap at 80 characters, and use `artifact`
if empty. Unnamed pastes use `image-001`. Reuse identical bytes; otherwise add `-002`, etc.
Number records locally and use this exact field spelling/order:

```text
#### Artifact 1
- Kind: Attached file
- Original name (JSON): "name"
- Preserved copy: [filename](<prompt_source_assets/filename>)
- Byte count: 0
- SHA-256: lowercase digest
- Fidelity: factual boundary
```

Kind is `Attached file`, `Attached image`, `Pasted image`, `Repository file snapshot`, or
`Requested artifact`. A pasted image uses this physical line:

`- Fidelity: Byte-for-byte copy of the clipboard image materialized by Codex Desktop; binary identity with any pre-clipboard source is not claimed.`

If unavailable, use numbered `Kind`, optional `Original name (JSON)`, `Preservation:
Unavailable`, and `Unavailable reason`; omit copy, size, hash, and placeholders. Exclude
absolute external paths from artifact metadata.

When done set `Completed`; add one `### Result` with a factual summary and relative changed
file links, or `Changed files: None.` Capture files are not task-work changes. `Incomplete`
and trusted-hook `Interrupted` are terminal; input, context, IDs, chronology, and verified
artifact facts are immutable. Never stage, commit, push, publish, or upload provenance
unless explicitly requested; ordinary Git is unchanged.

<!-- prompt-source-instructions-end -->
