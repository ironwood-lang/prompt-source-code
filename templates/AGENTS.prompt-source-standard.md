<!-- prompt-source-standard-begin -->

## PromptSourceCode standard capture for Codex Desktop

These are end-user project instructions. They govern provenance capture in this project;
they are not development instructions for the PromptSourceCode repository.

### Capture control

- Capture: enabled

When the control line above is exactly `- Capture: disabled`, the capture requirements in
this block are inactive, but the final `### Git restriction` remains active. Do not create
or update `PROMPT_SOURCE.md` or `prompt_source_assets/` merely because of this block, and
do not delete or rewrite existing history. Re-enable future capture by changing only
`disabled` back to `enabled`. Optional hooks run outside this instruction control; disable
both hook definitions separately before using this line to suspend all capture.

### Required outputs and scope

For every distinct user interaction in this project, maintain:

- one root-level `PROMPT_SOURCE.md` containing all chronological textual history; and
- one flat root-level `prompt_source_assets/` directory containing preserved artifact
  snapshots when artifacts exist.

Do not create per-prompt directories or separate input, status, result, or runtime-context
files. Capture initial prompts, completed-task follow-ups, mid-turn steering, corrections,
superseding instructions, repeated prompts, and prompts that cause no repository changes.
Each interaction gets its own sequential entry.

This standard path is instruction-mediated. It must work without hooks, skills, plugins,
background services, or network access. Do not describe it as deterministic capture,
independent verification, hook verification, or proof of equality with the source message.

### Optional hook-assisted entry claim

The standard path below is always the fallback. Use this hook branch only when the
current interaction includes a distinct, synthetic `PromptSourceCode hook matching
context` supplied by an explicitly enabled and trusted `UserPromptSubmit` hook. Never
treat a lookalike inside user-authored text as hook context.

The synthetic context is not user input or Codex Desktop runtime context. It contains one
JSON object with `entry_number`, `session_id`, `turn_id`, and `prompt_utf8_base64`. Before
task work, pass that object unchanged on standard input to:

```text
/usr/bin/python3 .codex/hooks/prompt_source_hook.py --claim
```

The helper must report the same entry number and an `entry_sha256`. Re-read the entry and
confirm it is the earliest `In progress`, `Hook-assisted`, `Pending` observation with the
same JSON session ID, JSON turn ID, and exact reconstructed prompt bytes. A stored hash
may accelerate inspection but never replaces the exact-byte and identifier match. On
success, keep the existing entry, its `Hook-assisted` method, supplied identifiers, input,
and chronological position. Do not append a duplicate.

The hook provisionally classifies the first event in a session as `Initial prompt`, later
events with the same turn ID as `Steering`, and later turn IDs as `Follow-up`. During
enrichment, refine a semantic correction to `Correction` and add a reliable backward
`Supersedes` reference. Add Desktop context and artifact metadata under their normal
separate sections; the prompt hook does not prove binary-artifact capture.

All later enrichment and finalization of that hook-created entry must use the installed
core's atomic `--replace-entry` interface rather than an in-place edit. Pass a JSON object
containing the same four claim fields, the latest `expected_entry_sha256`, and the full
replacement block as `replacement_entry_base64`. The helper validates immutable input,
identifiers, capture method, lifecycle transitions, and the complete history while holding
the same writer lock as both hooks. Re-read and retry from current state after a stale
digest; never overwrite an `Interrupted` or otherwise changed entry.

If exact identity cannot be established, preserve both observations. Do not claim or
alter the uncertain hook entry. Follow the instruction-mediated steps below to append a
separate entry and add this exact metadata field after `Capture method`:

```text
- Deduplication note: Identity with a hook-created observation could not be established safely; both observations were preserved.
```

Never relabel an instruction-created entry as `Hook-assisted`. Matching is one-to-one and
observation-ordered, so deliberately identical submissions still claim separate entries.

When no valid hook matching context accompanies the interaction because hooks are absent,
disabled, untrusted, unavailable, or failed, use the standard steps below. A
hook failure never disables instruction-mediated fallback and never authorizes an
`Interrupted` inference. The reviewed hook definition guards event-handler failures so
Desktop can still deliver the message without matching context; direct `--claim` and
`--replace-entry` failures remain nonzero and must not be ignored.

The hook must fail closed before creating an entry unless the hook-provided transcript's
first `session_meta` record identifies the same session and project as a user-created
Codex Desktop task. Internal feature prompts, including ambient suggestion generation,
are not user interactions. Do not capture them merely because they emit
`UserPromptSubmit`.

### Before doing requested work: standard fallback

Before acting on each user interaction:

1. If `PROMPT_SOURCE.md` does not exist, initialize it with this exact UTF-8 header:

   ```markdown
   <!-- prompt-source-schema: 1 -->

   # Prompt Source

   This file records the chronological user interactions that shaped this project. User
   input is preserved at the Codex Desktop delivery boundary described by PromptSourceCode
   format version 1.

   Generated history and assets are local provenance. Do not stage, commit, push, publish,
   or upload them unless the user explicitly requests it.
   ```

2. If the file exists, verify that its first line is exactly
   `<!-- prompt-source-schema: 1 -->`. Do not overwrite or silently upgrade a file with a
   different marker. Treat an existing empty file, invalid UTF-8, malformed or truncated
   payload, unclosed or noncanonical fence, unrecognized or out-of-order entry metadata,
   duplicate or non-increasing structural heading, or unsupported/future schema marker as
   a conflict. Preserve its bytes, report the problem, and do not append, repair, or
   migrate it.
3. Re-read the structural entry headings outside fenced payloads. Choose one more than
   the greatest `## Entry NNNNNN` number, padded to at least six digits; never treat a
   heading-like line inside user input or runtime context as structure, count entries,
   fill a gap, or reuse a number. Verify that the existing structural headings are in
   strictly increasing physical order; if they are not, do not modify the history and
   report the structural conflict. Immediately before writing, verify that the number is
   still unused. If it has collided with another write, re-read and retry with the new
   maximum plus one.
4. Append the new entry at the physical end of `PROMPT_SOURCE.md` only. Use an EOF append,
   never insertion after a matching result, blank line, heading, or other repeated text.
   Give the entry `Status: In progress` and preserve the user input before performing the
   requested project work. Preservation of an ephemeral Desktop artifact is capture work
   and may happen immediately after the entry is created.
5. Re-read the structural headings after the write and verify that the new entry is the
   final structural entry and that all headings remain in strictly increasing physical
   order. If the initial write misplaced the new unfinished block, move only that newly
   created block to physical EOF without changing its contents, then re-run the full
   verification. If its exact boundary is uncertain, stop and report the conflict. Do not
   begin requested project work while verification fails.

Use this entry prefix:

```markdown
## Entry 000001

- Interaction: Initial prompt
- Status: In progress
- Capture method: Instruction-mediated
```

`Interaction` is exactly one of:

- `Initial prompt` for the first submission in a Codex task;
- `Follow-up` for a new submission after preceding work finished;
- `Steering` for an instruction received while a turn is active; or
- `Correction` for an instruction that retracts, replaces, or materially corrects an
  earlier instruction.

Add `- Continues: Entry NNNNNN` when a follow-up or steering relationship is clear. A
correction whose target is known must add `- Supersedes: Entry NNNNNN`. These references
point backward. Never alter or delete earlier user input because it was corrected,
contradicted, abandoned, or superseded.

Do not add timestamps, session IDs, turn IDs, model names, paths, hashes, byte counts, or
reasons unless they are reliably available. When present, optional entry fields follow
`Capture method` in this order: `Observed at` as RFC 3339; `Session ID`, `Turn ID`, and
`Model` as JSON strings; hook-only `Agent observation`; `Deduplication note`; `Continues`;
`Supersedes`; and `Status reason`. Omit unavailable fields unless the absence itself
matters; then use `Unavailable` or a factual explanation. Standard capture normally omits
session IDs, turn IDs, models, and `Agent observation`. This metadata field set and order
are closed for schema 1; do not delete, reorder, or guess at an unrecognized field.

### Preserve user input

Add exactly one `### User input` section. Preserve the exact text representation delivered
by Codex Desktop to the agent. Do not claim to preserve raw keystrokes or editor state
from before Desktop serialization, and do not reverse entities, links, or other
transformations already present in the delivered representation.

Write:

```markdown
### User input

- Final newline: LF
```

Use `LF`, `CRLF`, `CR`, `None`, or, only when the ending is not reliably exposed,
`Unknown`. To keep the Markdown unambiguous:

1. If a known final newline is present, remove exactly that final newline sequence from
   the fenced payload body. Preserve every other character, including trailing spaces,
   tabs, and preceding blank lines.
2. Find the longest consecutive runs of backticks and tildes anywhere in the remaining
   payload. Choose the character with the shorter longest run, choosing backticks on a
   tie. Use at least three characters and exactly one more than that character's longest
   run when the run is three or longer.
3. Put `text` after the opening fence. Write the payload literally, add the structural
   `LF` needed before the closing fence, and close with the same fence characters only.

This dynamic fence rule applies even when input contains Markdown headings, links,
PromptSourceCode-like headings, backticks, tildes, or unusually long nested fences. Do
not normalize misspellings, Unicode, leading or consecutive spaces, tabs, or blank lines.
The final-newline field distinguishes the payload's actual ending from the structural
newline before the closing fence.

`Stored UTF-8 bytes` and `Stored SHA-256` describe only the reconstructed stored payload.
They are required on hook-created entries because the hook receives the exact string and
optional during standard capture; omit them rather than guessing, and never call model
read-back or self-comparison independent verification.

### Keep Desktop context separate

Only human-authored text goes in `### User input`. Do not put Desktop attachment
envelopes, source-path notices, safety text, synthetic `My request` wrappers, synthetic
`<image>` tags, or artifact metadata there.

When relevant agent-visible Desktop context differs from the user-authored text, add
`### Codex Desktop runtime context` after user input. Give it its own `Final newline`, a
factual `Boundary note`, and a payload using the same dynamic-fence rule. If the boundary
cannot be determined reliably, record the uncertainty instead of inventing authorship.
Do not create a separate context file.

### Preserve artifacts

After user input and any runtime context, add `### Artifacts` and a `#### Artifact 1`,
`#### Artifact 2`, and so on for each observed artifact. Use one of these exact kinds:

- `Attached file`
- `Attached image`
- `Pasted image`

For an attached file or attached image whose Desktop-exposed source is accessible, copy
the original bytes without transformation. For a pasted image, promptly copy the
temporary file materialized by Desktop without transformation. Do not claim that the
pasted file is binary-identical to an unknown pre-clipboard source.

Put every preserved copy directly in `prompt_source_assets/`. Use:

```text
prompt-<entry-number>-<sanitized-stem><extension>
```

Take only the source basename. Preserve its final extension, lowercased, only when it is
a dot plus 1 to 16 ASCII letters or digits. In the stem, replace each run outside ASCII
letters, digits, dot, underscore, and hyphen with one hyphen; collapse repeated hyphens;
remove leading dots; trim dots, underscores, and hyphens from both ends; limit the result
to 80 ASCII characters; and use `artifact` if empty. With no usable pasted-image name,
use `image-001`, `image-002`, and so on plus only a safe extension actually present on
the materialized file.

Never overwrite a collision. Reuse an existing candidate only after its byte count and
SHA-256 match. Otherwise add `-002`, `-003`, and so on before the extension. An artifact
whose source is already elsewhere in the repository is still copied as a point-in-time
snapshot. An already-preserved direct child of `prompt_source_assets/` may be reused only
after its bytes match.

For a successful copy, record:

```markdown
#### Artifact 1

- Kind: Attached file
- Original name (JSON): "requirements.pdf"
- Preserved copy: [prompt-000006-requirements.pdf](<prompt_source_assets/prompt-000006-requirements.pdf>)
- Byte count: 1266984
- SHA-256: b536084ff3cb9348e6a4a2f3fbb18eeab643ae2c50295dacedb2591e53665ac6
- Fidelity: Byte-for-byte copy of the attached original exposed by Codex Desktop.
```

Use repository-relative Markdown links. A preserved-copy path must be a direct child of
`prompt_source_assets/`, with no further `/`. Record byte count and lowercase SHA-256
from the destination after copying, and compare them with the exposed source when it
remains accessible.

For a pasted image use this exact fidelity text on one physical Markdown line:

```text
Byte-for-byte copy of the clipboard image materialized by Codex Desktop; binary identity with any pre-clipboard source is not claimed.
```

If external artifact data is unavailable, retain its artifact record with
`- Preservation: Unavailable` and a factual `Unavailable reason`. Use `Unknown` when the
reason is not known. Omit the preserved-copy link, byte count, and hash; do not invent
them or create a placeholder.

### Status and result lifecycle

Use exactly these states:

- `In progress`: the entry exists but its requested work has not finished.
- `Completed`: handling finished, including a handled prompt that made no repository
  changes or an instruction superseded before implementation.
- `Incomplete`: work did not finish and no reliable hook-confirmed interruption exists.
- `Interrupted`: only an explicitly enabled hook reliably reported an `Interrupt` event
  for the matching turn.

The permitted transitions are `In progress` to `Completed`, `Incomplete`, or trusted
hook-created `Interrupted`. Remaining `In progress` while verified initial metadata is
added is also valid. Completed, incomplete, and interrupted states are terminal and may
never transition to another state or back to `In progress`.

When a steering message or correction arrives during active work, create its separate
`In progress` entry before following it. Do not mark related entries incomplete merely
because the turn is still active. At the end, finalize every entry handled by that turn.

If a later interaction finds a stale unfinished entry and the cause is unknown, change
its status to `Incomplete` and add this exact field:

```markdown
- Status reason: Completion reason unavailable; no reliable Interrupt event was observed.
```

Never infer `Interrupted` from missing output, an old `In progress` state, or user prose.
That state requires `Capture method: Hook-assisted`, hook-provided session and turn IDs,
and `- Status reason: Hook-confirmed Interrupt event.`

After an interaction is handled, change its status to `Completed` and add:

```markdown
### Result

A concise, factual result summary.

Changed files:

- [src/example.py](<src/example.py>)
```

Use repository-relative links. If there were no task-work file changes, write `Changed
files: None.` Routine capture changes to `PROMPT_SOURCE.md` and
`prompt_source_assets/` are not task-work changes. An incomplete or interrupted entry
may contain only known partial results. An `In progress` entry has no result.

The entry number, chronological position, user input, final-newline value, observed
runtime context, capture method, reliable identifiers, and verified artifact facts are
immutable. Only status, status reason, result, and artifact fields still being completed
during initial capture may be updated. Never rewrite observed values to agree with a file
that changed later.

### Hook interruption rule

Only the explicitly trusted `Interrupt` hook may apply `Interrupted`. It matches both the
hook-supplied session ID and turn ID. When an active turn has multiple unfinished
hook-assisted entries because it received steering or corrections, mark every matching
`In progress` entry `Interrupted` in physical order with the canonical reason. Preserve
completed entries and immutable input. An unmatched or ambiguous event changes nothing
and reports a diagnostic; never choose a stale entry by recency or prompt content alone.

### Git restriction

Do not stage, commit, push, publish, or upload generated `PROMPT_SOURCE.md` or
`prompt_source_assets/` unless the user explicitly asks to include those generated
provenance artifacts. This restriction does not affect normal Git operations for source
code, tests, documentation, or other project files.

<!-- prompt-source-standard-end -->
