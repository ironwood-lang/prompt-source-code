# PromptSourceCode Format, Version 1

## Status and scope

This document defines the canonical version 1 format produced by PromptSourceCode for
Codex Desktop projects. It is the normative contract shared by the standard,
instruction-mediated capture path and the future optional hook-assisted path.

Version 1 has exactly two persistent outputs in a captured project:

```text
PROMPT_SOURCE.md
prompt_source_assets/
```

`PROMPT_SOURCE.md` is a single chronological history at the repository root.
`prompt_source_assets/` is a single flat directory for preserved artifact snapshots.
There are no per-prompt directories and no separate input, status, result, or runtime
context files.

The format targets Codex Desktop only. Standard capture does not require hooks, a skill,
a plugin, a background service, or network access.

## Fidelity boundary

The text fidelity boundary is the exact text representation delivered by Codex Desktop
to the Codex agent. This may already differ from raw keystrokes or editor state because
Desktop can serialize or transform input before delivery. PromptSourceCode makes no
claim about content that precedes that boundary.

Standard capture is model-mediated: the agent observes the delivered representation and
writes it to the history. Reading that text back or hashing the stored representation can
check the stored file, but it is not independent verification against the source message.
A future hook can capture the same agent-visible prompt string deterministically; it does
not move the fidelity boundary back to pre-serialization editor state.

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
of overwriting or duplicating it. Missing numbers are left missing. Full multi-writer
locking and crash-safe writes belong to the optional hook implementation;
instruction-mediated capture does not claim that protection.

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
- `Hook-assisted`: an explicitly enabled future hook captured the prompt and the agent
  reused or enriched that hook-created entry.

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
- `Continues` refers to the entry most directly continued by a follow-up or steering
  message.
- `Supersedes` is required for a correction when the replaced entry can be identified
  reliably. It points backward and does not alter the earlier user input.
- `Status reason` is used as defined by the lifecycle below.

Unavailable optional values are normally omitted. If the absence itself matters, use the
literal `Unavailable` or a factual explanation. Never invent timestamps, identifiers,
model names, paths, byte counts, hashes, or reasons.

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

When known and useful, these optional fields may follow `Final newline` before the fence:

```markdown
- Stored UTF-8 bytes: 1234
- Stored SHA-256: 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
```

They describe the reconstructed stored payload, not independent equality with the source
message. Omit them rather than guessing.

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
work can be finalized honestly. Artifact metadata may be appended while initial capture
is still in progress, but observed values are not rewritten later to match a changed
file.

A correction or superseding instruction never deletes or edits an earlier entry. The new
entry uses `Interaction: Correction` and `Supersedes: Entry NNNNNN`; the earlier user input
and provenance remain untouched. The earlier entry's status and result may complete its
normal lifecycle, for example by stating that it was superseded before implementation,
but its original instruction is never rewritten. A completed earlier entry is not
retroactively changed merely because a later correction exists.

## Future hook deduplication contract

The optional hook enhancement MUST produce this same document and entry schema. When a
hook and the agent observe the same submission, there is still exactly one entry:

1. A hook-created entry is marked `Hook-assisted` and records hook-provided session and
   turn IDs.
2. Before appending, the agent searches recent unfinished hook-created entries for the
   same session ID, turn ID, and exact prompt bytes. It enriches the earliest unmatched
   entry rather than adding another.
3. Matching is one-to-one and order-preserving. Two intentionally repeated identical
   messages remain two entries; each hook observation can be claimed at most once.
4. A stored SHA-256 may accelerate comparison but does not replace exact-byte and
   identifier matching, and it is not a global content deduplication key.
5. If identity cannot be established reliably, the implementation preserves both
   observations and marks the uncertainty rather than silently deleting history.

The hook design must also associate all steering entries and any `Interrupt` event with
the supplied turn ID. Implementing hooks, trust onboarding, locking, and concurrent-write
protection is outside Milestone 1.

## Git policy

By default, PromptSourceCode MUST NOT stage, commit, push, publish, or upload generated
`PROMPT_SOURCE.md` or `prompt_source_assets/`. It may do so only when the user explicitly
requests inclusion of those generated provenance artifacts.

This restriction applies only to generated PromptSourceCode history and assets. It does
not restrict the normal Git workflow for source code, tests, documentation, or other
project files.
