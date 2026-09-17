# PromptSourceCode Format, Schema 1

## Status and scope

This document is the frozen, normative PromptSourceCode schema-1 contract for Codex
Desktop projects. It is shared by the standard, instruction-mediated capture path and the
explicitly enabled optional hook-assisted path. Schema-1 implementations may fix code or
clarify prose, but they MUST NOT reinterpret a valid schema-1 history or make one invalid.

Schema 1 has exactly two persistent outputs in a captured project:

```text
PROMPT_SOURCE.md
prompt_source_assets/
```

`PROMPT_SOURCE.md` is a single chronological history at the repository root.
`prompt_source_assets/` is a single flat directory for preserved artifact snapshots.
There are no per-prompt directories and no separate input, status, result, or runtime
context files.

The format targets Codex Desktop only. Standard capture does not require hooks, a skill,
a plugin, a background service, or network access. Hook assistance does not change the
two-output topology.

## Schema marker and versioning policy

The exact first-line marker is:

```text
<!-- prompt-source-schema: 1 -->
```

The integer is the storage-format compatibility version. It is not a product build,
release tag, Codex version, or semantic-version string. Schema 1 is a closed contract:
its entry metadata fields, structural sections, payload reconstruction rules, lifecycle,
and artifact semantics are the ones defined in this document.

A future change MUST use a new schema marker when it changes required storage topology,
required or permitted entry metadata, the interpretation of existing bytes, payload or
newline reconstruction, lifecycle transitions, artifact fidelity, or any other rule that
would make a valid schema-1 history mean something different or become invalid. Tests,
implementation corrections, and documentation clarifications may retain schema 1 only
when valid histories keep the same meaning and remain valid.

Schema 1 supplies no extension namespace and no automatic migration. An unrecognized
entry metadata field or structural variant is not silently discarded. A writer preserves
the existing bytes and stops rather than guessing. Future migration guidance must be
explicit and must preserve the source history and artifacts until a user deliberately
accepts conversion.

## Fidelity boundary

The text fidelity boundary is the exact text representation delivered by Codex Desktop
to the Codex agent. This may already differ from raw keystrokes or editor state because
Desktop can serialize or transform input before delivery. PromptSourceCode makes no
claim about content that precedes that boundary.

Standard capture is model-mediated: the agent observes the delivered representation and
writes it to the history. Reading that text back or hashing the stored representation can
check the stored file, but it is not independent verification against the source message.
The optional `UserPromptSubmit` hook captures the same agent-visible prompt string
deterministically; it does not move the fidelity boundary back to pre-serialization
editor state. Artifact and Desktop-context enrichment remains agent-mediated when the
event does not expose sufficient structured information.

## File initialization

The history file is UTF-8. Its first line MUST be the exact schema marker:

```text
<!-- prompt-source-schema: 1 -->
```

The complete initial header MUST be:

```markdown
<!-- prompt-source-schema: 1 -->

# Prompt Source

This file records the chronological user interactions that shaped this project. User
input is preserved at the Codex Desktop delivery boundary described by PromptSourceCode
format version 1.

Generated history and assets are local provenance. Do not stage, commit, push, publish,
or upload them unless the user explicitly requests it.
```

No initialization timestamp, repository name, user identity, model name, session ID, or
other unavailable value is added to the header. The first entry follows after one blank
line.

If a root `PROMPT_SOURCE.md` already exists, a writer MUST verify the first-line marker
before modifying it. An absent or different marker is not silently upgraded or
overwritten.

## Entry identity and order

Each distinct user interaction is one entry, in observation order:

```markdown
## Entry 000001
```

Entry numbers are positive decimal integers, padded to at least six digits. They begin at
`000001`, increase by exactly one in a newly initialized file, and are never reused. Once
six digits are exhausted, numbering continues without truncation as `1000000` and so on.

Immediately before appending, a writer MUST re-read the history and select one more than
the greatest valid structural entry heading, not one more than the number of entries. A
heading-like line inside a fenced user-input or runtime-context payload is data and is not
an entry. The writer MUST verify that the candidate does not already exist. If a
concurrent write creates that number, the writer re-reads, renumbers, and retries instead
of overwriting or duplicating it. Missing numbers are left missing. The optional hook
writer serializes its own writes and agent-helper replacements with a project-directory
lock and same-directory atomic replacement. Instruction-mediated capture used without
that helper does not claim multi-writer or crash-safe protection.

Identical user messages are still distinct interactions and receive distinct entries.
Content equality by itself is never a reason to suppress an entry.

Before appending, a writer MUST verify that existing structural entry headings are in
strictly increasing physical order. A structural conflict is reported rather than
silently compounded. The new entry MUST be appended at the physical end of the file; a
writer MUST NOT insert it after a matched result, blank line, heading, or other repeated
text. After writing the initial `In progress` entry and before requested project work, the
writer MUST re-read the structure and verify that the new entry is the final structural
entry and that physical order is still strictly increasing. If the initial write misplaced
the new unfinished block, the writer may move only that newly created block to physical
EOF without changing its contents, then MUST repeat the full verification. If the block's
exact boundary is uncertain, the writer reports the conflict and does not modify history.

## Entry metadata

An entry begins with these required fields in this order:

```markdown
## Entry 000001

- Interaction: Initial prompt
- Status: In progress
- Capture method: Instruction-mediated
```

### Interaction values

`Interaction` has one of these values:

- `Initial prompt`: the first user submission in a Codex task.
- `Follow-up`: a new user submission after the preceding work has finished.
- `Steering`: an additional instruction submitted while a turn is active.
- `Correction`: an instruction that retracts, replaces, or materially corrects an earlier
  instruction, whether it arrives during or after a turn.

Every initial prompt, follow-up, steering message, and correction gets a separate entry.
This remains true when the message causes no code changes, repeats text, abandons a
direction, or supersedes an earlier instruction.

### Capture method values

`Capture method` has one of these values:

- `Instruction-mediated`: the standard `AGENTS.md` instructions caused the agent to
  create the entry.
- `Hook-assisted`: an explicitly enabled hook captured the prompt and the agent reused or
  enriched that hook-created entry.

Standard capture MUST NOT label itself deterministic, hook-verified, independently
verified, or `Hook-assisted`.

### Optional metadata

The following fields are optional and, when present, follow `Capture method` in this
order:

```markdown
- Observed at: 2026-09-16T14:20:31-03:00
- Session ID: "hook-provided-session-id"
- Turn ID: "hook-provided-turn-id"
- Model: "runtime-provided-model-name"
- Agent observation: Claimed
- Deduplication note: Identity with a hook-created observation could not be established safely; both observations were preserved.
- Continues: Entry 000001
- Supersedes: Entry 000002
- Status reason: Completion reason unavailable; no reliable Interrupt event was observed.
```

- `Observed at` is an RFC 3339 timestamp included only when read from a reliable local
  clock or supplied by a trusted capture event. It is not reconstructed later.
- `Session ID` and `Turn ID` are JSON strings included only when a hook or reliable
  runtime context provides them. They are omitted during ordinary standard capture.
- `Model` is a JSON string included only when a hook or reliable runtime context provides
  it. It is not inferred from the user interface or filled in later.
- `Agent observation` is hook-only matching state. A hook creates the entry as `Pending`;
  exact one-to-one agent matching changes it to `Claimed`. It is omitted for
  instruction-created entries.
- `Deduplication note` records the exact safe-preservation outcome when hook/agent identity
  cannot be established. It is never used to suppress an observation.
- `Continues` refers to the entry most directly continued by a follow-up or steering
  message.
- `Supersedes` is required for a correction when the replaced entry can be identified
  reliably. It points backward and does not alter the earlier user input.
- `Status reason` is used as defined by the lifecycle below.

Unavailable optional values are normally omitted. If the absence itself matters, use the
literal `Unavailable` or a factual explanation. Never invent timestamps, identifiers,
model names, paths, byte counts, hashes, or reasons.

The metadata field set and ordering above are closed for schema 1. Unrecognized or
out-of-order entry metadata makes the history unsafe for a schema-1 writer to modify.
This prevents a schema-1 update from silently deleting or misinterpreting data written
under another contract.

## User input representation

Every entry has exactly one `### User input` section immediately after its metadata. It
contains an explicit final-newline field followed by a dynamically fenced payload:

~~~~~markdown
### User input

- Final newline: LF

````text
Please update the parser.
````
~~~~~

Allowed `Final newline` values are:

- `LF`
- `CRLF`
- `CR`
- `None`
- `Unknown`, only when the delivered representation does not expose the fact reliably

The payload and marker encode the delivered text as follows:

1. Determine whether the input ends in `LF`, `CRLF`, `CR`, no newline, or an unknown
   ending.
2. When the final newline is known and present, remove exactly that one final newline
   sequence from the payload body. Do not remove any other trailing blank lines or spaces.
3. Write the remaining text literally between the opening fence and its structural
   newline before the closing fence.
4. Reconstruction removes the one structural `LF` immediately before the closing fence,
   then appends the newline sequence named by `Final newline`. With `None`, it appends
   nothing. With `Unknown`, exact reconstruction of the ending is intentionally not
   claimed.

This rule distinguishes otherwise identical text with and without a final newline while
keeping the document valid Markdown. An empty payload is allowed.

### Dynamic fence rule

The payload fence is selected per section:

1. Find the longest consecutive run of backticks anywhere in the payload body.
2. Find the longest consecutive run of tildes anywhere in the payload body.
3. Choose the character whose longest run is shorter; choose backticks on a tie.
4. Use a fence of that character whose length is the greater of three or one more than
   its longest run.
5. Put `text` after the opening fence and use only the repeated character on the closing
   fence.

Because the delimiter is longer than every same-character run in the payload, Markdown
headings, links, backticks, tildes, nested or unusually long code fences, and text that
resembles PromptSourceCode headings or delimiters remain payload rather than structure.
Literal spaces, tabs, blank lines, misspellings, and Unicode are not normalized. HTML
entities or transformed links delivered by Desktop remain in their delivered form; the
writer does not reverse Desktop serialization.

These fields follow `Final newline` before the fence:

```markdown
- Stored UTF-8 bytes: 1234
- Stored SHA-256: 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
```

They describe the reconstructed stored payload, not independent equality with the source
message. They are required on `Hook-assisted` entries because the hook has the exact
string, and optional on instruction-mediated entries where they must be omitted rather
than guessed.

## Separating authorship and context

Only user-authored textual input belongs in `### User input`. The following do not:

- Codex Desktop attachment envelopes, source-path notices, safety instructions, or
  `My request` wrappers not authored by the user;
- synthetic `<image>` or similar markers produced by Desktop or an agent;
- filenames, source paths, byte counts, hashes, or preservation notes generated as
  artifact metadata; and
- agent summaries or results.

When Desktop supplies relevant agent-visible context that differs from the user-authored
text, add a separate optional section after `### User input`:

~~~~markdown
### Codex Desktop runtime context

- Final newline: None
- Boundary note: Desktop-generated attachment envelope; not user-authored.

```text
Agent-visible context goes here.
```
~~~~

Runtime-context payloads use the same final-newline and dynamic-fence rules. `Boundary
note` is factual prose. If authorship cannot be separated reliably, record that uncertainty
instead of silently classifying synthetic content as user-authored. Do not create a
separate runtime-context file.

## Artifact preservation and metadata

Artifacts are described in an optional `### Artifacts` section after runtime context, or
after user input when there is no runtime context. Each artifact is numbered locally
within its entry:

```markdown
### Artifacts

#### Artifact 1

- Kind: Attached file
- Original name (JSON): "requirements.pdf"
- Preserved copy: [prompt-000006-requirements.pdf](<prompt_source_assets/prompt-000006-requirements.pdf>)
- Byte count: 1266984
- SHA-256: b536084ff3cb9348e6a4a2f3fbb18eeab643ae2c50295dacedb2591e53665ac6
- Fidelity: Byte-for-byte copy of the attached original exposed by Codex Desktop.
```

`Kind` has one of these values:

- `Attached file`
- `Attached image`
- `Pasted image`

For a successfully preserved artifact, `Kind`, `Preserved copy`, `Byte count`, `SHA-256`,
and `Fidelity` are required. `Original name (JSON)` is optional because Desktop may not
provide one. `Repository source`, source byte count or digest, reuse notes, and a
pre-clipboard comparison are optional and appear only when directly observed and
verified. Arbitrary string values such as original names use JSON string syntax so quotes,
backslashes, Unicode, and control characters are unambiguous. Absolute external source
paths are omitted unless they add necessary factual context; they are never converted
into repository links.

An attached file or attached image is the original file exposed by Desktop. Copy it
without transformation and compare source and destination byte count and SHA-256 when the
source path remains available.

A pasted image is the temporary file materialized and exposed by Desktop. Preserve that
file byte-for-byte and use this exact fidelity statement as one physical Markdown field
line so its boundary is deterministic:

```text
Byte-for-byte copy of the clipboard image materialized by Codex Desktop; binary identity with any pre-clipboard source is not claimed.
```

A pasted image can have different metadata, compression, or binary encoding from an
unknown pre-clipboard source even when decoded pixels match. It MUST NOT be described as
the attached original.

### Flat asset names

All preserved copies are direct children of `prompt_source_assets/`. A name has this
shape:

```text
prompt-<entry-number>-<sanitized-stem><extension>
```

Use the entry number exactly as displayed. To form the remainder:

1. Take only the basename of the Desktop-provided filename; discard directory parts.
2. Treat the final suffix as an extension only when it is a dot followed by 1 to 16 ASCII
   letters or digits. Preserve that useful extension, lowercased. Otherwise preserve no
   extension rather than inventing one.
3. In the stem, replace each maximal run outside ASCII letters, digits, dot, underscore,
   and hyphen with one hyphen. Collapse repeated hyphens, remove leading dots, trim dots,
   underscores, and hyphens from both ends, and limit the result to 80 ASCII characters.
4. Use `artifact` when the sanitized stem is empty.
5. For a pasted image with no usable Desktop filename, use `image-001`, `image-002`, and
   so on within the entry, plus a safe extension actually present on the materialized
   file.

If the candidate already exists and its byte count and SHA-256 equal the artifact being
captured, reuse it and record that fact. If its contents differ, append `-002`, `-003`,
and so on before the extension until an unused name is found. Never overwrite an
unrelated file.

An attached source that already lives elsewhere in the repository is still copied into
the assets directory as a point-in-time snapshot. Record its repository-relative source
as an optional `Repository source` Markdown link. If the source is already a direct child
of `prompt_source_assets/`, verify and reuse it only when its bytes match; otherwise use
the collision rule.

`Preserved copy` links are relative to the root history file and use the literal
`prompt_source_assets/<filename>` path. Percent-encode characters that are unsafe in a
Markdown link destination and use angle brackets around the destination. No preserved
copy link may contain another `/` after `prompt_source_assets/`.

`Byte count` is the destination file size in decimal. `SHA-256` is the lowercase,
64-character digest of the destination. Record them only after the copy exists. For an
attached original, compare them with the source when possible. For a pasted image, compare
them with the Desktop-materialized temporary file when possible.

### Unavailable artifacts

When an external source is missing, inaccessible, or disappears before it can be copied,
keep the prompt entry and artifact record. Use:

```markdown
- Preservation: Unavailable
- Unavailable reason: Source data was no longer accessible when preservation was attempted.
```

Include an original name, source description, or reason only when observed reliably.
Omit `Preserved copy`, `Byte count`, and `SHA-256`; do not create a placeholder file or
invent metadata. A known operating-system error may be quoted factually. If the reason is
not known, use `Unavailable reason: Unknown`.

## Status lifecycle

`Status` has exactly four values.

The permitted status transitions are:

| Current state | Permitted next state | Authority |
| --- | --- | --- |
| `In progress` | `In progress` | Capture or enrichment may add verified initial metadata without finalizing work. |
| `In progress` | `Completed` | The handling agent, after the interaction is finished. |
| `In progress` | `Incomplete` | A later interaction or directly observed failure, without a matching trusted interrupt. |
| `In progress` | `Interrupted` | Only the trusted `Interrupt` hook for the exact session and turn. |
| Any terminal state | The same state only | Later safe enrichment may not change `Completed`, `Incomplete`, or `Interrupted` into another state. |

No transition may go back to `In progress`. `Completed`, `Incomplete`, and `Interrupted`
are terminal lifecycle states. A terminal entry's factual result may be completed or
clarified only without changing immutable captured content or changing that terminal
state.

### In progress

Create the entry with `Status: In progress` before performing the requested work. Copying
an ephemeral pasted-image source promptly is capture work, not the requested project
work. A steering message or correction received during the turn gets its own `In
progress` entry; it does not cause active related entries to be declared incomplete.

### Completed

Change the status to `Completed` only after handling that interaction finishes and add a
`### Result` section. Completion describes handling, not necessarily code modification. A
question answered without repository edits and an instruction superseded before it was
implemented can both complete, with the factual outcome in the result.

### Incomplete

If a later interaction finds a stale `In progress` entry from work that did not finish,
change it to `Incomplete`. When the cause is not reliably known, use this exact reason:

```markdown
- Status reason: Completion reason unavailable; no reliable Interrupt event was observed.
```

Do not infer interruption from an unfinished entry. Application exit, crash, shutdown,
tool failure, user interruption, and other causes can look identical to standard capture.
When a different cause is directly observed, state only that factual cause. A partial
result may be added if known.

### Interrupted

Use `Interrupted` only when an explicitly enabled hook reliably reports an `Interrupt`
event for the affected turn. The entry MUST be `Hook-assisted`, MUST include the supplied
session and turn IDs, and MUST contain:

```markdown
- Status reason: Hook-confirmed Interrupt event.
```

An agent instruction, a missing result, or a later guess can never produce this state.
When one turn contains multiple unfinished hook-assisted interactions, including steering
or corrections, a matching trusted `Interrupt` event changes every `In progress` entry
with the exact supplied session and turn IDs to `Interrupted`, in physical order. Entries
that already completed remain completed. No matching entry, an identifier mismatch, or
malformed history produces no status change.

## Results and changed files

A completed entry has one `### Result` section with a concise factual summary and changed
files:

```markdown
### Result

Implemented the requested parser update and added regression coverage.

Changed files:

- [src/parser.py](<src/parser.py>)
- [tests/test_parser.py](<tests/test_parser.py>)
```

Paths are repository-relative Markdown links. Use `Changed files: None.` when the
interaction caused no task-work file changes. Routine updates to `PROMPT_SOURCE.md` and
routine captured copies under `prompt_source_assets/` are provenance operations and are
not listed as task-work changes. If the user's requested work directly modifies those
paths, list them normally.

An incomplete or interrupted entry may have a result containing only known partial work.
An `In progress` entry has no result yet.

## Immutable and mutable content

The following are immutable once captured:

- entry number and chronological position;
- user-input payload, final-newline value, and any stored byte count or digest;
- observed runtime-context payload and its authorship boundary note;
- capture method and hook-provided identifiers; and
- artifact identity and verified preservation metadata.

The lifecycle fields `Status`, `Status reason`, and `Result` are mutable so unfinished
work can be finalized honestly. `Agent observation` may move only from `Pending` to
`Claimed`. A hook's provisional `Interaction` may be refined to `Correction`, with a
reliable backward `Supersedes` reference, during agent enrichment. Artifact metadata may
be appended while initial capture is still in progress, but observed values are not
rewritten later to match a changed file.

A correction or superseding instruction never deletes or edits an earlier entry. The new
entry uses `Interaction: Correction` and `Supersedes: Entry NNNNNN`; the earlier user input
and provenance remain untouched. The earlier entry's status and result may complete its
normal lifecycle, for example by stating that it was superseded before implementation,
but its original instruction is never rewritten. A completed earlier entry is not
retroactively changed merely because a later correction exists.

## Hook-assisted capture and deduplication

The optional hook enhancement produces this same document and entry schema. Its source
assets are inert until the user installs, reviews, enables, and trusts both exact hook
definitions and restarts Desktop. Standard capture remains active when hooks are absent,
disabled, untrusted, unavailable, or failing.

Before treating `UserPromptSubmit` or `Interrupt` as a capture event, the handler MUST
validate the hook-provided transcript's first `session_meta` record. Its session and
project path must match the event, `originator` must be `Codex Desktop`, and
`thread_source` must be `user`. A subagent marker, absent or unreadable transcript,
Desktop feature task, CLI task, or metadata mismatch is not a user interaction and MUST
fail closed without changing history. The ordinary instructions remain the fallback for
an actual user interaction whose hook cannot establish this boundary.

When a hook and the agent observe the same submission, there is exactly one entry:

1. A hook-created entry is marked `Hook-assisted` and records hook-provided session and
   turn IDs.
2. The hook marks the entry `Agent observation: Pending` and supplies synthetic matching
   context separately from user input. Before appending, the agent searches unfinished
   hook-created entries for the same session ID, turn ID, and exact prompt bytes. It
   claims and enriches the earliest unmatched entry in physical observation order.
3. Matching is one-to-one and order-preserving. Two intentionally repeated identical
   messages remain two entries; each hook observation can be claimed at most once.
4. A stored SHA-256 may accelerate comparison but does not replace exact-byte and
   identifier matching, and it is not a global content deduplication key.
5. If identity cannot be established reliably, the implementation preserves both
   observations. The instruction-created entry uses the exact `Deduplication note` above;
   neither observation is deleted or relabeled.
6. An instruction-created entry is never relabeled `Hook-assisted`.

The hook classifies later events sharing a turn ID as steering and different-turn events
in the same session as follow-ups; the agent can refine semantic corrections without
changing the captured prompt. `Interrupt` uses both identifiers and never infers a stop
from user prose or an unfinished entry.

### Hook write safety

Every hook append, claim, interruption, and agent-helper replacement MUST hold the same
writer lock, validate the complete schema-1 history, and use a temporary file in the
history's directory followed by atomic replacement. The writer rejects malformed or
truncated history, a non-schema-1 marker, duplicate or non-increasing structural entry
headings, stale expected entry content, and immutable-field changes. It does not silently
repair unrelated corruption.

The blank line between structural entries is a document separator, not part of either
entry's optimistic-concurrency identity. Appending a later entry therefore cannot change
the digest of an earlier unchanged entry; an actual edit to that entry still does.

Temporary files and locking exist only during an active operation. They are not
persistent project outputs. A failed replacement before the atomic rename leaves the
last complete history in place. Hook code performs no network or Git operations and
writes no persistent diagnostic log; failures use stderr and exit status.

The trusted hook definition MUST keep a handler failure nonblocking for Desktop message
delivery: it preserves a local stderr diagnostic but returns without matching context so
the standard instruction-mediated path receives the interaction. This guard applies only
to event invocation. Direct agent claim and replacement helpers retain nonzero failures
for stale, ambiguous, or unsafe updates.

## Ordering, concurrency, and crash-safety guarantees

Both capture methods produce the same chronological schema but have different mechanical
guarantees:

| Property | Standard instruction-mediated path | Optional hook-assisted path |
| --- | --- | --- |
| Entry order | Agent verifies increasing structural headings, appends at physical EOF, and rechecks before task work. | The handler validates the full history and appends at physical EOF while holding the writer lock. |
| Concurrent writers | Detect-and-retry instructions are required, but no multi-process serialization is claimed. | All appends, claims, interrupts, and replacements share one project-directory lock. |
| Crash safety | No atomic multi-writer or crash-safe guarantee is claimed. A later interaction preserves and resolves a stale unfinished entry honestly. | Same-directory temporary write, file `fsync`, atomic replacement, and directory `fsync`; failure before replacement retains the last complete history. |
| Persistent runtime state | Only the canonical history and preserved assets. | The same; lock and temporary files exist only during an operation and no event log is written. |

Neither path may repair unrelated history corruption. The standard path's only bounded
repair is moving its own newly created, still-unfinished block to physical EOF when that
block's exact boundary is known and verification occurs before task work. The hook path
performs no structural repair.

## Invalid, truncated, incompatible, and future histories

A writer distinguishes an absent history from an unsafe existing history:

- An absent `PROMPT_SOURCE.md` may be initialized with the canonical schema-1 header.
- An existing empty file, missing or different first-line marker, unsupported or future
  marker, invalid UTF-8, truncated payload, unclosed or noncanonical fence, invalid
  newline marker, duplicate metadata, unrecognized or out-of-order entry metadata,
  duplicate or non-increasing structural entry number, missing required field, invalid
  lifecycle state, or stale optimistic digest is a conflict.
- A numbering gap by itself is valid. Writers append one more than the greatest valid
  structural number and never fill the gap.
- On conflict, preserve the history bytes and artifacts, report the problem, and perform
  no append, claim, interruption, replacement, or automatic migration.
- A guarded event-hook failure emits no matching context so standard capture can remain
  available, but it does not authorize rewriting an incompatible history.

These rules also apply when a future PromptSourceCode version uses a marker other than
schema 1. Schema 1 stops safely; it never prepends its header, treats the file as empty,
or promises an unimplemented migration.

## Git policy

By default, PromptSourceCode MUST NOT stage, commit, push, publish, or upload generated
`PROMPT_SOURCE.md` or `prompt_source_assets/`. It may do so only when the user explicitly
requests inclusion of those generated provenance artifacts.

This restriction applies only to generated PromptSourceCode history and assets. It does
not restrict the normal Git workflow for source code, tests, documentation, or other
project files.

## Future PromptSourceCode compatibility

Future implementations that still claim schema-1 write compatibility MUST preserve every
existing immutable value and artifact byte, honor the same capture-method and lifecycle
rules, and append without renumbering or normalization. A reader may inspect a schema-1
history in an otherwise untested environment, but that does not establish support for
live capture there.

See [`COMPATIBILITY.md`](COMPATIBILITY.md) for tested environments, upgrade steps, and the
required stop behavior for non-schema-1 histories.
